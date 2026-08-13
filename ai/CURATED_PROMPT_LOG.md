# Curated Prompt Log: Project B (Signal Harbour)

Student: Kaiyuan Lan (`z5444541`)  
Authorship: these are prompts and correction orders I issued. The coding assistant filed them here under my direction.  
Rule: preserve supplied text; do not invent prompts.


## Entry R0: Mandatory course forum and open source innovation addendum

**Timestamp:** 9 August 2026 (Sydney)  
**Origin:** Supplied by me in the Cursor chat that started this Project B continuity/innovation upgrade  
**Prompt significance:** Meaningful direction and mandatory stage order override  
**Attachments I named:** `/Users/jaysonlan/Desktop/z5444541_projectA.zip`; `/Users/jaysonlan/Downloads/project_brief_FINS3645 (3).pdf`; `/Users/jaysonlan/Downloads/project_overview (2).pdf`; `/Users/jaysonlan/Downloads/projectB_starter (2).zip`  
**Ed Discussion access?** Local files only after I attached or named them. The coding assistant did **not** independently access Ed Discussion. Forum text below was pasted by me into the prompt.

### Curated prompt text (body I supplied; long stage list abbreviated with `[...]` only after the forum evidence; full stage intent is preserved in the linked working docs)

```text
# MANDATORY COURSE FORUM AND OPEN SOURCE INNOVATION ADDENDUM

This section is a HARD RULE and overrides any earlier instruction that treats Project A merely as optional background or treats innovation as an optional final enhancement.

## 1. COURSE FORUM GUIDANCE

I supplied the following FINS3645 forum guidance.

READ THE ATTACHED PDF for criteria and marking rubric of PART B FIRST

### Forum item 1: augmented finVADER

Student question:

“Dear Alex,

Hope you are well. I am writing to inquire whether finVADER provided in Week9 can be used for Project B VADER.

Kind Regards,

Tevez Jin”

Alexander Dickerson’s answer:

“Hi Tevez,

You are one of the top students in the class: you can design your own augmented finVADER with AI.

I believe in you!

Best,

Alex”

### Forum item 2: Parts A and B are one project

Student question:

“Hi Alex,

Hope you are doing well.

I was wondering whether we might receive our marks or any feedback on the first assignment before assignment 2 is due next week.

Thank you in advance.

Kind regards,

Aurelia”

Alexander Dickerson’s answer:

“Hi Aurelia,

I can provide general feedback in class today.

We mark Part A and B concurrently. So you will receive marks for A and B at the same time.

The project is split to encourage students to work on it early. A and B are part of the same project, but we split it to stop students working on the entire thing in Week 11.

As such, we only begin grading A, once B is handed in, because it is the same project.

Best,

Alex”

Treat these as user supplied course forum evidence. Preserve them exactly in the curated prompt record because they formed part of my instruction.

Do not claim that the coding assistant independently accessed Ed Discussion unless it actually did.

## 2. REQUIRED INTERPRETATION OF THE FORUM GUIDANCE

The two forum answers mean:

1. Project B is not a separate generic portfolio exercise.
2. Signal Harbour must remain one coherent project across Parts A and B.
3. Project B must directly reuse and extend my own Project A data foundation.
4. Differences between the Part A and Part B descriptions, assumptions, calendars, terminology, app user, data definitions or claimed innovations may damage the assessment across both Parts.
5. I cannot rely on receiving marker feedback for Part A before finishing Part B.
6. The coding assistant must therefore perform a strict Project A audit under my direction before extending into Project B.
7. A custom AI assisted augmented finVADER is expressly encouraged by the course convenor.
8. Using only unchanged VADER or unchanged Week 9 finVADER would leave substantial originality unused.
9. The custom finVADER must still be implemented, tested and critically evaluated. Calling an ordinary dictionary “custom” is not enough.
10. The strongest innovation should connect the Part A Attention Pulse, Part B sentiment model, portfolio fusion and Streamlit app into one continuous Signal Harbour contribution.

Create:

ai/COURSE_FORUM_GUIDANCE.md

[... remainder of stages 2 to 23 as supplied in the same message: PROJECT_CONTINUITY_AUDIT.md; mandatory GitHub research; OPEN_SOURCE_RESEARCH.md; INNOVATION_SCORECARD.md; recommended Signal Harbour Context Weighted finVADER; custom finVADER development protocol; required innovation outputs; Project A and B consistency gate; updated stage order ending at Stage 23 before GitHub publication / Streamlit deployment / Moodle submission ...]

Begin with Project A. GitHub research cannot substitute for reading Project A.
```

