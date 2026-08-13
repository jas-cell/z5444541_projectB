# FINS3645 Week 8 / Week 9 course materials — Signal Harbour use

Student: Kaiyuan Lan (`z5444541`)  
Supplied: 2026-08-09 via Kaiyuan Downloads (`week07/08/09` zips + lecture PDFs)

## What the course materials contain

| Week | Folder | Relevant content |
|---|---|---|
| 7 | `financial_news_narrative`, `project_text_dff` | Mini finance lexicon tones; project headline coverage |
| 8 | `vader_model` | Build/extend VADER; human-audited finance lexicon procedure (`09_`, `10_`) |
| 9 | `fear_greed_index` | Recap VADER, introduce **finVADER**, score project headlines, fear/greed index |

## What Week 9 finVADER actually is

From `week9/fear_greed_index/01_recap_vader_meet_finvader.py` and `fear_greed_tools.build_finvader()`:

- Same VADER model
- Plus SentiBigNomics (~7,300 terms), valence scaled by **0.1**
- Plus Henry’s earnings list (189 words)
- Implemented in the course as the PetrKorab `finvader` package / equivalent prebuilt analyser

This is the **course benchmark**, not Signal Harbour’s primary innovation.

## How Signal Harbour uses it

1. Reproduce `build_finvader()` in `src/sentiment.py` as `build_week9_finvader()`.
2. Vendor `Henry.py` and `SentiBignomics.py` under `src/vendor/course_finvader/` (Apache-2.0) because PyPI `finvader` does not install on local Python 3.13.
3. Keep Week 9 finVADER as a labelled benchmark in `sentiment_model_comparison.csv`.
4. Keep Signal Harbour Context-Weighted finVADER as the primary contribution (custom lexicon/rules + coverage + Attention Pulse + lag).

## Week 8 relevance

Week 8 teaches that a custom finance lexicon must be documented, agreement-filtered, and human-reviewed — and that rejected terms (e.g. unsigned category words like some accounting vocabulary) should stay out. That pedagogy supports Signal Harbour’s lexicon audit CSV and rejection of unsigned terms such as bare `guidance`.

## Limits

- Course fear/greed index construction is a teaching path; Signal Harbour’s product index remains the lagged sector/context-weighted design required by Project B.
- Vendored lexicons reproduce the Week 9 benchmark and sit under the primary model as its base lexicon; they are not claimed as original Signal Harbour work.
