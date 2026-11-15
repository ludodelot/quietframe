# Experimental

Not part of the released tool, kept for reference.

`noise_model.py` generates synthetic camera-like noise for benchmarking denoisers. The finding it encodes:
on a Canon EOS R6 V the noise in Log code values is **spatially correlated** (not white): robust std of
`x[i+k]-x[i]` for k=2 and k=4 relative to k=1 was about 1.7 and 2.5, which a Gaussian-smoothed white-noise model with
sigma about 1.2 px reproduces. Chroma noise was about 0.09 of luma in code values. The benchmark harness that uses it
is unfinished, so no results are claimed from it.
