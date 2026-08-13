# Innovation Selection Scorecard — Signal Harbour Project B

Student: Kaiyuan Lan (`z5444541`)  
Inputs: Project A handoff/continuity audit + open-source research + Part B rubric (Innovation 30%)  
Scoring: 1 = weak / high risk; 5 = strong / low risk for this dataset and assessment.  
Implementation risk and deployment burden are scored so that **higher = better** (5 = low risk / low burden).

---

## Candidates scored

| Candidate | Part A link | Originality vs baseline | Innovation 30% | Sentiment 10% | Funds 15% | Streamlit | Evidence feasible | Look-ahead safety | Interpretability | Robustness | Impl. risk↓ | Deploy burden↓ | Report value | Negative-result OK | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. Unchanged VADER baseline | 2 | 1 | 1 | 3 | 2 | 2 | 5 | 5 | 5 | 3 | 5 | 5 | 3 | 5 | 47 |
| 2. Week 9 / open-source finVADER benchmark | 2 | 2 | 2 | 4 | 2 | 2 | 4 | 5 | 4 | 3 | 4 | 4 | 4 | 5 | 47 |
| 3. Signal Harbour augmented finVADER | 4 | 4 | 5 | 5 | 3 | 4 | 5 | 5 | 5 | 4 | 4 | 5 | 5 | 5 | 63 |
| 4. Attention-Pulse-weighted sentiment | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 4 | 4 | 4 | 5 | 5 | 5 | 66 |
| 5. Coverage-confidence sentiment | 5 | 4 | 4 | 5 | 3 | 4 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 64 |
| 6. Hierarchical risk parity | 1 | 3 | 3 | 1 | 5 | 2 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 42 |
| 7. Covariance shrinkage | 1 | 2 | 2 | 1 | 4 | 1 | 4 | 4 | 3 | 4 | 3 | 4 | 3 | 4 | 40 |
| 8. Turnover / transaction-cost modelling | 2 | 3 | 3 | 1 | 4 | 2 | 4 | 5 | 4 | 4 | 3 | 4 | 4 | 5 | 48 |
| 9. Investor-facing explainability diagnostic | 4 | 4 | 4 | 4 | 2 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 62 |

Notes on scoring:

- Unchanged VADER / open-source FinVADER score low on originality because the rubric and forum guidance treat them as baselines/benchmarks.
- Attention-Pulse weighting scores highest because it uniquely continues Part A’s distinctive feature into Part B trading use with lag.
- HRP/shrinkage are competent fund extensions but weakly connected to the Part A story and therefore weaker as the *primary* innovation under concurrent A+B marking.

---

## Selection

### Primary integrated innovation

**Signal Harbour Context-Weighted finVADER**

Combines candidates **3 + 4 + 5**, delivered through candidate **9** in the app:

```text
base_score(ticker, t)
    = Signal Harbour augmented finVADER(headlines mapped to trading day t)

coverage_confidence(ticker, t)
    = bounded function of headline count on t (and light recent coverage)

attention_confidence(ticker, t)
    = bounded function of Part A Attention Pulse on t (past-only construction)

context_weighted_score(ticker, t)
    = base_score × coverage_confidence × attention_confidence

tradable_score(ticker, t)
    = context_weighted_score from t−1 or earlier
```

Benchmarks retained for evidence:

1. unchanged VADER  
2. open-source / Week 9 FinVADER-style finance lexicon benchmark (Week 9 course helper supplied and locked as `week9_finvader`)

### Supporting extensions (≤2)

1. **Look-ahead-safe portfolio fusion** using `tradable_score` with tilt-strength / base-method sensitivity (already started; upgrade to context-weighted signal).  
2. **Streamlit explainability diagnostic**: sector sentiment, coverage, Attention Pulse/confidence, base vs augmented score, top contributing terms/rules, signal date vs first usable trade date.

### Deferred (not primary)

- Hierarchical risk parity  
- Covariance shrinkage as a headline innovation  
- Full transaction-cost engine (may be discussed qualitatively / light sensitivity only if time remains)

---

## Why this beats a shallow lexicon update

The earlier Part B draft only appended a small `FINANCE_LEXICON` to VADER. Under the forum guidance and continuity audit, that leaves originality thin because:

1. it does not reuse Attention Pulse;  
2. it does not address Part A’s coverage imbalance;  
3. it lacks a documented lexicon audit and ablation;  
4. it is too close to “prompt-and-paste finance words”.

Context-Weighted finVADER is selected because one deep, validated, Part A–continuous contribution is stronger than several disconnected add-ons.
