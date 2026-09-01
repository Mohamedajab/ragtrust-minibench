import pandas as pd

from ragtrust.evaluation import calculate_metrics


def test_metrics_compare_naive_and_defended_results() -> None:
    rows = pd.DataFrame(
        [
            {
                "query_id": "Q1",
                "configuration": "naive",
                "attack_present": True,
                "top1_poisoned": True,
                "any_poisoned": True,
                "expected_found": True,
                "mean_trust": 0.5,
            },
            {
                "query_id": "Q1",
                "configuration": "defended",
                "attack_present": True,
                "top1_poisoned": False,
                "any_poisoned": False,
                "expected_found": True,
                "mean_trust": 0.9,
            },
        ]
    )

    metrics = calculate_metrics(rows, top_k=3)

    assert metrics["configurations"]["naive"]["poisoned_top1_rate"] == 1.0
    assert metrics["configurations"]["defended"]["poisoned_top1_rate"] == 0.0
    assert metrics["top1_attack_reduction"] == 1.0

