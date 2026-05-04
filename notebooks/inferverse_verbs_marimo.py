import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    from inferverse import InferPipeline
    return InferPipeline, pl


@app.cell
def _(pl):
    data = pl.DataFrame(
        {
            "group": ["control"] * 30 + ["treatment"] * 30,
            "outcome": [0, 1, 0, 0, 1, 1] * 10,
        }
    )
    data
    return (data,)


@app.cell
def _(data):
    marimo.md("## 1) `specify()`\nDeclare response and explanatory variables.")
    return


@app.cell
def _(InferPipeline, data):
    specified = InferPipeline(data).specify(response="outcome", explanatory="group")
    specified
    return (specified,)


@app.cell
def _():
    marimo.md("## 2) `hypothesize()`\nDeclare the null hypothesis.")
    return


@app.cell
def _(specified):
    pipeline = specified.hypothesize("independence")
    pipeline
    return (pipeline,)


@app.cell
def _():
    marimo.md("## 3) `generate()`\nGenerate null-world simulations.")
    return


@app.cell
def _(pipeline):
    generated = pipeline.generate(reps=300, seed=42)
    generated.head()
    return (generated,)


@app.cell
def _():
    marimo.md("## 4) `calculate()`\nCompute the statistic across replicates.")
    return


@app.cell
def _(generated, pipeline):
    null_dist = pipeline.calculate(generated, stat="diff_in_props")
    null_dist.head()
    return (null_dist,)


@app.cell
def _():
    marimo.md("## 5) `visualize()`\nPlot the null distribution.")
    return


@app.cell
def _(data, null_dist, pipeline, pl):
    observed = (
        data.group_by("group")
        .agg(pl.col("outcome").mean().alias("p"))
        .sort("group")
        .select((pl.col("p").first() - pl.col("p").last()).alias("diff"))
        .item()
    )

    chart = pipeline.visualize(
        null_dist,
        observed_stat=observed,
        direction="two-sided",
        title="Null distribution for difference in proportions",
    )
    chart
    return chart, observed


@app.cell
def _(null_dist, observed, pipeline):
    p_val = pipeline.p_value(null_dist, observed_stat=observed, direction="two-sided")
    marimo.md(f"### Approximate p-value: `{p_val:.4f}`")
    return


if __name__ == "__main__":
    app.run()
