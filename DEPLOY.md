# Deploy Signal Harbour (Part B)

The App brief expects a **public GitHub repo** and a **live Streamlit URL**.
This machine does not have the GitHub CLI (`gh`) installed, so the browser steps below are yours.

## 1. Local git (already prepared when this file is used)

```bash
cd /Users/jaysonlan/Desktop/z5444541_projectB
git status
```

If `.git` is missing:

```bash
git init
git add -A
git status   # confirm no .env / parquet secrets
git commit -m "Submit-ready Signal Harbour Part B package"
```

## 2. Public GitHub repo (browser or gh)

1. Create a new **public** repository (for example `z5444541_projectB`).
2. Do **not** add a README on GitHub if the local folder already has one.
3. Push:

```bash
git branch -M main
git remote add origin https://github.com/<YOUR_USER>/z5444541_projectB.git
git push -u origin main
```

## 3. Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. New app → select the public repo → main file `streamlit_app.py`.
3. Python version 3.11+; install from `requirements.txt`.
4. Confirm the app theme is light (`.streamlit/config.toml` pins `base = "light"`).
5. Copy the live URL into `SUBMISSION_CHECKLIST.md` and Moodle.

## 4. Smoke check after deploy

- All five tabs load.
- Headings are readable (not white-on-pale).
- No runtime VADER / backtest imports.
- Compare numbers match local `results/tables/performance_metrics.csv`.
