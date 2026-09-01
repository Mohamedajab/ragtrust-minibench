"""Streamlit view of the latest retrieval experiment."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


RESULTS_DIR = Path(__file__).resolve().parent / "results"

st.set_page_config(page_title="RAGTrust MiniBench", page_icon="🔎", layout="wide")
st.title("RAGTrust MiniBench")
st.caption("A small retrieval-poisoning and provenance experiment")

try:
    results = pd.read_csv(RESULTS_DIR / "retrieval_results.csv")
    with (RESULTS_DIR / "summary.json").open(encoding="utf-8") as summary_file:
        summary = json.load(summary_file)
except FileNotFoundError:
    st.info("Run `python run_experiment.py` first.")
    st.stop()

naive = summary["configurations"]["naive"]
defended = summary["configurations"]["defended"]

columns = st.columns(4)
columns[0].metric("Queries", summary["total_queries"])
columns[1].metric("Naive poisoned top-1", f"{naive['poisoned_top1_rate']:.1%}")
columns[2].metric(
    "Defended poisoned top-1", f"{defended['poisoned_top1_rate']:.1%}"
)
columns[3].metric("Attack reduction", f"{summary['top1_attack_reduction']:.1%}")

st.subheader("Retrieval comparison")
chart_data = pd.DataFrame(
    {
        "Configuration": ["Naive", "Defended"],
        "Poisoned top-1": [
            naive["poisoned_top1_rate"],
            defended["poisoned_top1_rate"],
        ],
        "Clean recall@k": [naive["clean_recall_at_k"], defended["clean_recall_at_k"]],
    }
).set_index("Configuration")
st.bar_chart(chart_data)

st.subheader("Individual queries")
st.dataframe(
    results[
        [
            "query_id",
            "configuration",
            "attack_present",
            "top_result",
            "top1_poisoned",
            "any_poisoned",
            "expected_found",
            "mean_trust",
        ]
    ],
    hide_index=True,
    use_container_width=True,
)

