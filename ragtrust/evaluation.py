"""Build result tables and metrics for retrieval experiments."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .retrieval import SearchResult


def result_row(query: dict, configuration: str, results: list[SearchResult]) -> dict:
    expected_ids = set(query["expected_doc_ids"])
    retrieved_ids = [result.doc_id for result in results]
    return {
        "query_id": query["query_id"],
        "configuration": configuration,
        "query": query["query"],
        "attack_present": bool(query["attack_present"]),
        "retrieved_ids": retrieved_ids,
        "top_result": retrieved_ids[0] if retrieved_ids else "",
        "top1_poisoned": bool(results and results[0].is_poisoned),
        "any_poisoned": any(result.is_poisoned for result in results),
        "expected_found": bool(expected_ids.intersection(retrieved_ids)),
        "mean_trust": (
            sum(result.trust_score for result in results) / len(results)
            if results
            else 0.0
        ),
        "scores": [result.final_score for result in results],
    }


def build_results(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def calculate_metrics(results: pd.DataFrame, top_k: int) -> dict:
    metrics = {"total_queries": int(results["query_id"].nunique()), "top_k": top_k}
    configurations = {}

    for name, group in results.groupby("configuration"):
        attacked = group[group["attack_present"]]
        clean = group[~group["attack_present"]]
        configurations[name] = {
            "poisoned_top1_rate": float(attacked["top1_poisoned"].mean()),
            "contamination_rate_at_k": float(attacked["any_poisoned"].mean()),
            "clean_recall_at_k": (
                float(clean["expected_found"].mean()) if not clean.empty else 0.0
            ),
            "mean_result_trust": float(group["mean_trust"].mean()),
        }

    naive_rate = configurations["naive"]["poisoned_top1_rate"]
    defended_rate = configurations["defended"]["poisoned_top1_rate"]
    metrics["configurations"] = configurations
    metrics["top1_attack_reduction"] = naive_rate - defended_rate
    return metrics


def save_results(results: pd.DataFrame, metrics: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_table = results.copy()
    for column in ("retrieved_ids", "scores"):
        csv_table[column] = csv_table[column].map(json.dumps)
    csv_table.to_csv(output_dir / "retrieval_results.csv", index=False)
    with (output_dir / "summary.json").open("w", encoding="utf-8") as summary_file:
        json.dump(metrics, summary_file, indent=2)
        summary_file.write("\n")
