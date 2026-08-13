# Third-Party Notices — Signal Harbour Project B

Student: Kaiyuan Lan (`z5444541`)

## Vendored code (benchmark only)

| Item | Detail |
|---|---|
| Repository | PetrKorab/FinVADER |
| URL | https://github.com/PetrKorab/FinVADER |
| Licence | Apache License 2.0 |
| Files reused | `src/vendor/course_finvader/Henry.py`, `src/vendor/course_finvader/SentiBignomics.py` |
| Nature of adaptation | Lexicon modules vendored unchanged to reproduce FINS3645 Week 9 `build_finvader()` on Python 3.13 (PyPI `finvader` unavailable). Analyser assembly is reimplemented in `src/sentiment.py` following the Week 9 teaching helper. |
| Required notice | Apache-2.0 text retained in `src/vendor/course_finvader/LICENSE_Apache-2.0.txt`; see also `NOTICE.md` there. |
| Use in Signal Harbour | **Week 9 / course finVADER benchmark only.** Not the primary innovation model. |

Copyright notice for the vendored FinVADER materials follows the upstream Apache-2.0 licence terms in `LICENSE_Apache-2.0.txt`.

## Methodological references only (no source copy)

See `ai/OPEN_SOURCE_RESEARCH.md` for inspection cards. Examples: cjhutto/vaderSentiment, PyPortfolioOpt, skfolio, Streamlit portfolio dashboard interaction patterns, look-ahead unit-test ideas.

## Ordinary runtime dependencies

NLTK VADER, pandas, numpy, scipy, matplotlib, streamlit, pytest — used under their respective licences.
