#!/usr/bin/env python3
"""Head-to-head speed on the hosted runner (RTX 5090): our PTX vs emmy's reference, built to
PTX with NVRTC, under the same launch. Metrics only.

    python tools/remote_speed.py            # every problem in problems/ and corpus/
    python tools/remote_speed.py m0 a0      # id prefixes
"""

import json
import re
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import requests

sys.path.insert(0, str(Path(__file__).parent))
from test import ROOT, SETS, nvrtc_cubin   # noqa: E402

RUNNER = "http://runner.riftstack.ai:48701"


def run(ptx: str, k: dict) -> float | str:
    """Median kernel time in us on the runner, or the failure text."""
    args = []
    for a in k["args"]:
        a = dict(a)
        if a.pop("intermediate", False):   # timing only: any data of the right shape will do
            a["seed"] = 0
        args.append(a)
    body = {"ptx": ptx, "entry": k["entry"], "grid": k["grid"], "block": k["block"],
            "smem_bytes": k["smem_bytes"], "zero_outputs": k["zero_outputs"], "args": args,
            "warmup": 20, "iters": 200, "max_return": 1}
    for _ in range(60):
        r = requests.post(f"{RUNNER}/run", json=body, timeout=(10, 300)).json()
        if r.get("stage") != "busy":
            break
        time.sleep(2)
    return r["median_us"] if r.get("ok") else f"{r.get('stage')}: {r.get('stderr', '')[:60]}"


def main() -> int:
    only = sys.argv[1:]
    dirs = sorted(p for s in SETS if s.exists() for p in s.iterdir() if (p / "meta.json").exists())
    dirs = [d for d in dirs if not only or any(d.name.startswith(o) for o in only)]
    rows = []
    for d in dirs:
        meta = json.loads((d / "meta.json").read_text())
        ours_us = ref_us = 0.0
        note = ""
        for k in meta["kernels"]:
            ir = d / f"{k['entry']}.ir.json"
            ptx = subprocess.run([sys.executable, str(ROOT / "compile.py"), str(ir)],
                                 capture_output=True, text=True, check=True).stdout
            try:
                ref = nvrtc_cubin((d / f"{k['entry']}.ref.cu").read_text(), ptx=True).decode()
            except RuntimeError as e:   # e.g. an argument named `log` shadows log() under NVRTC
                note = "ref build failed: " + str(e)[7:60]
                break
            # local NVRTC (CUDA 13.3) stamps a newer PTX ISA than the runner's ptxas (13.0) reads; ours uses 8.0 too
            ref = re.sub(r"^\.version \d+\.\d+", ".version 8.0", ref, count=1, flags=re.M)
            o, r = run(ptx, k), run(ref, k)
            if isinstance(o, str) or isinstance(r, str):
                note = o if isinstance(o, str) else "ref " + r
                break
            ours_us, ref_us = ours_us + o, ref_us + r
        ratio = ours_us / ref_us if ref_us and not note else None
        rows.append((d.name, ours_us, ref_us, ratio, note))
        print(f"  {d.name:<24} ours {ours_us:9.1f} us   ref {ref_us:9.1f} us   "
              f"{f'{ratio:.2f}x' if ratio else note}", flush=True)

    ratios = [r[3] for r in rows if r[3]]
    print(f"\n  measured {len(ratios)}/{len(rows)}   geomean ours/ref "
          f"{math.exp(np.mean(np.log(ratios))):.3f}   faster-or-equal {sum(r <= 1.02 for r in ratios)}"
          f"   slower >1.1x {sum(r > 1.1 for r in ratios)}")
    print("  slowest:", ", ".join(f"{r[0]} {r[3]:.2f}x" for r in sorted((r for r in rows if r[3]), key=lambda r: -r[3])[:8]))
    (ROOT / "metrics").mkdir(exist_ok=True)
    (ROOT / "metrics" / "remote_speed.json").write_text(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
