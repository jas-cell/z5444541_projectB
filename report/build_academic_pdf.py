#!/usr/bin/env python3
"""Build a plain academic PDF from the Part B source claims. Numbers locked to source."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from PIL import Image as PILImage
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
FIGDIR = ROOT.parent / "results" / "figures"
PADDED = ROOT / "exhibits_padded"
OUT = ROOT / "report.pdf"
PAD_PX = 8

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#444444")
RULE = colors.HexColor("#222222")
PALE = colors.HexColor("#f4f4f4")
LINE = colors.HexColor("#b0b0b0")


def styles():
    base = getSampleStyleSheet()
    s = {}
    s["title"] = ParagraphStyle(
        "title",
        parent=base["Title"],
        fontName="Times-Bold",
        fontSize=16,
        leading=20,
        textColor=INK,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    s["subtitle"] = ParagraphStyle(
        "subtitle",
        parent=base["Normal"],
        fontName="Times-Italic",
        fontSize=11,
        leading=14,
        textColor=INK,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    s["meta"] = ParagraphStyle(
        "meta",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        leading=13,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=1,
    )
    s["h1"] = ParagraphStyle(
        "h1",
        parent=base["Heading1"],
        fontName="Times-Bold",
        fontSize=13,
        leading=16,
        textColor=INK,
        spaceBefore=14,
        spaceAfter=8,
        borderPadding=0,
    )
    s["h2"] = ParagraphStyle(
        "h2",
        parent=base["Heading2"],
        fontName="Times-Bold",
        fontSize=11.5,
        leading=14,
        textColor=INK,
        spaceBefore=10,
        spaceAfter=6,
    )
    s["body"] = ParagraphStyle(
        "body",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=10.5,
        leading=14.2,
        textColor=INK,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        firstLineIndent=12,
    )
    s["body0"] = ParagraphStyle(
        "body0",
        parent=s["body"],
        firstLineIndent=0,
    )
    s["note"] = ParagraphStyle(
        "note",
        parent=base["Normal"],
        fontName="Times-Italic",
        fontSize=9.5,
        leading=12.5,
        textColor=MUTED,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        spaceBefore=2,
        leftIndent=8,
        rightIndent=8,
    )
    s["caption"] = ParagraphStyle(
        "caption",
        parent=base["Normal"],
        fontName="Times-Italic",
        fontSize=9,
        leading=12,
        textColor=INK,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=12,
    )
    s["th"] = ParagraphStyle(
        "th",
        parent=base["Normal"],
        fontName="Times-Bold",
        fontSize=8,
        leading=10,
        textColor=INK,
        alignment=TA_CENTER,
    )
    s["td"] = ParagraphStyle(
        "td",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=8,
        leading=10,
        textColor=INK,
        alignment=TA_CENTER,
    )
    s["tdl"] = ParagraphStyle(
        "tdl",
        parent=s["td"],
        alignment=TA_LEFT,
    )
    s["eq"] = ParagraphStyle(
        "eq",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        leading=15,
        textColor=INK,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=4,
    )
    s["eqnote"] = ParagraphStyle(
        "eqnote",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=9.5,
        leading=12.5,
        textColor=INK,
        alignment=TA_LEFT,
        spaceAfter=8,
        leftIndent=18,
    )
    s["ref"] = ParagraphStyle(
        "ref",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=9.5,
        leading=13,
        textColor=INK,
        leftIndent=14,
        firstLineIndent=-14,
        spaceAfter=5,
    )
    s["footer"] = ParagraphStyle(
        "footer",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=8,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
    return s


S = styles()


def P(text, style="body"):
    return Paragraph(text, S[style])


def tbl(headers, rows, col_widths=None):
    head = [Paragraph(h, S["th"]) for h in headers]
    data = [head]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            st = S["tdl"] if i == 0 else S["td"]
            cells.append(Paragraph(str(cell), st))
        data.append(cells)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("BACKGROUND", (0, 0), (-1, 0), PALE),
                ("TEXTCOLOR", (0, 0), (-1, -1), INK),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def pad_figure(src: Path) -> Path:
    """Add white padding so axis titles are not flush with the page edge."""
    PADDED.mkdir(exist_ok=True)
    dest = PADDED / src.name
    im = PILImage.open(src).convert("RGBA")
    bg = PILImage.new("RGB", (im.width + 2 * PAD_PX, im.height + 2 * PAD_PX), "white")
    bg.paste(im, (PAD_PX, PAD_PX), im)
    bg.save(dest, "PNG")
    return dest


def fig(src_name: str, caption: str, *, reserved_top_mm: float = 0.0, center: bool = False):
    """One readable figure: original PNG, fitted inside the text frame, not stretched."""
    padded = pad_figure(FIGDIR / src_name)
    img = Image(str(padded))
    max_w = 158 * mm
    max_h = 192 * mm
    native_w = float(img.imageWidth)
    native_h = float(img.imageHeight)
    scale = min(max_w / native_w, max_h / native_h)
    img.drawWidth = native_w * scale
    img.drawHeight = native_h * scale
    img.hAlign = "CENTER"
    cell = Table([[img]], colWidths=[158 * mm])
    cell.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    inner = Table([[cell], [P(caption, "caption")]], colWidths=[158 * mm])
    inner.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    if not center:
        return inner
    n_lines = max(2, (len(caption) // 92) + 1)
    caption_h = n_lines * 12 + 18
    content_h = img.drawHeight + 10 + caption_h
    frame_h = 232 * mm - reserved_top_mm * mm
    if frame_h - content_h < 12 * mm:
        return inner
    wrapper = Table([[inner]], colWidths=[158 * mm], rowHeights=[frame_h])
    wrapper.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return wrapper


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(doc.leftMargin, A4[1] - 14 * mm, A4[0] - doc.rightMargin, A4[1] - 14 * mm)
    canvas.setFont("Times-Italic", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, A4[1] - 12 * mm, "Kaiyuan Lan (z5444541)  |  FINS3645 Project B")
    canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 12 * mm, "Signal Harbour")
    canvas.line(doc.leftMargin, 12 * mm, A4[0] - doc.rightMargin, 12 * mm)
    canvas.drawCentredString(A4[0] / 2, 8 * mm, str(doc.page))
    canvas.restoreState()


def story():
    w = 6.5 * inch
    c6 = [1.55 * inch] + [0.99 * inch] * 5
    c5 = [1.7 * inch] + [1.2 * inch] * 4
    c2 = [2.4 * inch, 4.1 * inch]
    flow = []

    flow.append(P("Signal Harbour", "title"))
    flow.append(
        P(
            "Systematic multi-asset funds, a sector news-sentiment index, and a Streamlit research app",
            "subtitle",
        )
    )
    flow.append(P("FINS3645 Project B", "meta"))
    flow.append(P("Kaiyuan Lan (z5444541)", "meta"))
    flow.append(P("Sample through December 2023", "meta"))
    flow.append(Spacer(1, 10))

    # --- 1 ---
    flow.append(P("1. Customer, data, and backtest design", "h1"))
    flow.append(
        P(
            "Signal Harbour is a research product for a small wealth-advisory firm. The day-to-day user is a "
            "portfolio analyst who needs comparable walk-forward evidence before an investment-committee "
            "discussion (Hutto and Gilbert, 2014, supply the baseline sentiment tool the course builds on). "
            "The menu covers Equity, Crypto, and Combined sleeves. Each sleeve is evaluated with equal weight, "
            "minimum variance, maximum Sharpe, and risk parity (Markowitz, 1952).",
            "body0",
        )
    )
    flow.append(
        P(
            "Prices are adjusted-close simple returns within ticker. Equity and Combined sleeves use a "
            "252-session estimation window and 252-day annualisation. Crypto sleeves use a 365-day native "
            "window. Crypto returns are computed on the native calendar and only then left-aligned onto equity "
            "dates for Combined funds. That order keeps weekend compounding from being invented or deleted "
            "in the merge."
        )
    )
    flow.append(
        P(
            "On monthly decision date <i>T</i>, target weights use returns strictly before <i>T</i>. Those "
            "targets become effective on the next session; the close-to-close return on <i>T</i> still uses "
            "prior holdings. Between rebalances, holdings drift with relative performance. Optimisation is "
            "long-only, with a 25% name cap in the broad sleeves. Covariance is annualised inside the solver. "
            "A candidate solution is kept only when it improves on equal weight."
        )
    )
    flow.append(P("Backtest conventions", "h2"))
    flow.append(
        P(
            "The risk-free rate is zero in the Maximum Sharpe objective and in every reported Sharpe ratio. "
            "Headline fund results assume zero trading costs. Table 5 applies the same turnover-cost stresses "
            "to the MinVar base and the sentiment-fusion sleeve. The Streamlit application reads precomputed "
            "CSV files. It does not re-run VADER, rebuild the sentiment series, or execute backtests at runtime."
        )
    )
    flow.append(P("First-live timing", "h2"))
    flow.append(
        P(
            "The decision date and the first earning date are not the same under this convention. After the "
            "252-session warm-up, the first Equity and Combined decision date is 4 January 2021; those targets "
            "first earn a return on 5 January 2021. On the native crypto calendar, the first decision date is "
            "1 January 2021 and the first live return is 2 January 2021. These are the starting dates of the "
            "out-of-sample paths in Figure A1, not the start of the raw price histories."
        )
    )
    flow.append(P("Why timing and drift are specified this way", "h2"))
    flow.append(
        P(
            "A desk that forms weights after the close cannot book the full close-to-close return on <i>T</i> "
            "as if the new book had already been traded at the previous close. Assigning <i>T</i> to the old "
            "holdings and switching on the next session is the conservative sequence, and it is reproducible."
        )
    )
    flow.append(
        P(
            "Drift is a separate issue. A strategy described as monthly rebalancing is not monthly if it is "
            "reset to target weights every day. Letting prices move the holdings, then measuring turnover "
            "against those drifted weights, keeps the wealth path and the cost exercise aligned. Annualising "
            "covariance inside the optimiser, and rejecting solutions that fail to beat equal weight, also "
            "responds to the project brief: SLSQP can report success without leaving its starting vector when "
            "daily variances are small. In the retained Equity sample, Minimum Variance differs from Equal "
            "Weight at every monthly decision. The mean half-L1 distance is about 0.72. That check shows the "
            "optimisation actually moved the weights."
        )
    )

    # --- 2 ---
    flow.append(P("2. Out-of-sample fund results", "h1"))
    flow.append(
        P(
            "Table 1 and Figure A1 report the full fund menu. Among mixed-asset portfolios, Combined Risk "
            "Parity has the highest zero-risk-free-rate Sharpe ratio, 0.91. CAGR is 14.3%, volatility is 16.2%, "
            "and maximum drawdown is -19.3% (Figures A2 and A4). Combined Maximum Sharpe finishes with slightly "
            "more wealth (1.55x and a 15.7% CAGR), but its drawdown reaches -26.2%. These are research paths "
            "under the stated assumptions.",
            "body0",
        )
    )
    flow.append(P("How to read the mixed-asset ranking", "h2"))
    flow.append(
        P(
            "The mixed result is mainly about diversification under a calendar a desk can actually trade. A "
            "stand-alone crypto portfolio compounds through weekends because it is evaluated on 365 native days. "
            "In the Combined backtest, crypto returns are aligned to equity sessions, so the mixed desk earns "
            "that leg only when the equity book can also be traded. Under that constraint, Risk Parity repeatedly "
            "cuts exposure to the most volatile names in the trailing covariance estimate. It does so without "
            "forecasting expected returns."
        )
    )
    flow.append(
        P(
            "Maximum Sharpe has a heavier estimation burden because it must estimate means as well as covariance. "
            "Over a three-year live window, noisy means encourage larger bets. That shows up in the deeper "
            "drawdown and in the concentrated December 2023 snapshot in Table 3. For a small advisory firm the "
            "distinction is practical. Combined Risk Parity is the stronger default comparison. Combined Maximum "
            "Sharpe belongs in a satellite discussion with clients who accept concentration and drawdown risk."
        )
    )
    flow.append(P("Equity and crypto sleeves", "h2"))
    flow.append(
        P(
            "On equities, Equal Weight leads with a Sharpe ratio of 0.86. Risk Parity reaches 0.76, ahead of "
            "Minimum Variance at 0.47, but it still does not displace the transparent baseline. Optimisation is "
            "not pointless for that reason. Once the walk-forward rule is imposed, this sample did not pay enough "
            "for the extra estimation to beat Equal Weight. Minimum Variance does not forecast expected returns, "
            "so its weaker realised Sharpe is more plausibly linked to unstable covariance estimates and binding "
            "caps than to mean estimation."
        )
    )
    flow.append(
        P(
            "Crypto Minimum Variance is the strongest crypto sleeve, with a 1.04 Sharpe ratio and a 62.1% CAGR. "
            "Crypto Maximum Sharpe is why CAGR and Sharpe are kept separate in this report: CAGR is -2.7%, even "
            "though the annualised arithmetic mean-to-volatility ratio remains positive at 0.35."
        )
    )

    flow.append(
        P(
            "Table 1. Out-of-sample performance. CAGR is the annualised return from the growth-of-one path. "
            "Sharpe is annualised arithmetic mean divided by annualised volatility, risk-free rate zero. "
            "Equity-calendar funds use 252 days; native crypto funds use 365. Source: <i>performance_metrics.csv</i>. "
            "See Figures A1 and A4.",
            "caption",
        )
    )
    flow.append(
        tbl(
            ["Fund", "CAGR", "Vol.", "Sharpe", "MaxDD", "Terminal"],
            [
                ["Eq EW", "13.3%", "16.1%", "0.86", "-20.2%", "1.45x"],
                ["Eq MinVar", "5.4%", "12.7%", "0.47", "-14.9%", "1.17x"],
                ["Eq MaxSharpe", "7.0%", "17.5%", "0.48", "-22.8%", "1.22x"],
                ["Eq RP", "10.4%", "14.5%", "0.76", "-18.4%", "1.34x"],
                ["Cry EW", "37.1%", "81.7%", "0.80", "-81.7%", "2.58x"],
                ["Cry MinVar", "62.1%", "71.2%", "1.04", "-71.5%", "4.25x"],
                ["Cry MaxSharpe", "-2.7%", "76.2%", "0.35", "-85.6%", "0.92x"],
                ["Cry RP", "41.0%", "79.7%", "0.83", "-80.1%", "2.80x"],
                ["Comb EW", "15.5%", "21.5%", "0.78", "-27.7%", "1.54x"],
                ["Comb MinVar", "5.4%", "12.8%", "0.48", "-15.1%", "1.17x"],
                ["Comb MaxSharpe", "15.7%", "23.3%", "0.74", "-26.2%", "1.55x"],
                ["Comb RP", "14.3%", "16.2%", "0.91", "-19.3%", "1.49x"],
                ["Eq MinVar+Sent", "5.3%", "12.7%", "0.47", "-14.9%", "1.17x"],
            ],
            c6,
        )
    )
    flow.append(Spacer(1, 8))

    flow.append(P("Concentration and the Combined sleeve", "h2"))
    flow.append(
        P(
            "Figure A3 follows the decision weights of Combined Minimum Variance and Risk Parity, with an Other "
            "residual so that each area sums to one. Risk Parity stays more dispersed, which matches the shallower "
            "drawdown in Figure A2. Minimum Variance is willing to cluster in names that look low-volatility in "
            "the trailing covariance matrix. That is coherent with its objective. It can still become a problem "
            "when the selected cluster later weakens."
        )
    )
    flow.append(
        P(
            "Across families, the Combined sleeve tempers crypto-native volatility while keeping exposure to both "
            "asset classes. Crypto Equal Weight and Crypto Risk Parity reach high terminal growth, but their "
            "drawdowns remain extreme. The -2.7% CAGR and positive 0.35 Sharpe for Crypto Maximum Sharpe also "
            "warn against reading one metric in isolation. Once the mixed fund is evaluated on the equity calendar, "
            "Combined Risk Parity, rather than the best pure-crypto result, is the more usable default for a "
            "mixed-client conversation."
        )
    )

    flow.append(
        P(
            "Table 2. Latest Combined Risk Parity decision weights, top five. Source: <i>latest_holdings_snapshot.csv</i>.",
            "caption",
        )
    )
    flow.append(
        tbl(
            ["Ticker", "Weight"],
            [["MRK", "3.81%"], ["ABBV", "3.74%"], ["WMT", "3.37%"], ["KO", "3.19%"], ["TMUS", "3.17%"]],
            c2,
        )
    )
    flow.append(Spacer(1, 6))
    flow.append(
        P(
            "Table 3. Latest Combined Maximum Sharpe decision weights, top five. Source: <i>latest_holdings_snapshot.csv</i>.",
            "caption",
        )
    )
    flow.append(
        tbl(
            ["Ticker", "Weight"],
            [["GE", "25.00%"], ["NVDA", "20.09%"], ["SO", "16.86%"], ["ADBE", "10.32%"], ["BTC-USD", "10.29%"]],
            c2,
        )
    )
    flow.append(
        P(
            "These tables are end-of-sample snapshots. They describe concentration at the final decision date, "
            "not the full path from 2021 to 2023. A large December 2023 weight cannot be used as an ex-post "
            "explanation for performance earlier in the sample.",
            "note",
        )
    )

    # --- 3 ---
    flow.append(P("3. Sentiment model, sector index, and fusion", "h1"))
    flow.append(
        P(
            "Part B keeps the headline-processing rules from Part A: ticker-date-title duplicates are removed, "
            "and each headline is mapped to the same or next equity session. Base VADER and the Week 9 finVADER "
            "analyser are then re-scored without alteration for comparison. The Week 9 benchmark combines NLTK "
            "VADER, SentiBigNomics scaled by 0.1, and the Henry lexicon, matching the course helper and Korab’s "
            "FinVADER resources. Loughran and McDonald (2011) give the wider rationale for finance-specific dictionaries.",
            "body0",
        )
    )
    flow.append(
        P(
            "Signal Harbour starts from that Week 9 base and adds documented masks, finance terms, and "
            "negation-aware phrases. The resulting score is multiplied by coverage confidence and by the elevated "
            "Attention Pulse confidence developed in Part A. Abnormally low headline volume never raises confidence. "
            "Missing ticker-days are inserted as neutral on a complete equity ticker-day grid before sector "
            "aggregation. The sector index in Figure A5 and the tradable signal therefore share the same no-news "
            "convention. Any score used in a portfolio is lagged by one equity session."
        )
    )
    flow.append(P("The sector index as an economic series", "h2"))
    flow.append(
        P(
            "Figure A5 is a delayed description of the news climate. It is not a stand-alone timing rule. "
            "Context-weighted sector means are mildly positive over 2020 to 2023, but their ordering moves with "
            "the macro cycle. During the February to April 2020 COVID stress window, Energy is the weakest sector "
            "at about 0.005, while Technology and Real Estate are closer to 0.05. That pattern is consistent with "
            "an energy-demand shock and comparatively resilient digital and property-related language in the "
            "supplied corpus. It is not a statement about realised sector returns."
        )
    )
    flow.append(
        P(
            "The ranking changes in 2022. Energy becomes the strongest sector on the index at roughly 0.061, "
            "while Materials and Communications sit near the bottom, around 0.023 to 0.030. A year dominated by "
            "inflation, energy cash flows, and supply concerns makes that ordering economically plausible. "
            "Healthcare rises from about 0.036 in 2021 to 0.053 in 2023. Technology recovers from 0.033 in 2022 "
            "to 0.051 in 2023."
        )
    )
    flow.append(
        P(
            "Coverage is not uniform. Technology and Consumer average more than five headlines on news-bearing "
            "ticker-days; Materials and Real Estate are nearer two and have larger exact-zero raw-score shares "
            "(Figure A11). Context weighting therefore discounts sparse observations rather than treating every "
            "sector as equally well measured. Communications stays in a relatively narrow 0.027 to 0.038 range across "
            "2020 to 2023. Energy moves from 0.017 in 2020 to 0.061 in 2022 before easing to 0.041 in 2023. Consumer "
            "remains roughly between 0.037 and 0.045. Neutral filling compresses the index level, so the useful "
            "information is mainly in relative movement across sectors and years. Figure A11 is the coverage check "
            "for whether a move reflects dense headline flow or a thin signal."
        )
    )
    flow.append(P("Continuity with Part A", "h2"))
    flow.append(
        P(
            "Two design choices keep continuity with Part A. First, Attention Pulse remains a volume-confidence "
            "feature. It was descriptive in Part A and is not converted here into a contemporaneous trading trigger. "
            "Using only its elevated-volume confidence keeps the construction past-looking, without reversing the "
            "earlier claim that the pulse itself was not backtested alpha."
        )
    )
    flow.append(
        P(
            "Second, the phrase and lexicon layer is recorded in the audit material rather than hidden inside a "
            "package label. The Week 9 FinVADER lexicons are vendored with Apache-2.0 notices. Signal Harbour’s "
            "own terms, phrases, and masks are identified separately. Without that record, calling the model "
            "“augmented finVADER” would say very little about what actually changed."
        )
    )
    flow.append(P("Distributional model comparison", "h2"))
    flow.append(
        P(
            "Table 4 and Figure A8 compare polarity shares across a 4,000-headline sample. A lower neutral share "
            "is only a distributional observation. It is not evidence of better prediction. I labelled the "
            "120-headline worksheet myself. Signal Harbour buckets agree with those labels on 60.8% of the full "
            "sample (56.0% development, 68.9% holdout; n=120). The automated pseudo-label "
            "field is not treated as ground truth. Figure A9 therefore looks at component effects through ablation "
            "on the Week 9 analyser rather than reporting labelled precision or recall. On the 800-headline ablation "
            "sample, removing neutral overrides has no effect: <i>no_neutral_overrides</i> matches "
            "<i>full_signal_harbour</i> because the retained masks rarely fire. The components that visibly move "
            "the neutral share are custom terms and phrases. Figure A10 reports active ticker counts. Figure A11 "
            "is the separate coverage-intensity exhibit."
        )
    )
    flow.append(
        P(
            "Table 4. Model polarity shares on 4,000 headlines. The comparison is distributional only. "
            "Source: <i>sentiment_model_comparison.csv</i>; Figure A8.",
            "caption",
        )
    )
    flow.append(
        tbl(
            ["Model", "Mean", "Positive", "Neutral", "Negative"],
            [
                ["Base VADER", "0.106", "37.5%", "49.6%", "12.9%"],
                ["Week 9 finVADER", "0.069", "26.6%", "62.1%", "11.3%"],
                ["Signal Harbour", "0.081", "29.8%", "58.7%", "11.6%"],
            ],
            c5,
        )
    )
    flow.append(Spacer(1, 8))

    flow.append(P("Fusion result", "h2"))
    flow.append(
        P(
            "The main fusion test applies the lagged context-weighted score to Equity Minimum Variance. Figure A6 "
            "shows that the two wealth paths are almost indistinguishable, but the overlay is slightly worse: the "
            "zero-risk-free-rate Sharpe ratio falls from 0.4740 to 0.4711 and CAGR from 5.36% to 5.32%. Figure A7 "
            "and Table 6 extend the stress across tilt strengths and base portfolios. None of the tested "
            "specifications overtakes Equity Equal Weight. Table 5 then applies the same turnover-cost assumptions "
            "to the MinVar base and the fusion sleeve. Even modest costs preserve, and slightly widen, the "
            "disadvantage of the overlay. What remains usable is a continuous, look-ahead-safe monitoring pipeline. "
            "It is not a marketed alpha claim."
        )
    )
    flow.append(
        P(
            "Table 5. Base versus fusion under equal turnover costs. TO is average annual turnover. "
            "Source: <i>fusion_cost_sensitivity.csv</i>.",
            "caption",
        )
    )
    flow.append(
        tbl(
            ["Sleeve", "Cost", "Sharpe", "CAGR", "TO", "Terminal"],
            [
                ["Base", "0 bp", "0.474", "5.36%", "1.90", "1.169x"],
                ["Fusion", "0 bp", "0.471", "5.32%", "1.91", "1.167x"],
                ["Base", "5 bp", "0.467", "5.26%", "1.90", "1.165x"],
                ["Fusion", "5 bp", "0.464", "5.22%", "1.91", "1.164x"],
                ["Base", "10 bp", "0.459", "5.16%", "1.90", "1.162x"],
                ["Fusion", "10 bp", "0.456", "5.12%", "1.91", "1.161x"],
                ["Base", "25 bp", "0.437", "4.86%", "1.90", "1.152x"],
                ["Fusion", "25 bp", "0.434", "4.82%", "1.91", "1.151x"],
            ],
            c6,
        )
    )
    flow.append(Spacer(1, 6))
    flow.append(
        P(
            "Table 6. Fusion robustness across equity bases and tilt strengths at zero cost. "
            "Source: <i>fusion_sensitivity.csv</i>; Figure A7.",
            "caption",
        )
    )
    flow.append(
        tbl(
            ["Base", "Tilt", "CAGR", "Sharpe", "MaxDD"],
            [
                ["EW", "0.15", "13.24%", "0.853", "-20.2%"],
                ["EW", "0.35", "13.17%", "0.849", "-20.2%"],
                ["EW", "0.60", "13.08%", "0.845", "-20.3%"],
                ["RP", "0.15", "10.39%", "0.753", "-18.4%"],
                ["RP", "0.35", "10.34%", "0.751", "-18.4%"],
                ["RP", "0.60", "10.29%", "0.748", "-18.5%"],
                ["MinVar", "0.15", "5.34%", "0.473", "-14.9%"],
                ["MinVar", "0.35", "5.32%", "0.471", "-14.9%"],
                ["MinVar", "0.60", "5.29%", "0.469", "-14.9%"],
            ],
            c5,
        )
    )
    flow.append(Spacer(1, 8))
    flow.append(
        P(
            "The negative fusion result does not mean finance-aware sentiment has no research value. Table 4 and "
            "Figures A8 and A9 show that Week 9 finVADER and Signal Harbour redistribute polarity mass relative to "
            "social-media VADER, and the Explain view can identify the terms and confidence weights behind a lagged "
            "score. The narrower conclusion is that, in this 2021 to 2023 equity sample, a multiplicative portfolio "
            "tilt was not rewarded after the one-session lag. That outcome is consistent with headline tone being "
            "partly contemporaneous with price information already present in the estimation window, and with the "
            "lag removing the most mechanical portion of any apparent edge. Repeating the test on Equal Weight and "
            "Risk Parity bases also shows that the result is not merely an artefact of a damaged MinVar path. "
            "Recommendation 3 follows from that: keep sentiment for monitoring and explanation, and do not present "
            "it as an independent return engine."
        )
    )

    # --- 4 ---
    flow.append(P("4. The Signal Harbour application", "h1"))
    flow.append(
        P(
            "The application follows the analyst’s pre-committee workflow. Each tab answers a different question "
            "using precomputed research files, which keeps the free-tier deployment light and makes the displayed "
            "evidence reproducible.",
            "body0",
        )
    )
    flow.append(
        P(
            "<b>Compare.</b> Rank sleeves by zero-risk-free-rate Sharpe and terminal growth, then plot a shortlist "
            "of wealth paths from the research sample through December 2023."
        )
    )
    flow.append(
        P(
            "<b>Fact sheet.</b> Inspect one fund at a time: CAGR, volatility, Sharpe, drawdown, and the latest "
            "decision weights. A residual is stated whenever only the top holdings are displayed."
        )
    )
    flow.append(
        P(
            "<b>Allocate.</b> Combine completed fund return streams without re-optimising names. Equity-only blends "
            "use intersecting equity sessions; blends containing crypto use the native union calendar."
        )
    )
    flow.append(
        P(
            "<b>Sentiment and Explain.</b> Review the sector news climate, model comparisons, coverage diagnostics, "
            "and the prior-session fields that produced the lagged tradable score. Headlines are not re-scored live."
        )
    )
    flow.append(P("Calendar treatment in Allocate", "h2"))
    flow.append(
        P(
            "Allocate uses a different calendar rule from the Combined-fund backtest because it mixes already-built "
            "return streams rather than re-optimising the underlying names. Any selection containing a Crypto fund "
            "uses the native union calendar, annualises at 365 days, and records zero for a closed equity leg. "
            "Equity-only blends remain on intersecting equity sessions and use 252-day annualisation. A 60/40 "
            "equity-crypto research allocation can therefore retain crypto weekend returns instead of silently "
            "dropping Saturdays."
        )
    )
    flow.append(
        P(
            "A few product choices are worth stating because they affect what a user actually sees. The light theme "
            "is pinned so a dark-mode browser cannot place white headings on a pale custom background. Allocate does "
            "not imply that a crypto sleeve exists only on equity-open dates. Explain displays the signal-date fields "
            "that entered the one-session lag; same-day headlines are not paired with yesterday’s tradable score. "
            "The fact sheet states the residual weight whenever the top-20 table is not the complete portfolio."
        )
    )
    flow.append(
        P(
            "For the advisory firm described in Part A, the interface maps onto a short meeting sequence. Begin with "
            "Combined Risk Parity and its drawdown profile (Recommendation 1; Sharpe 0.91). Introduce Combined "
            "Maximum Sharpe only when a client asks for more growth and accepts a deeper loss profile "
            "(Recommendation 2). Open Explain when the committee wants news-context colour, with Recommendation 3 "
            "already setting the boundary: sentiment is a monitoring layer, not a trading engine. If Energy’s "
            "stronger 2022 news-climate reading is questioned, the answer is in Section 3. Every series is labelled "
            "as an out-of-sample research path through December 2023 rather than as a live production feed."
        )
    )

    # --- 5 ---
    flow.append(P("5. Recommendations", "h1"))
    flow.append(
        P(
            "The three recommendations below are taken from the verified tables and exhibits.",
            "body0",
        )
    )
    flow.append(
        P(
            "<b>1. Default mixed sleeve.</b> Use Combined Risk Parity as the primary balanced multi-asset comparison "
            "within this sample. Its zero-risk-free-rate Sharpe ratio is 0.91 and its maximum drawdown is -19.3% "
            "(Table 1; Figures A1, A2 and A4)."
        )
    )
    flow.append(
        P(
            "<b>2. Satellite growth sleeve.</b> Keep Combined Maximum Sharpe as an optional higher-growth alternative "
            "rather than the default. Terminal wealth reaches 1.55x, but maximum drawdown deepens to -26.2% and the "
            "latest holdings are more concentrated (Tables 1 and 3; Figure A3)."
        )
    )
    flow.append(
        P(
            "<b>3. Sentiment as monitoring, not alpha.</b> Retain the lagged context-weighted layer in the "
            "explainability workflow, but do not market it as a return engine. Relative to Equity MinVar, Sharpe "
            "moves from 0.4740 to 0.4711 and deteriorates further under equal cost assumptions (Figure A6; Tables 5 and 6)."
        )
    )

    # --- 6 ---
    flow.append(P("6. Critical reflection and limits", "h1"))
    flow.append(
        P(
            "Several choices make the study internally consistent and, at the same time, narrow what can be claimed "
            "from it.",
            "body0",
        )
    )
    flow.append(
        P(
            "<b>Short live window.</b> Equity and Combined returns run from 5 January 2021 to December 2023. The "
            "rankings are therefore exposed to the COVID recovery, the 2022 inflation and rate shock, and the 2023 "
            "equity rebound. A longer sample could reorder Equal Weight and Risk Parity."
        )
    )
    flow.append(
        P(
            "<b>Headline results exclude costs.</b> Table 1 is a zero-cost laboratory. Table 5 shows that even 5 to 25 "
            "basis points per unit of turnover reduce the fusion result. Applying the same grid to every fund would "
            "probably narrow the gap between higher-turnover Maximum Sharpe paths and lower-turnover Risk Parity."
        )
    )
    flow.append(
        P(
            "<b>Uneven news coverage.</b> Materials and Real Estate have thinner headline intensity and larger "
            "exact-zero raw-score shares than Technology or Consumer (Figure A11). Their sector readings require "
            "greater caution."
        )
    )
    flow.append(
        P(
            "<b>Labelled sentiment evidence is a small worksheet, not a precision claim.</b> I labelled all 120 "
            "headlines in <i>kaiyuan_review_label</i>. Agreement with Signal Harbour buckets is 60.8% on that sheet "
            "(headline_kaiyuan_label_agreement.csv). That is a polarity-match rate on n=120, not labelled "
            "precision or recall."
        )
    )
    flow.append(
        P(
            "<b>End-point holdings are not path explanations.</b> The December 2023 snapshots in Tables 2 and 3 describe "
            "concentration at the last decision date. They cannot explain the complete 2021 to 2023 wealth path."
        )
    )
    flow.append(P("Product-level reflection", "h2"))
    flow.append(
        P(
            "Building Signal Harbour on the actual Week 9 analyser was a stronger continuity choice than attaching "
            "a few finance terms to plain VADER. The report records the provenance of both the course lexicons and "
            "the project-specific additions, and the application is explicit that it reads precomputed files rather "
            "than re-scoring headlines at runtime. Under those conditions, credibility comes from design quality, "
            "auditability, and restrained claims, not from the appearance of a live model."
        )
    )
    flow.append(
        P(
            "If I extended the project, I would make three changes. First, I would apply the turnover-cost grid "
            "from Table 5 to every fund family so that Recommendation 1 is tested under the same frictions. "
            "Second, I would expand the labelled worksheet beyond n=120 before treating polarity agreement as a "
            "model-selection statistic. Third, I would publish "
            "the public GitHub repository and Streamlit deployment, then resolve any remaining theme issues before "
            "submission. Those steps would improve validation and delivery. They would not alter the central result "
            "that the sentiment overlay is economically flat to negative in this sample."
        )
    )
    flow.append(P("What out-of-sample means here", "h2"))
    flow.append(
        P(
            "The fund weights are walk-forward and use only past returns, and the tradable sentiment input is delayed "
            "by one equity session. The research choices around lexicon retention, tilt strength, and the base sleeve "
            "receiving the overlay were nevertheless made with knowledge of the full study period. That is a normal "
            "limitation in a fixed-sample coursework project. The negative fusion result should therefore be read as "
            "a stress test of one pre-specified overlay design, not as proof that every possible news rule failed "
            "under a sealed holdout. The development-holdout split in the headline worksheet offers partial discipline "
            "for labelling work, but it is not a complete untouched test set."
        )
    )
    flow.append(
        P(
            "Signal Harbour gives a small advisory desk a coherent menu of systematic funds, a lagged sector "
            "news-climate monitor linked to Part A, and an auditable explanation for why a name was tilted. It should "
            "not claim that the tilt paid in this sample, and it should not hide the calendar, cost, or coverage "
            "frictions that an investment committee would reasonably raise. Remaining packaging work is operational: "
            "keep the light theme pinned and verify that the live URL matches the version described here."
        )
    )

    # Appendix A
    flow.append(PageBreak())
    flow.append(P("Appendix A. Exhibits", "h1"))
    flow.append(
        P(
            "Each exhibit is discussed in Sections 2 to 4. Captions restate the sample, source, and the claim the "
            "figure is meant to support.",
            "body0",
        )
    )
    flow.append(Spacer(1, 8))
    exhibits = [
        (
            "growth_of_one_dollar.png",
            "Figure A1. Growth of $1 across funds, out-of-sample through December 2023. Combined Risk Parity is "
            "steadier than Combined Maximum Sharpe; Crypto Minimum Variance leads terminal wealth among the crypto "
            "sleeves. Source: fund_returns.csv.",
        ),
        (
            "combined_drawdowns.png",
            "Figure A2. Combined-fund drawdowns. Risk Parity has the shallower path, supporting Recommendation 1; "
            "Maximum Sharpe reaches the deeper trough expected of the higher-growth satellite. Wealth paths prepend "
            "1.0 so that the first loss is visible.",
        ),
        (
            "combined_weights_over_time.png",
            "Figure A3. Combined Minimum Variance and Risk Parity decision weights, with an Other residual so the "
            "stacked areas sum to one. Maximum Sharpe concentration is summarised in Table 3 rather than in this panel.",
        ),
        (
            "fund_sharpe_barplot.png",
            "Figure A4. Zero-risk-free-rate Sharpe rankings. Combined Risk Parity leads the mixed sleeves; Equity "
            "Equal Weight leads equities; Crypto Minimum Variance leads crypto. Annualisation is 252 or 365 days by sleeve.",
        ),
        (
            "sector_sentiment_index.png",
            "Figure A5. Context-weighted sector sentiment, shown as a 21-session average. The series uses the complete "
            "ticker-day grid, sets no-news observations to neutral, and is lagged before any trading use.",
        ),
        (
            "fusion_before_after.png",
            "Figure A6. Equity Minimum Variance against the lagged context-weighted sentiment tilt. The overlay does "
            "not improve the corrected baseline, which supports Recommendation 3.",
        ),
        (
            "fusion_sensitivity.png",
            "Figure A7. Fusion sensitivity by tilt strength and equity base at zero cost. None of the tested "
            "specifications overtakes Equity Equal Weight (Table 6).",
        ),
        (
            "sentiment_model_comparison.png",
            "Figure A8. Polarity shares for Base VADER, Week 9 finVADER, and Signal Harbour on 4,000 headlines "
            "(Table 4). The comparison is distributional only.",
        ),
        (
            "innovation_ablation.png",
            "Figure A9. Ablation of Signal Harbour components on the Week 9 finVADER base analyser, with Week 9-only "
            "and plain-VADER references.",
        ),
        (
            "context_weighted_sector_sentiment.png",
            "Figure A10. Average active tickers per sector-day under the complete-grid context-weighted index. This "
            "is the coverage companion to Figure A5.",
        ),
        (
            "sentiment_coverage_neutrality.png",
            "Figure A11. Sector coverage intensity: mean headlines on news-bearing ticker-days (bars) and the share "
            "of exact-zero raw scores (line). This exhibit is distinct from the polarity comparison in Figure A8.",
        ),
    ]
    for i, (fname, cap) in enumerate(exhibits):
        if i > 0:
            flow.append(PageBreak())
            flow.append(Spacer(1, 8))
        reserved = 36.0 if i == 0 else 0.0
        flow.append(fig(fname, cap, reserved_top_mm=reserved))

    # Appendix B
    flow.append(PageBreak())
    flow.append(P("Appendix B. Core equations and references", "h1"))
    flow.append(P("Minimum variance", "h2"))
    flow.append(
        P(
            "minimise  w^T SigmaAnn w    subject to    1^T w = 1    and    0 &lt;= w(i) &lt;= wMax",
            "eq",
        )
    )
    flow.append(
        P(
            "SigmaAnn = ppy * Cov(R), where ppy is 252 on the equity calendar or 365 on the native crypto calendar.",
            "eqnote",
        )
    )
    flow.append(P("Maximum Sharpe", "h2"))
    flow.append(P("maximise  (w^T muAnn) / sqrt(w^T SigmaAnn w)", "eq"))
    flow.append(
        P(
            "The risk-free rate is zero; the long-only and name-cap constraints are unchanged.",
            "eqnote",
        )
    )
    flow.append(P("Reported performance", "h2"))
    flow.append(P("Sharpe = (mean(r) * ppy) / (std(r) * sqrt(ppy))", "eq"))
    flow.append(P("CAGR = WT raised to the power (ppy/T), minus 1", "eq"))
    flow.append(P("Context-weighted score", "h2"))
    flow.append(
        P(
            "sCw(i, t) = s(i, t) * coverageConf(i, t) * attentionConf(i, t)",
            "eq",
        )
    )
    flow.append(P("Tradable score = sCw(i, t minus 1).", "eq"))
    flow.append(P("Sentiment tilt", "h2"))
    flow.append(
        P(
            "wTilt is proportional to w * exp(lambda * (score minus mean(score))). "
            "The tilted vector is then projected back onto the capped simplex.",
            "eqnote",
        )
    )
    flow.append(P("References", "h2"))
    flow.append(
        P(
            "Hutto, C. J., and Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. <i>ICWSM</i>.",
            "ref",
        )
    )
    flow.append(
        P(
            "Korab, P. FinVADER lexicons (SentiBigNomics / Henry path used in FINS3645 Week 9). Apache 2.0; vendored under src/vendor/course_finvader.",
            "ref",
        )
    )
    flow.append(
        P(
            "Loughran, T., and McDonald, B. (2011). When is a liability not a liability? <i>The Journal of Finance</i>, 66(1), 35 to 65.",
            "ref",
        )
    )
    flow.append(
        P(
            "Markowitz, H. (1952). Portfolio selection. <i>The Journal of Finance</i>, 7(1), 77 to 91.",
            "ref",
        )
    )
    flow.append(
        P(
            "FINS3645 Project 2026 brief and data access helper; Kaiyuan Lan, Project A Signal Harbour / Attention Pulse (2026).",
            "ref",
        )
    )
    return flow


def main():
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="Signal Harbour: FINS3645 Project B",
        author="Kaiyuan Lan (z5444541)",
    )
    doc.build(story(), onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUT)


if __name__ == "__main__":
    main()
