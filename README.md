# FINS3645 Project B - Signal Harbour

Kaiyuan Lan (`z5444541`)

- **Live app:** https://z5444541projectb-r9um2cjlkbqb35gndanq4f.streamlit.app/
- **Public repo:** https://github.com/jas-cell/z5444541_projectB

`Signal Harbour` is a Streamlit investment dashboard built for FINS3645 Part B. The app offers systematic equity, crypto, and combined funds, displays each fund's realised out-of-sample performance and latest holdings, provides an allocation sandbox, and surfaces a sector-level news sentiment index built from mapped equity headlines.

## What this project contains

- `streamlit_app.py`: app entrypoint at the repo root.
- `src/`: Part B implementation for cleaning, feature construction, portfolio backtests, sentiment scoring, and sentiment fusion.
- `scripts/run_part_b.py`: reproducible build script for the Part B outputs.
- `results/data/`: app-readable precomputed outputs.
- `results/tables/`: report tables including `performance_metrics.csv`, fusion diagnostics, and fund fact-sheet summaries.
- `results/figures/`: report and app figures.
- `report/`: assessed report is `report/report.docx` and `report/report.pdf` (authored by me).
- `ai/`: AI workflow files and iteration record.

## Reproducing the outputs

Create a virtual environment, install the requirements, and run the full build from the project root:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt pytest
python scripts/run_part_b.py
python -m pytest -q
python scripts/check_handin.py
```

The data helper downloads the official hosted ZIP through `src/data_access.py`. To work offline, set `FINS_DATA_ZIP` to a local copy of the project data ZIP before running the script.

## Running the app locally

After `results/` has been built:

```bash
streamlit run streamlit_app.py
```

The deployed app does not run VADER or recompute backtests. It reads the committed outputs under `results/data/` and `results/tables/`.

## Current Part B design

- Funds: Equity, Crypto, and Combined families.
- Methods: Equal Weight, Minimum Variance, Maximum Sharpe, and Risk Parity.
- Backtest design: monthly walk-forward out-of-sample rebalancing with a 252-day estimation window for equity and combined funds and a 365-day window for crypto.
- Primary innovation: **Signal Harbour Context-Weighted finVADER** — documented finance lexicon/phrase layer + coverage confidence + Part A Attention Pulse confidence, lagged one equity session before use.
- Benchmarks retained: unchanged VADER and the Week 9 course finVADER helper reproduced under `src/vendor/course_finvader/` (Signal Harbour starts from that Week 9 base).
- Fusion extension: a one-day-lagged context-weighted tilt applied to the equity sleeve, plus a robustness grid across base methods and tilt strengths.
- App: compare / fact sheet / allocate / sentiment / explain-signal tabs; deployed app reads only precomputed `results/`.
- Report: I author `report/report.docx` and `report/report.pdf`.

## Key generated files

- Required outputs:
  - `results/data/fund_returns.csv`
  - `results/data/fund_weights.csv`
  - `results/data/sector_sentiment_index.csv`
  - `results/tables/performance_metrics.csv`
- Additional evidence:
  - `results/tables/fusion_before_after.csv`
  - `results/tables/fusion_sensitivity.csv`
  - `results/tables/fund_fact_sheets.csv`
  - `results/tables/latest_holdings_snapshot.csv`
  - `report/REPORT_EVIDENCE_NOTES.md`

## Deployment note

Deployed for hand-in: public repo https://github.com/jas-cell/z5444541_projectB, live app https://z5444541projectb-r9um2cjlkbqb35gndanq4f.streamlit.app/ (entrypoint `streamlit_app.py`, deployed from `main` on Streamlit Community Cloud). The deployment steps followed are summarised in `docs/STUDENT_DEPLOY.md`.
