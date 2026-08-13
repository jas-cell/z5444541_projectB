# AI Iteration Log - Project B

Student: Kaiyuan Lan (z5444541)

This log records how I used a coding assistant on FINS3645 Project B. It is chronological and evidence-focused. I record what I asked, what the assistant produced, what I checked, mistakes or risks found, changes made, and verification.

Authorship note: I own the assessed report, critiques, and final evaluations. Package reviews are mine, optionally with third-party Claude suggestions. The coding assistant implements under my direction.

There is no Entry 5: an earlier report-builder packaging note was dropped from this coding log because the assessed report is authored by me in `report/report.docx` / `report/report.pdf`, not by a Python narrative module.


## Entry 1 - Project setup and baseline read

| Field | Record |
|---|---|
| Objective | Start Project B from the supplied starter, set up the correct folder, and identify what must be built before touching model code. |
| Actual prompt/action | I asked the coding assistant to follow the staged Part B plan and start. It read the project-level instructions, unzipped the supplied `projectB_starter (1).zip`, renamed it to `z5444541_projectB`, and read the Project B sections of `PROJECT_BRIEF.md`. |
| Prompt significance | Meaningful direction and substantive setup. |
| AI output used | A clean Project B workspace from the official starter, plus a working plan for funds, sentiment, fusion, precomputed Streamlit artifacts, deployment prep, and the AI workflow pack. |
| Student review | I checked the brief wording directly, especially Part B required filenames, no-look-ahead backtest rules, required output artifacts, app requirements, and AI workflow requirements. I inspected `scripts/run_part_b.py`, `scripts/check_handin.py`, `tests/test_smoke.py`, and the starter `AGENTS.md`. |
| Problem caught | The starter is only a skeleton: `scripts/run_part_b.py` loads price data but does not compute returns, funds, sentiment, fusion, tables, figures, or app-ready artifacts. The provided `AGENTS.md` is also a placeholder and would fail the AI workflow requirement if submitted unchanged. |
| Diagnosis | Starter issue, not a modelling error. Jumping straight to packaging would leave no reproducible Station 3 outputs. |
| Change | I replaced the placeholder `AGENTS.md` with project-specific instructions and created this `ai/AI_ITERATION_LOG.md` before substantive implementation. |
| Verification | Confirmed the starter file list and brief requirements from the local files. |


## Entry 2 - Baseline checks and environment correction

| Field | Record |
|---|---|
| Objective | Run the untouched starter checks before implementation so I know the genuine starting point. |
| Actual prompt/action | I directed the assistant to run `python scripts/check_handin.py`, `python -m pytest -q`, and `python scripts/run_part_b.py`, then fix the environment as needed. |
| Prompt significance | Substantive diagnostic action. |
| AI output used | Diagnosis that `python` was missing; `python3` lacked packages; a local `.venv` inside the project made `check_handin.py` flag package parquet files, so the venv was moved to `/private/tmp/z5444541_projectB_venv`. |
| Student review | I checked the actual failure messages and re-ran with dependencies installed and the virtual environment outside the hand-in folder. |
| Problem caught | Wrong Python command and an in-folder venv can create false hand-in failures. The data helper also needs network access once to fetch/cache the official data bundle. |
| Diagnosis | Environment/setup issue. The starter could load data once dependencies and network access were available; it still did not implement Part B outputs. |
| Change | Use `/private/tmp/z5444541_projectB_venv/bin/python` for local verification. Keep dependency environments outside `z5444541_projectB`. |
| Verification | `pytest` `2 passed`. `scripts/run_part_b.py` loaded equities `(50300, 9)` and crypto `(14620, 8)`. `scripts/check_handin.py` passed 16 structural checks and warned only about missing results artifacts and removable Python cache files. |


## Entry 3 - First complete Station 3/4 pass

