# Mindshare Take-Home — Solution (Fable test run)

End-to-end solution to the **Intercom/Fin Senior GTM Data Analyst — Mindshare** take-home:
all 6 analysis questions answered, full assumption log, reproducible code, and the
3-slide deck for the CMO / VP Demand Gen audience.

## The deliverables

| File | What it is |
|---|---|
| **[`slides/mindshare_fy27_slides.pdf`](slides/mindshare_fy27_slides.pdf)** | **The 3 slides** (submission artifact). HTML source alongside it. |
| **[`ANALYSIS.md`](ANALYSIS.md)** | Full write-up: answers to Q1–Q6, methodology, assumption log A1–A10, limitations, and the Q&A defense points. |
| [`analysis.py`](analysis.py) | Single reproducible script — computes every number cited anywhere, writes `outputs/` tables and `figures/` charts. `pip install pandas matplotlib openpyxl`, then `python analysis.py`. |
| [`sql/queries.sql`](sql/queries.sql) | Snowflake-style equivalents of every analysis step (the day-one production version). |
| `data/` | The three weekly tables exported as CSV from the source workbook (column names lower-cased; otherwise untouched). |
| `outputs/` | Computed tables, one per question (`q1_…` through `q5_…`). |
| `figures/` | Brand-styled charts used in the slides. |

## The story in three lines

1. **Mindshare is eroding, not growing** — warm (Direct + Organic) traffic −25% YoY, intent visits −31%, inbound MQLs −28%, while Paid visits +103% with −24% efficiency decay. Capture is crowding out creation.
2. **Brand is the quality engine** — warm traffic converts to high-intent actions up to 1.7× better than Paid; the Sep '25 Fin launch (the window's one natural experiment) drove a 5.7× sustained Fin-traffic lift and +20% S1 q/q. Bonus finding: UTM attribution is 99.6% blind — nobody can prove channel ROI until it's fixed.
3. **FY27: shift ~$3M (15% of the paid run-rate proxy) from unbranded capture to creation** — quarterly Fin brand moments, EMEA SB/MM brand program, APAC activation fix — targeting +285 S1 opps/yr (+20%), with guardrails (branded-search floor, quarterly stage gates) and two zero-cost data fixes.

## Rebuilding the PDF

The deck is `slides/mindshare_fy27_slides.html` (1280×720 per slide, Intercom-style palette).
Re-render after edits with Edge headless:

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu `
  --no-pdf-header-footer --print-to-pdf="<abs path>\slides\mindshare_fy27_slides.pdf" `
  "file:///<abs path>/slides/mindshare_fy27_slides.html"
```
