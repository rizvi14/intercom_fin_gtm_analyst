# Mindshare GTM Take-Home — Prep Plan

## Context

You're prepping for a **Senior GTM Data Analyst — Mindshare** take-home at Intercom/Fin. You have 2 hours for analysis + 3 slides + a 30-min defense to the CMO/VP Demand Gen/Hiring Manager. The data is 3 weekly-grain tables (`web_visits_weekly`, `mql_funnel_weekly`, `utm_source_weekly`) covering Dec 2024 – Jun 2026 (78 ISO weeks). You'll run the analysis in **Databricks**, want a **heavy marketing primer**, and slides in **Intercom corporate aesthetic**.

Goal of this plan: get you from "I just opened the data" to "deck submitted + I can defend every number" with the shortest path to highest-impact deliverables. You don't have time to chase everything — this plan picks the 3 numbers that matter and ignores the rest.

---

## 1. Distilled Checklist (the actual rubric)

The PDF lists 6 analytical questions. They map to **3 slide moments** for the deck. Tackle in this order — each step feeds the next:

- [ ] **A. Define mindshare** as a measurable index from the data (Q1) → grounds everything else
- [ ] **B. Trend the index** over 78 weeks, by region (Q2) → headline for Slide 1
- [ ] **C. Channel role split** — visit-share vs MQL-share gap by `attribution_channel_group` (Q3) → headline for Slide 2 (part 1)
- [ ] **D. Channel quality** — S1 conversion rate + Core-MQL ratio: warm channels vs Paid (Q4) → headline for Slide 2 (part 2)
- [ ] **E. Region × segment opportunity gap** — where visit-share ≠ MQL-share ≠ S1-share (Q5) → feeds Slide 3
- [ ] **F. FY27 reallocation recommendation** with a $/% number and an expected lift (Q6) → headline for Slide 3
- [ ] **G. Stress-test every number** — be ready for "is this signal or noise?" and "convince me brand isn't a vanity metric"

Evaluation criteria you're graded against (memorize these — they're the rubric the panel actually scores):
1. **Analytical rigor** — numbers support the recommendation
2. **Marketing fluency** — brand vs capture, attribution, mindshare-as-strategy
3. **Communication** — clear story to skeptics
4. **Business judgment** — realistic, prioritized, quantified FY27 recommendation

---

## 2. Marketing Fluency Primer

You said you're weak on MMM and marketing terminology. Here's what you need — calibrated to this specific assignment so you can speak fluently in the defense:

