#!/usr/bin/env python3
"""Run compile.py over every problem and print the metrics table.

    python tools/test.py                    # problems/ + corpus/ on the local GPU
    python tools/test.py p0 r0              # only problem ids starting with these prefixes
    python tools/test.py --ref              # also time emmy's ref.cu (built with NVRTC) for speed ratios
    python tools/test.py --remote           # check correctness on the hosted runner via submit.py instead

Each problem runs in its own subprocess (`--worker`) so a crashing kernel cannot poison the
CUDA context of the next one. Results are appended to metrics/history.jsonl and the table is
written to metrics/latest.md.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SETS = [ROOT / "problems", ROOT / "corpus"]
CATEGORY = {"p": "1 pointwise", "r": "2 reduction", "m": "3 matmul", "f": "4 fused", "a": "5 attention"}
# The unmarked Kernel IR vocabulary of TASK.md: 17 statements + 4 expressions.
NODE_KINDS = ["Tile", "Load", "Assign", "Let", "Accum", "Init", "Write", "Loop", "StridedLoop",
              "Cond", "Smem", "Sync", "CpAsyncCopy", "CpAsyncCommit", "CpAsyncWait", "WarpShuffle",
              "TreeHalve", "Var", "Literal", "BinaryExpr", "TernaryExpr"]
EXPR_KINDS = {"Var", "Literal", "BinaryExpr", "TernaryExpr"}


# ---- the local GPU, through the CUDA driver API ----------------------------------------
class Gpu:
    def __init__(self):
        self.cu = ctypes.WinDLL("nvcuda.dll") if sys.platform == "win32" else ctypes.CDLL("libcuda.so.1")
        self.check(self.cu.cuInit(0), "cuInit")
        dev, ctx = ctypes.c_int(), ctypes.c_void_p()
        self.check(self.cu.cuDeviceGet(ctypes.byref(dev), 0), "cuDeviceGet")
        self.check(self.cu.cuDevicePrimaryCtxRetain(ctypes.byref(ctx), dev), "cuDevicePrimaryCtxRetain")
        self.check(self.cu.cuCtxSetCurrent(ctx), "cuCtxSetCurrent")

    def check(self, err, what):
        if err:
            name = ctypes.c_char_p()
            self.cu.cuGetErrorName(err, ctypes.byref(name))
            raise RuntimeError(f"{what}: {name.value.decode() if name.value else err}")

    def function(self, cubin: bytes, entry: str, smem: int):
        mod, fn = ctypes.c_void_p(), ctypes.c_void_p()
        self.check(self.cu.cuModuleLoadData(ctypes.byref(mod), cubin), "cuModuleLoadData")
        self.check(self.cu.cuModuleGetFunction(ctypes.byref(fn), mod, entry.encode()),
                   f"cuModuleGetFunction({entry})")
        if smem > 48 * 1024:   # CU_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES
            self.check(self.cu.cuFuncSetAttribute(fn, 8, smem), "cuFuncSetAttribute")
        return fn

    def alloc(self, arr: np.ndarray) -> ctypes.c_uint64:
        p = ctypes.c_uint64()
        self.check(self.cu.cuMemAlloc_v2(ctypes.byref(p), ctypes.c_size_t(max(arr.nbytes, 4))), "cuMemAlloc")
        self.check(self.cu.cuMemcpyHtoD_v2(p, ctypes.c_void_p(arr.ctypes.data), ctypes.c_size_t(arr.nbytes)), "cuMemcpyHtoD")
        return p

    def zero(self, p, nbytes):
        self.check(self.cu.cuMemsetD8_v2(p, 0, ctypes.c_size_t(nbytes)), "cuMemsetD8")

    def read(self, p, like: np.ndarray) -> np.ndarray:
        out = np.empty_like(like)
        self.check(self.cu.cuMemcpyDtoH_v2(ctypes.c_void_p(out.ctypes.data), p, ctypes.c_size_t(out.nbytes)), "cuMemcpyDtoH")
        return out

    def launch(self, fn, k, ptrs, sync=True):
        params = (ctypes.c_void_p * len(ptrs))(*[ctypes.cast(ctypes.byref(p), ctypes.c_void_p) for p in ptrs])
        g, b = k["grid"], k["block"]
        self.check(self.cu.cuLaunchKernel(fn, g[0], g[1], g[2], b[0], b[1], b[2], k["smem_bytes"],
                                          None, params, None), "cuLaunchKernel")
        if sync:
            self.check(self.cu.cuCtxSynchronize(), "kernel execution")

    def time_us(self, fn, k, ptrs, iters=50, reps=5) -> float:
        """Median over `reps` of the mean time of `iters` back-to-back launches (after warmup)."""
        start, stop = ctypes.c_void_p(), ctypes.c_void_p()
        self.cu.cuEventCreate(ctypes.byref(start), 0)
        self.cu.cuEventCreate(ctypes.byref(stop), 0)
        for _ in range(200):     # warm up long enough for a laptop GPU to reach its boost clock
            self.launch(fn, k, ptrs, sync=False)
        self.check(self.cu.cuCtxSynchronize(), "warmup")
        times = []
        for _ in range(reps):
            self.cu.cuEventRecord(start, None)
            for _ in range(iters):
                self.launch(fn, k, ptrs, sync=False)
            self.cu.cuEventRecord(stop, None)
            self.cu.cuEventSynchronize(stop)
            ms = ctypes.c_float()
            self.cu.cuEventElapsedTime(ctypes.byref(ms), start, stop)
            times.append(ms.value * 1000 / iters)
        return statistics.median(times)


def ptxas(ptx_path: Path, cubin_path: Path) -> tuple[bool, str, int | None, int | None]:
    r = subprocess.run(["ptxas", "-arch=sm_89", "-v", str(ptx_path), "-o", str(cubin_path)],
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    regs = re.search(r"Used (\d+) registers", out)
    spill = re.findall(r"(\d+) bytes spill (?:stores|loads)", out)
    return (r.returncode == 0, out.strip(),
            int(regs.group(1)) if regs else None, sum(map(int, spill)) if spill else 0)


def inputs_for(k, produced):
    arrs = {}
    for a in k["args"]:
        shape = a["shape"]
        if a.get("output"):
            arrs[a["name"]] = np.zeros(shape, np.float32)
        elif "data" in a:
            arrs[a["name"]] = np.array(a["data"], np.float32).reshape(shape)
        elif a.get("intermediate"):
            arrs[a["name"]] = produced[a["name"]]
        else:
            arrs[a["name"]] = np.random.default_rng(a["seed"]).standard_normal(shape).astype(np.float32)
    return arrs


def headroom(got, ref, rtol, atol) -> float:
    """max |got - ref| / allowed; allclose passes when this is <= 1."""
    allowed = atol + rtol * np.abs(ref)
    err = np.abs(got.astype(np.float64) - ref.astype(np.float64))
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(allowed > 0, err / allowed, np.where(err > 0, np.inf, 0.0))
    if np.isnan(got).any():
        return float("inf")
    return float(ratio.max()) if ratio.size else 0.0


def worker(pdir: Path, with_ref: bool) -> dict:
    """Compile, assemble and run every kernel of one problem on the local GPU."""
    meta = json.loads((pdir / "meta.json").read_text())
    expected = dict(np.load(pdir / "expected.npz")) if (pdir / "expected.npz").exists() else {}
    row = dict(id=pdir.name, compile_s=0.0, ptxas=True, regs=0, spills=0, us=0.0, ref_us=None,
               passed=None, headroom=0.0, error="")
    gpu = Gpu()
    produced, ref_total = {}, 0.0
    tmp = Path(tempfile.mkdtemp(prefix="emmy_"))
    for k in meta["kernels"]:
        ir = pdir / f"{k['entry']}.ir.json"
        t0 = time.perf_counter()
        r = subprocess.run([sys.executable, str(ROOT / "compile.py"), str(ir)], capture_output=True, text=True)
        row["compile_s"] += time.perf_counter() - t0
        if r.returncode:
            row.update(ptxas=False, passed=False, error=(r.stderr.strip().splitlines() or ["?"])[-1][:120])
            return row
        ptx = tmp / f"{k['entry']}.ptx"
        ptx.write_text(r.stdout)
        ok, log, regs, spills = ptxas(ptx, tmp / f"{k['entry']}.cubin")
        if not ok:
            row.update(ptxas=False, passed=False, error="ptxas: " + log.splitlines()[0][:110])
            return row
        row["regs"] = max(row["regs"], regs or 0)
        row["spills"] += spills
        try:
            arrs = inputs_for(k, produced)
            fn = gpu.function((tmp / f"{k['entry']}.cubin").read_bytes(), k["entry"], k["smem_bytes"])
            ptrs = [gpu.alloc(arrs[n]) for n in k["arg_order"]]
            for n, p in zip(k["arg_order"], ptrs):
                if n in k["zero_outputs"]:
                    gpu.zero(p, arrs[n].nbytes)
            gpu.launch(fn, k, ptrs)
            outs = {a["name"] for a in k["args"] if a.get("output")}
            for n, p in zip(k["arg_order"], ptrs):
                if n in outs:
                    produced[n] = gpu.read(p, arrs[n])
            ref_fn = None
            if with_ref and (pdir / f"{k['entry']}.ref.cu").exists():
                try:    # the reference only feeds the speed ratio; its build failing is not ours
                    ref_fn = gpu.function(nvrtc_cubin((pdir / f"{k['entry']}.ref.cu").read_text()),
                                          k["entry"], k["smem_bytes"])
                except RuntimeError as e:
                    row["error"] = "ref timing skipped: " + str(e)[:80]
                    ref_total, with_ref = 0.0, False
            # interleave ours and the reference, best of 3: GPU clock drift hits both alike
            ours, refs = [], []
            for _ in range(3 if ref_fn else 1):
                ours.append(gpu.time_us(fn, k, ptrs))
                if ref_fn:
                    refs.append(gpu.time_us(ref_fn, k, ptrs))
            row["us"] += min(ours)
            ref_total += min(refs) if refs else 0.0
        except RuntimeError as e:
            row.update(passed=False, error=str(e)[:120])
            return row
    if with_ref and ref_total:
        row["ref_us"] = ref_total
    if expected:
        heads = [headroom(produced[n], ref, meta["rtol"], meta["atol"]) for n, ref in expected.items()]
        row["headroom"] = max(heads)
        row["passed"] = row["headroom"] <= 1.0
    return row


def nvrtc_cubin(src: str) -> bytes:
    """Build emmy's reference CUDA with NVRTC (no host compiler needed). Metrics only:
    the reference is never part of compile.py's output."""
    import glob
    import shutil
    bindir = Path(shutil.which("ptxas")).parent
    dll = (glob.glob(str(bindir / "x64" / "nvrtc64_*_0.dll")) + glob.glob(str(bindir / "nvrtc64_*_0.dll")) +
           glob.glob("/usr/local/cuda/lib64/libnvrtc.so*"))[0]
    lib = ctypes.WinDLL(dll) if sys.platform == "win32" else ctypes.CDLL(dll)
    prog = ctypes.c_void_p()
    lib.nvrtcCreateProgram(ctypes.byref(prog), src.encode(), b"ref.cu", 0, None, None)
    opts = (ctypes.c_char_p * 2)(b"-arch=sm_89", b"-default-device")
    if lib.nvrtcCompileProgram(prog, 2, opts):
        n = ctypes.c_size_t()
        lib.nvrtcGetProgramLogSize(prog, ctypes.byref(n))
        log = ctypes.create_string_buffer(n.value)
        lib.nvrtcGetProgramLog(prog, log)
        raise RuntimeError("nvrtc: " + log.value.decode(errors="replace")[:200])
    n = ctypes.c_size_t()
    lib.nvrtcGetCUBINSize(prog, ctypes.byref(n))
    buf = ctypes.create_string_buffer(n.value)
    lib.nvrtcGetCUBIN(prog, buf)
    return buf.raw


