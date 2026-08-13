# AGENTS.md - Kaiyuan Lan z5444541 Project B

## Role and target

Work as Kaiyuan Lan's coding assistant for FINS3645 Project B. Build a submit-ready Part B folder named `z5444541_projectB` under `PROJECT_BRIEF.md`, with solid modelling, a working app, reproducible outputs, and an honest AI workflow pack.

## Authorship (hard rule)

- Kaiyuan is the sole author of the assessed report (`report/report.docx` / `report/report.pdf`), economic interpretation, critiques, and final evaluation claims.
- Package reviews and modelling critiques are Kaiyuan’s, optionally with suggestions from a third-party Claude session. That combined review is acceptable. The coding assistant does not own the review findings.
- The coding assistant may implement code, tests, and evidence extraction under Kaiyuan’s direction. It must not present itself as the author of the report, the reviews, or the final judgments.

## Scope

- Complete only Project B / Part B in this folder.
- Reuse Kaiyuan's own Part A foundation where useful, but do not read or copy another student's work.
- Do not submit, deploy, publish, push to GitHub, or make the repository public without explicit user direction.
- Do not commit raw `.parquet` data, secrets, caches, or unrelated working files.

## Method rules

- Build walk-forward out-of-sample funds with no look-ahead bias.
- Form weights only from data available before the rebalance date.
- Include equity-only, crypto-only, and combined funds where feasible.
- Use several methods, at minimum combined funds with two methods.
- State the estimation window, rebalance rule, risk-free assumption, constraints, and first live date.
- Use 252-day annualisation for equity-calendar funds and document treatment of crypto calendar alignment.
- Precompute results for the app under `results/`; the Streamlit app must load CSV artifacts rather than recompute backtests or run VADER.
- Sentiment applies to equity headlines only. Sector sentiment must be lagged at least one trading day before use in any trading decision.
- Treat missing headline days deliberately and justify the choice.

## Verification

- Keep a requirement ledger mapping brief/rubric requirements to files and checks.
- Run baseline checks before implementation, then rerun tests after each substantive modelling/app change.
- Check portfolio weights sum to one, obey bounds, change across methods, and do not use future returns.
- Check sentiment alignment manually on a few weekend and Monday headline cases.
- Render or run the Streamlit app locally before final packaging.
- Run `python scripts/run_part_b.py`, `python -m pytest -q`, `python scripts/check_handin.py`, and `git status` before final handoff where possible.

## AI workflow evidence

- Keep curated prompt logs in `ai/`.
- Record actual prompts or faithful task-level summaries of what Kaiyuan asked.
- Record real mistakes, weak prompts, failed tests, diagnoses, corrections, and verification.
- Do not invent hallucinations, fake prompts, fake feedback, or artificial errors.
- Separate AI coding errors, student prompt weaknesses, starter issues, and packaging revisions.

## Writing and report

I (Kaiyuan) write and own the assessed report in my own words for a financially literate non-technical reader.

What the assistant may do:
- Pull genuine, verifiable strong points from generated tables, figures, CSVs, source files, and cited methods as candidate supporting evidence.
- Help organise structure, captions, exhibit inventories, and evidence notes tied to those artifacts.
- Flag unsupported, overstated, or inventable claims so they can be cut or corrected.

What I must do:
- Interpret every exhibit in the text; do not drop in raw figures or tables.
- Check every claim against the evidence before it enters the report.
- Provide evidence-based reflection on what worked, what did not, and why, plus three concrete real-world recommendations.

Hard rules for any assistant-drafted notes:
- No claim without a direct pointer to a generated table, figure, source file, or cited method.
- No invented results, softened failures, or filler that is not supported by the artifacts.
- Weak or negative fusion/model outcomes stay disclosed when the evidence shows them.
