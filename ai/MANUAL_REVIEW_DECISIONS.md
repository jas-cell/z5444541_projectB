# Manual package review decisions (Entries 8 to 10)

Student: Kaiyuan Lan (z5444541)  
Dates: 9 August 2026 (Sydney)

## Authorship

I own these review decisions and the final evaluation of the package. I reviewed the work myself and also used suggestions from a third-party Claude session. The coding assistant implemented fixes under my direction; it did not author the critiques or the judgments below.

## Prompt round 1 (after my first manual review + Claude suggestions)

> Log the useful findings in `ai/`, then fix in order: optimiser scaling, one Sharpe definition, true monthly drift, rebuild with costs, Week 9 based Signal Harbour or rename it, honest headline label naming, app calendar and explain dates, credible AI chronology, hygiene.

## Prompt round 2 (after my second manual review + Claude suggestions)

> Several of the “fixes” still overclaim. Do not invent human labels in code; that contradicts `CLAUDE.md`. If the review column stays blank, strip every human agreement claim; an automated keyword diagnostic must be named as such. Attribute the review correctly: I reviewed the package manually, with third party Claude suggestions. Rebuild the sector index with no news neutrals on the complete grid. Rerun ablation on the Week 9 base. Fix turnover timing (drift through the decision day). Fix mixed Allocate calendars so crypto weekends are not dropped. Remove overclaiming fusion notes; clean caches. Repo/deploy stay student owned.


## Decisions I accepted from those reviews

1. False human validation attribution must be removed (blank column is more honest than invented keyword labels).
2. Logs must attribute reviews to me, with optional third party Claude suggestions, and must not present the coding assistant as the source of the package review.
3. Figure A9 / ablation must use the Week 9 base.
4. Standalone sector index must obey the stated no news = neutral rule.
5. Turnover must use post return drifted weights.
6. Mixed allocation sandbox must not silently drop crypto sessions.
