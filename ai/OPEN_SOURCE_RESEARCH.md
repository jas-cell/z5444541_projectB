# Open-Source GitHub Research — Signal Harbour Project B

Student: Kaiyuan Lan (`z5444541`)  
Stage: 5 (after Project A continuity audit; before locking innovation architecture)  
Accessed: 2026-08-09 via GitHub web/raw content and GitHub API through Cursor WebFetch  
Integrity boundary: no FINS3645 student solutions searched or copied; licences checked before any adaptation decision.

---

## Raw GitHub search queries

These are the queries actually issued (exact strings). Local `urllib` SSL failed on this machine for some API calls; the same queries were re-issued successfully through Cursor WebFetch / GitHub search API where noted.

```text
FinVADER financial lexicon
VADER finance lexicon
custom VADER financial headlines
SentiBigNomics VADER
Henry finance lexicon sentiment
Loughran McDonald VADER
finance sentiment neutral override
financial phrase sentiment rules
explainable financial sentiment lexicon
portfolio optimisation Python risk parity
walk-forward maximum Sharpe
hierarchical risk parity Python
covariance shrinkage portfolio
CVaR portfolio optimisation
turnover constrained portfolio
multi-asset equity crypto optimisation
rolling portfolio optimisation backtest
expanding window portfolio backtest
portfolio weights drift transaction costs
out of sample asset allocation Python
portfolio fact sheet Python
walk forward no look ahead portfolio
Streamlit portfolio allocation dashboard
Streamlit fund fact sheet
Streamlit portfolio optimiser
Streamlit financial sentiment dashboard
Streamlit investor journey
Streamlit portfolio risk dashboard
portfolio optimisation pytest
backtest look ahead unit test
financial sentiment unit tests
Streamlit app testing
portfolio weight invariant test
reproducible quantitative finance pipeline
```

Representative search outcomes inspected:

| Query | Notable hits inspected |
|---|---|
| `FinVADER financial lexicon` | `PetrKorab/FinVADER` (Apache-2.0); `albyte-ai/finvader` (MIT, Rust) |
| `hierarchical risk parity Python` | `PyPortfolio/PyPortfolioOpt`; related HRP implementations |
| `Streamlit portfolio allocation dashboard` | `Mirco1006/Portfolio-Allocation-App`; other Streamlit MPT dashboards |
| `backtest look ahead unit test` | API returned 0 for that exact string; related repos found via web search: `SB-231/systematic-equity-backtester`, `marwanoo2/multi-asset-research-platform` |

---

## Repositories reviewed (≥10)

Shortlist for detailed inspection marked ★.

| # | Repository | Area | Licence verified | Decision summary |
|---|---|---|---|---|
| 1 ★ | PetrKorab/FinVADER | A sentiment | Apache-2.0 | **Benchmark only** |
| 2 ★ | cjhutto/vaderSentiment | A sentiment | MIT | **Benchmark / method pattern** |
| 3 ★ | albyte-ai/finvader | A sentiment | MIT | **Adapt ideas** (neutral override, phrases, explainability) — not copy Rust code |
| 4 ★ | consose/SentiBigNomics | A sentiment | Not cleanly SPDX on quick inspect; heavy research package | **Reject for runtime copy**; methodological reference only |
| 5 ★ | PyPortfolio/PyPortfolioOpt | B portfolio | MIT | **Benchmark / selective adapt** (already have MV/Sharpe/RP; HRP deferred) |
| 6 ★ | dcajasn/Riskfolio-Lib | B portfolio | BSD-3-Clause | **Reject as dependency**; CVaR/HRP ideas only if later needed |
| 7 ★ | skfolio/skfolio | B/C portfolio+WF | BSD-3-Clause | **Adapt idea**: clear estimation vs live split; do not import library |
| 8 ★ | ArturSepp/OptimalPortfolios | C backtest | MIT | **Adapt idea**: rebalance/live separation, turnover awareness |
| 9 ★ | Mirco1006/Portfolio-Allocation-App | D Streamlit | Not verified as SPDX in page summary | **Adapt interaction pattern only**; do not copy UI |
| 10 ★ | SB-231/systematic-equity-backtester | E testing | Not verified SPDX in page summary | **Adapt test idea**: signal-at-t / trade-at-t+1 invariants |
| 11 | marwanoo2/multi-asset-research-platform | C/E | Not verified | Look-ahead + costs test naming pattern |
| 12 | abdulahadalikhan12/Interactive-Portfolio-Builder-and-Optimizer | D Streamlit | Not deeply inspected | Reject as template-copy risk; tabs/compare pattern noted |

