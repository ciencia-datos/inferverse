import polars as pl

from inferverse import InferPipeline


def test_specify_and_hypothesize_store_state() -> None:
    df = pl.DataFrame({"group": ["a", "b"], "y": [1.0, 2.0]})
    pipe = InferPipeline(df).specify("y", "group").hypothesize("independence")

    assert pipe.response == "y"
    assert pipe.explanatory == "group"
    assert pipe.null == "independence"


def test_generate_and_calculate_diff_in_means() -> None:
    df = pl.DataFrame(
        {
            "group": ["control", "control", "treat", "treat"],
            "y": [1.0, 1.2, 1.6, 1.7],
        }
    )
    pipe = InferPipeline(df).specify("y", "group").hypothesize("independence")

    sims = pipe.generate(reps=20, seed=7)
    stats = pipe.calculate(sims, stat="diff_in_means")

    assert sims.height == df.height * 20
    assert set(stats.columns) == {"replicate", "stat"}
    assert stats.height == 20


def test_point_null_generation_recenters_data() -> None:
    df = pl.DataFrame({"y": [1.0, 2.0, 3.0, 4.0]})
    pipe = InferPipeline(df).specify("y").hypothesize("point", null_value=10.0)

    sims = pipe.generate(reps=50, seed=5)
    means = sims.group_by("replicate").agg(pl.col("y").mean().alias("m"))["m"]

    assert abs(means.mean() - 10.0) < 0.25


def test_p_value_two_sided() -> None:
    null_dist = pl.DataFrame({"stat": [-2.0, -1.0, 0.0, 1.0, 2.0]})
    p = InferPipeline.p_value(null_dist, observed_stat=1.0, direction="two-sided")

    assert p == 0.8


def test_visualize_returns_altair_chart() -> None:
    df = pl.DataFrame({"group": ["a", "a", "b", "b"], "y": [1, 0, 1, 1]})
    pipe = InferPipeline(df).specify("y", "group").hypothesize("independence")
    sims = pipe.generate(reps=10, seed=1)
    null_dist = pipe.calculate(sims, stat="diff_in_props")

    chart = pipe.visualize(null_dist, observed_stat=0.1, direction="greater")

    assert hasattr(chart, "to_dict")
    spec = chart.to_dict()
    assert "layer" in spec or "mark" in spec
