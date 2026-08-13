# Third-Party Notices — Signal Harbour Project B

Student: Kaiyuan Lan (`z5444541`)

## Vendored code (Week 9 benchmark + base lexicon of the primary model)

| Item | Detail |
|---|---|
| Repository | PetrKorab/FinVADER |
| URL | https://github.com/PetrKorab/FinVADER |
| Licence | Apache License 2.0 |
| Files reused | `src/vendor/course_finvader/Henry.py`, `src/vendor/course_finvader/SentiBignomics.py` |
| Nature of adaptation | Lexicon modules vendored unchanged (byte-identical to upstream `finvader/Henry.py` and `finvader/SentiBignomics.py`) to reproduce FINS3645 Week 9 `build_finvader()` on Python 3.13 (the latest PyPI `finvader` release, 1.0.4, declares `requires_python >=3.8,<3.12`; older releases pin `nltk==3.6.2`). Analyser assembly is reimplemented in `src/sentiment.py` following the Week 9 teaching helper. |
| Required notice | Apache-2.0 text retained in `src/vendor/course_finvader/LICENSE_Apache-2.0.txt`; see also `NOTICE.md` there. |
| Use in Signal Harbour | Two places: (1) the labelled **Week 9 / course finVADER benchmark**, and (2) as the **base lexicon of the primary Signal Harbour model** — `score_text_signal_harbour` starts from `build_week9_finvader()` (`src/sentiment.py`), per the project rule that the primary model builds on the Week 9 base. The innovation layer on top (neutral masks, added terms and phrases, context weights) is original work in `src/sentiment.py` and `src/resources/signal_harbour_lexicon.json`, not upstream code. |

Copyright notice for the vendored FinVADER materials follows the upstream Apache-2.0 licence terms in `LICENSE_Apache-2.0.txt`.

## Methodological references only (no source copy)

See `ai/OPEN_SOURCE_RESEARCH.md` for inspection cards. Examples: cjhutto/vaderSentiment, PyPortfolioOpt, skfolio, Streamlit portfolio dashboard interaction patterns, look-ahead unit-test ideas.

## Ordinary runtime dependencies

NLTK VADER, pandas, numpy, scipy, matplotlib, streamlit, pytest — used under their respective licences.
