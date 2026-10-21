"""Print each IR statement/expression kind once with its fields (exploration aid)."""
import json, sys, glob, dataclasses
from emmy.compiler.graph import Graph
seen = {}
def fields(o):
    if dataclasses.is_dataclass(o): return {f.name: getattr(o, f.name) for f in dataclasses.fields(o)}
    return vars(o) if hasattr(o, '__dict__') else None
def walk(o, path):
    if isinstance(o, (list, tuple)):
        for x in o: walk(x, path)
        return
    fs = fields(o)
    if fs is None or type(o).__name__ in ('DataType','ElementwiseImpl','ufunc'): return
    t = type(o).__name__
    if t not in seen:
        seen[t] = (path, {k: (repr(v)[:110]) for k, v in fs.items() if k not in ('body','else_body')})
    for k, v in fs.items():
        if not isinstance(v, (str, int, float, bool, type(None))): walk(v, path)
for f in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else 'problems/*/*.ir.json')):
    g = Graph.from_dict(json.load(open(f)))
    for n in g.nodes.values():
        if type(n.op).__name__ == 'KernelOp': walk(n.op.body, f.split('problems')[-1][1:20])
for t, (p, fs) in sorted(seen.items()):
    print(f'## {t}   (first in {p})')
    for k, v in fs.items(): print(f'   {k} = {v}')
