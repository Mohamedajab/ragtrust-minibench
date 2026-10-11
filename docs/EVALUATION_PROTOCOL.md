# Evaluation protocol and result interpretation

This document describes the **implemented** RAGTrust MiniBench experiment. It is a
small, deterministic retrieval study using synthetic documents; it does not run a
language model or establish resistance to prompt injection in production.

## Experimental unit and scope

- Corpus: `data/documents.json` (12 trusted documents and 6 attacker-inserted documents).
- Queries: `data/queries.json` (6 targeted/attacked and 6 clean queries).
- Evaluation unit: **one query under one ranking configuration**, not each
  returned document. Both arms use exactly the same query and corpus.
- Retrieval depth: `TOP_K = 3` in `run_experiment.py`.
- Arms: `naive` keyword relevance and `defended` provenance-aware re-ranking.

The repository's synthetic provenance scores are inputs to the experiment, not
independently verified proof of source authenticity.

## Reproduce locally

From the repository root, with a Python environment containing the packages in
`requirements.txt`:

```bash
python -m pip install -r requirements.txt
python -m pytest
python run_experiment.py
```

The runner rewrites `results/retrieval_results.csv` and `results/summary.json`.
Run it only in a clean working tree if you want to compare against the committed
artifacts without mixing changes. No network access, API key, or external model
call is part of the experiment.

To inspect individual rankings, open `results/retrieval_results.csv`. The
`retrieved_ids` and `scores` CSV cells contain JSON-encoded lists.

## Ranking and exact calculations

`KeywordRetriever.search` in `ragtrust/retrieval.py`:

1. Lowercases and tokenises query and document title/body using the
   `[a-z0-9]+` pattern, removes stop words and one-character tokens.
2. Uses unique query tokens and counts occurrences in each document.
3. Caps each query-token contribution at three, then divides the total by
   the number of unique query tokens:
   `relevance = sum(min(document_term_count[t], 3) for t in query_terms) / len(query_terms)`.
4. The naive arm ranks by relevance. The defended arm instead ranks by
   `relevance * trust_score * instruction_penalty`.
5. The instruction penalty is **0.25** when the document body matches the
   fixed phrase pattern in `ragtrust/defense.py`, otherwise **1.0**.
6. The implementation rounds displayed scores to four decimal places and
   sorts descending by score, breaking ties by ascending document ID.

This rule is transparent, not a verified semantic instruction detector. The
attacker is modelled as adding lower-trust content; the scoring routine assumes
the provided `trust_score` itself has not been forged.

## Metrics and denominators

`ragtrust/evaluation.py` calculates:

| Metric | Denominator | Positive event |
| --- | --- | --- |
| Poisoned top-1 rate | Attacked queries | First-ranked document has `is_poisoned=true` |
| Contamination rate@3 | Attacked queries | At least one of the three retrieved documents is poisoned |
| Clean recall@3 | **Clean queries only** | At least one expected trusted document ID is retrieved |
| Mean result trust | All queries in that arm | Mean trust score among retrieved results, then average over queries |
| Top-1 attack reduction | Difference of rates | Naive poisoned top-1 rate minus defended poisoned top-1 rate |

`expected_found` checks whether *any* `expected_doc_ids` overlaps the retrieved
IDs. Therefore, the clean-recall metric is not ranking quality, not answer
correctness, and not recall over all relevant documents.

## Saved results

For the committed 12-query, top-3 experiment:

| Metric | Naive | Defended |
| --- | ---: | ---: |
| Poisoned top-1 | 100% | 0% |
| Contamination@3 | 100% | 100% |
| Clean recall@3 | 100% | 100% |
| Mean result trust | 0.7856 | 0.8203 |

The top-1 difference is 100 percentage points **on six targeted synthetic
queries**. It is not a population estimate or a security guarantee. Poison still
reaches the top-three context for every attacked query in both arms; any
downstream generator receiving all three documents would still encounter it.

## How to extend without overstating results

- Freeze a new corpus/query split before inspecting new outcomes. Treat the
  current corpus as a development demonstration, not a blinded held-out test.
- Separate source-authentication experiments from relevance-ranking experiments:
  forged or absent metadata changes the threat model.
- Report utility at more than one `k` and evaluate legitimate community content,
  which may receive low trust even when useful.
- If an LLM is added, measure **answer-level effects** separately from retrieval
  contamination, and keep unsafe tool use or secret exposure out of this
  educational synthetic harness.
- Publish per-query outputs and failure cases alongside aggregates. Do not
  generalise from six attacked queries to production RAG deployments.

See [the interview guide](INTERVIEW_GUIDE.md) for a walkthrough of individual
examples and the existing [README](../README.md) for setup and context.

