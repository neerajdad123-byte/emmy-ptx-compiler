| problem | category | ptxas | result | headroom | compile s | regs | spills | us | vs ref | error |
|---|---|---|---|---|---|---|---|---|---|---|
| p00_scalar_add | 1 pointwise | ok | PASS | 0.000 | 0.79 | 16 | 0 | 48.0 | 0.97x |  |
| p01_vector_add | 1 pointwise | ok | PASS | 0.000 | 0.77 | 16 | 0 | 49.2 | 1.03x |  |
| p02_scale_shift | 1 pointwise | ok | PASS | 0.000 | 0.78 | 22 | 0 | 50.2 | 2.40x |  |
| p03_relu_mul | 1 pointwise | ok | PASS | 0.000 | 0.82 | 22 | 0 | 20.4 | 0.78x |  |
| p_add_3000 | 1 pointwise | ok | PASS | 0.000 | 0.84 | 22 | 0 | 26.5 | 0.55x |  |
| p_add_77 | 1 pointwise | ok | PASS | 0.000 | 0.85 | 12 | 0 | 13.8 | 0.97x |  |
| p_add_odd_1000 | 1 pointwise | ok | PASS | 0.000 | 0.80 | 16 | 0 | 24.0 | 1.17x |  |
| p_bias_row | 1 pointwise | ok | PASS | 0.000 | 0.80 | 22 | 0 | 12.5 | 0.66x |  |
| p_chain | 1 pointwise | ok | PASS | 0.008 | 0.84 | 21 | 0 | 25.6 | 1.11x |  |
| p_clamp | 1 pointwise | ok | PASS | 0.000 | 0.89 | 24 | 0 | 24.0 | 0.92x |  |
| p_div | 1 pointwise | ok | PASS | 0.008 | 0.83 | 21 | 0 | 50.9 | 2.07x |  |
| p_exp | 1 pointwise | ok | PASS | 0.016 | 0.82 | 16 | 0 | 49.1 | 1.92x |  |
| p_fma3 | 1 pointwise | ok | PASS | 0.000 | 0.82 | 30 | 0 | 50.2 | 2.52x |  |
| p_gelu | 1 pointwise | ok | PASS | 0.024 | 0.89 | 27 | 0 | 15.4 | 0.60x |  |
| p_gelu_tanh | 1 pointwise | ok | PASS | 0.014 | 0.90 | 27 | 0 | 26.4 | 1.52x |  |
| p_log | 1 pointwise | ok | PASS | 0.015 | 0.89 | 18 | 0 | 26.2 | - | ref timing skipped: nvrtc: ref.cu(7): error: expression preceding parentheses of apparent call must  |
| p_max | 1 pointwise | ok | PASS | 0.000 | 0.86 | 22 | 0 | 21.4 | 1.61x |  |
| p_min | 1 pointwise | ok | PASS | 0.000 | 0.84 | 22 | 0 | 49.2 | 3.51x |  |
| p_mul_big | 1 pointwise | ok | PASS | 0.000 | 0.85 | 22 | 0 | 15.4 | 1.00x |  |
| p_neg_abs | 1 pointwise | ok | PASS | 0.000 | 0.85 | 14 | 0 | 25.6 | 1.35x |  |
| p_pow2 | 1 pointwise | ok | PASS | 0.000 | 0.85 | 14 | 0 | 50.2 | 1.88x |  |
| p_rag_2d_33x31 | 1 pointwise | ok | PASS | 0.004 | 0.84 | 16 | 0 | 27.3 | 1.01x |  |
| p_rag_add_1 | 1 pointwise | ok | PASS | 0.000 | 0.86 | 12 | 0 | 39.1 | 1.50x |  |
| p_rag_add_1000 | 1 pointwise | ok | PASS | 0.000 | 0.85 | 16 | 0 | 14.3 | 1.03x |  |
| p_rag_add_31 | 1 pointwise | ok | PASS | 0.000 | 0.83 | 12 | 0 | 48.0 | 1.20x |  |
| p_rag_add_33 | 1 pointwise | ok | PASS | 0.000 | 0.83 | 26 | 0 | 26.6 | 0.54x |  |
| p_rag_add_4097 | 1 pointwise | ok | PASS | 0.000 | 0.87 | 12 | 0 | 12.8 | 0.52x |  |
| p_rag_bias_7x4097 | 1 pointwise | ok | PASS | 0.000 | 0.85 | 12 | 0 | 24.0 | 1.12x |  |
| p_relu_2d | 1 pointwise | ok | PASS | 0.000 | 0.85 | 18 | 0 | 12.8 | 0.52x |  |
| p_rsqrt | 1 pointwise | ok | PASS | 0.006 | 0.81 | 22 | 0 | 49.0 | 1.85x |  |
| p_scale_col | 1 pointwise | ok | PASS | 0.000 | 0.77 | 22 | 0 | 13.7 | 0.79x |  |
| p_scale_shift_odd | 1 pointwise | ok | PASS | 0.104 | 0.80 | 22 | 0 | 19.2 | 0.81x |  |
| p_sigmoid | 1 pointwise | ok | PASS | 0.004 | 0.78 | 18 | 0 | 48.1 | 1.88x |  |
| p_silu | 1 pointwise | ok | PASS | 0.010 | 0.77 | 20 | 0 | 14.0 | 0.29x |  |
| p_softplus | 1 pointwise | ok | PASS | 0.013 | 0.82 | 23 | 0 | 20.0 | 1.42x |  |
| p_sqrt | 1 pointwise | ok | PASS | 0.000 | 0.85 | 15 | 0 | 26.2 | 1.91x |  |
| p_square | 1 pointwise | ok | PASS | 0.000 | 0.81 | 30 | 0 | 19.5 | 0.79x |  |
| p_sub_2d | 1 pointwise | ok | PASS | 0.000 | 0.84 | 25 | 0 | 28.6 | 1.95x |  |
| p_tanh | 1 pointwise | ok | PASS | 0.008 | 0.81 | 19 | 0 | 13.9 | 0.58x |  |
| r01_array_sum | 2 reduction | ok | PASS | 0.001 | 0.77 | 16 | 0 | 48.1 | 1.00x |  |
| r02_big_sum | 2 reduction | ok | PASS | 0.000 | 0.77 | 16 | 0 | 46.1 | 2.19x |  |
| r03_mean | 2 reduction | ok | PASS | 0.000 | 0.78 | 16 | 0 | 34.9 | 1.07x |  |
| r04_row_sum | 2 reduction | ok | PASS | 0.007 | 0.78 | 18 | 0 | 48.2 | 3.67x |  |
| r_abs_sum | 2 reduction | ok | PASS | 0.000 | 0.77 | 16 | 0 | 50.2 | 3.81x |  |
| r_amax | 2 reduction | ok | PASS | 0.000 | 0.76 | 16 | 0 | 25.0 | 1.49x |  |
| r_col_sum | 2 reduction | ok | PASS | 0.009 | 0.79 | 18 | 0 | 13.7 | 0.70x |  |
| r_mean_8192 | 2 reduction | ok | PASS | 0.000 | 0.76 | 16 | 0 | 53.2 | 3.61x |  |
| r_rag_max_33 | 2 reduction | ok | PASS | 0.000 | 0.77 | 16 | 0 | 49.2 | 3.85x |  |
| r_rag_rowmax_5x1000 | 2 reduction | ok | PASS | 0.000 | 0.77 | 18 | 0 | 27.2 | 0.55x |  |
| r_rag_rows_33x31 | 2 reduction | ok | PASS | 0.004 | 0.81 | 18 | 0 | 24.1 | 1.17x |  |
| r_rag_rows_7x4097 | 2 reduction | ok | PASS | 0.013 | 0.77 | 18 | 0 | 48.7 | 2.31x |  |
| r_rag_sum_1 | 2 reduction | ok | PASS | 0.000 | 0.78 | 8 | 0 | 15.9 | 1.24x |  |
| r_rag_sum_1000 | 2 reduction | ok | PASS | 0.001 | 0.77 | 16 | 0 | 16.3 | 0.69x |  |
| r_rag_sum_31 | 2 reduction | ok | PASS | 0.000 | 0.76 | 16 | 0 | 12.3 | 0.89x |  |
| r_rag_sum_33 | 2 reduction | ok | PASS | 0.000 | 0.82 | 16 | 0 | 26.6 | 1.95x |  |
| r_rag_sum_4097 | 2 reduction | ok | PASS | 0.000 | 0.79 | 16 | 0 | 16.5 | 0.68x |  |
| r_row_max | 2 reduction | ok | PASS | 0.000 | 0.77 | 18 | 0 | 12.3 | 0.93x |  |
| r_row_mean | 2 reduction | ok | PASS | 0.000 | 0.77 | 18 | 0 | 24.9 | 1.72x |  |
| r_row_sum_128x1024 | 2 reduction | ok | PASS | 0.033 | 0.77 | 18 | 0 | 14.3 | 0.99x |  |
| r_row_sum_32x256 | 2 reduction | ok | PASS | 0.010 | 0.87 | 18 | 0 | 50.1 | 3.08x |  |
| r_row_sum_keepdim | 2 reduction | ok | PASS | 0.010 | 0.84 | 18 | 0 | 24.2 | 1.02x |  |
| r_row_sum_odd | 2 reduction | ok | PASS | 0.005 | 0.88 | 18 | 0 | 26.6 | 2.00x |  |
| r_row_sum_unpinned | 2 reduction | ok | PASS | 0.005 | 0.86 | 18 | 0 | 20.4 | 0.60x |  |
| r_sum_100k | 2 reduction | ok | PASS | 0.000 | 0.84 | 16 | 0 | 42.0 | 1.15x |  |
| r_sum_300 | 2 reduction | ok | PASS | 0.002 | 0.82 | 16 | 0 | 13.5 | 0.54x |  |
| r_sum_4096 | 2 reduction | ok | PASS | 0.000 | 0.83 | 16 | 0 | 17.4 | 0.68x |  |
| r_sum_unpinned | 2 reduction | ok | PASS | 0.000 | 0.86 | 18 | 0 | 34.8 | 1.13x |  |
| r_sumsq | 2 reduction | ok | PASS | 0.000 | 0.85 | 16 | 0 | 15.5 | 0.79x |  |
| m01_matmul_512 | 3 matmul | ok | PASS | 0.024 | 0.86 | 40 | 0 | 594.2 | 4.43x |  |
| m02_matmul_rect | 3 matmul | ok | PASS | 0.003 | 0.85 | 31 | 0 | 32.3 | 1.09x |  |
| m_mm_1024 | 3 matmul | ok | PASS | 0.051 | 0.87 | 64 | 0 | 3094.6 | 6.01x |  |
| m_mm_256 | 3 matmul | ok | PASS | 0.012 | 0.85 | 42 | 0 | 233.9 | 4.79x |  |
| m_mm_64 | 3 matmul | ok | PASS | 0.003 | 0.86 | 78 | 0 | 51.6 | 3.36x |  |
| m_mm_bias | 3 matmul | ok | PASS | 0.013 | 0.84 | 40 | 0 | 76.2 | 2.37x |  |
| m_mm_longk | 3 matmul | ok | PASS | 0.016 | 0.85 | 60 | 0 | 30.5 | 0.98x |  |
| m_mm_odd | 3 matmul | ok | PASS | 0.003 | 0.83 | 48 | 0 | 61.4 | 1.15x |  |
| m_mm_rect_tall | 3 matmul | ok | PASS | 0.007 | 0.92 | 64 | 0 | 16.4 | 0.60x |  |
| m_mm_rect_wide | 3 matmul | ok | PASS | 0.003 | 0.85 | 50 | 0 | 34.5 | 1.05x |  |
| m_mm_relu | 3 matmul | ok | PASS | 0.006 | 0.83 | 204 | 0 | 100.4 | 2.93x |  |
| m_mm_small_k | 3 matmul | ok | PASS | 0.001 | 0.87 | 32 | 0 | 31.8 | 1.12x |  |
| m_rag_1x64x64 | 3 matmul | ok | PASS | 0.001 | 0.93 | 40 | 0 | 13.7 | 0.24x |  |
| m_rag_33x31x17 | 3 matmul | ok | PASS | 0.001 | 0.87 | 28 | 0 | 32.8 | 0.62x |  |
| f01_rmsnorm | 4 fused | ok | PASS | 0.000 | 0.90 | 20 | 0 | 27.0 | 0.53x |  |
| f02_row_softmax | 4 fused | ok | PASS | 0.000 | 0.82 | 23 | 0 | 49.3 | 1.00x |  |
| f03_l2norm | 4 fused | ok | PASS | 0.000 | 0.82 | 18 | 0 | 13.4 | 0.27x |  |
| f_center | 4 fused | ok | PASS | 0.001 | 0.82 | 20 | 0 | 20.8 | 0.41x |  |
| f_l2norm_128x256 | 4 fused | ok | PASS | 0.000 | 0.83 | 18 | 0 | 13.7 | 0.53x |  |
| f_layernorm | 4 fused | ok | PASS | 0.000 | 0.80 | 40 | 0 | 31.7 | 1.24x |  |
| f_logsumexp | 4 fused | ok | PASS | 0.001 | 0.78 | 40 | 0 | 20.4 | 0.58x |  |
| f_max_norm | 4 fused | ok | PASS | 0.000 | 0.79 | 18 | 0 | 49.2 | 1.88x |  |
| f_rag_rms_7x1000 | 4 fused | ok | PASS | 0.000 | 0.82 | 20 | 0 | 14.4 | 0.76x |  |
| f_rag_softmax_1x4097 | 4 fused | ok | PASS | 0.000 | 0.78 | 22 | 0 | 52.4 | 1.03x |  |
| f_rag_softmax_33x31 | 4 fused | ok | PASS | 0.000 | 0.78 | 23 | 0 | 12.8 | 0.45x |  |
| f_rmsnorm_32x512 | 4 fused | ok | PASS | 0.000 | 0.83 | 20 | 0 | 15.4 | 0.97x |  |
| f_rmsnorm_rsqrt | 4 fused | ok | PASS | 0.000 | 0.78 | 20 | 0 | 13.5 | 0.27x |  |
| f_sigmoid_gate_norm | 4 fused | ok | PASS | 0.000 | 0.77 | 20 | 0 | 13.3 | 0.71x |  |
| f_softmax_128x128 | 4 fused | ok | PASS | 0.000 | 0.79 | 23 | 0 | 23.7 | 0.45x |  |
| f_softmax_32x1024 | 4 fused | ok | PASS | 0.000 | 0.79 | 23 | 0 | 50.1 | 3.74x |  |
| f_softmax_odd | 4 fused | ok | PASS | 0.000 | 0.77 | 23 | 0 | 13.5 | 0.76x |  |
| f_softmax_scaled | 4 fused | ok | PASS | 0.000 | 0.78 | 24 | 0 | 49.2 | 2.04x |  |
| a01_attention | 5 attention | ok | PASS | 0.002 | 0.78 | 48 | 0 | 279.6 | 1.97x |  |
| a02_attention_128 | 5 attention | ok | PASS | 0.001 | 0.77 | 80 | 0 | 72.7 | 1.11x |  |
| a_attn_128x128 | 5 attention | ok | PASS | 0.000 | 0.81 | 171 | 0 | 7046.8 | 5.66x |  |
| a_attn_128x64 | 5 attention | ok | PASS | 0.001 | 0.80 | 96 | 0 | 155.7 | 1.04x |  |
| a_attn_256x64 | 5 attention | ok | PASS | 0.000 | 0.78 | 64 | 0 | 4452.8 | 5.14x |  |
| a_attn_32x32 | 5 attention | ok | PASS | 0.000 | 0.77 | 59 | 0 | 40.0 | 0.62x |  |
| a_attn_noscale | 5 attention | ok | PASS | 0.001 | 0.78 | 51 | 0 | 30.6 | 0.46x |  |
| a_attn_rect | 5 attention | ok | PASS | 0.000 | 0.77 | 205 | 0 | 98.2 | 1.22x |  |
| a_rag_attn_33x17 | 5 attention | ok | PASS | 0.000 | 0.78 | 80 | 0 | 58.4 | 1.05x |  |

```
time                       2026-10-22 02:00:10
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
max_compile_s              0.93
total_spill_bytes          0
geomean_speed_vs_ref       1.154
mode                       local
```
