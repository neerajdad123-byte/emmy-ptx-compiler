| problem | category | ptxas | result | headroom | compile s | regs | spills | us | vs ref | error |
|---|---|---|---|---|---|---|---|---|---|---|
| p00_scalar_add | 1 pointwise | ok | PASS | 0.000 | 0.80 | 14 | 0 | 8.1 | 1.01x |  |
| p01_vector_add | 1 pointwise | ok | PASS | 0.000 | 0.80 | 14 | 0 | 6.4 | 0.99x |  |
| p02_scale_shift | 1 pointwise | ok | PASS | 0.000 | 0.76 | 17 | 0 | 7.0 | 0.99x |  |
| p03_relu_mul | 1 pointwise | ok | PASS | 0.000 | 0.75 | 18 | 0 | 6.6 | 1.02x |  |
| p_add_3000 | 1 pointwise | ok | PASS | 0.000 | 0.79 | 18 | 0 | 7.1 | 0.89x |  |
| p_add_77 | 1 pointwise | ok | PASS | 0.000 | 0.77 | 12 | 0 | 7.2 | 1.00x |  |
| p_add_odd_1000 | 1 pointwise | ok | PASS | 0.000 | 0.76 | 14 | 0 | 7.1 | 0.93x |  |
| p_bias_row | 1 pointwise | ok | PASS | 0.000 | 0.76 | 18 | 0 | 6.9 | 0.95x |  |
| p_chain | 1 pointwise | ok | PASS | 0.008 | 0.74 | 21 | 0 | 6.6 | 0.97x |  |
| p_clamp | 1 pointwise | ok | PASS | 0.000 | 0.75 | 20 | 0 | 9.4 | 1.23x |  |
| p_div | 1 pointwise | ok | PASS | 0.008 | 0.75 | 25 | 0 | 7.8 | 0.98x |  |
| p_exp | 1 pointwise | ok | PASS | 0.016 | 0.75 | 16 | 0 | 6.8 | 1.00x |  |
| p_fma3 | 1 pointwise | ok | PASS | 0.000 | 0.75 | 28 | 0 | 8.6 | 1.03x |  |
| p_gelu | 1 pointwise | ok | PASS | 0.024 | 0.75 | 30 | 0 | 9.2 | 0.96x |  |
| p_gelu_tanh | 1 pointwise | ok | PASS | 0.014 | 0.77 | 29 | 0 | 7.8 | 1.00x |  |
| p_log | 1 pointwise | ok | PASS | 0.015 | 0.75 | 15 | 0 | 7.2 | - | ref timing skipped: nvrtc: ref.cu(7): error: expression preceding parentheses of apparent call must  |
| p_max | 1 pointwise | ok | PASS | 0.000 | 0.74 | 18 | 0 | 7.3 | 1.05x |  |
| p_min | 1 pointwise | ok | PASS | 0.000 | 0.75 | 18 | 0 | 7.2 | 1.02x |  |
| p_mul_big | 1 pointwise | ok | PASS | 0.000 | 0.76 | 18 | 0 | 7.5 | 1.00x |  |
| p_neg_abs | 1 pointwise | ok | PASS | 0.000 | 0.75 | 14 | 0 | 6.3 | 1.03x |  |
| p_pow2 | 1 pointwise | ok | PASS | 0.000 | 0.75 | 14 | 0 | 6.6 | 0.96x |  |
| p_rag_2d_33x31 | 1 pointwise | ok | PASS | 0.004 | 0.74 | 18 | 0 | 6.9 | 1.01x |  |
| p_rag_add_1 | 1 pointwise | ok | PASS | 0.000 | 0.81 | 12 | 0 | 6.8 | 0.93x |  |
| p_rag_add_1000 | 1 pointwise | ok | PASS | 0.000 | 0.80 | 14 | 0 | 7.3 | 1.05x |  |
| p_rag_add_31 | 1 pointwise | ok | PASS | 0.000 | 0.81 | 12 | 0 | 6.9 | 1.04x |  |
| p_rag_add_33 | 1 pointwise | ok | PASS | 0.000 | 0.83 | 18 | 0 | 7.4 | 0.98x |  |
| p_rag_add_4097 | 1 pointwise | ok | PASS | 0.000 | 0.82 | 12 | 0 | 6.7 | 0.97x |  |
| p_rag_bias_7x4097 | 1 pointwise | ok | PASS | 0.000 | 0.80 | 12 | 0 | 6.6 | 0.93x |  |
| p_relu_2d | 1 pointwise | ok | PASS | 0.000 | 0.80 | 18 | 0 | 6.3 | 1.00x |  |
| p_rsqrt | 1 pointwise | ok | PASS | 0.006 | 0.81 | 17 | 0 | 6.4 | 1.00x |  |
| p_scale_col | 1 pointwise | ok | PASS | 0.000 | 0.82 | 17 | 0 | 7.6 | 1.05x |  |
| p_scale_shift_odd | 1 pointwise | ok | PASS | 0.104 | 0.82 | 17 | 0 | 9.2 | 1.00x |  |
| p_sigmoid | 1 pointwise | ok | PASS | 0.004 | 0.93 | 18 | 0 | 7.7 | 1.15x |  |
| p_silu | 1 pointwise | ok | PASS | 0.010 | 0.79 | 20 | 0 | 6.8 | 0.94x |  |
| p_softplus | 1 pointwise | ok | PASS | 0.013 | 0.77 | 21 | 0 | 9.3 | 1.24x |  |
| p_sqrt | 1 pointwise | ok | PASS | 0.000 | 0.81 | 15 | 0 | 6.2 | 0.92x |  |
| p_square | 1 pointwise | ok | PASS | 0.000 | 0.79 | 26 | 0 | 9.1 | 0.99x |  |
| p_sub_2d | 1 pointwise | ok | PASS | 0.000 | 0.80 | 22 | 0 | 7.1 | 1.05x |  |
| p_tanh | 1 pointwise | ok | PASS | 0.008 | 0.76 | 19 | 0 | 6.5 | 0.86x |  |
| r01_array_sum | 2 reduction | ok | PASS | 0.001 | 0.78 | 40 | 0 | 6.0 | 0.85x |  |
| r02_big_sum | 2 reduction | ok | PASS | 0.000 | 0.82 | 40 | 0 | 11.5 | 1.07x |  |
| r03_mean | 2 reduction | ok | PASS | 0.000 | 0.81 | 40 | 0 | 8.7 | 1.04x |  |
| r04_row_sum | 2 reduction | ok | PASS | 0.007 | 0.83 | 36 | 0 | 7.1 | 1.01x |  |
| r_abs_sum | 2 reduction | ok | PASS | 0.000 | 0.80 | 40 | 0 | 6.1 | 0.97x |  |
| r_amax | 2 reduction | ok | PASS | 0.000 | 0.80 | 40 | 0 | 6.7 | 0.97x |  |
| r_col_sum | 2 reduction | ok | PASS | 0.009 | 0.82 | 36 | 0 | 6.8 | 0.92x |  |
| r_mean_8192 | 2 reduction | ok | PASS | 0.000 | 0.80 | 40 | 0 | 6.7 | 1.01x |  |
| r_rag_max_33 | 2 reduction | ok | PASS | 0.000 | 0.78 | 40 | 0 | 6.5 | 0.92x |  |
| r_rag_rowmax_5x1000 | 2 reduction | ok | PASS | 0.000 | 0.80 | 36 | 0 | 6.7 | 0.94x |  |
| r_rag_rows_33x31 | 2 reduction | ok | PASS | 0.004 | 0.77 | 18 | 0 | 6.4 | 1.04x |  |
| r_rag_rows_7x4097 | 2 reduction | ok | PASS | 0.013 | 0.84 | 36 | 0 | 6.7 | 1.08x |  |
| r_rag_sum_1 | 2 reduction | ok | PASS | 0.000 | 0.83 | 8 | 0 | 6.8 | 1.02x |  |
| r_rag_sum_1000 | 2 reduction | ok | PASS | 0.001 | 0.82 | 40 | 0 | 6.4 | 0.99x |  |
| r_rag_sum_31 | 2 reduction | ok | PASS | 0.000 | 0.80 | 40 | 0 | 6.9 | 1.00x |  |
| r_rag_sum_33 | 2 reduction | ok | PASS | 0.000 | 0.79 | 40 | 0 | 6.0 | 0.97x |  |
| r_rag_sum_4097 | 2 reduction | ok | PASS | 0.000 | 0.77 | 40 | 0 | 6.2 | 0.93x |  |
| r_row_max | 2 reduction | ok | PASS | 0.000 | 0.77 | 36 | 0 | 6.8 | 0.99x |  |
| r_row_mean | 2 reduction | ok | PASS | 0.000 | 0.90 | 36 | 0 | 8.9 | 1.14x |  |
| r_row_sum_128x1024 | 2 reduction | ok | PASS | 0.033 | 0.85 | 36 | 0 | 6.9 | 0.99x |  |
| r_row_sum_32x256 | 2 reduction | ok | PASS | 0.010 | 0.84 | 18 | 0 | 6.2 | 1.04x |  |
| r_row_sum_keepdim | 2 reduction | ok | PASS | 0.010 | 0.80 | 18 | 0 | 6.2 | 1.02x |  |
| r_row_sum_odd | 2 reduction | ok | PASS | 0.005 | 0.79 | 18 | 0 | 8.1 | 0.94x |  |
| r_row_sum_unpinned | 2 reduction | ok | PASS | 0.005 | 0.88 | 36 | 0 | 8.3 | 1.04x |  |
| r_sum_100k | 2 reduction | ok | PASS | 0.000 | 0.91 | 40 | 0 | 14.2 | 1.06x |  |
| r_sum_300 | 2 reduction | ok | PASS | 0.002 | 0.86 | 40 | 0 | 6.9 | 1.02x |  |
| r_sum_4096 | 2 reduction | ok | PASS | 0.000 | 0.89 | 40 | 0 | 6.4 | 1.01x |  |
| r_sum_unpinned | 2 reduction | ok | PASS | 0.000 | 0.80 | 33 | 0 | 7.6 | 0.99x |  |
| r_sumsq | 2 reduction | ok | PASS | 0.000 | 0.83 | 40 | 0 | 6.1 | 0.94x |  |
| m01_matmul_512 | 3 matmul | ok | PASS | 0.024 | 0.95 | 40 | 0 | 112.5 | 1.18x |  |
| m02_matmul_rect | 3 matmul | ok | PASS | 0.003 | 0.88 | 34 | 0 | 9.4 | 1.03x |  |
| m_mm_1024 | 3 matmul | ok | PASS | 0.051 | 0.84 | 108 | 0 | 389.7 | 0.95x |  |
| m_mm_256 | 3 matmul | ok | PASS | 0.012 | 0.82 | 56 | 0 | 33.1 | 1.26x |  |
| m_mm_64 | 3 matmul | ok | PASS | 0.003 | 0.88 | 38 | 0 | 7.5 | 1.00x |  |
| m_mm_bias | 3 matmul | ok | PASS | 0.013 | 0.92 | 56 | 0 | 13.8 | 1.39x |  |
| m_mm_longk | 3 matmul | ok | PASS | 0.016 | 0.87 | 60 | 0 | 12.4 | 1.35x |  |
| m_mm_odd | 3 matmul | ok | PASS | 0.003 | 0.78 | 40 | 0 | 8.0 | 1.02x |  |
| m_mm_rect_tall | 3 matmul | ok | PASS | 0.007 | 0.80 | 66 | 0 | 8.0 | 1.00x |  |
| m_mm_rect_wide | 3 matmul | ok | PASS | 0.003 | 0.79 | 51 | 0 | 10.4 | 0.98x |  |
| m_mm_relu | 3 matmul | ok | PASS | 0.006 | 0.87 | 80 | 0 | 11.7 | 0.92x |  |
| m_mm_small_k | 3 matmul | ok | PASS | 0.001 | 0.78 | 38 | 0 | 7.9 | 1.03x |  |
| m_rag_1x64x64 | 3 matmul | ok | PASS | 0.001 | 0.88 | 40 | 0 | 6.9 | 0.86x |  |
| m_rag_33x31x17 | 3 matmul | ok | PASS | 0.001 | 0.83 | 28 | 0 | 8.8 | 1.06x |  |
| f01_rmsnorm | 4 fused | ok | PASS | 0.000 | 0.86 | 40 | 0 | 9.3 | 0.95x |  |
| f02_row_softmax | 4 fused | ok | PASS | 0.000 | 0.81 | 23 | 0 | 6.6 | 0.96x |  |
| f03_l2norm | 4 fused | ok | PASS | 0.000 | 0.80 | 40 | 0 | 6.5 | 0.97x |  |
| f_center | 4 fused | ok | PASS | 0.001 | 0.78 | 36 | 0 | 6.9 | 1.04x |  |
| f_l2norm_128x256 | 4 fused | ok | PASS | 0.000 | 0.77 | 18 | 0 | 6.3 | 1.00x |  |
| f_layernorm | 4 fused | ok | PASS | 0.000 | 0.86 | 40 | 0 | 13.1 | 0.99x |  |
| f_logsumexp | 4 fused | ok | PASS | 0.001 | 0.88 | 39 | 0 | 9.0 | 0.88x |  |
| f_max_norm | 4 fused | ok | PASS | 0.000 | 0.86 | 36 | 0 | 6.8 | 1.01x |  |
| f_rag_rms_7x1000 | 4 fused | ok | PASS | 0.000 | 0.83 | 40 | 0 | 9.4 | 1.03x |  |
| f_rag_softmax_1x4097 | 4 fused | ok | PASS | 0.000 | 0.82 | 21 | 0 | 7.0 | 0.87x |  |
| f_rag_softmax_33x31 | 4 fused | ok | PASS | 0.000 | 0.83 | 23 | 0 | 7.1 | 1.13x |  |
| f_rmsnorm_32x512 | 4 fused | ok | PASS | 0.000 | 0.86 | 40 | 0 | 9.8 | 0.99x |  |
| f_rmsnorm_rsqrt | 4 fused | ok | PASS | 0.000 | 0.81 | 20 | 0 | 8.5 | 0.91x |  |
| f_sigmoid_gate_norm | 4 fused | ok | PASS | 0.000 | 0.83 | 21 | 0 | 6.5 | 0.97x |  |
| f_softmax_128x128 | 4 fused | ok | PASS | 0.000 | 0.81 | 23 | 0 | 6.7 | 1.04x |  |
| f_softmax_32x1024 | 4 fused | ok | PASS | 0.000 | 0.84 | 25 | 0 | 6.4 | 0.97x |  |
| f_softmax_odd | 4 fused | ok | PASS | 0.000 | 0.81 | 23 | 0 | 6.3 | 0.97x |  |
| f_softmax_scaled | 4 fused | ok | PASS | 0.000 | 0.82 | 25 | 0 | 6.8 | 1.00x |  |
| a01_attention | 5 attention | ok | PASS | 0.002 | 0.83 | 255 | 408 | 79.0 | 0.84x |  |
| a02_attention_128 | 5 attention | ok | PASS | 0.001 | 0.86 | 80 | 0 | 37.0 | 0.86x |  |
| a_attn_128x128 | 5 attention | ok | PASS | 0.000 | 0.91 | 168 | 16 | 1217.3 | 1.00x |  |
| a_attn_128x64 | 5 attention | ok | PASS | 0.001 | 0.83 | 96 | 0 | 101.8 | 1.03x |  |
| a_attn_256x64 | 5 attention | ok | PASS | 0.000 | 0.82 | 255 | 1576 | 573.2 | 0.88x |  |
| a_attn_32x32 | 5 attention | ok | PASS | 0.000 | 0.77 | 57 | 0 | 19.7 | 1.21x |  |
| a_attn_noscale | 5 attention | ok | PASS | 0.001 | 0.75 | 51 | 0 | 18.9 | 0.93x |  |
| a_attn_rect | 5 attention | ok | PASS | 0.000 | 0.76 | 202 | 0 | 59.9 | 0.88x |  |
| a_rag_attn_33x17 | 5 attention | ok | PASS | 0.000 | 0.85 | 80 | 0 | 8.9 | 0.94x |  |

```
time                       2026-10-22 07:02:57
problems                   109
node_coverage              21/21
node_kinds_seen_unhandled  []
op_coverage                18/18
ops_unhandled              []
ptxas_accept               109/109
pass_by_category           {'1 pointwise': '39/39', '2 reduction': '29/29', '3 matmul': '14/14', '4 fused': '18/18', '5 attention': '9/9'}
pass_total                 109/109
worst_headroom             0.10385415080946388
headroom_over_0.5          []
max_compile_s              0.95
total_spill_bytes          2000
geomean_speed_vs_ref       0.999
mode                       local
```