### Core concept: Mindshare
The **share of attention / awareness** your brand owns in the category. Not "market share" (that's revenue/customers); mindshare is whether buyers think of *you* unprompted when the problem arises. It's measured indirectly through **proxies of unprompted attention**: people who type your URL directly, search your name organically, click through from a referral that mentions you. In this dataset, that's `Direct` + `Organic` + (arguably) `Powered By` channels and brand-page reach.

### Demand creation vs demand capture (the central tension in this assignment)
- **Demand creation** = generating *new* interest in your category or brand. Brand campaigns, content, PR, events, organic SEO content. Pays off slowly, hard to attribute, builds the long-term funnel. This is what Mindshare team owns.
- **Demand capture** = monetizing demand that *already exists*. Paid search on brand keywords, retargeting, paid social to warm audiences. Fast attribution, looks great in dashboards — but most of the credit was earned by the brand activity upstream. This is what Demand Gen team typically owns.
- **The CMO's hypothesis**: Intercom is over-invested in capture (it shows ROI fast) and under-invested in creation (it builds the funnel that capture skims from). Your job is to prove or refute that with this data.

### MMM — what it is and why this assignment isn't really MMM
**Marketing Mix Modeling** = a statistical regression that takes historical spend + outcomes across channels and estimates the incremental contribution of each channel, accounting for diminishing returns and ad stock (delayed effect of brand). True MMM needs **spend data**, which you don't have. So **don't call your work MMM** — call it **"channel role analysis + attribution-based quality scoring."** If asked about MMM in the Q&A, the right answer is: *"True MMM would require spend data and a longer time horizon to model ad stock; with the data here I used a channel-share gap framework as a proxy for understanding where each channel sits on the create-vs-capture spectrum."* That's the fluent answer.

### Attribution model used here: last-touch within 90 days
The **last marketing channel that touched the lead within 90 days before they became an MQL** gets 100% of the credit. This is **biased toward demand-capture channels** (the closer of the deal, not the brand activity that initially put you on the radar). Knowing this is critical — you can use it as a defense: *"Last-touch under-credits brand. The fact that warm channels still outperform Paid on quality is evidence brand is doing even more than the numbers show."*

### MQL → S1 → S2 funnel
- **MQL** (Marketing Qualified Lead) = behavioral threshold crossed (requested demo, started trial, downloaded content, etc.). Marketing's currency.
- **S1** = first sales stage — the SDR/AE accepted the lead as worth pursuing. **This is the quality bar** — a high MQL→S1 rate means marketing is sending real opportunities, not junk.
- **S2** = qualified opportunity created — sales confirmed there's budget/authority/need. Pipeline-ready.
- **Why S1 matters more than MQL volume for your story**: 10,000 low-quality MQLs that don't convert to S1 are worse than 5,000 that do. This is the lever for arguing brand quality.

### Core vs Non-Core MQLs
- **Core** = high-intent actions: Demo, Trial, Contact Sales, Livechat. These signal a buyer in-market.
- **Non-Core** = lower-intent: Content download, webinar, content syndication, nurture. Awareness-stage.
- **Why this matters**: Core MQL ratio is another quality signal. Warm channels should produce a higher Core-MQL %.

### Inbound vs Outbound
- **Inbound** = lead came to you (filled a form, started a trial)
- **Outbound** = SDR cold-prospected them
- **Filter outbound out of any mindshare analysis** — outbound MQLs say nothing about brand strength; they say something about how hard the BDR team works. Use `sales_motion = 'inbound'` as your filter on the MQL table.

### The 5 channel groups in your data — what they actually mean
- **Direct** — typed URL or bookmark. *Strongest pure-brand signal.* People who already know you.
- **Organic** — SEO traffic. Mix of branded search ("intercom pricing") and non-branded ("best customer service software"). Both signal earned attention, but branded is the cleaner mindshare proxy. You can't separate them in this dataset — flag this as a limitation.
- **Paid** — paid ads. Mix of capture (Google brand-term ads, retargeting) and creation (brand display campaigns). Mostly capture.
- **Powered By** — "Powered by Intercom" attribution links on customer widgets. *Product-led growth virality* — a unique brand signal driven by Intercom's customer footprint, not paid media. Treat this as its own category.
- **Other** — long tail. Probably small but check before excluding.

### The 4 UTM-source categories
- **Direct/Unknown** — dominates because `dim_leads.utm_source_last` is sparse. The PDF *flags this as a real finding to investigate.* Translation: a lot of MQLs come in with no UTM, which usually means brand-driven (direct entry) — but the data hygiene is also a gap to flag. Don't pretend Direct/Unknown = pure brand without acknowledging the data quality caveat.
- **Google** — paid + organic search blended (UTM doesn't always distinguish).
- **Email** — nurture / lifecycle.
- **Other** — everything else.

### Vocabulary you should use confidently in the meeting
- "Visit-share-vs-MQL-share gap" — your channel-role framework
- "Mindshare index" — your composite proxy
- "Last-touch under-credits upstream brand activity" — your attribution caveat
- "Demand creation vs capture mix" — the strategic framing
- "Core MQL ratio" and "S1 conversion rate" — your quality measures
- "Branded vs non-branded organic" — the limitation you should pre-flag
- "Ad stock / lagged brand effect" — if MMM comes up

---

## 3. Approach to Each Analysis Question

Direction only — not answers. Your job is to actually run these.

### Q1: Define mindshare
**Approach**: Build a **composite Mindshare Index** justified by 2–3 proxy categories:
- **Awareness proxy** = unique cookies from `Direct` + `Organic` channels (and optionally `Powered By`), filtered to *brand-discovery* `visit_path_category` values (Homepage, Blog & Resources, Customer Stories, Learning Center, Fin Blueprint, Competitive Comparisons)
- **Intent-from-brand proxy** = `pricing_page_visits` + `demo_page_visits` from those same warm channels (proves the attention converts to consideration)
- **Optional reach proxy** = total `unique_cookies` on warm channels (top-line size)

**Justification framing in slide**: "Mindshare = humans who arrive without a paid prompt and engage with brand or buying-intent surfaces."

**Pitfall to flag**: you can't distinguish branded vs non-branded organic — call this out and explain it likely *under*states mindshare (non-branded organic includes a lot of "best CS software" searches that brand wins).

### Q2: Trend the signal
**Approach**:
- Aggregate Mindshare Index weekly across all 78 weeks
- Smooth with a **4-week rolling average** to kill noise
- Calculate **CAGR or % change**: first 3 months avg vs last 3 months avg (cleaner than week 1 vs week 78)
- Break out by `region` (5 lines); for segment, you can only use the MQL table since web data has no segment dimension — note this gap
- **Inflection check**: visually scan for jumps; cross-reference with date for plausible explanations (new product launch? campaign? — you won't know, but flag and ask)
- **Significance check** (light): compare last-quarter mean ± std dev to first-quarter — if they overlap, call it noise. You don't need a formal test, just rigor.

**Output for slide**: One line chart, regional overlay. Headline: "Mindshare grew X% overall but concentrated in [region]; [region] is flat."

### Q3: Channel role analysis
**Approach**:
- Build a 5-row table: for each `attribution_channel_group`, compute (a) % share of total visits, (b) % share of total MQLs (you'll need to map: web data has channel, MQL table doesn't — use `utm_source_weekly` as the join bridge, or use channel-share within MQL by inferring through utm source category)
- **Gap = (visit-share %) − (MQL-share %)**
- Positive gap = **awareness channel** (drives reach, doesn't close)
- Negative gap = **capture channel** (small reach, high conversion → riding on brand demand)
- Cross-check with `cta_clicks`, `demo_form_submits` per visit by channel as a sanity layer

**Critical caveat to flag**: the channel attribution model differs between web (immediate channel of visit) and MQL (last-touch within 90 days), so the share-gap is directional not exact. Acknowledge this in the slide footnote.

**Output for slide**: Diverging bar chart of visit-share minus MQL-share, ordered.

### Q4: Quality of mindshare traffic
**Approach**:
- Use `utm_source_weekly` directly — it has `s1_conversion_rate_pct` already calculated by `utm_source_category` × `region`
- Compare **Direct/Unknown** vs **Google** vs **Email**: which has higher S1 rate?
- Confirm with the MQL table: filter `sales_motion = 'inbound'`, then compare S1 rate and Core/Non-Core split. Warm-source MQLs should skew Core.
- **Quantify the leverage**: if warm S1 rate is X% vs paid Y%, then a 1-point shift in MQL mix toward warm = (X-Y) × total MQLs additional S1s

**Pitfall**: utm_source is sparse and Direct/Unknown dominates — this is *itself* a finding (lots of MQLs arrive with no source = strong brand pull). Frame it that way.

**Output for slide**: Side-by-side bars — MQL→S1 conversion rate by channel.

### Q5: Regional / segment recommendations
**Approach**:
- Build a region-level table: % of total visits, % of total MQLs, % of total S1s. Where the three diverge = opportunity.
- Segment-level: same comparison but only on the MQL table (`company_reporting_segment`: VSB/SB/MM/ENT). Look for ENT under-indexed in MQL volume but high S1 rate = invest more brand to feed that funnel.
- Cross-cut: which **region × segment** cell has the biggest gap between attention-share and pipeline-share? That's your concentration point.

**Output**: A 2-axis matrix or a ranked table — 3 priority cells with the gap quantified.

### Q6: FY27 recommendation
**Approach**:
- Anchor on a specific shift: "Shift $X (or X% of FY27 marketing budget) from [Paid capture in low-leverage cell] to [Brand creation in high-leverage cell]"
- Quantify expected lift: use the warm-vs-paid S1-rate differential from Q4 × the MQL volume you'd redirect
- **You don't have $ budget data** — so phrase as a **% of mix shift** (e.g., "rebalance 15% of paid spend toward brand-creation in EMEA Enterprise") and let the CMO map to dollars internally
- **Sensitivity check**: state what happens if the warm-channel quality lift is half what the data shows. If the recommendation still holds, that's defensible.
- **Prioritize** — give one bold recommendation + two secondary moves. Not a 10-item list.

**Defense prep — rehearse answers to these**:
- "VP Demand Gen says brand is a vanity metric — convince me." → Lead with the **S1 conversion rate differential** (it's pipeline impact, not awareness)
- "Is the trend signal or noise?" → Show the rolling avg + first-quarter vs last-quarter delta
- "Why this region/segment?" → The visit-share-vs-MQL-share gap is X points wide there, biggest in the dataset
- "Last-touch under-credits brand — so isn't your channel comparison biased?" → Yes, and **in our favor** — warm channels look good *despite* being under-credited

---

## 4. Three-Slide Structure

You get 3 slides max. Each has **one headline insight** (BLUF style — the chart title *is* the conclusion), one main chart, 2–3 supporting bullets, a methodology footnote.

### Slide 1 — Diagnosis: "Mindshare is growing, but unevenly"
- **Headline**: "Mindshare grew X% over 18 months — concentrated in [region], flat in [region]"
- **Hero chart**: Line chart of weekly Mindshare Index, 4-week rolling avg, one line per region
- **Sidebar**: Definition of Mindshare Index (the proxies you chose, 1-line each)
- **Bullets** (3 max): overall trajectory, regional winner, regional laggard
- **Footnote**: methodology — what's in the index, the branded-vs-non-branded organic caveat

### Slide 2 — Proof: "Warm channels build brand AND outconvert paid"
- **Headline**: "Direct + Organic carry [X]% of attention but only [Y]% of MQL credit — and convert [Z]pp better to S1"
- **Hero chart**: 2-panel —
  - Left: Visit-share vs MQL-share by channel (diverging bars showing the gap)
  - Right: MQL→S1 conversion rate by channel (Direct/Organic vs Google vs Email)
- **Bullets**: the gap quantified, the conversion lift quantified, the Core-MQL ratio differential
- **Footnote**: last-touch attribution methodology + that it *under-credits* brand

### Slide 3 — Recommendation: "FY27: Reweight toward brand creation in [region × segment]"
- **Headline**: "Shift [X]% of FY27 paid mix to brand creation in [EMEA Enterprise / specific cell] → expected +[Y] S1s"
- **Hero chart**: Region × segment opportunity matrix OR an "investment shift" before/after bar
- **Bullets**: the specific shift, expected impact (volume + quality), sensitivity (what if lift is half), risks
- **Footnote**: assumptions baked into the recommendation

---

## 5. Claude Design Prompt (paste into Claude Design or Canva-friendly)

```
Design a 3-slide executive presentation deck for Intercom's CMO and VP of Demand Gen on
"FY27 Mindshare Strategy." Audience is senior marketing leadership; slides will be presented
in a 10-minute walkthrough followed by skeptical Q&A.

BRAND AESTHETIC — Intercom corporate
- Color palette: deep navy/near-black primary (#0A1F44 or #000000), clean white background,
  one bright accent for callouts (Intercom's signature electric blue #2962FF or
  #0057FF range). Use a single warm accent (e.g., yellow #FFC700 or coral) sparingly for
  highlighting one number per slide. Avoid more than 3 colors total per slide.
- Typography: modern geometric sans-serif (Inter, Söhne, or Intercom Sans). Bold weight
  for headlines (28–36pt), regular for body (14–18pt), tabular numerals for any numbers.
- Layout: generous white space, left-aligned, no centered text except titles. 16:9 aspect.
- Chart style: minimal axes, no chart junk, direct data labels on bars/lines instead of
  legends where possible. One color for the "brand" series, neutral grey for context.
- Vibe: confident, executive-ready, data-forward. Not consulting-overdesigned; closer to
  a Stripe / Linear / Intercom in-product feel.

STRUCTURE — three slides, BLUF (bottom line up front) headlines

SLIDE 1 — Diagnosis (Mindshare trajectory)
- Title headline (the conclusion, not the topic): "Mindshare grew [X]% over 18 months —
  concentrated in [region], stalling in [region]"
- Hero visual (right ~65% of slide): line chart of weekly Mindshare Index over 78 weeks
  with one line per region (NAMER, EMEA, APAC, LATAM), 4-week rolling average. Annotate
  the growth region's line endpoint with a callout label.
- Left sidebar (~35%): definition box "Mindshare Index = [proxies]" + 3 supporting
  bullet points (one regional winner, one laggard, one inflection insight).
- Footer: methodology footnote in 10pt grey.

SLIDE 2 — Proof (Brand pays back)
- Title headline: "Warm channels carry [X]% of attention but get [Y]% of MQL credit —
  and convert [Z]pp better to S1"
- Two side-by-side charts:
  LEFT: Diverging horizontal bar — visit-share % minus MQL-share % by channel
  (Direct, Organic, Paid, Powered By, Other). Positive bars (awareness channels) in
  brand accent color, negative (capture channels) in dark grey.
  RIGHT: Vertical bar chart — MQL→S1 conversion rate by source (Direct/Unknown,
  Google, Email). Highlight the warm-channel bar in the accent color, others in grey.
- Below charts: 2–3 short proof bullets quantifying the lift and the Core-MQL ratio gap.
- Footer: last-touch attribution caveat in small grey type.

SLIDE 3 — Recommendation (FY27 shift)
- Title headline: "FY27: Shift [X]% of paid mix toward brand creation in [region ×
  segment] — projected +[Y] incremental S1s"
- Main visual: an investment-shift before/after stacked bar (current mix vs proposed
  mix) OR a 2×2 region-segment opportunity matrix with the priority cells highlighted
  in accent color.
- Right sidebar: "What this assumes" box with 2–3 sensitivity bullets (what changes
  if warm-channel lift is half, key risks).
- Bottom strip: 3 small icons or text callouts for the 3 prioritized moves
  (1 primary, 2 secondary).

REQUIREMENTS
- One headline insight per slide; the title itself is the conclusion, never the topic.
- Tabular numerals everywhere. Percentages and dollar values bold in the accent color.
- No more than 5 lines of body text per slide outside of charts.
- Methodology footnote at the bottom of each slide in 10pt grey, max one line.
- Charts use direct labels, not legends, when possible. No 3D, no shadows, no gradients
  on data marks.
- Output as 16:9, PowerPoint or Figma-editable.

Tone: confident, evidence-led, no marketing jargon. Speak to a CMO who has seen 500
decks and a VP Demand Gen who's skeptical of brand metrics.
```

---

## 6. Execution Time Budget (2 hours)

You're tight on time. Allocate ruthlessly:

| Block | Time | Output |
|---|---|---|
| 0:00–0:15 | Load data in Databricks, profile each table (rowcounts, null %, distinct values for region/channel/segment) | Confidence in data shape |
| 0:15–0:30 | Build Mindshare Index → weekly trend chart (overall + by region) | Slide 1 chart |
| 0:30–0:55 | Channel role analysis (visit-share vs MQL-share gap) + quality (S1 rate by source) | Slide 2 charts |
| 0:55–1:15 | Region × segment opportunity table + pick the 1 priority cell | Slide 3 input |
| 1:15–1:30 | Quantify the FY27 shift recommendation + sensitivity | Slide 3 headline |
| 1:30–2:00 | Build slides (use Claude Design or Canva with the prompt above), polish headlines, write methodology footnotes | Final deck |

**Cut list** if you're behind: skip the segment breakdown of the index trend (too much for one slide anyway), skip statistical-significance testing (use rolling avg + first-vs-last quarter delta as your rigor proxy), skip the Powered By analysis unless it's an obvious story.

---

## 7. Verification — Before You Submit

- [ ] Every number on the slides is reproducible from a single Databricks notebook cell — keep the notebook clean so you can show it in Q&A
- [ ] The 3 slide headlines, read in sequence, tell the full story without the charts (diagnosis → proof → recommendation)
- [ ] Methodology footnotes name your proxies, your filters (`sales_motion = inbound`), and the last-touch caveat
- [ ] You can answer in under 30 seconds: "What's mindshare in your definition?" "Why this region?" "Is this signal or noise?" "What's the dollar impact?" "Why isn't this just MMM?"
- [ ] You've stress-tested the recommendation: if warm-channel quality lift is half what you measured, does the recommendation still hold?
- [ ] Submission email: `cara.debbaudt@intercom.consulting`, subject `Mindshare Take-Home — [Your Name]`