def remote(pdir: Path) -> dict:
    t0 = time.perf_counter()
    r = subprocess.run([sys.executable, str(ROOT / "submit.py"), str(pdir), "--compiler", str(ROOT / "compile.py")],
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    errs = [float(x) for x in re.findall(r"max abs err ([0-9.e+-]+)", out)]
    us = [float(x) for x in re.findall(r"\(([0-9.]+) us\)", out)]
    return dict(id=pdir.name, compile_s=time.perf_counter() - t0, ptxas="ptxas rejected" not in out,
                regs=max(map(int, re.findall(r"(\d+) registers", out)), default=0), spills=None,
                us=sum(us), ref_us=None, passed=r.returncode == 0, headroom=None,
                error="" if r.returncode == 0 else out.strip().splitlines()[-1][:120] if out.strip() else "?")


# ---- coverage ------------------------------------------------------------------------
def coverage(dirs: list[Path]) -> tuple[set, set, set, set]:
    """(node kinds seen, node kinds handled, ops seen, ops handled) over the IRs in `dirs`."""
    import dataclasses
    sys.path.insert(0, str(ROOT))
    import compile as C
    from emmy.compiler.graph import Graph
    kinds, ops = set(), set()

    def walk(o):
        if isinstance(o, (list, tuple)):
            for x in o:
                walk(x)
            return
        if not dataclasses.is_dataclass(o) or type(o).__name__ in ("DataType",):
            return
        kinds.add(type(o).__name__)
        if type(o).__name__ in ("Assign", "Accum"):
            ops.add(o.op.name)
        for f in dataclasses.fields(o):
            walk(getattr(o, f.name))

    for d in dirs:
        for ir in d.glob("*.ir.json"):
            g = Graph.from_dict(json.loads(ir.read_text()))
            for n in g.nodes.values():
                if type(n.op).__name__ == "KernelOp":
                    walk(n.op.body)
    handled_kinds = {k for k in NODE_KINDS if hasattr(C.Kernel, "s_" + k) or k in EXPR_KINDS}
    handled_ops = set()
    for op in ops:
        k = C.Kernel(None, [], {})
        try:
            k.elementwise(op, "%f0", ["%f1", "%f2", "%f3"])
            handled_ops.add(op)
        except C.Unsupported:
            pass
    seen = {k for k in kinds if k in NODE_KINDS}
    return seen, handled_kinds, ops, handled_ops


# ---- table -----------------------------------------------------------------------------
def fmt_row(r: dict) -> list[str]:
    cat = CATEGORY.get(r["id"][0], "?")
    hr = r.get("headroom")
    speed = f"{r['us'] / r['ref_us']:.2f}x" if r.get("ref_us") else "-"
    return [r["id"], cat, "ok" if r["ptxas"] else "FAIL",
            "-" if r["passed"] is None else ("PASS" if r["passed"] else "FAIL"),
            "-" if hr is None else ("inf" if hr == float("inf") else f"{hr:.3f}"),
            f"{r['compile_s']:.2f}", str(r["regs"]), "-" if r["spills"] is None else str(r["spills"]),
            f"{r['us']:.1f}" if r["us"] else "-", speed, r["error"]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("only", nargs="*", help="problem id prefixes")
    ap.add_argument("--ref", action="store_true", help="also time ref.cu built with NVRTC")
    ap.add_argument("--remote", action="store_true", help="use the hosted runner via submit.py")
    ap.add_argument("--worker", help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.worker:
        print(json.dumps(worker(Path(args.worker), args.ref)))
        return 0

    dirs = sorted((p for s in SETS if s.exists() for p in s.iterdir() if (p / "meta.json").exists()),
                  key=lambda p: (p.name[0] not in CATEGORY, "prmfa".find(p.name[0]), p.name))
    if args.only:
        dirs = [d for d in dirs if any(d.name.startswith(o) for o in args.only)]

    rows = []
    for d in dirs:
        if args.remote:
            row = remote(d)
        else:
            cmd = [sys.executable, __file__, "--worker", str(d)] + (["--ref"] if args.ref else [])
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                row = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 and r.stdout.strip() \
                    else dict(id=d.name, compile_s=0, ptxas=False, regs=0, spills=0, us=0, ref_us=None,
                              passed=False, headroom=None, error=(r.stderr.strip().splitlines() or ["crash"])[-1][:120])
            except subprocess.TimeoutExpired:
                row = dict(id=d.name, compile_s=0, ptxas=False, regs=0, spills=0, us=0, ref_us=None,
                           passed=False, headroom=None, error="timeout")
        rows.append(row)
        print("  " + "  ".join(fmt_row(row)[:6]), flush=True)

    head = ["problem", "category", "ptxas", "result", "headroom", "compile s", "regs", "spills",
            "us", "vs ref", "error"]
    table = [head] + [fmt_row(r) for r in rows]
    widths = [max(len(t[i]) for t in table) for i in range(len(head))]
    print()
    for t in table:
        print("  ".join(c.ljust(w) for c, w in zip(t, widths)).rstrip())

    # ---- summary metrics ---------------------------------------------------------------
    seen, handled, ops, handled_ops = coverage(dirs)
    n = len(rows)
    by_cat = {}
    for r in rows:
        c = CATEGORY.get(r["id"][0], "?")
        tot, ok = by_cat.get(c, (0, 0))
        by_cat[c] = (tot + 1, ok + bool(r["passed"]))
    heads = [r["headroom"] for r in rows if r.get("passed") and r.get("headroom") is not None]
    ratios = [r["us"] / r["ref_us"] for r in rows if r.get("ref_us") and r.get("passed")]
    summary = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "problems": n,
        "node_coverage": f"{len(handled)}/{len(NODE_KINDS)}",
        "node_kinds_seen_unhandled": sorted(seen - handled),
        "op_coverage": f"{len(handled_ops)}/{len(ops)}",
        "ops_unhandled": sorted(ops - handled_ops),
        "ptxas_accept": f"{sum(bool(r['ptxas']) for r in rows)}/{n}",
        "pass_by_category": {c: f"{ok}/{tot}" for c, (tot, ok) in sorted(by_cat.items())},
        "pass_total": f"{sum(bool(r['passed']) for r in rows)}/{n}",
        "worst_headroom": max(heads) if heads else None,
        "headroom_over_0.5": [r["id"] for r in rows if r.get("passed") and (r.get("headroom") or 0) > 0.5],
        "max_compile_s": round(max((r["compile_s"] for r in rows), default=0), 2),
        "total_spill_bytes": sum(r["spills"] or 0 for r in rows),
        "geomean_speed_vs_ref": round(float(np.exp(np.mean(np.log(ratios)))), 3) if ratios else None,
        "mode": "remote" if args.remote else "local",
    }
    print()
    for k, v in summary.items():
        print(f"  {k:<26} {v}")

    out = ROOT / "metrics"
    out.mkdir(exist_ok=True)
    with open(out / "history.jsonl", "a") as f:
        f.write(json.dumps(summary) + "\n")
    md = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    md += ["| " + " | ".join(c.replace("|", "/") for c in fmt_row(r)) + " |" for r in rows]
    md += ["", "```", *[f"{k:<26} {v}" for k, v in summary.items()], "```", ""]
    (out / "latest.md").write_text("\n".join(md))
    return 0 if all(r["passed"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