---

## Detailed inspection cards (shortlist)

### 1. PetrKorab/FinVADER ★

| Field | Evidence |
|---|---|
| Repository | PetrKorab/FinVADER |
| URL | https://github.com/PetrKorab/FinVADER |
| Accessed state | commit `400d64501a64` (2023-12-07); package version noted in `__init__.py` as `1.0.7` |
| Licence | Apache-2.0 (API licence field + README badge) |
| Project purpose | Inject SentiBigNomics and Henry lexicons into NLTK VADER |
| Files inspected | `README.md`, `finvader/__init__.py`, `finvader/finvader.py` |
| Tests inspected | Benchmark notebook claimed (`finvader_benchmark.ipynb`); no compact pytest suite inspected |
| Relevant idea | `SentimentIntensityAnalyzer().lexicon.update(...)`; SentiBigNomics valences rescaled by constant `0.1` before merge; Henry list merged with dict merge |
| Weakness | Downloads NLTK lexicon inside function; Python 3.8–3.11 claim; no Attention Pulse / coverage layer; not Signal Harbour-specific; installing unchanged FinVADER is **not** innovation |
| Compatibility | Usable as optional benchmark if `finvader` installs under the local Python; else reconstruct labelled open-source-style benchmark carefully |
| Decision | **Benchmark only** |
| Signal Harbour implementation | `src/sentiment.py` (`score_with_open_source_finvader` path); comparison tables |
| Attribution | Cite Petr Koráb FinVADER + Apache-2.0 in report/THIRD_PARTY_NOTICES if package code executed |
| Verification | Compare compound distributions vs base VADER on same headlines |

### 2. cjhutto/vaderSentiment ★

| Field | Evidence |
|---|---|
| Repository | cjhutto/vaderSentiment |
| URL | https://github.com/cjhutto/vaderSentiment |
| Accessed state | `master` LICENSE.txt inspected via API |
| Licence | MIT (C.J. Hutto) |
| Project purpose | Lexicon + rule-based social-media-oriented sentiment |
| Files inspected | repo page; `LICENSE.txt`; NLTK-wrapped usage already in course stack; source length ~690 lines reviewed via raw fetch metadata |
| Tests inspected | Upstream package tests exist historically; not re-run here |
| Relevant idea | Preserve casing/punctuation/negation/boosters; lexicon update is the intended extension point |
| Weakness | Finance false neutrals / false negatives on market jargon |
| Compatibility | Already required via NLTK VADER in Part B |
| Decision | **Benchmark** (unchanged VADER) |
| Signal Harbour implementation | `src/sentiment.py` base scorer |
| Attribution | MIT notice if redistributing lexicon file; NLTK usage is dependency citation |
| Verification | Neutral-rate and example audits |

### 3. albyte-ai/finvader ★

| Field | Evidence |
|---|---|
| Repository | albyte-ai/finvader |
| URL | https://github.com/albyte-ai/finvader |
| Accessed state | README on `main` (repo created 2026-07) |
| Licence | MIT |
| Project purpose | Rust finance-aware VADER with phrase rules, neutral-override masking, catalyst detection, trigger explainability |
| Files inspected | `README.md` (method stages documented) |
| Tests inspected | Claims CI + hand-labelled 60-headline set; not re-executed (Rust) |
| Relevant idea | Neutral override for finance-false VADER words; multi-word phrases (`beats expectations`); expose contributing terms; do not trust “more lexicon = better” without audits |
| Weakness | Different language stack; claimed 100% on tiny set is not transferable proof; must not copy their lexicon wholesale |
| Compatibility | Methodological only for Python Signal Harbour |
| Decision | **Adapt ideas** into Python lexicon/rule audit + explainability panel |
| Signal Harbour implementation | `src/sentiment.py` phrase/neutral-override candidates; Streamlit explainability; lexicon audit CSV |
| Attribution | Cite as methodological inspiration in report; no Rust code copied |
| Verification | Ablation + blinded headline review sheet |

