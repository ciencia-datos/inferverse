"""Inferverse workflow script for Google Colab.

Usage in Colab:
1) Upload this file to a Colab runtime, or copy cells into a notebook.
2) Run the install cell first.
"""

# %% [markdown]
# # Inferverse verbs in Google Colab
#
# This notebook mirrors the marimo example in `notebooks/inferverse_verbs_marimo.py`.

# %%
# Install dependencies (Colab cell)
# !pip install -q "git+https://github.com/ciencia-datos/inferverse.git" polars altair

# %%
import polars as pl
from inferverse import InferPipeline

# Example data
data = pl.DataFrame(
    {
        "group": ["control"] * 30 + ["treatment"] * 30,
        "outcome": [0, 1, 0, 0, 1, 1] * 10,
    }
)

data.head()

# %%
# 1) specify(): declare response and explanatory variables
specified = InferPipeline(data).specify(response="outcome", explanatory="group")
specified

# %%
# 2) hypothesize(): declare the null hypothesis
pipeline = specified.hypothesize("independence")
pipeline

# %%
# 3) generate(): create null-world simulations
generated = pipeline.generate(reps=300, seed=42)
generated.head()

# %%
# 4) calculate(): compute statistic across replicates
null_dist = pipeline.calculate(generated, stat="diff_in_props")
null_dist.head()

# %%
# 5) visualize(): plot null distribution
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

# %%
# Approximate p-value
p_val = pipeline.p_value(null_dist, observed_stat=observed, direction="two-sided")
print(f"Approximate p-value: {p_val:.4f}")