| Field | Record |
|---|---|
| Objective | Build a first complete Part B pipeline: funds, sentiment, fusion outputs, figures, and a precomputed-results app. |
| Actual prompt/action | I directed the assistant to port relevant Part A cleaning/date-alignment logic, implement walk-forward portfolio methods, add VADER-plus-finance-lexicon sentiment scoring, create a lagged sentiment tilt, replace the runner and Streamlit app, and add focused tests. |
| Prompt significance | Substantive production and diagnostic iteration. |
| AI output used | New modules in `src/etl.py`, `src/features.py`, `src/portfolios.py`, `src/sentiment.py`, and `src/fusion.py`; a reproducible `scripts/run_part_b.py`; app-ready outputs under `results/`; Streamlit app that reads precomputed CSVs only. |
| Student review | I ran the pipeline and inspected the metrics table, required output filenames, hand-in checker, app imports, and tests. I checked that the sentiment tilt does not claim artificial outperformance relative to the base equity minimum-variance fund. |
| Problem caught | Network access still needed for the data helper; generated `.venv`, `__pycache__`, and `.pytest_cache` can pollute the submission folder. |
| Diagnosis | Reproducibility/package risks rather than model-result failures. |
| Change | Kept the virtual environment outside the project folder, removed generated caches, and verified the app does not import `nltk` or `data_access`. |
| Verification | Pipeline produced `fund_returns.csv`, `fund_weights.csv`, `sector_sentiment_index.csv`, `performance_metrics.csv`, and six figures. `pytest` `6 passed`. Hand-in checker 22 checks with a missing-artifact reminder. |


## Entry 4 - Fusion robustness and evidence packaging

| Field | Record |
|---|---|
| Objective | Test whether the sentiment overlay adds value across reasonable specifications, then package reusable evidence tables and figures. |
| Actual prompt/action | I directed the assistant to add a fixed robustness grid across equity base methods and tilt strengths, regenerate outputs, improve the app presentation of the strongest funds and fusion findings, create fact-sheet and holdings tables, and rewrite the starter README. |
| Prompt significance | Substantive production and interpretive revision. |
| AI output used | `results/tables/fusion_sensitivity.csv`, `results/figures/fusion_sensitivity.png`, `results/tables/fund_fact_sheets.csv`, `results/tables/latest_holdings_snapshot.csv`. |
| Student review | I checked whether any tilt specification materially beat the underlying equity baseline, reviewed strongest fund metrics, and inspected latest holdings and end-of-sample sector sentiment. |
| Problem caught | The first fusion result was technically correct but too thin without a sensitivity table. The README still sounded like the starter template. |
| Diagnosis | Evidence around the model was not yet rich enough. |
| Change | Added the robustness grid and made the negative result explicit: the lagged sentiment overlay is stable but does not beat the strongest equity baseline. Reframed the app and README around Signal Harbour. |
| Verification | Pipeline completed; `pytest` `6 passed`; best tilt variant still below the un-tilted equity equal-weight baseline on Sharpe. |


## Entry 6 - Course-forum continuity and Context-Weighted finVADER upgrade

| Field | Record |
|---|---|
| Objective | Treat Parts A and B as one project, audit Project A, research open-source methods, and replace the shallow lexicon overlay with Signal Harbour Context-Weighted finVADER. |
| Actual prompt/action | I supplied a mandatory addendum with two Ed-forum exchanges (pasted by me; the assistant did not scrape Ed), required continuity audit, GitHub research, innovation scorecard, and Context-Weighted finVADER protocol. Under my direction the assistant moved the agent root to `z5444541_projectB`, read final Project A, drafted the continuity/research docs I requested, and implemented the upgraded sentiment/fusion/app path. |
| Prompt significance | Meaningful direction and substantive production. |
| AI output used | Continuity and research drafts; rewritten `src/sentiment.py`; Part A Attention Pulse ported into `src/features.py`; fusion renamed to context-weighted path; Streamlit explainability tab; new innovation tables/figures in the runner. |
| Student review | I reviewed the regenerated model tables later; Entry 10 restored blank `kaiyuan_review_label` and demoted keyword labels to an automated pseudo-label diagnostic only. |
| Problem caught | Earlier Part B draft treated a small finance lexicon as the innovation and did not use Attention Pulse. Week 9 finVADER file was not found locally at that time. |
| Diagnosis | Under concurrent marking and the forum guidance I pasted, a shallow lexicon update leaves continuity and originality thin. Reconstructing Week 9 from memory would be dishonest. |
| Change | I selected Context-Weighted finVADER as primary innovation; kept unchanged VADER and open-source FinVADER-style scoring as benchmarks; deferred HRP/shrinkage as primary innovations. |
| Verification | Unit tests cover lag, Attention Pulse past-only construction, phrase lift, and blank human labels. Pipeline regenerated in later entries. |


