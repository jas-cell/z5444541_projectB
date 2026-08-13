# Extracted for provenance from FINS3645 week9/fear_greed_tools.py
def build_finvader():
    """Build the finVADER analyser once, so we can score many headlines quickly.

    finVADER is VADER with two finance word lists added: SentiBigNomics (about 7,300
    economics terms) and Henry's list (189 words from earnings releases). The finvader
    package rebuilds that combined word list on every single call, which is fine for a
    few sentences but slow for 100,000 headlines. Here we build the combined analyser
    one time and reuse it. The scores are identical to calling finvader() each time.
    """
    import nltk
    nltk.download("vader_lexicon", quiet=True)
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from finvader.SentiBignomics import lexicon1
    from finvader.Henry import lexicon2

    analyzer = SentimentIntensityAnalyzer()
    # 0.1 is finVADER's tuning constant: SentiBigNomics scores run -1 to 1, and this
    # shrinks them before they mix with VADER's -4 to 4 valences.
    sentibignomics = {term: value * 0.1 for term, value in lexicon1().items()}
    analyzer.lexicon.update({**sentibignomics, **lexicon2()})
    return analyzer


