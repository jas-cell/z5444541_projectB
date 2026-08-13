# Project A Handoff — Signal Harbour

Student: Kaiyuan Lan (`z5444541`)  
Final Project A package inspected: `/Users/jaysonlan/Desktop/z5444541_projectA`  
Also named by Kaiyuan: `/Users/jaysonlan/Desktop/z5444541_projectA.zip`  
Inspected on: 2026-08-09  
Purpose: freeze the Part A positions that Part B must extend without rewriting Part A.

---

## 1. Product identity

| Item | Project A position |
|---|---|
| Product name | **Signal Harbour** |
| Value proposition | Auditable multi-asset feature layer for news-aware investment research |
| Customer / buyer | Small wealth-advisory firm / research team |
| Daily user | Portfolio analyst preparing evidence before an investment committee considers a fund |
| Immediate job in Part A | Make evidence going into later fund decisions traceable — **not** choose a portfolio |

---

## 2. Data foundation to reuse

| Area | Frozen Project A rule |
|---|---|
| Data entry | Hosted ZIP only through `src/data_access.py` |
| Sample | 2020–2023; remove crypto rows after 2023 |
| Equity calendar | Native US exchange sessions (~252/year); balanced 50 × 1,006 |
| Crypto calendar | Native 7-day calendar; returns computed first |
| Combined calendar | Left-align already-computed crypto returns to equity sessions |
| Return definition | Adjusted-close simple return within ticker on native dates |
| Extreme returns | Retain after price/OHLC/robust review; not auto-deleted |
| News unit | Headlines (`title`) |
| Deduplication | Exact duplicates on `(ticker, date, title)` |
| Missing publisher | Retain; publisher absence is not headline absence |
| Headline mapping | Same or next observed equity session; 6 unmappable year-end rows excluded |
| Text panel | Complete ticker × equity-session grid; zero article count when no headlines |
| LM vocabulary | Separate negative / positive / uncertainty counts — **descriptive only** |
| Sentiment in Part A | **None.** No scoring, no index, no netting |
| Attention Pulse | `AP = (log(1+N) − median₆₀,past) / scaled-MAD₆₀,past`; baseline shifted one day; min 20 history; IQR fallback if MAD≈0 |
| Attention Pulse use in A | Contemporaneous descriptive association with absolute returns; **not** a trading signal |
| Design system | Accessible exhibit language in `src/visuals.py` (shared colour/type/caption band) |

---

## 3. Key verified quantities from final Part A artifacts

| Quantity | Value (from Part A report / tables) |
|---|---|
| Equity rows | 50,300 |
| Crypto in-sample rows | 14,610 |
| Headlines mapped in-sample | 146,830 |
| Exact headline duplicates removed | 2,847 |
| Non-trading-date headlines | 12,557 (12,551 mapped forward; 6 excluded) |
| Top-decile Attention Pulse vs other days | +0.61 pp mean absolute equity return (descriptive) |
| LM word occurrences | Positive 22,488; Negative 20,941; Uncertainty 9,531 |

---

## 4. Explicit Part A limitations Part B must preserve

1. Attention Pulse is past-only in construction but was evaluated contemporaneously in Part A; it was **not** claimed to be tradable.
2. LM counts are not a sentiment score.
3. Headline coverage is uneven across sectors (Tech/Consumer heavy; Real Estate light).
4. Headlines are a noisy proxy; Part A already warned against over-interpretation.
5. No portfolio optimisation, backtest, or sentiment index exists in Part A and must not be back-dated into Part A claims.

---

## 5. What Part B should inherit vs invent

| Inherit unchanged | Invent / extend in Part B only |
|---|---|
| Product name, customer, daily user | Investable fund menu and fact sheets |
| Cleaning and mapping definitions | VADER / finVADER / Signal Harbour scoring |
| Return and calendar logic | Walk-forward optimisation and fusion |
| Attention Pulse equation | Lagged confidence use of Attention Pulse |
| Descriptive LM evidence | Lexicon/rule design informed by LM + corpus audit |
| Figure design language | Streamlit investor journey + explainability panel |

---

## 6. Handoff decision for this upgrade

Do **not** modify the submitted Project A package to fit a new Part B story.  
If Part B improves timing, lexicon, or fusion relative to an earlier Part B draft, disclose that improvement as Part B work. Do not claim the improved method already existed in Part A.
