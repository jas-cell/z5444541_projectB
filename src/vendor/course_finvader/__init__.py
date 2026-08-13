"""Vendored finance lexicons used by FINS3645 Week 9 finVADER.

Source: PetrKorab/FinVADER (Apache-2.0), commit/tag corresponding to package
files inspected 2026-08-09. Only Henry.py and SentiBignomics.py are vendored.
The Week 9 course script builds an analyser by updating NLTK VADER with these
lists (SentiBigNomics scaled by 0.1). See NOTICE.md in this folder.
"""
from .Henry import lexicon2
from .SentiBignomics import lexicon1

__all__ = ["lexicon1", "lexicon2"]