## Entry 7 - Week 8/9 course materials supplied; Week 9 finVADER benchmark locked

| Field | Record |
|---|---|
| Objective | Replace the earlier missing-course-file caveat with the actual FINS3645 Week 8/9 materials I supplied. |
| Actual prompt/action | I provided `week07_student_folder.zip`, `week08_student_folder.zip`, `week09_student_folder.zip`, and the Week 8/9 lecture slides. The assistant inspected `week9/fear_greed_index/01_recap_vader_meet_finvader.py` and `fear_greed_tools.build_finvader()`. |
| Prompt significance | Meaningful correction to the benchmark definition. |
| AI output used | Confirmed Week 9 finVADER is PetrKorab FinVADER (SentiBigNomics*0.1 + Henry). Vendored lexicon modules under `src/vendor/course_finvader/`. Implemented `build_week9_finvader()` to match the course helper. |
| Student review | I confirmed Week 9 differs from base VADER on sample headlines and that Signal Harbour remains a separate primary model on the Week 9 base. |
| Problem caught | Earlier draft used a thin Henry-style fallback and stated Week 9 was unavailable. That is no longer true. |
| Diagnosis | Course materials were not in the original Project B package; they arrived later from Ed downloads. |
| Change | Labelled benchmark is now `week9_finvader`; documentation wording updated; Apache-2.0 notices recorded. |
| Verification | Smoke check: sample headline base 0.296 vs Week 9 0.829. Regenerated comparison / ablation use `week9_finvader` as the base after Entry 10. |


## Entry 8 - Manual package review and modelling correction start

| Field | Record |
|---|---|
| Objective | Act on my package review (plus third party Claude suggestions), log those decisions honestly, then fix modelling defects. |
| Actual prompt/action | I manually reviewed the package (source, CSVs, reproduction, tests, Streamlit, AI pack) and also used suggestions from a third party Claude session. I accepted the material defects, logged the correction order in `ai/`, and directed the coding assistant to fix them. |
| Prompt significance | Meaningful direction and substantive correction. |
| AI output used | `ai/MANUAL_REVIEW_DECISIONS.md`; this Entry 8; Entry R1 in `CURATED_PROMPT_LOG.md`; then code changes starting in `src/portfolios.py`, `src/fusion.py`, and `src/sentiment.py`. |
| Student review | I confirmed key symptoms in retained outputs (min-var often equal-weight; CAGR/vol labelled as Sharpe). |
| Problem caught | Silent SLSQP stall and inconsistent Sharpe; constant-weight “monthly” backtest; “augmented finVADER” starting from plain VADER; blank human labels; AI-log credibility issues. |
| Diagnosis | Passing `result.success` is not optimisation. Labelling CAGR/vol as Sharpe makes Maximum Sharpe inconsistent. Driftless weights inflate “monthly rebalancing”. Innovation naming ran ahead of the implementation. |
| Change | Log prompts first; then rescale optimiser objectives, unify Sharpe as zero-rf mean/vol, implement holdings drift with next-day effectiveness, rebuild Signal Harbour on Week 9 finVADER. |
| Verification | Completed in Entry 9: method-weight differentiation; conventional Sharpe; drift tests; regenerated pipeline; pytest and hand-in checker pass. |


## Entry 9 - Blocker fixes after my manual review

