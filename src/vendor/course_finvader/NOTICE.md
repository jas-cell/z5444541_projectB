# NOTICE — course / open-source finVADER lexicons

- Upstream project: PetrKorab/FinVADER
- URL: https://github.com/PetrKorab/FinVADER
- Licence: Apache License 2.0 (see LICENSE_Apache-2.0.txt)
- Files vendored: `Henry.py`, `SentiBignomics.py`
- Reason: FINS3645 Week 9 uses this package as finVADER; PyPI `finvader` does not install on Python 3.13 used in this local environment, so the lexicon modules are vendored to reproduce the course benchmark exactly.
- Adaptation: these lexicons power the labelled Week 9 / course finVADER benchmark, and that Week 9 analyser is also the base lexicon of the primary Signal Harbour model (`score_text_signal_harbour` starts from `build_week9_finvader()` in `src/sentiment.py`). The lexicons themselves are not claimed as original work — Signal Harbour's innovation layer (neutral masks, added terms and phrases, context weights) is separate, in `src/sentiment.py` and `src/resources/signal_harbour_lexicon.json`. The Week 9 teaching script `build_finvader()` logic is reimplemented in `src/sentiment.py`.
