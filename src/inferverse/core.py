from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import altair as alt
import polars as pl
from scipy import stats

from .visualize import visualize_distribution

StatType = Literal["mean", "proportion", "prop", "diff_in_means", "diff_in_props"]
HypothesisType = Literal["independence", "point"]


@dataclass
class InferPipeline:
    data: pl.DataFrame
    response: str | None = None
    explanatory: str | None = None
    null: HypothesisType | None = None
    null_value: float | None = None

    def specify(self, response: str, explanatory: str | None = None) -> "InferPipeline":
        if response not in self.data.columns:
            raise ValueError(f"Response column '{response}' not found.")
        if explanatory is not None and explanatory not in self.data.columns:
            raise ValueError(f"Explanatory column '{explanatory}' not found.")
        self.response = response
        self.explanatory = explanatory
        return self

    def hypothesize(self, null: HypothesisType, null_value: float | None = None) -> "InferPipeline":
        if null not in ("independence", "point"):
            raise ValueError("null must be one of {'independence', 'point'}")
        self.null = null
        self.null_value = null_value
        return self

    def generate(self, reps: int = 1000, seed: int | None = None) -> pl.DataFrame:
        self._validate_ready_for_generate()
        generated: list[pl.DataFrame] = []

        if self.null == "independence":
            for i in range(reps):
                sample = self.data.with_columns(pl.col(self.explanatory).shuffle(seed=None if seed is None else seed + i))
                generated.append(sample.with_columns(pl.lit(i).alias("replicate")))
        elif self.null == "point":
            if self.null_value is None:
                raise ValueError("null_value is required for point null.")
            centered = self.data.with_columns((pl.col(self.response) - pl.col(self.response).mean() + self.null_value).alias(self.response))
            for i in range(reps):
                sample = centered.sample(n=centered.height, with_replacement=True, shuffle=True, seed=None if seed is None else seed + i)
                generated.append(sample.with_columns(pl.lit(i).alias("replicate")))

        return pl.concat(generated)

    def calculate(self, generated: pl.DataFrame, stat: StatType = "mean") -> pl.DataFrame:
        if "replicate" not in generated.columns:
            raise ValueError("generated data must include 'replicate'.")

        if stat in ("mean", "proportion", "prop"):
            return generated.group_by("replicate").agg(pl.col(self.response).mean().alias("stat"))

        if stat in ("diff_in_means", "diff_in_props"):
            if self.explanatory is None:
                raise ValueError(f"{stat} requires an explanatory variable.")
            groups = generated.select(self.explanatory).unique().to_series().to_list()
            if len(groups) != 2:
                raise ValueError(f"{stat} requires exactly 2 groups in explanatory variable.")
            summary = generated.group_by(["replicate", self.explanatory]).agg(pl.col(self.response).mean().alias("group_stat")).pivot(index="replicate", on=self.explanatory, values="group_stat")
            return summary.with_columns((pl.col(groups[0]) - pl.col(groups[1])).alias("stat")).select(["replicate", "stat"])

        raise ValueError(f"Unsupported stat: {stat}")

    def visualize(
        self,
        distribution: pl.DataFrame,
        stat_col: str = "stat",
        bins: int = 30,
        observed_stat: float | None = None,
        direction: str = "two-sided",
        title: str = "Simulated null distribution",
    ) -> alt.Chart:
        """Visualize a simulated distribution using infer-style defaults."""
        return visualize_distribution(
            distribution=distribution,
            stat_col=stat_col,
            bins=bins,
            observed_stat=observed_stat,
            direction=direction,
            title=title,
        )

    @staticmethod
    def p_value(null_distribution: pl.DataFrame, observed_stat: float, direction: str = "two-sided") -> float:
        values = null_distribution["stat"].to_numpy()
        if direction == "greater":
            return float((values >= observed_stat).mean())
        if direction == "less":
            return float((values <= observed_stat).mean())
        if direction == "two-sided":
            return float((abs(values) >= abs(observed_stat)).mean())
        raise ValueError("direction must be one of {'greater', 'less', 'two-sided'}")

    @staticmethod
    def ci_from_t(sample: pl.Series, alpha: float = 0.05) -> tuple[float, float]:
        arr = sample.to_numpy()
        mean = arr.mean()
        sem = stats.sem(arr)
        lo, hi = stats.t.interval(1 - alpha, len(arr) - 1, loc=mean, scale=sem)
        return float(lo), float(hi)

    def _validate_ready_for_generate(self) -> None:
        if self.response is None:
            raise ValueError("Call specify() before generate().")
        if self.null is None:
            raise ValueError("Call hypothesize() before generate().")
        if self.null == "independence" and self.explanatory is None:
            raise ValueError("independence null requires an explanatory variable.")
