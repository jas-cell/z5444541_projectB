# Requirement Ledger - Project B

Student: Kaiyuan Lan (z5444541)  
Last filled: 13 August 2026

Status key: **Done** = verified with file/test evidence in this folder. **Student-owned** = needs my browser / hand-in step.

## Authorship

I am the sole author of the assessed report prose, economic interpretation, critiques, and final evaluations. Package reviews are mine, optionally with third-party Claude suggestions. The coding assistant implements under my direction.

## Mandatory structure

| Requirement | Source | Evidence target | Verification | Status |
|---|---|---|---|---|
| Folder named `z5444541_projectB` | Brief Section 6 | Project root | `scripts/check_handin.py` | Done |
| Replace placeholder agent instructions | Brief Section 7 | `AGENTS.md`, `CLAUDE.md` | Hand-in checker + manual read | Done |
| Keep prompt logs / AI workflow pack | Brief Section 7, rubric | `ai/AI_ITERATION_LOG.md`, `ai/CURATED_PROMPT_LOG.md`, `ai/MANUAL_REVIEW_DECISIONS.md` | Manual review | Done |
| Report PDF under `report/` | Brief Section 5 | `report/report.pdf` (+ `report.docx`) | Files present; prose authored by me | Done |
| Full code under `src/` and `scripts/` | Brief Section 6 | Python modules and runner | `python scripts/run_part_b.py`, `pytest` | Done |
| App entrypoint at root | Brief Section 6, Appendix D | `streamlit_app.py` | Entrypoint present; light theme pinned in `.streamlit/config.toml` | Done |
| Precomputed app artifacts under `results/` | Brief Section 5 | `results/data/*.csv`, `results/tables/*.csv`, `results/figures/*.png` | Runner regenerates; app loads CSVs only | Done |
| No raw parquet, secrets, caches, or junk committed | Brief Appendix D | Project tree | Hand-in checker; delete `__pycache__` / `.DS_Store` before zip | Done (re-clean before zip) |

## Station 3 - Funds and backtests

| Requirement | Source | Evidence target | Verification | Status |
|---|---|---|---|---|
| Combined equity-plus-crypto fund with at least two methods | Brief Part B minimum | `results/data/fund_returns.csv`, `fund_weights.csv`, report tables | Pipeline output and metrics table | Done |
| Higher-band equity-only and crypto-only funds | Rubric HD band | Same as above | Families present in metrics CSV | Done |
| Several optimisation methods | Rubric HD band | Portfolio module and metrics | Four methods (EW, Min-Var, Max Sharpe, Risk Parity) | Done |
| Walk-forward out-of-sample backtest | Brief Station 3 | `src/portfolios.py`, report method section | Unit checks for rebalance/estimation windows | Done |
| No look-ahead bias | Brief Station 3 | Backtest + fusion | Date audit and tests; lagged sentiment | Done |
| Monthly or less frequent rebalancing | Brief Station 3 | Backtest settings | Monthly decision + next-session effective + holdings drift | Done |
| State first live date and estimation window | Brief Station 3 | Report and README | Explicit first-live dates in my report | Done |
| Fact sheet per fund | Brief Station 3 | App and report outputs | Streamlit Fact sheet tab + report tables | Done |
| Performance metrics table | Required exhibit | `results/tables/performance_metrics.csv` | File exists; conventional zero-rf Sharpe | Done |
| Growth-of-one-dollar figure | Required exhibit | `results/figures/` | Rendered figure | Done |
| Drawdown figure | Required exhibit | `results/figures/` | Rendered figure | Done |
| Portfolio weights-over-time figure | Required exhibit | `results/figures/` | Rendered figure | Done |
| Sharpe or return-vs-risk barplot | Required exhibit | `results/figures/` | Rendered figure | Done |

## Station 3 - Sentiment and fusion

| Requirement | Source | Evidence target | Verification | Status |
|---|---|---|---|---|
| Apply sentiment model to headlines | Brief Station 3 | `src/sentiment.py`, generated artifacts | Pipeline run; Signal Harbour on Week 9 base | Done |
| Build sector sentiment index | Required output | `results/data/sector_sentiment_index.csv` | Complete grid; no-news = neutral | Done |
| Equal-weight ticker-day sentiment within sector | Brief Station 3 | Sentiment implementation | Code review and sample check | Done |
| Decide treatment of ticker-days with no headlines | Brief Station 3 | Report method section | Neutral on no-news; justified in report | Done |
| Lag signal at least one trading day | Brief Station 3 | `src/sentiment.py`, `src/fusion.py` | Date alignment tests | Done |
| Justify text handling | Brief Station 3 | Report method section | Lexicon / phrase / confidence notes | Done |
| Fusion before-vs-after table and figure | Required exhibit | `results/tables/`, `results/figures/` | Cost table + fusion exhibits | Done |
| Critical assessment of fusion result, including negative result if applicable | Rubric HD band | Report | Flat/negative fusion vs baselines disclosed | Done |

## Station 4 - App

| Requirement | Source | Evidence target | Verification | Status |
|---|---|---|---|---|
| Compare funds | Brief Station 4 | Streamlit app | Compare tab loads precomputed returns | Done |
| Open fund fact sheet | Brief Station 4 | Streamlit app | Fact sheet tab | Done |
| Set allocation across funds | Brief Station 4 | Streamlit app | Allocate tab; mixed union calendar fixed | Done |
| Read sentiment analytics | Brief Station 4 | Streamlit app | Sentiment + Explain tabs | Done |
| App loads precomputed results, not VADER/backtests | Brief common mistakes | `streamlit_app.py` | Code review: CSV load only | Done |
| App runs on a basic machine | Brief Appendix B | Requirements and runtime | Syntax + theme pin; final dark-OS smoke is student-owned | Done (code); student smoke recommended |
| Prepare public GitHub/Streamlit deployment instructions | Brief Appendix D | `DEPLOY.md`, README | Instructions written; live URL student-owned | Done (docs); deploy Student-owned |

## Innovation and writing

| Requirement | Source | Evidence target | Verification | Status |
|---|---|---|---|---|
| Distinctive implemented extension | Rubric Innovation 30% | Code, report, exhibit | Context-Weighted finVADER + Attention Pulse + Explain tab | Done |
| Original coherent design system or app feature | Rubric app/presentation | App and figures | Signal Harbour product continuity from Part A | Done |
| Evidence-based interpretation for every exhibit | Brief and rubric | `report/report.docx` / `report/report.pdf` | Authored and interpreted by me | Done |
| Three concrete real-world recommendations | Rubric writing 10% | Report final section | Three numbered recommendations in my report | Done |
| Written narrative no more than 10 pages, about 5,000 words excluding appendix/references | Brief Part B | `report/report.pdf` | Current PDF ~13 pages including appendix/references | Done |

## Student-owned before hand-in

| Item | Status |
|---|---|
| Public GitHub repo + live Streamlit URL | Student-owned — follow `DEPLOY.md` |
| Optional: fill `kaiyuan_review_label` by hand | Optional / blank by design |
| Hand-in zip after deleting `__pycache__` / `.DS_Store` | Student-owned |
