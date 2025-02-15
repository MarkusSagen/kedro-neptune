import pandas as pd
from kedro.pipeline import (
    Pipeline,
    node,
)

try:
    from neptune.new.handler import Handler
    from neptune.new.utils import stringify_unsupported
except ImportError:
    from neptune.handler import Handler
    from neptune.utils import stringify_unsupported


# ------- Number of moons predictor --------
def prepare_dataset(planets: pd.DataFrame) -> pd.DataFrame:
    planets["Has Many Moons"] = planets["Number of Moons"].apply(lambda moons: moons > 10)

    return planets


def judge_model(neptune_run: Handler, dataset: pd.DataFrame):
    def classifier(mass):
        return mass > 2.0

    compute_acc = dataset.copy()
    compute_acc["Predict"] = compute_acc["Mass (1024kg)"].apply(classifier)
    accuracy = (
        compute_acc[compute_acc["Predict"] == compute_acc["Has Many Moons"]].count() / compute_acc.count() * 100.0
    )

    neptune_run["accuracy"] = stringify_unsupported(accuracy)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                prepare_dataset,
                ["planets"],
                "dataset",
                name="prepare_dataset",
            ),
            node(
                judge_model,
                ["neptune_run", "dataset"],
                None,
                name="judge_model",
            ),
        ]
    )
