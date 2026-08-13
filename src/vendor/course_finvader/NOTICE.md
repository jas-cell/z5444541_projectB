# NOTICE — course / open-source finVADER lexicons

- Upstream project: PetrKorab/FinVADER
- URL: https://github.com/PetrKorab/FinVADER
- Licence: Apache License 2.0 (see LICENSE_Apache-2.0.txt)
- Files vendored: `Henry.py`, `SentiBignomics.py`
- Reason: FINS3645 Week 9 uses this package as finVADER; PyPI `finvader` does not install on Python 3.13 used in this local environment, so the lexicon modules are vendored to reproduce the course benchmark exactly.
- Adaptation: Signal Harbour does **not** use these lexicons as its primary innovation model. They power the labelled Week 9 / course finVADER benchmark only. The Week 9 teaching script `build_finvader()` logic is reimplemented in `src/sentiment.py`.