Full stage list and technical specification were retained in the same user message (Stages 0 to 23). The complete addendum is also reflected in the derived working documents created from this entry:

* `ai/COURSE_FORUM_GUIDANCE.md`
* `ai/PROJECT_CONTINUITY_AUDIT.md`
* `ai/OPEN_SOURCE_RESEARCH.md`
* `ai/INNOVATION_SCORECARD.md`

### Immediate action taken

1. Moved the Cursor agent root to `/Users/jaysonlan/Desktop/z5444541_projectB` (existing Part B workspace).
2. Located final Project A at `/Users/jaysonlan/Desktop/z5444541_projectA` and the named ZIP/PDF attachments.
3. Began Stage 0 to 4 documentation before locking innovation architecture.


## Linked research search section

Raw GitHub search queries actually issued during Stage 5 are appended in `ai/OPEN_SOURCE_RESEARCH.md` under **Raw GitHub search queries**. They are not rewritten after the fact.


## Entry R1: Manual package review and modelling correction order (9 August 2026)

**Timestamp:** 9 August 2026 evening (Sydney)  
**Origin:** My own manual review of the Project B package, with suggestions from a third party Claude session  
**Prompt significance:** Meaningful direction and mandatory correction order  
**Note:** Curated record of the correction order I issued to the coding assistant.

### Prompt I issued (me to coding assistant)

```text
I checked the submission myself (manual review), also using suggestions from a third party Claude session:
source, CSVs, clean copy reproduction, tests with the data ZIP, Streamlit, and the AI pack.

Log the important critiques in ai/, then keep fixing in this order:

1) Min variance is silently stalling (tiny covariance scale + success=True). Brief warned about this. Rescale and prove methods differ.
2) One Sharpe definition everywhere: stop optimising mean/vol and labelling CAGR/vol as Sharpe.
3) Monthly rebalancing must allow holdings to drift; document execution timing. Same for fusion.
4) Rebuild all results; add turnover and simple cost sensitivity.
5) Either put Signal Harbour on the real Week 9 finVADER base or stop calling it augmented finVADER. Fix profit falls regressions, debt masking, negation.
6) Handle the 120 headline review sheet honestly (blank kaiyuan_review_label unless I fill them); add a development/holdout split. Neutrality rates are not accuracy.
7) Fix Allocate calendars, explain tab date alignment, sector NaNs, slider defaults.
8) Make the AI pack a real chronology. Do not invent fake mistakes.
9) Clean hygiene; git/repo/deploy remain student owned later steps.

Until the modelling and app blockers above are fixed, more visual polish will not fix the substance.
```

### Immediate action taken

Opened `ai/MANUAL_REVIEW_DECISIONS.md`, appended this curated prompt entry, started Entry 8 in `AI_ITERATION_LOG.md`, and began code fixes with optimiser / Sharpe / drift first.


## Entry R2: Second manual review (false human labels and remaining blockers) (9 August 2026)

**Timestamp:** 9 August 2026 late evening (Sydney)  
**Origin:** My second manual review, with further third party Claude suggestions  
**Prompt significance:** Meaningful correction of honesty/attribution defects

### Prompt I issued (me to coding assistant)

```text
The “human validation” is still generated by code and then described as a human review sheet. That contradicts CLAUDE.md. Either I genuinely label the rows, or every claim of human agreement attributed to me becomes “automated rule based pseudo label diagnostic”. Prefer blank kaiyuan_review_label.

Also fix AI log attribution: reviews were my manual checks plus third party Claude suggestions. Do not present the coding assistant as the source of the package review.

Then: rebuild sector index with no news neutrals on the complete grid; rerun ablation on the Week 9 base; fix turnover timing; fix mixed Allocate calendars; remove the obsolete fusion improvement note; clean caches. Repo/deploy remain mine.
```


## Entry R3: Must fix before submission (10 August 2026)

**Timestamp:** 10 August 2026 (Sydney)  
**Origin:** My manual readiness check of the current folder (Must fix items only)  
**Prompt significance:** Meaningful direction: must fix items only  
**Note:** Logged the Must fix list I issued.

### Prompt I issued (me to coding assistant)

```text
Before I submit, fix these three things only:

1) The Streamlit app is unreadable in dark mode: pale page background with white headings. Pin the app to light theme in .streamlit/config.toml so the tabs stay readable.

2) Deployment still isn’t done. Get a public GitHub repo and a live Streamlit URL in place early; the brief asks for a deployed app from a public repo.

3) Don’t ship a duplicate figure. sentiment_coverage_neutrality.png is the same bytes as sentiment_model_comparison.png: either make it a real coverage figure or delete it.
```