| Field | Record |
|---|---|
| Objective | Implement the correction order from Entry 8 / `MANUAL_REVIEW_DECISIONS.md` and re-verify. |
| Actual prompt/action | I continued directing the assistant from my review prompts: rescale optimiser, unify Sharpe, monthly drift + next session timing, Week 9 based Signal Harbour, honest review sheet naming with holdout, app calendar/explain date fixes, AI pack cleanup. |
| Prompt significance | Substantive production and verification. |
| AI output used | Rewritten `src/portfolios.py`, `src/fusion.py`, `src/sentiment.py`, `streamlit_app.py`, `scripts/run_part_b.py`, tests, `CLAUDE.md`, regenerated `results/`. |
| Student review | I checked regenerated metrics: Equity Min-Var vs Equal Weight mean half-L1 ≈ 0.72 and 100% of rebalances differ by >1%; profit-falls headlines now negative under Signal Harbour; fusion Sharpe 0.4740 → 0.4711 with cost table; pytest 22 passed; hand-in checker 22 passed. |
| Problem caught | None new beyond the modelling blockers already listed in Entry 8; remaining packaging steps stayed mine. |
| Diagnosis | Corrected optimiser, Sharpe definition, drift engine, and Week 9 base were the material blockers for method honesty. |
| Change | Annualised covariance in SLSQP; conventional zero-rf Sharpe; drifting holdings; Week 9 base for Signal Harbour; debt mask retired; negation-aware phrases; elevated-only attention confidence; explain_* lagged fields; stratified samples; method divergence + cost tables. |
| Verification | `python scripts/run_part_b.py` completed; `pytest` 22 passed; `check_handin.py` ready-to-zip with only `__pycache__` reminder. Remaining student-owned: public GitHub and live Streamlit URL. |

### Classification notes
- Silent optimiser stall / inconsistent Sharpe / constant-weight “monthly” engine: AI modelling errors.
- “Augmented finVADER” starting from plain VADER: naming overclaim (AI + weak prompt specificity).
- Blank validation labels: incomplete student review (left blank on purpose; automated pseudo-label column is diagnostic only).


## Entry 10 - Second manual review: false human labels and remaining blockers

| Field | Record |
|---|---|
| Objective | Correct overclaims introduced while responding to the first review. |
| Actual prompt/action | My second manual review (again with third party Claude suggestions) found: keyword labels written into `kaiyuan_review_label` and described as human validation; wrong attribution in the AI pack; ablation on plain VADER; sector index ignoring no-news neutrals; turnover timing bug; mixed Allocate dropping crypto weekends. I ordered fixes. |
| Prompt significance | Meaningful correction of attribution and modelling honesty. |
| AI output used | Blank `kaiyuan_review_label`; renamed automated `rule_based_pseudo_label` diagnostic; Week-9-base ablation; complete-grid sector index; post-return turnover; mixed union calendar; updated evidence notes. |
| Student review | I confirmed inventing labels under my name violated `CLAUDE.md` and was worse than a blank column; required correct attribution (my review + third party Claude suggestions). |
| Problem caught | Pseudo-labels mislabelled as human; AI-log attribution error; ablation base wrong; sector index incomplete; turnover understated; Allocate calendar inconsistent. |
| Diagnosis | Pressure to “complete validation” produced deceptive naming. Honesty requires blank student labels or explicit automated-diagnostic language. |
| Change | Implemented the accepted correction order; removed human-agreement claims from assessed outputs. |
| Verification | Pipeline regenerated: sector index ends 2023-12-29 for all sectors; ablation uses `week9_finvader` base; 120/120 Kaiyuan labels blank; cost table compares base vs fusion; pytest 24 passed; hand-in 23 checks passed after cache cleanup. |


## Entry 11 - Must-fix before submission (theme, deploy, duplicate figure)

| Field | Record |
|---|---|
| Objective | Close the remaining must-fix gaps from my readiness check before treating Part B as submit-ready. |
| Actual prompt/action | After my own readiness check of the folder, I asked the coding assistant to fix only: Streamlit light-theme pin; public repo + live app prep; replace or delete the duplicate coverage figure. |
| Prompt significance | Meaningful direction. |
| AI output used | `.streamlit/config.toml` theme pin; real coverage figure in `run_part_b.py`; deploy/git preparation. |
| Student review | I confirmed light theme pin and distinct coverage figure hashes. Public GitHub URL and live Streamlit URL remain my browser steps (`DEPLOY.md`). |
| Problem caught | Dark-theme illegibility; undeployed app; byte-identical figure pair. |
| Diagnosis | Presentation and packaging gaps, not a modelling failure. |
| Change | Pinned Streamlit light theme; replaced duplicate coverage figure with a real coverage figure; wrote `DEPLOY.md` and `git init` (no push — `gh` unavailable). Also hardened `scripts/check_handin.py` junk check to catch `~$` Office lock files. |
| Verification | Coverage vs model-comparison MD5s differ; hand-in checker passes. Deploy URL still student-owned. |
