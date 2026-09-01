"""Run naive and provenance-aware retrieval over the local benchmark."""

from __future__ import annotations

import json
from pathlib import Path

from ragtrust import KeywordRetriever, ProvenanceReranker
from ragtrust.evaluation import build_results, calculate_metrics, result_row, save_results


PROJECT_DIR = Path(__file__).resolve().parent
TOP_K = 3


def load_json(filename: str) -> list[dict]:
    with (PROJECT_DIR / "data" / filename).open(encoding="utf-8") as data_file:
        data = json.load(data_file)
    if not isinstance(data, list):
        raise ValueError(f"{filename} must contain a JSON list")
    return data


def run_experiment() -> tuple[object, dict]:
    documents = load_json("documents.json")
    queries = load_json("queries.json")
    retriever = KeywordRetriever()
    reranker = ProvenanceReranker()
    rows = []

    for query in queries:
        naive_results = retriever.search(query["query"], documents, top_k=TOP_K)
        defended_results = retriever.search(
            query["query"],
            documents,
            top_k=TOP_K,
            score_function=reranker.score,
        )
        rows.append(result_row(query, "naive", naive_results))
        rows.append(result_row(query, "defended", defended_results))

    results = build_results(rows)
    metrics = calculate_metrics(results, TOP_K)
    save_results(results, metrics, PROJECT_DIR / "results")
    return results, metrics


def print_report(metrics: dict) -> None:
    naive = metrics["configurations"]["naive"]
    defended = metrics["configurations"]["defended"]
    print("\nRAGTrust MiniBench")
    print(f"Queries: {metrics['total_queries']}")
    print(f"Top-k: {metrics['top_k']}")
    print("\nNaive retrieval")
    print(f"Poisoned top-1 rate: {naive['poisoned_top1_rate']:.1%}")
    print(f"Clean recall@k: {naive['clean_recall_at_k']:.1%}")
    print("\nProvenance-aware retrieval")
    print(f"Poisoned top-1 rate: {defended['poisoned_top1_rate']:.1%}")
    print(f"Clean recall@k: {defended['clean_recall_at_k']:.1%}")
    print(f"Attack reduction: {metrics['top1_attack_reduction']:.1%}")


if __name__ == "__main__":
    _, experiment_metrics = run_experiment()
    print_report(experiment_metrics)

