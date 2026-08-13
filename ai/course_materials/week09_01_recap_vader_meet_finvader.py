"""01 Recap VADER, then meet finVADER.

Week 8 built a sentiment score with VADER. VADER reads a general-purpose word list,
so it was never built for finance words like guidance, hawkish, or impairment.

finVADER is the same VADER model with two finance word lists added:
  - SentiBigNomics, about 7,300 economics and finance terms;
  - Henry's list, 189 words from company earnings releases.

This script scores six finance headlines with both models and reads where the finance
word list changes the answer. Nothing is downloaded and nothing is saved except a small
comparison table.
"""
from __future__ import annotations

import sys
from pathlib import Path

# --- Make fear_greed_tools importable --------------------------------------------
# Running the whole file sets __file__, so this folder is already known. Running a
# selection in the PyCharm console does not set it, so fall back to searching the
# working directory and its parents for the folder holding fear_greed_tools.py.
try:
    HERE = Path(__file__).resolve().parent
except NameError:
    _CWD = Path.cwd()
    _SEARCH = [_CWD, *_CWD.parents]
    _SEARCH += [d / "fins2026" / "week9" / "fear_greed_index" for d in (_CWD, *_CWD.parents)]
    HERE = next((d for d in _SEARCH if (d / "fear_greed_tools.py").is_file()), _CWD)
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pandas as pd

from fear_greed_tools import EXAMPLE_HEADLINES, build_finvader, build_vader, save_table, vader_compound

pd.set_option("display.width", 160)
pd.set_option("display.max_colwidth", 52)


# --- 1. Recap VADER on finance headlines -----------------------------------------
# VADER returns a compound score in the range -1 to 1. We keep only that number today.
vader = build_vader()
recap = pd.DataFrame({
    "headline": EXAMPLE_HEADLINES,
    "vader_compound": [vader_compound(vader, h) for h in EXAMPLE_HEADLINES],
})
print("VADER compound score for six finance headlines")
print(recap.to_string(index=False))


# --- 2. What finVADER adds -------------------------------------------------------
# finVADER loads the two finance word lists on top of VADER. We can read their sizes.
from finvader.SentiBignomics import lexicon1
from finvader.Henry import lexicon2

print("\nThe two finance word lists finVADER adds")
print(f"  SentiBigNomics terms: {len(lexicon1()):,}")
print(f"  Henry list terms:     {len(lexicon2()):,}")


# --- 3. Score the same headlines with finVADER -----------------------------------
# This is the official package call, one headline at a time. It is easy to read and
# fine for a few sentences. Script 02 uses a faster version for the full data.
from finvader import finvader

finvader_official = [
    finvader(h, use_sentibignomics=True, use_henry=True, indicator="compound")
    for h in EXAMPLE_HEADLINES
]

# The prebuilt analyser gives the identical answer, and we use it from here on.
finvader_analyzer = build_finvader()
finvader_fast = [vader_compound(finvader_analyzer, h) for h in EXAMPLE_HEADLINES]

print("\nThe official finvader() call and the prebuilt analyser agree")
check = pd.DataFrame({"official": finvader_official, "prebuilt": finvader_fast})
print(check.round(4).to_string(index=False))


# --- 4. Where the finance word list changes the answer ---------------------------
compare = recap.copy()
compare["finvader_compound"] = finvader_fast
compare["difference"] = (compare["finvader_compound"] - compare["vader_compound"]).round(4)
compare["vader_compound"] = compare["vader_compound"].round(4)
compare["finvader_compound"] = compare["finvader_compound"].round(4)

print("\nVADER against finVADER, same six headlines")
print(compare.to_string(index=False))
print(
    "\nRead the difference column. A positive number means finVADER is more positive"
    "\nthan VADER; a negative number means it is more negative. The finance word list"
    "\nmoves headlines that turn on words like beats, surge, guidance, and dividend."
)

save_table(compare, "01_vader_vs_finvader_headlines.csv")

print("\nRun 02_score_headlines.py next.")
