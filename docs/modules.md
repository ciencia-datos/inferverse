# Inferverse Module Documentation

This document explains the modules currently available in `inferverse` and what each one is responsible for.

## Package layout

- `inferverse.__init__`
- `inferverse.core`
- `inferverse.visualize`

---

## `inferverse.__init__`

**Purpose:** Public package entrypoint.

This module defines what users get when they import directly from `inferverse`.

### Public exports

- `InferPipeline` (from `inferverse.core`)
- `visualize` (from `inferverse.visualize`)
- `visualize_distribution` (from `inferverse.visualize`)

Use this module when you want a stable, concise public import surface:

```python
from inferverse import InferPipeline, visualize_distribution
```

---

## `inferverse.core`

**Purpose:** End-to-end infer-style workflow for simulation-based inference.

This module contains the main orchestration class, `InferPipeline`, which supports the core workflow:

1. `specify()` variables
2. `hypothesize()` a null model
3. `generate()` simulated data under the null
4. `calculate()` replicate statistics
5. `visualize()` and/or compute `p_value()`

### Key concepts in this module

- **Null types**
  - `independence`: shuffles explanatory labels to break association.
  - `point`: recenters response to a specified null mean and bootstraps.
- **Statistic types**
  - One-sample style: `mean`, `proportion`, `prop`
  - Two-group style: `diff_in_means`, `diff_in_props`

### Typical usage pattern

```python
pipeline = (
    InferPipeline(df)
    .specify(response="y", explanatory="group")
    .hypothesize("independence")
)
null_samples = pipeline.generate(reps=1000, seed=123)
null_dist = pipeline.calculate(null_samples, stat="diff_in_means")
p = pipeline.p_value(null_dist, observed_stat=0.21)
```

---

## `inferverse.visualize`

**Purpose:** Visualization helpers for simulated null distributions.

This module is focused on plotting and contains:

- `visualize_distribution(...)`: creates an Altair histogram of simulated statistics and highlights tail regions based on p-value direction.
- `visualize(...)`: backwards-compatible alias for `visualize_distribution`.

### Visual semantics

- Bars in the body are shown in blue (`#4C78A8`).
- Tail bars are shown in red (`#E45756`).
- Optionally overlays a dashed vertical rule at `observed_stat`.

Use this module directly when you already have a distribution DataFrame and want a reusable chart function.
