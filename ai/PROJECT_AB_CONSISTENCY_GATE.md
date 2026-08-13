# Project A–B Final Consistency Gate

Student: Kaiyuan Lan (`z5444541`)  
Checked: 13 August 2026  
Rule: concurrent marking means an inconsistency is a whole-project defect.

Authorship: I own the assessed report prose and final evaluations. Package reviews are mine, optionally with third-party Claude suggestions.

| Gate item | Status | Evidence / note |
|---|---|---|
| Same product identity | Pass | Signal Harbour in A report, B README, B app, B report |
| Same target user | Pass | Small wealth-advisory firm; portfolio analyst as day-to-day user |
| Same data provenance | Pass | Both use `src/data_access.py` hosted ZIP helper |
| Same cleaning definitions | Pass | B `etl.clean_headlines` dedups on `(ticker, date, title)`; price unique ticker-date |
| Same return definition | Pass | Adjusted-close simple returns within ticker |
| Same date limits | Pass | Analysis constrained to 2020–2023 |
| Same calendar logic | Pass | Equity native sessions; crypto native then left-align for combined |
| Same headline mapping | Pass | Same/next equity session via `searchsorted` |
| Same Attention Pulse equation | Pass | Ported into B `features.add_attention_pulse` with past-only baseline |
| No B claim that A already contained sentiment | Pass | Scoring begins in B; A diagnostics stay descriptive |
| No claim that contemporaneous A diagnostics were tradable | Pass | B uses lagged `tradable_score` only |
| B explains descriptive A feature → lagged tested signal | Pass | Context-weighted score × lag in sentiment module, app explain tab, my report |
| Week 9 finVADER benchmark available | Pass | Course Week 9 helper reproduced; lexicons vendored under `src/vendor/course_finvader` |
| Signal Harbour starts from Week 9 base | Pass | `score_text_signal_harbour` uses `build_week9_finvader()` |
| Report DOCX/PDF are my authored deliverables | Pass | `report/report.docx` and `report/report.pdf`; prose drafted by me, typeset via `report/build_academic_docx.py` / `build_academic_pdf.py` (scripts retained in `report/`) |

## Inherited limitations disclosed, not hidden

1. Uneven sector headline coverage (from Part A) → coverage confidence in B.
2. Attention Pulse in A was descriptive → elevated pulse confidence only in B, then lagged.
3. Fusion remains economically flat/negative versus Equity Equal Weight and versus the corrected Min-Var baseline once drift and conventional Sharpe are used.
4. I labelled all 120 rows of the headline worksheet in `kaiyuan_review_label`. The `rule_based_pseudo_label` column is an automated diagnostic only and is not reported as human validation.

## Residual actions before hand-in / public deploy

| Item | Status |
|---|---|
| Gate table above | All Pass |
| `kaiyuan_review_label` filled by me on all 120 rows | Done |
| Delete `__pycache__` / `.DS_Store` before zip | Open before hand-in zip |
| Public GitHub + live Streamlit | Student-owned — `DEPLOY.md` |
| Hand-in upload | Student-owned; agent does not publish without explicit instruction |
