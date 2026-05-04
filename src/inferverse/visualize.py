from __future__ import annotations

import altair as alt
import polars as pl


def visualize_distribution(
    distribution: pl.DataFrame,
    stat_col: str = "stat",
    bins: int = 30,
    observed_stat: float | None = None,
    direction: str = "two-sided",
    title: str = "Simulated null distribution",
) -> alt.Chart:
    """Create an infer-like visualization of a simulated distribution."""
    if stat_col not in distribution.columns:
        raise ValueError(f"Column '{stat_col}' not found in distribution.")
    if direction not in {"greater", "less", "two-sided"}:
        raise ValueError("direction must be one of {'greater', 'less', 'two-sided'}")

    df = distribution.select(stat_col).to_pandas()

    if observed_stat is None:
        df["tail"] = "body"
    elif direction == "greater":
        df["tail"] = df[stat_col].ge(observed_stat).map({True: "tail", False: "body"})
    elif direction == "less":
        df["tail"] = df[stat_col].le(observed_stat).map({True: "tail", False: "body"})
    else:
        df["tail"] = df[stat_col].abs().ge(abs(observed_stat)).map({True: "tail", False: "body"})

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{stat_col}:Q", bin=alt.Bin(maxbins=bins), title=stat_col),
        y=alt.Y("count():Q", title="count"),
        color=alt.Color("tail:N", scale=alt.Scale(domain=["body", "tail"], range=["#4C78A8", "#E45756"]), legend=None),
        tooltip=[alt.Tooltip("count():Q", title="count")],
    ).properties(title=title)

    if observed_stat is not None:
        rule = alt.Chart(pl.DataFrame({"x": [observed_stat]}).to_pandas()).mark_rule(color="#222", strokeDash=[4, 4]).encode(x="x:Q")
        chart = chart + rule

    return chart


def visualize(*args, **kwargs) -> alt.Chart:
    """Backwards-compatible alias for visualize_distribution."""
    return visualize_distribution(*args, **kwargs)
