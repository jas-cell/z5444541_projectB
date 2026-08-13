# Project A–B Continuity Audit

Student: Kaiyuan Lan (`z5444541`)  
Audited against: final Project A package + current Part B workspace + proposed Context-Weighted finVADER design  
Date: 2026-08-09  
Rule: do not rewrite submitted Project A; fix Part B continuity gaps in Part B.

---

## Continuity matrix

| Area | Project A position | Project B continuation | Consistent? | Required correction |
|---|---|---|---|---|
| Product name | Signal Harbour | Signal Harbour in README, report, app | Yes | Keep; do not rebrand |
| Customer | Small wealth-advisory firm | Report/app speak to advisory / investor product | Mostly | Strengthen explicit “small wealth-advisory firm” language in app/report so buyer identity matches A |
| Daily user | Portfolio analyst | App journey currently framed as general investor | Partial | Keep investor journey, but state the day-to-day research user is still the portfolio analyst preparing committee evidence |
| Equity calendar | Exchange sessions | Equity & Combined funds on equity calendar; 252 annualisation | Yes | Retain |
| Crypto calendar | Seven-day native calendar | Crypto-only funds use native 365-day calendar | Yes | Retain |
| Combined calendar | Crypto returns aligned to equity sessions | Combined funds use pre-aligned crypto returns | Yes | Retain; never recompute crypto returns after merge |
| Return definition | Adjusted-close simple return | Backtest inputs from same simple returns | Yes | Retain |
| Sample | 2020–2023 | Current outputs stay inside sample; first live dates in 2021 | Yes | No claims after 2023 |
| News unit | Headline | Sentiment input is `title` | Yes | Retain; do not switch to article bodies |
| Deduplication | ticker-date-title | Part B ETL must keep the same key | Yes if ETL matches A | Re-verify Part B `etl.py` uses `(ticker, date, title)` and not ticker-date only |
| Headline mapping | Same or next trading day | Part B mapping must match A | Yes if code matches A | Re-verify searchsorted same/next-day mapping and exclusion of unmappable end-of-sample rows |
| Signal timing | Part A descriptive only | Part B already lags sentiment one trading day before trade use | Yes for lag principle | Extend: Attention Pulse / coverage confidence used in fusion must also be lagged; never same-day trade on same-day pulse |
| LM vocabulary | Descriptive category counts | Current Part B lexicon is a small ad-hoc overlay, not clearly tied to Part A LM evidence | Partial / weak | Use Part A LM counts as candidate-generation / validation evidence; do not claim Part A already scored sentiment |
| Attention Pulse | Past-only abnormal headline volume | Current Part B does **not** use Attention Pulse | No — gap | Primary innovation must import the Part A equation as a lagged confidence input |
| Figure identity | Project A design system | Part B figures exist but are not explicitly framed as the A design system extension | Partial | Extend A’s accessible colour/type/caption conventions into B figures and Streamlit explainability panel |
| Limitations | Descriptive / non-causal | Current B report correctly treats fusion as modest/negative and headlines as noisy | Yes | Preserve; distinguish inherited descriptive limits from new Part B tests |

---

## Genuine Project A weaknesses discovered (not hidden)

| Weakness | Evidence | Part B treatment |
|---|---|---|
| Uneven headline coverage across sectors | Part A: Tech/Consumer dominate; Real Estate sparse | Coverage-confidence downweights sparse ticker-days; report must say denser coverage ≠ automatically better signal |
| Publisher mostly missing | 137,447 unavailable after dedup | Do not invent publisher-based features; retain rows |
| Attention Pulse association is contemporaneous in A | +0.61 pp abs-return gap is descriptive | Part B may use pulse only with a trading lag and must not claim A already traded on it |
| LM counts are unsigned and un-netted | Separate positive/negative/uncertainty counts | Useful for lexicon candidates and false-neutral audits; not a substitute for validated sentiment scores |
| No Week 9 finVADER file in Project A package | Not present in final A tree | Ask Kaiyuan if course file exists; otherwise label open-source FinVADER as an additional benchmark, not “Week 9 identical” |

---

## Current Part B draft weaknesses relative to the addendum

These are Part B gaps discovered before locking the upgraded innovation. They are **not** rewritten into Project A history.

1. **Shallow “custom lexicon”.** `src/sentiment.py` currently injects a small `FINANCE_LEXICON` into plain VADER. That is a start, but under the forum guidance it is insufficient as the sole innovation story.
2. **No Attention Pulse bridge.** The distinctive Part A feature is unused in Part B scoring/fusion.
3. **No coverage confidence.** Part A already documented sector imbalance; Part B should not ignore it.
4. **No formal model comparison table.** Base VADER vs finance-benchmark vs Signal Harbour augmentation is not yet evidenced as required innovation outputs.
5. **Explainability panel incomplete.** App surfaces sector sentiment and fusion, but not base-vs-augmented scores, contributing terms, Attention Pulse/confidence, or explicit signal date vs first usable trade date.
6. **Open-source research stage missing** from the earlier Part B draft — mandatory before locking innovation.

---

## Continuity decisions for the upgraded Part B design

| Decision | Rationale |
|---|---|
| Keep Signal Harbour product identity | Forum: A and B are one project |
| Keep Part A ETL/calendar/return/mapping definitions | Concurrent marking punishes contradictions |
| Primary innovation = Context-Weighted finVADER | Connects A Attention Pulse + B sentiment + fusion + app |
| Supporting extension 1 = lagged coverage/attention confidence in fusion | Direct reuse of Part A evidence |
| Supporting extension 2 = Streamlit explainability diagnostic | Makes the continuous contribution investor-visible |
| Do not retrofit Part A files | Weaknesses are disclosed; improvements are Part B only |
| Negative fusion result remains acceptable | Rubric and prior B evidence already support this |

---

## Consistency gate status (pre-implementation)

| Gate item | Status |
|---|---|
| Same product identity | Pass |
| Same target user language | Needs Part B wording tighten |
| Same data provenance | Pass if B continues using `data_access` |
| Same cleaning definitions | Re-verify in B ETL before final package |
| Same return definition | Pass |
| Same date limits | Pass |
| Same calendar logic | Pass |
| Same headline mapping | Re-verify |
| Same Attention Pulse equation | Fail until imported into B |
| No B claim that A already contained sentiment | Pass in current report; keep guarding |
| No claim that contemporaneous A diagnostics were tradable | Pass; keep guarding |
| B explains descriptive A feature → lagged tested signal | Fail until Context-Weighted design implemented and reported |

Next stage after this audit: GitHub open-source research (Stage 5), then innovation scorecard (Stage 6), then implementation.
