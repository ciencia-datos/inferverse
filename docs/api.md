# Inferverse API Documentation

This API reference covers the currently exported classes and functions in `inferverse`.

## Imports

```python
from inferverse import InferPipeline, visualize, visualize_distribution
```

---

## `InferPipeline`

```python
class InferPipeline:
    data: pl.DataFrame
    response: str | None = None
    explanatory: str | None = None
    null: Literal["independence", "point"] | None = None
    null_value: float | None = None
```

Infer-style pipeline object for simulation-based statistical inference.

### Constructor

#### `InferPipeline(data, response=None, explanatory=None, null=None, null_value=None)`

- **data** (`pl.DataFrame`): input dataset.
- Other fields are optional and usually configured through method chaining.

---

### Methods

#### `specify(response, explanatory=None) -> InferPipeline`

Define analysis variables.

- **response** (`str`): response/outcome column name.
- **explanatory** (`str | None`): group/predictor column for two-group tests.

Raises `ValueError` if either requested column is missing.

#### `hypothesize(null, null_value=None) -> InferPipeline`

Set the null hypothesis model.

- **null** (`"independence" | "point"`)
- **null_value** (`float | None`): required when `null="point"`.

Raises `ValueError` for unsupported null types.

#### `generate(reps=1000, seed=None) -> pl.DataFrame`

Generate simulated datasets under the configured null.

- **reps** (`int`): number of replicates.
- **seed** (`int | None`): base seed for reproducibility.

Returns a concatenated `pl.DataFrame` including a `replicate` column.

Behavior by null type:

- `independence`: shuffles explanatory values each replicate.
- `point`: recenters response around `null_value` and bootstraps rows with replacement.

Raises `ValueError` if pipeline is not fully configured.

#### `calculate(generated, stat="mean") -> pl.DataFrame`

Compute replicate-level statistics from generated data.

- **generated** (`pl.DataFrame`): must include `replicate`.
- **stat** (`"mean" | "proportion" | "prop" | "diff_in_means" | "diff_in_props"`)

Returns a DataFrame containing:

- `replicate`
- `stat`

Notes:

- `mean`, `proportion`, and `prop` currently compute the replicate mean of `response`.
- `diff_in_means` and `diff_in_props` require exactly 2 explanatory groups.

#### `visualize(distribution, stat_col="stat", bins=30, observed_stat=None, direction="two-sided", title="Simulated null distribution") -> alt.Chart`

Convenience wrapper around `visualize_distribution`.

- **distribution**: simulated null distribution DataFrame.
- **stat_col**: statistic column to plot.
- **bins**: max number of histogram bins.
- **observed_stat**: observed test statistic (optional vertical rule).
- **direction**: one of `greater`, `less`, `two-sided`.
- **title**: chart title.

#### `p_value(null_distribution, observed_stat, direction="two-sided") -> float` *(staticmethod)*

Compute a simulation-based p-value.

- **null_distribution** (`pl.DataFrame`): expects `stat` column.
- **observed_stat** (`float`)
- **direction** (`"greater" | "less" | "two-sided"`)

Returns p-value as `float`.

#### `ci_from_t(sample, alpha=0.05) -> tuple[float, float]` *(staticmethod)*

Compute a t-based confidence interval from a sample.

- **sample** (`pl.Series`)
- **alpha** (`float`): significance level

Returns `(lower, upper)` confidence bounds.

---

## Visualization functions

## `visualize_distribution(distribution, stat_col="stat", bins=30, observed_stat=None, direction="two-sided", title="Simulated null distribution") -> alt.Chart`

Create an infer-style histogram with optional highlighted tail region.

Parameters:

- **distribution** (`pl.DataFrame`)
- **stat_col** (`str`)
- **bins** (`int`)
- **observed_stat** (`float | None`)
- **direction** (`"greater" | "less" | "two-sided"`)
- **title** (`str`)

Raises `ValueError` if `stat_col` is missing or if `direction` is invalid.

## `visualize(*args, **kwargs) -> alt.Chart`

Alias for `visualize_distribution` kept for backwards compatibility.
