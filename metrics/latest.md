| problem | category | ptxas | result | headroom | compile s | regs | spills | us | vs ref | error |
|---|---|---|---|---|---|---|---|---|---|---|
| p00_scalar_add | 1 pointwise | ok | PASS | - | 4.23 | 16 | - | 23.8 | - |  |
| p01_vector_add | 1 pointwise | ok | PASS | - | 3.51 | 16 | - | 24.2 | - |  |
| p02_scale_shift | 1 pointwise | ok | PASS | - | 3.28 | 18 | - | 16.7 | - |  |
| p03_relu_mul | 1 pointwise | ok | PASS | - | 3.54 | 20 | - | 16.1 | - |  |
| p_add_3000 | 1 pointwise | ok | PASS | - | 3.32 | 20 | - | 15.8 | - |  |
| p_add_77 | 1 pointwise | ok | PASS | - | 3.58 | 12 | - | 24.0 | - |  |
| p_add_odd_1000 | 1 pointwise | ok | PASS | - | 3.32 | 16 | - | 23.8 | - |  |
| p_bias_row | 1 pointwise | ok | PASS | - | 4.12 | 20 | - | 16.1 | - |  |
| p_chain | 1 pointwise | ok | PASS | - | 3.11 | 23 | - | 16.1 | - |  |
| p_clamp | 1 pointwise | ok | PASS | - | 2.81 | 22 | - | 23.1 | - |  |
| p_div | 1 pointwise | ok | PASS | - | 2.72 | 23 | - | 17.2 | - |  |
| p_exp | 1 pointwise | ok | PASS | - | 2.66 | 18 | - | 16.2 | - |  |
| p_fma3 | 1 pointwise | ok | PASS | - | 2.81 | 30 | - | 19.8 | - |  |
| p_gelu | 1 pointwise | ok | PASS | - | 2.92 | 24 | - | 16.9 | - |  |
| p_gelu_tanh | 1 pointwise | ok | PASS | - | 3.04 | 23 | - | 16.9 | - |  |
| p_log | 1 pointwise | ok | PASS | - | 2.60 | 14 | - | 21.7 | - |  |
| p_max | 1 pointwise | ok | PASS | - | 2.80 | 20 | - | 16.5 | - |  |
| p_min | 1 pointwise | ok | PASS | - | 2.54 | 20 | - | 16.4 | - |  |
| p_mul_big | 1 pointwise | ok | PASS | - | 4.31 | 20 | - | 17.1 | - |  |
| p_neg_abs | 1 pointwise | ok | PASS | - | 2.71 | 14 | - | 25.7 | - |  |
| p_pow2 | 1 pointwise | ok | PASS | - | 2.73 | 14 | - | 16.3 | - |  |
| p_rag_2d_33x31 | 1 pointwise | ok | PASS | - | 2.59 | 16 | - | 23.6 | - |  |
| p_rag_add_1 | 1 pointwise | ok | PASS | - | 2.44 | 12 | - | 24.2 | - |  |
| p_rag_add_1000 | 1 pointwise | ok | PASS | - | 2.58 | 16 | - | 24.3 | - |  |
| p_rag_add_31 | 1 pointwise | ok | PASS | - | 2.39 | 12 | - | 23.9 | - |  |
| p_rag_add_33 | 1 pointwise | ok | PASS | - | 2.31 | 18 | - | 24.4 | - |  |
| p_rag_add_4097 | 1 pointwise | ok | PASS | - | 3.45 | 12 | - | 16.5 | - |  |
| p_rag_bias_7x4097 | 1 pointwise | ok | PASS | - | 3.61 | 12 | - | 16.4 | - |  |
| p_relu_2d | 1 pointwise | ok | PASS | - | 3.52 | 18 | - | 23.9 | - |  |
| p_rsqrt | 1 pointwise | ok | PASS | - | 3.52 | 16 | - | 16.2 | - |  |
| p_scale_col | 1 pointwise | ok | PASS | - | 3.36 | 17 | - | 16.6 | - |  |
| p_scale_shift_odd | 1 pointwise | ok | PASS | - | 3.32 | 18 | - | 16.8 | - |  |
| p_sigmoid | 1 pointwise | ok | PASS | - | 3.53 | 16 | - | 16.4 | - |  |
| p_silu | 1 pointwise | ok | PASS | - | 3.30 | 17 | - | 16.9 | - |  |
| p_softplus | 1 pointwise | ok | PASS | - | 2.82 | 21 | - | 16.3 | - |  |
| p_sqrt | 1 pointwise | ok | PASS | - | 2.85 | 15 | - | 16.3 | - |  |
| p_square | 1 pointwise | ok | PASS | - | 2.88 | 30 | - | 16.3 | - |  |
| p_sub_2d | 1 pointwise | ok | PASS | - | 2.92 | 24 | - | 16.5 | - |  |
| p_tanh | 1 pointwise | ok | PASS | - | 3.04 | 19 | - | 16.6 | - |  |
| r01_array_sum | 2 reduction | ok | PASS | - | 2.60 | 40 | - | 20.2 | - |  |
| r02_big_sum | 2 reduction | ok | PASS | - | 2.52 | 40 | - | 18.4 | - |  |
| r03_mean | 2 reduction | ok | PASS | - | 2.24 | 40 | - | 21.9 | - |  |
| r04_row_sum | 2 reduction | ok | PASS | - | 2.44 | 36 | - | 20.7 | - |  |
| r_abs_sum | 2 reduction | ok | PASS | - | 2.31 | 40 | - | 19.9 | - |  |
| r_amax | 2 reduction | ok | PASS | - | 2.43 | 40 | - | 12.8 | - |  |
| r_col_sum | 2 reduction | ok | PASS | - | 2.34 | 36 | - | 20.3 | - |  |
| r_mean_8192 | 2 reduction | ok | PASS | - | 2.44 | 40 | - | 20.3 | - |  |
| r_rag_max_33 | 2 reduction | ok | PASS | - | 2.49 | 40 | - | 20.5 | - |  |
| r_rag_rowmax_5x1000 | 2 reduction | ok | PASS | - | 2.21 | 36 | - | 24.0 | - |  |
| r_rag_rows_33x31 | 2 reduction | ok | PASS | - | 2.41 | 35 | - | 20.0 | - |  |
| r_rag_rows_7x4097 | 2 reduction | ok | PASS | - | 2.33 | 36 | - | 11.0 | - |  |
| r_rag_sum_1 | 2 reduction | ok | PASS | - | 2.12 | 8 | - | 24.3 | - |  |
| r_rag_sum_1000 | 2 reduction | ok | PASS | - | 2.32 | 40 | - | 20.4 | - |  |
| r_rag_sum_31 | 2 reduction | ok | PASS | - | 2.47 | 40 | - | 20.3 | - |  |
| r_rag_sum_33 | 2 reduction | ok | PASS | - | 2.28 | 40 | - | 20.1 | - |  |
| r_rag_sum_4097 | 2 reduction | ok | PASS | - | 2.27 | 40 | - | 23.5 | - |  |
| r_row_max | 2 reduction | ok | PASS | - | 2.37 | 36 | - | 20.2 | - |  |
| r_row_mean | 2 reduction | ok | PASS | - | 2.33 | 40 | - | 20.8 | - |  |
| r_row_sum_128x1024 | 2 reduction | ok | PASS | - | 2.17 | 36 | - | 20.7 | - |  |
| r_row_sum_32x256 | 2 reduction | ok | PASS | - | 2.29 | 35 | - | 20.4 | - |  |
| r_row_sum_keepdim | 2 reduction | ok | PASS | - | 2.32 | 35 | - | 20.2 | - |  |
| r_row_sum_odd | 2 reduction | ok | PASS | - | 2.20 | 35 | - | 20.4 | - |  |
| r_row_sum_unpinned | 2 reduction | ok | PASS | - | 2.19 | 36 | - | 20.2 | - |  |
| r_sum_100k | 2 reduction | ok | PASS | - | 2.31 | 40 | - | 32.9 | - |  |
| r_sum_300 | 2 reduction | ok | PASS | - | 2.17 | 40 | - | 20.8 | - |  |
| r_sum_4096 | 2 reduction | ok | PASS | - | 2.30 | 40 | - | 20.6 | - |  |
| r_sum_unpinned | 2 reduction | ok | PASS | - | 2.34 | 36 | - | 19.7 | - |  |
| r_sumsq | 2 reduction | ok | PASS | - | 2.24 | 40 | - | 20.6 | - |  |
| m01_matmul_512 | 3 matmul | ok | PASS | - | 4.18 | 40 | - | 40.0 | - |  |
| m02_matmul_rect | 3 matmul | ok | PASS | - | 2.91 | 35 | - | 16.3 | - |  |
| m_mm_1024 | 3 matmul | ok | PASS | - | 7.58 | 108 | - | 81.2 | - |  |
| m_mm_256 | 3 matmul | ok | PASS | - | 3.59 | 57 | - | 17.2 | - |  |
| m_mm_64 | 3 matmul | ok | PASS | - | 2.85 | 38 | - | 23.3 | - |  |
| m_mm_bias | 3 matmul | ok | PASS | - | 3.10 | 58 | - | 17.2 | - |  |
| m_mm_longk | 3 matmul | ok | PASS | - | 2.71 | 64 | - | 15.2 | - |  |
| m_mm_odd | 3 matmul | ok | PASS | - | 2.86 | 40 | - | 16.1 | - |  |
| m_mm_rect_tall | 3 matmul | ok | PASS | - | 3.47 | 64 | - | 16.2 | - |  |
| m_mm_rect_wide | 3 matmul | ok | PASS | - | 3.26 | 52 | - | 10.5 | - |  |
| m_mm_relu | 3 matmul | ok | PASS | - | 3.63 | 94 | - | 13.8 | - |  |
| m_mm_small_k | 3 matmul | ok | PASS | - | 3.45 | 34 | - | 18.7 | - |  |
| m_rag_1x64x64 | 3 matmul | ok | PASS | - | 2.25 | 40 | - | 20.4 | - |  |
| m_rag_33x31x17 | 3 matmul | ok | PASS | - | 2.46 | 40 | - | 20.2 | - |  |
| f01_rmsnorm | 4 fused | ok | PASS | - | 3.49 | 38 | - | 16.0 | - |  |
| f02_row_softmax | 4 fused | ok | PASS | - | 3.03 | 18 | - | 14.3 | - |  |
| f03_l2norm | 4 fused | ok | PASS | - | 3.34 | 38 | - | 14.4 | - |  |
| f_center | 4 fused | ok | PASS | - | 3.26 | 36 | - | 15.2 | - |  |
| f_l2norm_128x256 | 4 fused | ok | PASS | - | 3.20 | 34 | - | 14.7 | - |  |
| f_layernorm | 4 fused | ok | PASS | - | 3.22 | 40 | - | 17.3 | - |  |
| f_logsumexp | 4 fused | ok | PASS | - | 2.48 | 39 | - | 20.9 | - |  |
| f_max_norm | 4 fused | ok | PASS | - | 3.04 | 36 | - | 14.9 | - |  |
| f_rag_rms_7x1000 | 4 fused | ok | PASS | - | 2.80 | 38 | - | 19.6 | - |  |
| f_rag_softmax_1x4097 | 4 fused | ok | PASS | - | 2.72 | 18 | - | 15.2 | - |  |
| f_rag_softmax_33x31 | 4 fused | ok | PASS | - | 2.57 | 18 | - | 20.9 | - |  |
| f_rmsnorm_32x512 | 4 fused | ok | PASS | - | 3.01 | 38 | - | 15.6 | - |  |
| f_rmsnorm_rsqrt | 4 fused | ok | PASS | - | 3.18 | 34 | - | 15.5 | - |  |
| f_sigmoid_gate_norm | 4 fused | ok | PASS | - | 3.17 | 25 | - | 15.0 | - |  |
| f_softmax_128x128 | 4 fused | ok | PASS | - | 3.05 | 18 | - | 14.7 | - |  |
| f_softmax_32x1024 | 4 fused | ok | PASS | - | 3.14 | 18 | - | 15.3 | - |  |
| f_softmax_odd | 4 fused | ok | PASS | - | 3.05 | 18 | - | 15.0 | - |  |
| f_softmax_scaled | 4 fused | ok | PASS | - | 3.08 | 25 | - | 15.3 | - |  |
| a01_attention | 5 attention | ok | PASS | - | 2.75 | 255 | - | 72.1 | - |  |
| a02_attention_128 | 5 attention | ok | PASS | - | 2.78 | 80 | - | 43.0 | - |  |
| a_attn_128x128 | 5 attention | ok | PASS | - | 3.37 | 168 | - | 1229.8 | - |  |
| a_attn_128x64 | 5 attention | ok | PASS | - | 2.81 | 96 | - | 71.7 | - |  |
| a_attn_256x64 | 5 attention | ok | PASS | - | 3.20 | 255 | - | 1053.5 | - |  |
| a_attn_32x32 | 5 attention | ok | PASS | - | 2.71 | 60 | - | 34.4 | - |  |
| a_attn_noscale | 5 attention | ok | PASS | - | 2.66 | 50 | - | 18.8 | - |  |
| a_attn_rect | 5 attention | ok | PASS | - | 2.48 | 201 | - | 71.2 | - |  |
| a_rag_attn_33x17 | 5 attention | ok | PASS | - | 2.40 | 80 | - | 24.6 | - |  |

```
time                       2026-10-25 10:10:59
problems                   109
node_coverage              21/21
node_kinds_seen_unhandled  []
op_coverage                18/18
ops_unhandled              []
ptxas_accept               109/109
pass_by_category           {'1 pointwise': '39/39', '2 reduction': '29/29', '3 matmul': '14/14', '4 fused': '18/18', '5 attention': '9/9'}
pass_total                 109/109
worst_headroom             None
headroom_over_0.5          []
max_compile_s              7.58
total_spill_bytes          0
geomean_speed_vs_ref       None
mode                       remote
```
