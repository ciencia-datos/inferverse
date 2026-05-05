# inferverse

<p align="center">
  <img src="assets/inferverse-logo.svg" alt="Inferverse logo" width="520" />
</p>

`inferverse` is a Python-first statistical inference workflow inspired by `tidyverse::infer`.



## Core verbs

- `specify()` — choose response and (optionally) explanatory variables.
- `hypothesize()` — declare a null hypothesis (`independence` or `point`).
- `generate()` — simulate data under the null.
- `calculate()` — compute a statistic for each simulation replicate.
- `visualize()` — create an infer-style Altair histogram and optionally highlight p-value tails.

## Stack

- `polars` for fast DataFrame operations with tidy-like syntax.
- `uv` for dependency management and packaging.
- `scipy` and `statsmodels` for the stats ecosystem.
- `altair` for visualization.

## Quick start

```python
import polars as pl
from inferverse import InferPipeline

df = pl.DataFrame({
    "group": ["control", "control", "treat", "treat"],
    "y": [1.1, 0.9, 1.5, 1.7],
})

pipeline = (
    InferPipeline(df)
    .specify(response="y", explanatory="group")
    .hypothesize("independence")
)

null_samples = pipeline.generate(reps=1000, seed=123)
null_distribution = pipeline.calculate(null_samples, stat="diff_in_means")
chart = pipeline.visualize(null_distribution)
```

See `examples.py` for a complete A/B testing workflow and saved chart output.

## Feedback

[![Google Form](https://img.shields.io/badge/Google%20Form-Share%20feedback-7248B9?logo=googleforms&logoColor=white)](https://forms.gle/3KfUhaC2KSSqENAC9)

## White paper

Read the white paper here: [AI Challenge 2026 White Paper](https://ciencia-datos.github.io/AI_Challenge_2026/).