### 4. consose/SentiBigNomics ★

| Field | Evidence |
|---|---|
| Repository | consose/SentiBigNomics |
| URL | https://github.com/consose/SentiBigNomics |
| Accessed state | README |
| Licence | Not treated as cleared for bundling; package is research-heavy |
| Project purpose | Aspect-based economic sentiment with large lexicon |
| Files inspected | README |
| Tests inspected | Example API only |
| Relevant idea | Fine-grained finance polarity; aspect rules |
| Weakness | spaCy large models; heavy deps; unsuitable for free Streamlit tier and course light-app constraint |
| Compatibility | Poor for deployment |
| Decision | **Reject for code reuse**; conceptual reference only |
| Signal Harbour implementation | None directly |
| Attribution | Literature/method mention if discussed |
| Verification | N/A |

### 5. PyPortfolio/PyPortfolioOpt ★

| Field | Evidence |
|---|---|
| Repository | PyPortfolio/PyPortfolioOpt |
| URL | https://github.com/PyPortfolio/PyPortfolioOpt |
| Accessed state | LICENSE (MIT, Robert Andrew Martin); README/test discussion |
| Licence | MIT |
| Project purpose | Efficient frontier, HRP, covariance shrinkage, constraints |
| Files inspected | LICENSE; README/test notes via GitHub/search synthesis |
| Tests inspected | pytest suite claimed near-full coverage |
| Relevant idea | HRP and Ledoit-Wolf shrinkage as optional fund extensions; weight-sum invariants |
| Weakness | Adding every optimiser dilutes Signal Harbour story; HRP less directly tied to Part A Attention Pulse |
| Compatibility | Could be dependency, but current Part B already implements EW/MV/MaxSharpe/RP without it |
| Decision | **Benchmark / deferred** — do not make HRP the primary innovation |
| Signal Harbour implementation | Keep local `src/portfolios.py`; optional later comparison table row |
| Attribution | Cite if algorithms adapted closely |
| Verification | Weight-sum and no-look-ahead tests already in Part B tests |

### 6. dcajasn/Riskfolio-Lib ★

| Field | Evidence |
|---|---|
| Repository | dcajasn/Riskfolio-Lib |
| URL | https://github.com/dcajasn/Riskfolio-Lib |
| Accessed state | LICENSE.txt via API → BSD-3-Clause |
| Licence | BSD-3-Clause |
| Project purpose | Broad risk-based portfolio optimisation including CVaR |
| Files inspected | licence API payload; repo description |
| Tests inspected | Not deeply inspected |
| Relevant idea | CVaR / risk-contribution diagnostics |
| Weakness | Heavy API surface; high implementation risk vs interpretability for this assessment |
| Compatibility | Would bloat requirements |
| Decision | **Reject as dependency** for this submission |
| Signal Harbour implementation | None in primary path |
| Attribution | N/A unless later adapted |
| Verification | N/A |

### 7. skfolio/skfolio ★

| Field | Evidence |
|---|---|
| Repository | skfolio/skfolio |
| URL | https://github.com/skfolio/skfolio |
| Accessed state | LICENSE → BSD-3-Clause |
| Licence | BSD-3-Clause |
| Project purpose | sklearn-style portfolio optimisation and validation |
| Files inspected | licence; repo page |
| Tests inspected | Not deeply inspected |
| Relevant idea | Explicit cross-validation / walk-forward mental model separating fit and predict periods |
| Weakness | Full library adoption would rewrite an already working local backtest |
| Compatibility | Good conceptually; unnecessary as dependency |
| Decision | **Adapt idea only** (keep estimation window vs first live date explicit) |
| Signal Harbour implementation | `src/portfolios.py`, report method wording |
| Attribution | Methodological citation if discussed |
| Verification | Existing first-live-date assertions |

### 8. ArturSepp/OptimalPortfolios ★

