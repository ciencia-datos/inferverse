import polars as pl

from inferverse import InferPipeline

# Toy A/B conversion dataset
ab = pl.DataFrame(
    {
        "group": ["control"] * 40 + ["treatment"] * 40,
        "converted": [0, 1, 0, 1, 0, 0, 1, 0] * 10,
    }
)

pipeline = InferPipeline(ab).specify(response="converted", explanatory="group").hypothesize("independence")
generated = pipeline.generate(reps=500, seed=42)
null_dist = pipeline.calculate(generated, stat="diff_in_props")

observed = (
    ab.group_by("group")
    .agg(pl.col("converted").mean().alias("p"))
    .sort("group")
    .select((pl.col("p").first() - pl.col("p").last()).alias("diff"))
    .item()
)

p_value = pipeline.p_value(null_dist, observed_stat=observed)
print(f"Observed statistic: {observed:.4f}")
print(f"Approximate p-value: {p_value:.4f}")

chart = pipeline.visualize(
    null_dist,
    observed_stat=observed,
    direction="two-sided",
    title="Null distribution of diff_in_props",
)
chart.save("null_distribution.html")
print("Saved chart to null_distribution.html")
