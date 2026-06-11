# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not a software project** — it is a workspace for completing the **Intercom/Fin "Senior GTM Data Analyst — Mindshare" take-home assignment**. There is no application to build, no test suite to run, no lint target. The repo holds the assignment prompt, the dataset, and (eventually) the candidate's deliverables.

The user is the interview candidate. Tasks here are analytical and presentational: defining mindshare from the data, trending it, comparing channels, and producing a 3-slide deck for senior marketing leadership at Intercom.

## Files in the repo

- `mindshare_take_home_candidate.pdf` — the assignment prompt. **Always read this first** when starting a new session; it defines the 6 analytical questions, the dataset schemas, the stakeholders, and the evaluation rubric.
- `Copy of Senior Mindshare GTM Data Analyst Case Study Prompt Data Set .xlsx` — the source workbook. Contains the same three weekly-grain tables that the prompt describes as CSVs: `web_visits_weekly` (~24.5K rows), `mql_funnel_weekly` (~1.6K rows), `utm_source_weekly` (~323 rows). Covers Dec 2024 – Jun 2026 (78 ISO weeks).
- `README.md` — placeholder ("mindshare interview"); contains no useful guidance.

## Working environment

- The candidate runs analysis in **Databricks** (PySpark / SQL notebooks), not locally. Do not assume Python or Jupyter is available in this folder — the data has been imported to Databricks separately.
- Local `openpyxl` is **not installed**, so reading the Excel file via pandas locally will fail. The PDF documents every column, so prefer reading the PDF for schema understanding over trying to parse the workbook.
- Platform: Windows + PowerShell. Use PowerShell syntax (not bash) for any local commands.

## Key context for analysis discussions

The assignment has a specific marketing vocabulary the candidate must use fluently in defense. When discussing the work:

- **Mindshare** is being treated as a composite proxy index built from `Direct` + `Organic` (and optionally `Powered By`) channel traffic on brand-discovery `visit_path_category` surfaces, plus buying-intent surfaces (pricing/demo) from those same warm channels.
- The framing tension is **demand creation vs demand capture** — the CMO's hypothesis is that Intercom is over-invested in capture (Paid) and under-invested in creation (brand).
- Attribution is **last-touch within 90 days**, which biases credit toward capture channels — this caveat is a recurring talking point.
- Quality measures are **MQL → S1 conversion rate** and **Core-MQL ratio**, not MQL volume.
- **This is not MMM** (no spend data available). Frame the work as "channel role analysis + attribution-based quality scoring."
- Always filter to `sales_motion = 'inbound'` when discussing brand-sourced pipeline; outbound MQLs are SDR-driven and don't reflect mindshare.

## Prep artifacts

The candidate's prep plan — distilled checklist, marketing primer, per-question approach, 3-slide structure, Claude Design prompt for the deck, and 2-hour time budget — lives in-repo at:

`prep/mindshare-prep-plan.md`

This is the authoritative working doc for the assignment. **Read it before doing analysis work or duplicating prep**. Update it in place when the candidate's plan changes — do not fork or rewrite it.

Persistent cross-session memory about the user, the assignment, and stakeholders lives outside the repo at:

`C:\Users\moriz\.claude\projects\C--Users-moriz-OneDrive-Desktop-Github-repositories-intercom-fin-gtm-analyst\memory\`

## Deliverable and submission

- **3 slides max** (PDF or PowerPoint) plus optional analysis code/queries.
- Submit to `cara.debbaudt@intercom.consulting` with subject `Mindshare Take-Home — [Candidate Name]`.
- The 30-min presentation expects skeptical, interrupting Q&A from the CMO, VP Demand Gen, hiring manager Raunak Kumar, and Sr. Analyst Matthew Kong.

## What to avoid

- Do **not** answer the 6 assignment questions for the candidate. The candidate has explicitly asked for *direction and approach*, not finished answers — they need to do the analysis themselves to defend it.
- Do not invent build/lint/test commands; none exist in this repo.
- Do not generate analysis code unsolicited. Offer it, but wait for the candidate to ask.
