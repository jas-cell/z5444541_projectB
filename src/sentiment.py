"""Signal Harbour sentiment models: Week-9-based augmentation + context weights."""
from __future__ import annotations

from functools import lru_cache
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


LEXICON_PATH = Path(__file__).resolve().parent / "resources" / "signal_harbour_lexicon.json"
TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
NEGATION_RE = re.compile(
    r"\b(?:not|no|never|without|neither|nor|n't)\b[\w\s-]{0,18}$",
    flags=re.IGNORECASE,
)


@lru_cache(maxsize=1)
def load_lexicon_spec() -> dict[str, Any]:
    return json.loads(LEXICON_PATH.read_text(encoding="utf-8"))


def _vader():
    from nltk.sentiment import SentimentIntensityAnalyzer

    return SentimentIntensityAnalyzer()


def retained_term_lexicon(spec: dict[str, Any] | None = None) -> dict[str, float]:
    spec = spec or load_lexicon_spec()
    return {
        row["text"].lower(): float(row["valence"])
        for row in spec.get("terms", [])
        if row.get("retained")
    }


def retained_phrases(spec: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    spec = spec or load_lexicon_spec()
    return [row for row in spec.get("phrases", []) if row.get("retained")]


def neutral_masks(spec: dict[str, Any] | None = None) -> list[str]:
    spec = spec or load_lexicon_spec()
    return [
        row["text"].lower()
        for row in spec.get("neutral_overrides", [])
        if row.get("retained") and row.get("action") == "mask"
    ]


def _mask_neutral_tokens(text: str, masks: list[str]) -> str:
    if not masks:
        return text
    pattern = re.compile(r"\b(" + "|".join(re.escape(m) for m in masks) + r")\b", flags=re.IGNORECASE)
    return pattern.sub(" norx ", text)


def _phrase_adjustment(text: str, phrases: list[dict[str, Any]]) -> tuple[float, list[str]]:
    """Apply phrase lifts, skipping matches that sit immediately after a negation cue."""

    lowered = text.lower()
    score = 0.0
    hits: list[str] = []
    for row in phrases:
        phrase = row["text"].lower()
        start = 0
        while True:
            idx = lowered.find(phrase, start)
            if idx < 0:
                break
            prefix = lowered[max(0, idx - 24):idx]
            if NEGATION_RE.search(prefix):
                start = idx + len(phrase)
                continue
            score += float(row["valence"]) / 4.0
            hits.append(phrase)
            lowered = lowered[:idx] + " " * len(phrase) + lowered[idx + len(phrase):]
            start = idx + len(phrase)
    return float(np.clip(score, -0.75, 0.75)), hits


def score_text_base_vader(text: str, analyser=None) -> float:
    analyser = analyser or _vader()
    return float(analyser.polarity_scores(str(text))["compound"])


@lru_cache(maxsize=1)
def build_week9_finvader():
    """Reproduce FINS3645 Week 9 `fear_greed_tools.build_finvader()`.

    Week 9 finVADER = NLTK VADER + SentiBigNomics (scaled by 0.1) + Henry.
    Lexicon modules are vendored under `src/vendor/course_finvader/` because the
    PyPI `finvader` package does not install on Python 3.13. Scores match the
    course prebuilt analyser path.
    """

    from src.vendor.course_finvader import lexicon1, lexicon2

    analyser = _vader()
    sentibignomics = {term: value * 0.1 for term, value in lexicon1().items()}
    analyser.lexicon.update({**sentibignomics, **lexicon2()})
    return analyser


def score_text_week9_finvader(text: str, analyser=None) -> float:
    """Course Week 9 / PetrKorab finVADER benchmark compound score."""

    analyser = analyser or build_week9_finvader()
    return float(analyser.polarity_scores(str(text))["compound"])


# Backward-compatible alias used in earlier draft tables.
def score_text_open_source_finvader_style(text: str, analyser=None) -> float:
    return score_text_week9_finvader(text, analyser=analyser)


def score_text_signal_harbour(
    text: str,
    analyser=None,
    *,
    spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Signal Harbour context rules on top of the Week 9 finVADER base analyser.

    Primary path = Week 9 finVADER lexicon (SentiBigNomics*0.1 + Henry) plus
    Signal Harbour masks, finance terms, and negation-aware phrases. This is an
    augmentation of the course Week 9 benchmark, not a plain-VADER heuristic.
    """

    spec = spec or load_lexicon_spec()
    analyser = analyser or build_week9_finvader()
    original = str(text)
    masks = neutral_masks(spec)
    masked = _mask_neutral_tokens(original, masks)
    local = _vader()
    local.lexicon.update(analyser.lexicon)
    local.lexicon.update(retained_term_lexicon(spec))
    base_aug = float(local.polarity_scores(masked)["compound"])
    phrase_adj, phrase_hits = _phrase_adjustment(original, retained_phrases(spec))
    # Blend: keep lexicon compound dominant; phrase rules provide bounded additive lift.
    compound = float(np.clip(base_aug + 0.35 * phrase_adj, -1.0, 1.0))
    contributing = sorted(
        {
            tok.lower()
            for tok in TOKEN_RE.findall(original)
            if tok.lower() in retained_term_lexicon(spec)
        }
        | set(phrase_hits)
        | {m for m in masks if re.search(rf"\b{re.escape(m)}\b", original, flags=re.IGNORECASE)}
    )
    return {
        "headline_sentiment": compound,
        "base_aug_compound": base_aug,
        "phrase_adjustment": phrase_adj,
        "contributing_terms": "|".join(contributing),
    }


def coverage_confidence(headline_count: pd.Series, *, cap: float = 5.0) -> pd.Series:
    """Bounded confidence from same-day headline count: 0 -> 0.35, rich coverage -> ~1."""

    counts = headline_count.astype(float).clip(lower=0.0)
    raw = np.log1p(counts) / np.log1p(cap)
    return pd.Series(0.35 + 0.65 * np.clip(raw, 0.0, 1.0), index=headline_count.index)


def attention_confidence(attention_pulse: pd.Series, *, scale: float = 2.0) -> pd.Series:
    """Bounded confidence from elevated Attention Pulse only.

    Abnormally *high* headline volume raises confidence. Abnormally low volume does
    not — depressed attention stays at the neutral floor. Missing pulse (warmup)
    uses 0.70 so the model still runs.
    """

    pulse = attention_pulse.astype(float)
    elevated = np.clip(pulse.fillna(0.0) / scale, 0.0, 1.0)
    conf = 0.55 + 0.45 * elevated
    conf = conf.where(pulse.notna(), 0.70)
    return pd.Series(conf, index=attention_pulse.index)


def score_headlines(
    mapped_headlines: pd.DataFrame,
    *,
    model: str = "signal_harbour",
) -> pd.DataFrame:
    """Score mapped headlines. model in {base_vader, open_source_finvader, signal_harbour}."""

    rows = mapped_headlines.loc[mapped_headlines["trade_date"].notna()].copy()
    titles = rows["title"].astype(str)
    if model == "base_vader":
        analyser = _vader()
        rows["headline_sentiment"] = titles.map(lambda text: score_text_base_vader(text, analyser))
        rows["contributing_terms"] = ""
    elif model in {"week9_finvader", "open_source_finvader"}:
        analyser = build_week9_finvader()
        rows["headline_sentiment"] = titles.map(lambda text: score_text_week9_finvader(text, analyser))
        rows["contributing_terms"] = ""
    elif model == "signal_harbour":
        analyser = build_week9_finvader()
        scored = titles.map(lambda text: score_text_signal_harbour(text, analyser))
        detail = pd.DataFrame(list(scored))
        rows = pd.concat([rows.reset_index(drop=True), detail.reset_index(drop=True)], axis=1)
    else:
        raise ValueError(f"unknown sentiment model: {model}")

    ticker_day = rows.groupby(["trade_date", "ticker", "sector"], observed=True).agg(
        sentiment=("headline_sentiment", "mean"),
        headline_count=("headline_sentiment", "size"),
        contributing_terms=("contributing_terms", lambda values: "|".join(sorted({p for v in values for p in str(v).split("|") if p}))),
    ).reset_index()
    return ticker_day.sort_values(["ticker", "trade_date"]).reset_index(drop=True)


def compare_models_on_headlines(mapped_headlines: pd.DataFrame, sample_n: int = 5000) -> pd.DataFrame:
    """Score a stable sample under all three models for validation tables."""

    rows = mapped_headlines.loc[mapped_headlines["trade_date"].notna()].copy()
    if len(rows) > sample_n:
        rows = rows.sample(sample_n, random_state=5444541)
    rows = rows.sort_values(["trade_date", "ticker"]).reset_index(drop=True)
    analyser = _vader()
    week9 = build_week9_finvader()
    rows["base_vader"] = rows["title"].astype(str).map(lambda t: score_text_base_vader(t, analyser))
    rows["week9_finvader"] = rows["title"].astype(str).map(lambda t: score_text_week9_finvader(t, week9))
    # Keep alias column for any older notes that still look for the old name.
    rows["open_source_finvader"] = rows["week9_finvader"]
    detail = rows["title"].astype(str).map(lambda t: score_text_signal_harbour(t, week9))
    detail_df = pd.DataFrame(list(detail))
    rows["signal_harbour"] = detail_df["headline_sentiment"].to_numpy()
    rows["contributing_terms"] = detail_df["contributing_terms"].to_numpy()
    return rows


def model_comparison_summary(scored_sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model in ["base_vader", "week9_finvader", "signal_harbour"]:
        s = scored_sample[model].astype(float)
        rows.append({
            "model": model,
            "n_headlines": int(s.shape[0]),
            "mean_compound": float(s.mean()),
            "std_compound": float(s.std(ddof=1)),
            "share_positive": float((s > 0.05).mean()),
            "share_neutral": float((s.abs() <= 0.05).mean()),
            "share_negative": float((s < -0.05).mean()),
            "share_exact_zero": float((s == 0.0).mean()),
        })
    return pd.DataFrame(rows)


def sector_sentiment_index(scores: pd.DataFrame, sentiment_col: str = "context_weighted_sentiment") -> pd.DataFrame:
    """Equal-weight ticker-day sentiment within each equity sector."""

    col = sentiment_col if sentiment_col in scores.columns else "sentiment"
    aggregations: dict[str, tuple[str, str]] = {
        "sentiment": (col, "mean"),
        "active_tickers": ("ticker", "nunique"),
        "headline_count": ("headline_count", "sum"),
    }
    if "coverage_confidence" in scores.columns:
        aggregations["mean_coverage_confidence"] = ("coverage_confidence", "mean")
    if "attention_confidence" in scores.columns:
        aggregations["mean_attention_confidence"] = ("attention_confidence", "mean")
    if "attention_pulse" in scores.columns:
        aggregations["mean_attention_pulse"] = ("attention_pulse", "mean")
    out = scores.groupby(["trade_date", "sector"], observed=True).agg(**aggregations).reset_index()
    out = out.sort_values(["sector", "trade_date"]).reset_index(drop=True)
    out["sentiment_lag1"] = out.groupby("sector", observed=True)["sentiment"].shift(1)
    return out


def attach_context_weights(
    scores: pd.DataFrame,
    attention_panel: pd.DataFrame,
) -> pd.DataFrame:
    """Merge Part A Attention Pulse and form lagged context-weighted tradable scores."""

    out = scores.copy()
    pulse = attention_panel[["trade_date", "ticker", "attention_pulse", "article_count"]].drop_duplicates(
        ["trade_date", "ticker"]
    )
    out = out.merge(pulse, on=["trade_date", "ticker"], how="left", validate="one_to_one")
    out["headline_count"] = out["headline_count"].fillna(0).astype("int64")
    out["coverage_confidence"] = coverage_confidence(out["headline_count"])
    out["attention_confidence"] = attention_confidence(out["attention_pulse"])
    out["context_weighted_sentiment"] = (
        out["sentiment"].astype(float)
        * out["coverage_confidence"].astype(float)
        * out["attention_confidence"].astype(float)
    )
    return out.sort_values(["ticker", "trade_date"]).reset_index(drop=True)


def ticker_sentiment_signal(
    scores: pd.DataFrame,
    trading_calendar: pd.Series | pd.DatetimeIndex,
    tickers: list[str],
    *,
    sentiment_col: str = "context_weighted_sentiment",
    sector_map: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Complete ticker-day signal grid; no-news days neutral; lag one trading day before use."""

    calendar = pd.DatetimeIndex(pd.to_datetime(trading_calendar)).drop_duplicates().sort_values()
    grid = pd.MultiIndex.from_product([calendar, tickers], names=["trade_date", "ticker"]).to_frame(index=False)
    cols = [
        "trade_date",
        "ticker",
        "sector",
        "sentiment",
        "headline_count",
        "coverage_confidence",
        "attention_confidence",
        "attention_pulse",
        "context_weighted_sentiment",
        "contributing_terms",
    ]
    available = [c for c in cols if c in scores.columns]
    signal = grid.merge(scores[available], on=["trade_date", "ticker"], how="left")
    if sector_map is not None and {"ticker", "sector"}.issubset(sector_map.columns):
        smap = sector_map.drop_duplicates("ticker").set_index("ticker")["sector"]
        signal["sector"] = signal["sector"].fillna(signal["ticker"].map(smap))
    signal["sentiment"] = signal["sentiment"].fillna(0.0)
    signal["headline_count"] = signal["headline_count"].fillna(0).astype("int64")
    if "coverage_confidence" in signal.columns:
        signal["coverage_confidence"] = signal["coverage_confidence"].fillna(0.35)
    else:
        signal["coverage_confidence"] = coverage_confidence(signal["headline_count"])
    if "attention_confidence" in signal.columns:
        signal["attention_confidence"] = signal["attention_confidence"].fillna(0.70)
    else:
        signal["attention_confidence"] = 0.70
    if "attention_pulse" not in signal.columns:
        signal["attention_pulse"] = np.nan
    if "context_weighted_sentiment" in signal.columns:
        signal["context_weighted_sentiment"] = signal["context_weighted_sentiment"].fillna(0.0)
    else:
        signal["context_weighted_sentiment"] = (
            signal["sentiment"] * signal["coverage_confidence"] * signal["attention_confidence"]
        )
    if "contributing_terms" not in signal.columns:
        signal["contributing_terms"] = ""
    else:
        signal["contributing_terms"] = signal["contributing_terms"].fillna("")

    use_col = sentiment_col if sentiment_col in signal.columns else "sentiment"
    by_ticker = signal.groupby("ticker", observed=True)
    signal["tradable_score"] = by_ticker[use_col].shift(1).fillna(0.0)
    signal["sentiment_lag1"] = signal["tradable_score"]
    signal["signal_date"] = by_ticker["trade_date"].shift(1)
    # Explanatory fields aligned to the signal date that produced today's tradable_score.
    for col in [
        "sentiment",
        "headline_count",
        "coverage_confidence",
        "attention_confidence",
        "attention_pulse",
        "context_weighted_sentiment",
        "contributing_terms",
        "sector",
    ]:
        signal[f"explain_{col}"] = by_ticker[col].shift(1)
    signal["first_usable_trade_date"] = signal["trade_date"]
    return signal.sort_values(["ticker", "trade_date"]).reset_index(drop=True)


def lexicon_audit_table() -> pd.DataFrame:
    spec = load_lexicon_spec()
    rows: list[dict[str, Any]] = []
    for row in spec.get("neutral_overrides", []):
        rows.append({
            "kind": "neutral_override",
            "text": row["text"],
            "valence": "",
            "source": row.get("source", ""),
            "reason": row.get("reason", ""),
            "retained": bool(row.get("retained")),
        })
    for row in spec.get("phrases", []):
        rows.append({
            "kind": "phrase",
            "text": row["text"],
            "valence": row.get("valence", ""),
            "source": row.get("source", ""),
            "reason": row.get("reason", ""),
            "retained": bool(row.get("retained")),
        })
    for row in spec.get("terms", []):
        rows.append({
            "kind": "term",
            "text": row["text"],
            "valence": row.get("valence", ""),
            "source": row.get("source", ""),
            "reason": row.get("reason", ""),
            "retained": bool(row.get("retained")),
        })
    return pd.DataFrame(rows)


def _rule_based_pseudo_label(title: str) -> str:
    """Automated keyword diagnostic only — not a human or Kaiyuan review label.

    Whole-word cues only (so ``cut`` does not match inside ``executive``). Stem
    families are counted once. Ambiguous / cancelling cues default to neutral.
    Never write this into ``kaiyuan_review_label``.
    """

    text = str(title).lower()
    if re.search(r"\b(?:not|fails to)\s+beat\b", text):
        return "negative"

    def _hit(patterns: list[str]) -> bool:
        return any(re.search(rf"\b{p}\b", text) for p in patterns)

    neg_hit = _hit([
        r"falls?", r"fell", r"down", r"miss(?:es|ed)?", r"cuts?", r"plunge[sd]?",
        r"drops?", r"losses?", r"lawsuit", r"fraud", r"probe", r"downgrade[sd]?",
        r"underperform(?:s|ed)?", r"bankrupt(?:cy)?", r"recall", r"slash(?:es|ed)?",
        r"warning", r"declines?", r"slumps?", r"crash(?:es|ed)?", r"investigation",
    ])
    pos_hit = _hit([
        r"beats?", r"surge[sd]?", r"raises?", r"upgrade[sd]?", r"outperform(?:s|ed)?",
        r"buyback", r"repurchase", r"soar(?:s|ed)?", r"rall(?:y|ies)", r"jumps?",
        r"tops estimates", r"raises guidance", r"beats expectations",
    ])
    # "record" alone is ambiguous (record high vs record loss); require a clear partner.
    if re.search(r"\brecord\b", text) and re.search(r"\b(high|profit|growth|beat)\b", text):
        pos_hit = True
    if re.search(r"\brecord\b", text) and re.search(r"\b(loss|low|miss)\b", text):
        neg_hit = True

    if neg_hit and not pos_hit:
        return "negative"
    if pos_hit and not neg_hit:
        return "positive"
    return "neutral"


def build_validation_sample(scored_sample: pd.DataFrame, n: int = 120) -> pd.DataFrame:
    """Stratified model-comparison worksheet for optional student review.

    ``kaiyuan_review_label`` is left blank on purpose. An automated
    ``rule_based_pseudo_label`` column may be attached for diagnostic contrast only;
    it must never be described as human validation.
    """

    df = scored_sample.copy()
    df["year"] = pd.to_datetime(df["trade_date"]).dt.year
    df["base_bucket"] = pd.cut(
        df["base_vader"],
        bins=[-1.01, -0.05, 0.05, 1.01],
        labels=["negative", "neutral", "positive"],
    )
    df["changed"] = (df["signal_harbour"] - df["week9_finvader"]).abs() > 0.05
    parts = []
    for _, group in df.groupby(["sector", "year", "base_bucket"], observed=True):
        take = min(2, len(group))
        if take:
            parts.append(group.sample(take, random_state=5444541))
    changed = df.loc[df["changed"]]
    if not changed.empty:
        parts.append(changed.sample(min(30, len(changed)), random_state=5444541))
    sample = pd.concat(parts, ignore_index=True).drop_duplicates(
        subset=["trade_date", "ticker", "title"]
    )
    if len(sample) > n:
        sample = sample.sample(n, random_state=5444541)
    score_cols = ["base_vader", "week9_finvader", "signal_harbour"]
    if "week9_finvader" not in sample.columns and "open_source_finvader" in sample.columns:
        sample = sample.copy()
        sample["week9_finvader"] = sample["open_source_finvader"]
    out = sample[[
        "trade_date", "ticker", "sector", "title", "year", "base_bucket",
        *score_cols, "contributing_terms", "changed",
    ]].copy()
    out["model_bucket_signal_harbour"] = np.where(
        out["signal_harbour"] > 0.05, "positive",
        np.where(out["signal_harbour"] < -0.05, "negative", "neutral"),
    )
    out["rule_based_pseudo_label"] = out["title"].map(_rule_based_pseudo_label).astype("string")
    # Blank on purpose — do not invent student review labels in code.
    out["kaiyuan_review_label"] = pd.Series([""] * len(out), dtype="string")
    rng = np.random.default_rng(5444541)
    mask = rng.random(len(out)) < 0.70
    out["split"] = np.where(mask, "development", "holdout")
    out["sample_role"] = "model_comparison_worksheet"
    return out.sort_values(["split", "sector", "trade_date"]).reset_index(drop=True)


def pseudo_label_diagnostic_summary(review_sample: pd.DataFrame) -> pd.DataFrame:
    """Agreement of models with the automated keyword pseudo-label (not human truth)."""

    df = review_sample.copy()
    if "rule_based_pseudo_label" not in df.columns:
        df["rule_based_pseudo_label"] = df["title"].map(_rule_based_pseudo_label)
    rows = []
    for model in ["base_vader", "week9_finvader", "signal_harbour"]:
        bucket = np.where(df[model] > 0.05, "positive", np.where(df[model] < -0.05, "negative", "neutral"))
        for split in ["development", "holdout", "all"]:
            part = df if split == "all" else df.loc[df["split"].eq(split)]
            if part.empty:
                continue
            labels = part["rule_based_pseudo_label"].astype(str)
            pred = pd.Series(bucket, index=df.index).loc[part.index]
            rows.append({
                "model": model,
                "split": split,
                "n": int(len(part)),
                "agreement_with_pseudo_label": float((labels.to_numpy() == pred.to_numpy()).mean()),
                "pseudo_negative_share": float(labels.eq("negative").mean()),
                "pseudo_neutral_share": float(labels.eq("neutral").mean()),
                "pseudo_positive_share": float(labels.eq("positive").mean()),
                "label_source": "automated_rule_based_pseudo_label",
            })
    return pd.DataFrame(rows)