| Field | Evidence |
|---|---|
| Repository | ArturSepp/OptimalPortfolios |
| URL | https://github.com/ArturSepp/OptimalPortfolios |
| Accessed state | LICENSE.txt → MIT (Artur Sepp) |
| Licence | MIT |
| Project purpose | Optimal portfolio construction and backtesting analytics |
| Files inspected | licence; README/repo purpose |
| Tests inspected | Not deeply inspected |
| Relevant idea | Separate estimation, rebalance, and live performance; turnover/cost awareness |
| Weakness | Broader than course scope; copying would hide Signal Harbour design |
| Compatibility | Method only |
| Decision | **Adapt idea** for fusion sensitivity / optional turnover note |
| Signal Harbour implementation | `src/fusion.py` robustness grid; report cost discussion |
| Attribution | Methodological |
| Verification | Fusion sensitivity CSV |

### 9. Mirco1006/Portfolio-Allocation-App ★

| Field | Evidence |
|---|---|
| Repository | Mirco1006/Portfolio-Allocation-App |
| URL | https://github.com/Mirco1006/Portfolio-Allocation-App |
| Accessed state | README/repo summary |
| Licence | Not verified to SPDX in this pass — **no code copied** |
| Project purpose | Streamlit Markowitz app with KPI cards, weights, drawdown, correlation |
| Files inspected | README structure description |
| Tests inspected | Claims pure functions for testability |
| Relevant idea | Investor journey tabs: compare → fact sheet metrics → allocation controls; keep optimisation offline |
| Weakness | Live yfinance optimisation apps violate Part B “precomputed results” deployment rule if copied |
| Compatibility | Interaction pattern only |
| Decision | **Adapt interaction pattern**; reject runtime optimiser-in-app design |
| Signal Harbour implementation | `streamlit_app.py` explainability + allocation validation |
| Attribution | “Inspired by common Streamlit portfolio dashboard navigation patterns” — no code reuse |
| Verification | App loads only `results/` artifacts |

### 10. SB-231/systematic-equity-backtester ★

| Field | Evidence |
|---|---|
| Repository | SB-231/systematic-equity-backtester |
| URL | https://github.com/SB-231/systematic-equity-backtester |
| Accessed state | README |
| Licence | Not verified SPDX in this pass — **no code copied** |
| Project purpose | No-lookahead equity backtester with turnover/cost tests |
| Files inspected | README test list |
| Tests inspected | Documented: weights shifted one period; turnover math; weight-sum invariants |
| Relevant idea | Dedicated look-ahead unit tests; signal date ≠ trade date |
| Weakness | Different data/engine; not a sentiment product |
| Compatibility | Test design only |
| Decision | **Adapt test ideas** |
| Signal Harbour implementation | `tests/test_project_b_logic.py` lag/invariant tests |
| Attribution | Methodological |
| Verification | pytest |

---

## Synthesis for Signal Harbour

| Adopt / adapt | Why |
|---|---|
| VADER lexicon.update extension pattern (FinVADER / vaderSentiment) | Transparent, course-aligned |
| Neutral-override + phrase candidates (albyte-ai idea) | Targets false neutrals/false negatives in headlines |
| Contributing-term explainability (albyte-ai idea) | Streamlit innovation surface |
| Estimation vs live separation (skfolio / OptimalPortfolios idea) | Already partially present; keep explicit |
| Look-ahead unit tests (SB-231 idea) | Safety for Attention Pulse confidence lag |
| Precomputed-results app journey (Streamlit dashboards, selectively) | Matches brief; avoid live recompute |

| Reject / defer | Why |
|---|---|
| Unchanged FinVADER as “the innovation” | Convenor + addendum: design your own |
| SentiBigNomics full runtime package | Deploy burden |
| Riskfolio-Lib / full CVaR stack | Complexity vs interpretability |
| HRP as primary innovation | Weak Part A continuity vs Attention Pulse path |
| Copying any Streamlit MPT template wholesale | Academic integrity + wrong deployment model |

**No third-party source files were copied into Signal Harbour during this research stage.** Repositories are methodological references unless later implementation explicitly reuses code and updates `THIRD_PARTY_NOTICES.md`.
