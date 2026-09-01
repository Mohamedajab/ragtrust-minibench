# RAGTrust MiniBench interview guide

Use this as a study guide. The strongest explanation is one you can support by
opening the relevant function and describing it in your own words.

## Thirty-second explanation

RAGTrust MiniBench studies retrieval poisoning. An attacker adds a low-trust
document that repeats the terms in a target query so a simple retriever ranks it
highly. I compare naive keyword ranking with transparent provenance-aware
re-ranking. The defence reduces poisoned top-one results from 100% to 0% while
preserving clean recall, but poison remains somewhere in the top three for all
attacked queries.

## Two-minute explanation

Retrieval-augmented generation first selects documents and then gives them to a
language model. If an attacker can insert content into the document collection,
they may not need to attack the model directly. They can manipulate which
context the model sees.

The benchmark contains twelve trusted documents, six targeted poisoned
documents, and twelve queries. The naive retriever tokenises the query and
counts matching terms in every document. Counts are capped, but repetition can
still raise a document's relevance score.

The defence multiplies relevance by source trust. It also applies a penalty to
instruction-like content. This moves the expected trusted document into first
place. However, the poison still appears in the top three, so a model consuming
all three results remains exposed. The result distinguishes safer ordering from
safe context construction.

## Code flow

1. `run_experiment.py` loads documents and queries from JSON.
2. `tokenize()` lowercases text, removes punctuation and drops common words.
3. `KeywordRetriever.search()` calculates capped term-frequency relevance.
4. The naive configuration sorts directly by relevance.
5. `ProvenanceReranker.score()` combines relevance, source trust and an
   instruction penalty.
6. Both rankings are converted into query-level result rows.
7. pandas calculates poisoned top-one rate, contamination@k and clean recall@k.
8. Results are saved as CSV and JSON and displayed in Streamlit.

## Files to know

| File | Purpose |
|---|---|
| `ragtrust/retrieval.py` | Tokenisation, relevance scoring and ranking. |
| `ragtrust/defense.py` | Provenance score and suspicious-language penalty. |
| `ragtrust/evaluation.py` | Query results, metrics and artifact saving. |
| `data/documents.json` | Trusted and poisoned synthetic documents. |
| `data/queries.json` | Targeted and clean queries with expected documents. |
| `run_experiment.py` | Reproducible experiment entry point. |

## Metrics in plain language

- **Poisoned top-1 rate:** how often poison is the first result on targeted
  queries.
- **Contamination@3:** how often any poison appears among the first three
  results.
- **Clean recall@3:** how often the expected document is found for clean
  queries.
- **Mean result trust:** the average provenance value of retrieved content.

Top-one rate measures the attacker's ranking success. Contamination@3 is the
stricter security measure because many RAG systems send several results to the
model.

## Important design decisions

### Why keyword retrieval rather than embeddings?

It exposes the mechanism clearly. You can calculate the score by hand and show
how repetition changes it. Embeddings are a natural extension after the basic
experiment is understood.

### Why cap term counts at three?

Without a cap, copying one word hundreds of times would dominate the score. The
cap limits that trivial behaviour while preserving a small keyword-stuffing
effect.

### Where do trust scores come from?

They are synthetic metadata based on source type: official policies are high
trust and community uploads are low trust. This is an experimental assumption,
not a solved provenance system.

### Why does poison remain in the top three?

The defence re-ranks rather than removes. The poisoned documents remain highly
relevant to their target query. Their penalty is sufficient to move them below
trusted content but not below every partially relevant document.

## Likely questions and good answers

### Is a fixed trust score secure?

No. An attacker might forge metadata or compromise a trusted source. Future work
should authenticate provenance and test missing or conflicting trust signals.

### Does 100% attack reduction mean the system is safe?

Only for the top-one metric in this small dataset. Contamination@3 remains 100%,
so downstream exposure has not been eliminated.

### What utility trade-off did you measure?

Clean recall@3 remains 100% in this dataset. A larger evaluation should also
measure rank position, answer quality, and cases where useful community content
has low trust.

### How would embeddings change the attack?

Instead of repeating exact words, an attacker could use semantically similar
phrases or optimise content toward an embedding. The same provenance idea could
be applied after vector similarity, but the results would need new testing.

### What is the central result?

Provenance-aware ranking can improve which source appears first, but re-ranking
alone is not equivalent to sanitising the context supplied to a model.

## Five-minute demonstration

```powershell
python run_experiment.py
python -m pytest
streamlit run app.py
```

Open `Q001`, compare `D001` with `P001`, and show how repeated terms raise the
naive score. Then show the trust and instruction penalties and explain why the
trusted result moves to first place while the poison remains in the top three.

## Exercises before discussing the project

1. Change one poison document's trust score and find the point where it returns
   to first place.
2. Remove the instruction-like sentence but keep keyword stuffing. Which part
   of the defence still helps?
3. Change `top_k` from three to one and explain why the security conclusion
   changes.
4. Implement a separate quarantine threshold and compare recall with exposure.

## Possible CV bullet

> Developed a reproducible retrieval-poisoning benchmark with provenance-aware
> re-ranking; reduced poisoned top-one retrieval from 100% to 0% while showing
> that top-three context contamination remained unresolved.

