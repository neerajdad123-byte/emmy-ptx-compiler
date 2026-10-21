# Emmy Kernel IR -> PTX compiler

A compiler from Emmy's Kernel IR straight to PTX, for the
[Emmy Hackathon 2026](https://github.com/cloudrift-ai/emmy-hackathon-2026) (task: [TASK.md](TASK.md)).

```bash
pip install emmy-ml==0.3.11            # the only dependency: loads the IR
python compile.py path/to/kernel.ir.json > out.ptx
```

`compile.py` imports only emmy (to deserialize the IR with `Graph.from_dict`) and the Python
standard library. The IR -> PTX lowering is all in that one file; no emmy renderer, nvcc or
other compiler is involved.

## How it works

1. **Load.** `Graph.from_dict` gives the typed `KernelOp`. The `meta.json` next to the IR gives
   the parameter order (`arg_order`), buffer shapes and the launch geometry.
2. **Prescan.** Collect shared arrays (static, or one dynamic pool above 48 KiB) and the
   buffers the kernel writes (the others are read through `ld.global.nc`).
3. **Walk.** Each IR statement kind has one method, `s_<Kind>`, that appends PTX lines.
   Index expressions are compiled recursively by `expr()`, with constant folding. `env` maps
   IR names to virtual registers (`%f` float, `%r` int, `%rd` address, `%p` predicate).
4. **Emit.** Header, shared declarations, signature, register counts, body. ptxas does the real
   register allocation.

| IR | PTX |
|---|---|
| `Tile` | `gid = ctaid*ntid + tid`, a bounds guard when the launch has more threads than cells, row-major axis decode (plus emmy's grouped CTA rasterization) |
| `Load` / `Write` | flattened row-major offset; `ld/st.v2/.v4` for grouped values; `red.global.add` for atomic writes |
| `Assign` | one instruction (`add.f32`, `max.f32`, `rcp.rn.f32` ...) or a short sequence (`exp` = `ex2.approx(x*log2e)`, `tanh`, `erf`, `gelu`, `pow` ...) |
| `Accum` / `Init` | a register updated in place, seeded with the op's identity before the loop over its reduced axis |
| `Loop` / `StridedLoop` | counter + `setp` + `bra`; fully unrolled when the IR asks and the body is small |
| `Cond` | `setp` + `@!p bra` |
| `WarpShuffle` | `shfl.sync.bfly.b32` butterfly, then the IR's combine statements |
| `Smem` / `Sync` / `TreeHalve` | `.shared` arrays, `bar.sync`, shared-memory halving tree + broadcast |
| `CpAsyncCopy/Commit/Wait` | `cp.async.cg/ca.shared.global`, `cp.async.commit_group`, `cp.async.wait_group` |

## Testing (dev tools, not part of the compiler)

```bash
python submit.py r01_array_sum --compiler compile.py    # one problem on the hosted runner
python tools/test.py                                    # every problem on a local GPU: metrics table
python tools/test.py --remote                           # every problem on the hosted runner
```

`tools/test.py` reports ptxas acceptance, pass/fail, error headroom (max error / tolerance),
compile time, registers, spills and kernel time, and appends a summary to
`metrics/history.jsonl`. `tools/expressions_corpus.py` and `tools/expressions_ragged.py` hold
about 100 extra torch expressions (new shapes and ops, tiny and ragged tails) used as a stand-in
for the hidden set, generated with `tools/generate.py`. `tools/dev/` has the Windows shims
needed to run emmy's CLI there.
