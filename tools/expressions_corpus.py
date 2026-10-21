"""Practice corpus: variations of the five open categories (new shapes and ops), standing in
for the hidden set. Generate with:

    python tools/generate.py tools/expressions_corpus.py --emmy tools/dev/emmy_win.cmd (Windows) or emmy --out corpus

Ids start with the category letter (p r m f a) so test.py groups them.
"""

import numpy as np

R = "WORK=t128,REDUCE=coop"   # pinned single-block cooperative reduction (category 2)
f64 = lambda a: a.astype(np.float64)
f32 = lambda a: np.asarray(a).astype(np.float32)


def _softmax(x, axis=-1):
    e = np.exp(x - x.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


def _erf(x):
    from math import erf
    return np.vectorize(erf)(x)


def P(id, code, ref, tol=1e-5):
    return dict(id=id, code=code, ref=ref, rtol=tol, atol=tol)


OPEN = [
    # ---- category 1: pointwise -------------------------------------------------------
    P("p_add_3000", "torch.randn(3000) + torch.randn(3000)", lambda a, b: [a + b], 0),
    P("p_add_odd_1000", "torch.randn(1000) + torch.randn(1000)", lambda a, b: [a + b], 0),
    P("p_add_77", "torch.randn(77) + torch.randn(77)", lambda a, b: [a + b], 0),
    P("p_sub_2d", "torch.randn(64, 48) - torch.randn(64, 48)", lambda a, b: [a - b], 0),
    P("p_mul_big", "torch.randn(262144) * torch.randn(262144)", lambda a, b: [a * b], 0),
    P("p_div", "torch.randn(4096) / (torch.randn(4096).abs() + 1.0)",
      lambda a, b: [f32(f64(a) / (np.abs(f64(b)) + 1.0))], 1e-5),
    P("p_neg_abs", "torch.neg(torch.randn(2048).abs())", lambda a: [-np.abs(a)], 0),
    P("p_max", "torch.maximum(torch.randn(4096), torch.randn(4096))", lambda a, b: [np.maximum(a, b)], 0),
    P("p_min", "torch.minimum(torch.randn(4096), torch.randn(4096))", lambda a, b: [np.minimum(a, b)], 0),
    P("p_relu_2d", "torch.relu(torch.randn(128, 128))", lambda a: [np.maximum(a, 0)], 0),
    P("p_scale_shift_odd", "torch.randn(5000) * 3.5 - 0.25",
      lambda a: [a * np.float32(3.5) - np.float32(0.25)], 1e-6),
    P("p_exp", "torch.exp(torch.randn(4096))", lambda a: [f32(np.exp(f64(a)))], 1e-5),
    P("p_log", "torch.log(torch.randn(4096).abs() + 1.0)", lambda a: [f32(np.log(np.abs(f64(a)) + 1))], 1e-5),
    P("p_sqrt", "torch.sqrt(torch.randn(4096).abs())", lambda a: [f32(np.sqrt(np.abs(f64(a))))], 1e-5),
    P("p_rsqrt", "torch.rsqrt(torch.randn(4096).abs() + 0.5)",
      lambda a: [f32(1 / np.sqrt(np.abs(f64(a)) + 0.5))], 1e-5),
    P("p_sigmoid", "torch.sigmoid(torch.randn(8192))", lambda a: [f32(1 / (1 + np.exp(-f64(a))))], 1e-5),
    P("p_tanh", "torch.tanh(torch.randn(8192))", lambda a: [f32(np.tanh(f64(a)))], 1e-5),
    P("p_silu", "torch.nn.functional.silu(torch.randn(8192))",
      lambda a: [f32(f64(a) / (1 + np.exp(-f64(a))))], 1e-5),
    P("p_gelu", "torch.nn.functional.gelu(torch.randn(8192))",
      lambda a: [f32(0.5 * f64(a) * (1 + _erf(f64(a) / np.sqrt(2))))], 1e-5),
    P("p_gelu_tanh", "torch.nn.functional.gelu(torch.randn(8192), approximate='tanh')",
      lambda a: [f32(0.5 * f64(a) * (1 + np.tanh(np.sqrt(2 / np.pi) * (f64(a) + 0.044715 * f64(a) ** 3))))], 1e-5),
    P("p_softplus", "torch.nn.functional.softplus(torch.randn(8192))",
      lambda a: [f32(np.logaddexp(0, f64(a)))], 1e-5),
    P("p_square", "torch.randn(4096) * torch.randn(4096) * torch.randn(4096)",
      lambda a, b, c: [a * b * c], 1e-6),
    P("p_pow2", "torch.randn(4096) ** 2", lambda a: [f32(f64(a) ** 2)], 1e-5),
    P("p_clamp", "torch.clamp(torch.randn(4096), -0.5, 0.5)", lambda a: [np.clip(a, -0.5, 0.5)], 0),
    P("p_fma3", "x = torch.randn(4096); y = torch.randn(4096); z = torch.randn(4096); x * y + z",
      lambda x, y, z: [f32(f64(x) * f64(y) + f64(z))], 1e-6),
    P("p_bias_row", "torch.randn(256, 64) + torch.randn(64)", lambda a, b: [a + b], 0),
    P("p_scale_col", "torch.randn(64, 256) * torch.randn(64, 1)", lambda a, b: [a * b], 0),
    P("p_chain", "x = torch.randn(4096); torch.sigmoid(x) * torch.tanh(x) + x",
      lambda x: [f32(1 / (1 + np.exp(-f64(x))) * np.tanh(f64(x)) + f64(x))], 1e-5),

    # ---- category 2: reductions (pinned cooperative schedule) --------------------------
    dict(P("r_sum_4096", "torch.randn(4096).sum()", lambda x: [f32(f64(x).sum())], 1e-4), knobs=R),
    dict(P("r_sum_100k", "torch.randn(100000).sum()", lambda x: [f32(f64(x).sum())], 1e-3), knobs=R),
    dict(P("r_sum_300", "torch.randn(300).sum()", lambda x: [f32(f64(x).sum())], 1e-4), knobs=R),
    dict(P("r_mean_8192", "torch.randn(8192).mean()", lambda x: [f32(f64(x).mean())], 1e-4), knobs=R),
    dict(P("r_amax", "torch.randn(16384).amax()", lambda x: [x.max()], 1e-6), knobs=R),
    dict(P("r_sumsq", "x = torch.randn(8192); (x * x).sum()", lambda x: [f32((f64(x) ** 2).sum())], 1e-4), knobs=R),
    dict(P("r_abs_sum", "torch.randn(8192).abs().sum()", lambda x: [f32(np.abs(f64(x)).sum())], 1e-4), knobs=R),
    dict(P("r_row_sum_128x1024", "torch.randn(128, 1024).sum(-1)", lambda x: [f32(f64(x).sum(-1))], 1e-4), knobs=R),
    dict(P("r_row_sum_32x256", "torch.randn(32, 256).sum(-1)", lambda x: [f32(f64(x).sum(-1))], 1e-4), knobs=R),
    dict(P("r_row_mean", "torch.randn(64, 512).mean(-1)", lambda x: [f32(f64(x).mean(-1))], 1e-4), knobs=R),
    dict(P("r_row_max", "torch.randn(64, 512).amax(-1)", lambda x: [x.max(-1)], 1e-6), knobs=R),
    dict(P("r_col_sum", "torch.randn(512, 64).sum(0)", lambda x: [f32(f64(x).sum(0))], 1e-4), knobs=R),
    dict(P("r_row_sum_odd", "torch.randn(48, 300).sum(-1)", lambda x: [f32(f64(x).sum(-1))], 1e-4), knobs=R),
    dict(P("r_row_sum_keepdim", "torch.randn(64, 256).sum(-1, keepdim=True)",
           lambda x: [f32(f64(x).sum(-1, keepdims=True))], 1e-4), knobs=R),
    P("r_sum_unpinned", "torch.randn(1 << 20).sum()", lambda x: [f32(f64(x).sum())], 1e-2),
    P("r_row_sum_unpinned", "torch.randn(256, 4096).sum(-1)", lambda x: [f32(f64(x).sum(-1))], 1e-3),

    # ---- category 3: matmul ------------------------------------------------------------
    P("m_mm_256", "torch.randn(256, 256) @ torch.randn(256, 256)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
    P("m_mm_1024", "torch.randn(1024, 1024) @ torch.randn(1024, 1024)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
    P("m_mm_64", "torch.randn(64, 64) @ torch.randn(64, 64)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
    P("m_mm_rect_tall", "torch.randn(512, 128) @ torch.randn(128, 64)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
    P("m_mm_rect_wide", "torch.randn(64, 128) @ torch.randn(128, 512)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
    P("m_mm_longk", "torch.randn(64, 2048) @ torch.randn(2048, 64)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
    P("m_mm_odd", "torch.randn(96, 160) @ torch.randn(160, 80)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
    P("m_mm_small_k", "torch.randn(256, 16) @ torch.randn(16, 256)", lambda a, b: [f32(f64(a) @ f64(b))], 1e-3),
    P("m_mm_bias", "torch.randn(128, 256) @ torch.randn(256, 128) + torch.randn(128)",
      lambda a, b, c: [f32(f64(a) @ f64(b) + f64(c))], 1e-3),
    P("m_mm_relu", "torch.relu(torch.randn(256, 128) @ torch.randn(128, 256))",
      lambda a, b: [f32(np.maximum(f64(a) @ f64(b), 0))], 1e-3),

    # ---- category 4: fused -------------------------------------------------------------
    P("f_softmax_32x1024", "torch.softmax(torch.randn(32, 1024), dim=-1)",
      lambda x: [f32(_softmax(f64(x)))], 1e-4),
    P("f_softmax_128x128", "torch.softmax(torch.randn(128, 128), dim=-1)", lambda x: [f32(_softmax(f64(x)))], 1e-4),
    P("f_softmax_odd", "torch.softmax(torch.randn(50, 200), dim=-1)", lambda x: [f32(_softmax(f64(x)))], 1e-4),
    P("f_rmsnorm_32x512", "x = torch.randn(32, 512); w = torch.randn(512); "
      "x / torch.sqrt((x * x).mean(-1, keepdim=True) + 1e-6) * w",
      lambda x, w: [f32(f64(x) / np.sqrt((f64(x) ** 2).mean(-1, keepdims=True) + 1e-6) * f64(w))], 1e-3),
    P("f_rmsnorm_rsqrt", "x = torch.randn(64, 256); x * torch.rsqrt((x * x).mean(-1, keepdim=True) + 1e-5)",
      lambda x: [f32(f64(x) / np.sqrt((f64(x) ** 2).mean(-1, keepdims=True) + 1e-5))], 1e-3),
    P("f_l2norm_128x256", "x = torch.randn(128, 256); x / torch.sqrt((x * x).sum(-1, keepdim=True))",
      lambda x: [f32(f64(x) / np.sqrt((f64(x) ** 2).sum(-1, keepdims=True)))], 1e-3),
    P("f_layernorm", "x = torch.randn(64, 512); (x - x.mean(-1, keepdim=True)) / "
      "torch.sqrt(((x - x.mean(-1, keepdim=True)) ** 2).mean(-1, keepdim=True) + 1e-5)",
      lambda x: [f32((f64(x) - f64(x).mean(-1, keepdims=True)) / np.sqrt(f64(x).var(-1, keepdims=True) + 1e-5))], 1e-3),
    P("f_center", "x = torch.randn(64, 512); x - x.mean(-1, keepdim=True)",
      lambda x: [f32(f64(x) - f64(x).mean(-1, keepdims=True))], 1e-4),
    P("f_logsumexp", "x = torch.randn(64, 256); torch.log(torch.exp(x - x.amax(-1, keepdim=True)).sum(-1, keepdim=True)) "
      "+ x.amax(-1, keepdim=True)",
      lambda x: [f32(np.log(np.exp(f64(x) - f64(x).max(-1, keepdims=True)).sum(-1, keepdims=True))
                     + f64(x).max(-1, keepdims=True))], 1e-4),
    P("f_max_norm", "x = torch.randn(64, 512); x / x.abs().amax(-1, keepdim=True)",
      lambda x: [f32(f64(x) / np.abs(f64(x)).max(-1, keepdims=True))], 1e-4),
    P("f_softmax_scaled", "torch.softmax(torch.randn(64, 256) * 0.125, dim=-1)",
      lambda x: [f32(_softmax(f64(x) * 0.125))], 1e-4),
    P("f_sigmoid_gate_norm", "x = torch.randn(64, 512); torch.sigmoid(x) / torch.sigmoid(x).sum(-1, keepdim=True)",
      lambda x: [f32((s := 1 / (1 + np.exp(-f64(x)))) / s.sum(-1, keepdims=True))], 1e-4),

    # ---- category 5: attention-like ----------------------------------------------------
    P("a_attn_32x32", "q = torch.randn(32, 32); kt = torch.randn(32, 32); v = torch.randn(32, 32); "
      "torch.softmax(q @ kt / 5.656854, dim=-1) @ v",
      lambda q, kt, v: [f32(_softmax(f64(q) @ f64(kt) / 5.656854) @ f64(v))], 1e-3),
    P("a_attn_128x64", "q = torch.randn(128, 64); kt = torch.randn(64, 128); v = torch.randn(128, 64); "
      "torch.softmax(q @ kt / 8.0, dim=-1) @ v",
      lambda q, kt, v: [f32(_softmax(f64(q) @ f64(kt) / 8.0) @ f64(v))], 1e-3),
    P("a_attn_256x64", "q = torch.randn(256, 64); kt = torch.randn(64, 256); v = torch.randn(256, 64); "
      "torch.softmax(q @ kt / 8.0, dim=-1) @ v",
      lambda q, kt, v: [f32(_softmax(f64(q) @ f64(kt) / 8.0) @ f64(v))], 1e-3),
    P("a_attn_rect", "q = torch.randn(64, 32); kt = torch.randn(32, 128); v = torch.randn(128, 16); "
      "torch.softmax(q @ kt / 5.656854, dim=-1) @ v",
      lambda q, kt, v: [f32(_softmax(f64(q) @ f64(kt) / 5.656854) @ f64(v))], 1e-3),
    P("a_attn_noscale", "q = torch.randn(64, 16); kt = torch.randn(16, 64); v = torch.randn(64, 64); "
      "torch.softmax(q @ kt, dim=-1) @ v",
      lambda q, kt, v: [f32(_softmax(f64(q) @ f64(kt)) @ f64(v))], 1e-3),
    P("a_attn_128x128", "q = torch.randn(128, 128); kt = torch.randn(128, 128); v = torch.randn(128, 128); "
      "torch.softmax(q @ kt / 11.313708, dim=-1) @ v",
      lambda q, kt, v: [f32(_softmax(f64(q) @ f64(kt) / 11.313708) @ f64(v))], 1e-3),
]
