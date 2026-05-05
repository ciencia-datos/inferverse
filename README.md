# inferverse

<p align="center">
  <img src="assets/inferverse-logo.svg" alt="Inferverse logo" width="520" />
</p>

`inferverse` is a Python-first statistical inference workflow inspired by `tidyverse::infer`.

`inferverse` is currently in beta and built for learners and practitioners who need practical statistical reasoning.
Modern data work needs more than summaries: it needs principled inference to separate signal from noise.
The package makes core statistics workflows reproducible, from hypothesis setup to null-distribution simulation.
It brings inference-friendly verbs into Python so analysts can run rigorous tests without leaving their data pipeline.
By combining approachable syntax with scientific rigor, `inferverse` helps teams make evidence-based decisions with confidence.



## Introduction to statistical inference

[![Google Drive](https://img.shields.io/badge/Google%20Drive-Watch%20intro%20video-34A853?logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1TWgLDTzn53AvYPF6ZrWSR6N2ZIFyI4x5/view?usp=sharing)



## Introduction to statistical inference

[![Google Drive](https://img.shields.io/badge/Google%20Drive-Watch%20intro%20video-34A853?logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1TWgLDTzn53AvYPF6ZrWSR6N2ZIFyI4x5/view?usp=sharing)



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

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1U6tYzvFLxvL4jS7lQWmbz6SdIwoRnqAE?usp=sharing)

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


## Documentation

- Module documentation: [`docs/modules.md`](docs/modules.md)
- API reference: [`docs/api.md`](docs/api.md)



## Educational Resources

- [Introduction to Modern Statistics (OpenIntro)](https://openintrostat.github.io/ims/)
- [ModernDive (2nd edition)](https://moderndive.com/v2/)


## White paper

Read the white paper here: [AI Challenge 2026 White Paper](https://ciencia-datos.github.io/AI_Challenge_2026/).

## Feedback

[![Google Form](https://img.shields.io/badge/Google%20Form-Share%20feedback-7248B9?logo=googleforms&logoColor=white)](https://forms.gle/3KfUhaC2KSSqENAC9)
