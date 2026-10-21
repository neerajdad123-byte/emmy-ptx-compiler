"""Tiny and ragged shapes (1, 31, 33, 1000, 4097): tails break compilers more than ops do.

    python tools/generate.py tools/expressions_ragged.py --emmy tools/dev/emmy_win.cmd (Windows) or emmy --out corpus
"""

import numpy as np

R = "WORK=t128,REDUCE=coop"
f64 = lambda a: a.astype(np.float64)
f32 = lambda a: np.asarray(a).astype(np.float32)


def _softmax(x):
    e = np.exp(x - x.max(-1, keepdims=True))
    return e / e.sum(-1, keepdims=True)


def P(id, code, ref, tol=1e-5, **kw):
    return dict(id=id, code=code, ref=ref, rtol=tol, atol=tol, **kw)


OPEN = (
    [P(f"p_rag_add_{n}", f"torch.randn({n}) + torch.randn({n})", lambda a, b: [a + b], 0)
     for n in (1, 31, 33, 1000, 4097)]
    + [P("p_rag_2d_33x31", "torch.sigmoid(torch.randn(33, 31))", lambda a: [f32(1 / (1 + np.exp(-f64(a))))]),
       P("p_rag_bias_7x4097", "torch.randn(7, 4097) * torch.randn(4097)", lambda a, b: [a * b], 0)]
    + [P(f"r_rag_sum_{n}", f"torch.randn({n}).sum()", lambda x: [f32(f64(x).sum())], 1e-4, knobs=R)
       for n in (1, 31, 33, 1000, 4097)]
    + [P("r_rag_max_33", "torch.randn(33).amax()", lambda x: [x.max()], 1e-6, knobs=R),
       P("r_rag_rows_33x31", "torch.randn(33, 31).sum(-1)", lambda x: [f32(f64(x).sum(-1))], 1e-4, knobs=R),
       P("r_rag_rows_7x4097", "torch.randn(7, 4097).sum(-1)", lambda x: [f32(f64(x).sum(-1))], 1e-4, knobs=R),
       P("r_rag_rowmax_5x1000", "torch.randn(5, 1000).amax(-1)", lambda x: [x.max(-1)], 1e-6, knobs=R),
       P("m_rag_33x31x17", "torch.randn(33, 31) @ torch.randn(31, 17)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
       P("m_rag_1x64x64", "torch.randn(1, 64) @ torch.randn(64, 64)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
       P("f_rag_softmax_33x31", "torch.softmax(torch.randn(33, 31), dim=-1)", lambda x: [f32(_softmax(f64(x)))], 1e-4),
       P("f_rag_softmax_1x4097", "torch.softmax(torch.randn(1, 4097), dim=-1)", lambda x: [f32(_softmax(f64(x)))], 1e-4),
       P("f_rag_rms_7x1000", "x = torch.randn(7, 1000); x / torch.sqrt((x * x).mean(-1, keepdim=True) + 1e-5)",
         lambda x: [f32(f64(x) / np.sqrt((f64(x) ** 2).mean(-1, keepdims=True) + 1e-5))], 1e-3),
       P("a_rag_attn_33x17", "q = torch.randn(33, 17); kt = torch.randn(17, 31); v = torch.randn(31, 13); "
         "torch.softmax(q @ kt / 4.123106, dim=-1) @ v",
         lambda q, kt, v: [f32(_softmax(f64(q) @ f64(kt) / 4.123106) @ f64(v))], 1e-3)]
)
