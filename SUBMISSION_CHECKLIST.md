# Submission checklist - Part B

Tick every item before you hand in. Run `python scripts/check_handin.py` to verify
the mechanical ones.

## Verified in this folder

- [x] Folder is named `z5444541_projectB`.
- [x] `report/report.pdf` and `report/report.docx` are present; I author the report prose.
- [x] The report includes the required exhibits (Tables 1–6 and Figures A1–A10), each captioned and interpreted.
- [x] Equity, crypto, and combined funds across four methods, walk-forward OOS, with fact sheets.
- [x] Light theme pinned in `.streamlit/config.toml` (readable headings; still open the app once on your machine before zip).
- [x] No `report/~$report.docx` Word lock file in the tree at last check.
- [x] Raw data loads through `src/data_access.py`; no raw data or secrets committed. Derived `results/` artifacts are present.
- [x] `AGENTS.md` and `CLAUDE.md` are project-specific, not the starter stubs.
- [x] `ai/` contains prompt logs and AI notes; reviews attributed to me (optionally with third party Claude suggestions).
- [x] Requirement ledger filled (`ai/REQUIREMENT_LEDGER.md`); A–B consistency gate filled (`ai/PROJECT_AB_CONSISTENCY_GATE.md`).
- [x] Coverage figure is distinct from the model-comparison figure (different MD5 hashes).
- [x] `kaiyuan_review_label` filled by me on all 120 worksheet rows; automated `rule_based_pseudo_label` is diagnostic only.

## Still yours before hand-in

- [x] Editing pass on the report done by me in Google Docs (own words; label-validation, coverage, calendar and deployment corrections); revised `report/report.docx` and `report/report.pdf` exported from that document (see `ai/AI_ITERATION_LOG.md` Entry 12).
- [ ] Final dark-OS / local smoke: `streamlit run streamlit_app.py` and skim tabs.
- [x] Public GitHub repo: https://github.com/jas-cell/z5444541_projectB + live Streamlit URL: https://z5444541projectb-r9um2cjlkbqb35gndanq4f.streamlit.app/ (deployed from `main`, verified loading all five tabs with current `results/` data).
- [x] `kaiyuan_review_label` filled by me on all 120 rows (`positive` / `neutral` / `negative`).
- [ ] Delete `__pycache__` / `.DS_Store` / `*.pyc`, then hand-in zip + paste public repo link and live Streamlit URL.
