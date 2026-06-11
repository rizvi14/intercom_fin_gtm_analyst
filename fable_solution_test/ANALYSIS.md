# Mindshare Take-Home — Full Analysis & Methodology

**Role:** Senior GTM Data Analyst — Mindshare (Intercom / Fin)
**Data:** 78 ISO weeks (Dec 2 2024 – May 25 2026) across `web_visits_weekly`, `mql_funnel_weekly`, `utm_source_weekly`
**Code:** [`analysis.py`](analysis.py) (pandas, fully reproducible) · [`sql/queries.sql`](sql/queries.sql) (Snowflake equivalents) · computed tables in [`outputs/`](outputs/) · charts in [`figures/`](figures/)
**Deliverable slides:** [`slides/`](slides/)

---

## Executive summary (the 30-second version)

Mindshare is **eroding, not growing**: brand-driven traffic is down 25% YoY while Paid visits doubled — and the doubled Paid spend bought *less efficient* traffic (conversion per visit down 24%). Warm traffic converts to high-intent actions up to **1.7× better** than Paid, and the one brand investment in the window — the **Sep '25 Fin launch moment** — produced a sustained 5.7× lift in Fin-surface traffic and a ~20% quarter-over-quarter lift in S1 conversions. The FY27 recommendation: **shift ~$3M (≈15% of the paid-capture run-rate proxy) from unbranded paid capture into demand creation** — quarterly Fin brand moments, EMEA/APAC regional brand programs — plus two zero-cost data fixes (UTM capture, segment enrichment) that currently blind us to brand's contribution.

---

## Q1 — Defining mindshare

**Definition.** Mindshare = the share of future buyers who think of Intercom/Fin *before* a vendor search begins. It cannot be observed directly in web data, so I use a three-layer proxy stack, each layer one step closer to revenue:

| Layer | Proxy | Why it's valid | Weight |
|---|---|---|---|
| **Awareness** | Unique visitors from **Direct + Organic** on marketing surfaces | Direct = typed/bookmarked the brand (recall). Organic for a known brand is dominated by branded queries. Neither is bought per-click. | 50% |
| **Intent** | Pricing + demo page visits from warm channels | People evaluating *because of* brand pull, not ad capture | 30% |
| **Brand-sourced pipeline** | Inbound **core** MQLs (Demo / Trial / Contact Sales) | The VP Demand Gen answer: mindshare expressed as pipeline. Outbound excluded (SDR-driven, not brand). | 20% |

These combine into a monthly **Mindshare Index** (each component indexed to window mean = 100; see `outputs/q1_mindshare_index_monthly.csv`, `figures/fig5_mindshare_index.png`).

**Powered By** (the "Powered by Intercom" messenger links) is genuine brand *reach* — 4.2M visits, the largest single reach channel — but it is tracked **separately, not inside the index**, because it suffered a structural break in Mar 2025 (see Q2) that would otherwise dominate the composite and turn the index into a measure of one program.

**Why not UTM-based brand attribution?** Because it's broken: 99.6% of MQLs carry `utm_source = Direct/Unknown` (Q4). Behavioral channel data is the only usable lens — itself a finding.

## Q2 — Is mindshare growing?

**No. It declined materially, then stabilized at a lower plateau, with an early recovery signal in spring 2026.**

All YoY numbers use the two seasonally matched 26-week windows the data allows: **Y1 = Dec 2 '24 – May 26 '25** vs **Y2 = Dec 1 '25 – May 25 '26** (avoids partial-quarter and seasonality artifacts).

| Metric | Y1 | Y2 | YoY |
|---|---:|---:|---:|
| Warm visits (Direct + Organic) | 2.46M | 1.85M | **−25%** |
| Warm unique visitors | 2.10M | 1.62M | −23% |
| Warm intent visits (pricing + demo) | 255K | 176K | **−31%** |
| Paid visits | 902K | 1.83M | **+103%** |
| Powered By visits | 2.54M | 713K | −72% |
| Inbound MQLs | 11,742 | 8,409 | **−28%** |
| Inbound S1 conversions | 767 | 720 | −6% |

By region (warm visits YoY): NAMER **−27%**, EMEA **−22%**, APAC **−14%**, LATAM **−47%**. The erosion is everywhere; no region is growing brand traffic.

**Three inflections (signal, not noise):**

1. **Mar 2025 — Powered By structural break.** ~640K visits/month (Dec–Feb) → ~310K (Mar) → ~100–170K thereafter. A −72% collapse of the largest free brand-reach channel. Step-change shape says program or tracking change, not demand decay — first diagnostic question for the team.
2. **Sep–Nov 2025 — the Fin brand moment.** Fin-surface visits jumped from ~4.5K/week to ~25.6K/week (5.7×) and *stayed* elevated through May 2026. Inbound S1s rose 397 → 475 (+20%) vs the prior quarter. This is the window's one natural experiment in brand investment (detail in Q4).
3. **Spring 2026 — early recovery.** Apr–May warm visits are **+3.8% YoY** (627.7K vs 604.7K) — the first positive YoY brand reading in the dataset, coinciding with the sustained Fin halo.

**Statistical rigor.** The full-window weekly trend is −454 visits/week (t = −6.1), but that overstates decay: it is dominated by the elevated Dec '24–Feb '25 start. Excluding the first 13 weeks the slope is −82/week (t = −1.5, not significant) — i.e., *decline to a plateau*, not continuous decay. The last 26 weeks trend +853/week (t = +4.2), though part of that is the holiday-trough recovery; the matched-week +3.8% YoY is the honest version of the recovery claim. Weekly t-stats ignore autocorrelation and are directional only — the matched 26-week windows are the robust comparison. The S1-rate improvement (6.5% → 8.6%) is on n = 767/720 conversions, large enough that it is not small-sample noise.

**The quality offset:** while volume fell 28%, MQL→S1 conversion improved 6.5% → 8.6%, so S1 output fell only 6%. The funnel got *smaller but warmer* — consistent with brand-driven buyers being closer to purchase, and with the thesis that what remains of inbound is disproportionately brand-sourced.

## Q3 — Channel roles: who builds, who captures

Computed on marketing surfaces only (excludes Product Login, Support/Help Center, etc.). High-intent conversion = demo form + contact sales + successful signup (the events that mint core MQLs). Full table: `outputs/q3_channel_roles.csv`.

| Channel | Visit share | High-intent conv. share | Conv / 1k visitors | Role |
|---|---:|---:|---:|---|
| Paid | 28.9% | 37.7% | 17.7 | **Capture** |
| Powered By | 28.1% | 6.9% | 3.6 | Awareness — pure reach |
| Direct | 26.2% | 23.1% | 13.1 | Awareness — brand recall |
| Organic | 10.6% | 22.8% | **30.5** | **Hybrid — best efficiency** |
| Other | 6.2% | 9.6% | 21.2 | Mixed long-tail |

- **Organic is the standout**: 22.8% of all high-intent conversions from 10.6% of visits — 2.2× pull-through, 1.7× Paid's per-visitor efficiency.
- **Are we over-invested in capture? Yes — at the margin.** Paid visits doubled YoY (+103%), but Paid's own efficiency fell **21.4 → 16.2 conversions per 1k visits (−24%)**: classic diminishing returns on the marginal capture dollar. Meanwhile total inbound MQLs still fell 28% — doubling capture did not offset the brand erosion, because capture harvests demand that creation must first produce.
- Mix shift Y1→Y2: Paid went from **15% to 42%** of marketing visits (Powered By's collapse and Direct's decline did the rest). The traffic portfolio has quietly inverted from brand-led to bought.

## Q4 — Do warm channels produce higher-quality MQLs?

**Finding zero: we can't answer this from CRM attribution — and that's a headline finding.** `dim_leads.utm_source_last` is 99.6% `Direct/Unknown` (45,575 of 45,760 MQLs). Last-touch UTM capture is effectively dead. Until it's fixed, *paid channels can't prove their MQL quality either* — the skepticism cuts both ways. (Last-touch within 90 days additionally biases whatever credit exists toward capture channels.)

So quality is assessed on three defensible proxies:

1. **Web behavior by channel** (Q3 table): warm visitors take high-intent actions at up to 1.7× the Paid rate (Organic 30.5 vs Paid 17.7 per 1k). Per-visitor contact-sales submits — the single highest-value action — run 1.8/1k on Organic vs 1.2/1k on Paid.
2. **Funnel composition** (inbound only): core MQLs convert to S1 at **8.1% vs 1.7%** for non-core; MQL-Contact Sales converts at **20.4%** (50.6% engaged rate) vs Demo 6.8% and Trial 4.4%. The MQL types that warm traffic disproportionately generates (self-directed demo/contact-sales requests) are the highest-converting types; paid-typical types (Event 2.2%, Nurture 1.5%, Content Syndication 0.6%) barely convert. Inbound beats outbound 7.2% vs 4.0%.
3. **The Fin natural experiment** (`outputs/q4_fin_launch_experiment.csv`): comparing Sep–Nov '25 (launch quarter) to Jun–Aug '25 — Fin-surface visits 6.8K → 39.5K/week avg, inbound MQLs +6%, **S1 conversions +20% (397 → 475)**, S1 rate 6.5% → 7.3%. Brand activity coincided with more *and better* pipeline, and the traffic lift sustained for 8+ months.

**Honest caveat on causality:** weekly correlation between warm visits and core MQLs is modest (r ≈ 0.32 weekly, 0.41 for intent visits at monthly grain) — weekly noise and the 90-day lag between awareness and MQL wash it out. The co-movement case rests on the matched YoY windows (warm −25%, inbound MQLs −28%, while Paid +103%) and the before/after experiment, not on week-to-week correlation. I'd say this in the room before the VP Demand Gen does.

**Quantified leverage:** every 1,000 visitors shifted from Paid-efficiency to Organic-efficiency yields **+12.8 high-intent conversions** (30.5 − 17.7); at the core-MQL S1 rate of 8.1%, ≈ **+1 S1 opportunity per 1,000 visitors shifted**.

## Q5 — Where to invest regionally / by segment

Region map (share of warm traffic vs share of inbound pipeline, full window — `outputs/q5_region_gap.csv`):

| Region | Warm traffic share | Inbound MQL share | S1 share | S1 rate |
|---|---:|---:|---:|---:|
| NAMER | 41.6% | 61.5% | 63.4% | 7.4% |
| EMEA | 34.6% | 33.1% | 33.7% | 7.3% |
| APAC | 17.1% | 5.3% | 2.7% | 3.7% |
| LATAM | 6.7% | 0.1% | 0.2% | 11.4% |

- **NAMER** — brand converts best here and over-delivers pipeline vs traffic (61.5% of MQLs on 41.6% of warm traffic). Mature engine: maintain, don't grow allocation.
- **EMEA** — the balanced scale play: pipeline share matches traffic share at NAMER-level S1 rates, with strong SB (11.8% S1) and MM (8.8%). Incremental brand dollars convert here at proven rates. **First priority for net-new brand investment.**
- **APAC** — the **activation gap**: 17% of warm traffic produces 5% of MQLs and 2.7% of S1s, at a 3.7% S1 rate (half of EMEA/NAMER). Awareness exists; conversion doesn't. *Diagnose before scaling spend*: localization, regional pricing/payment, sales coverage and follow-up SLAs. Brand dollars poured on a broken conversion path are wasted.
- **LATAM** — warm traffic exists (6.7%) but essentially zero pipeline (44 inbound MQLs in 18 months — likely no GTM motion). The 11.4% S1 rate is on tiny n. Watch list, not an FY27 priority.

Segment (`outputs/q5_segment_quality.csv`):

- **SB / VSB are the quality core** (11.8% / 10.7% S1) but SB inbound MQLs fell **−40% YoY** and MM −27% — the brand erosion is concentrated exactly where conversion is best. Recovering SB/MM inbound is the highest-leverage segment goal.
- **ENT is the inverse**: MQLs **+34% YoY** (the only growing segment) but a 2.9% S1 rate. Enterprise interest in Fin is rising faster than our motion converts it — a sales-process/routing question worth a dedicated diagnostic, and the CMO's best growth story if fixed.
- **Unknown segment = 17% of inbound MQLs (5,625) with zero S1 credit** — un-enriched leads either aren't routed or aren't credited. Free pipeline recovery via enrichment; also depresses every measured conversion rate.

## Q6 — FY27 recommendation

> **Shift ~$3.0M (≈15%) of the paid-capture run-rate from unbranded capture into demand creation, hold a branded-search floor, and fix two measurement gaps — targeting recovery of half the brand-traffic decline, worth ≈ +285 S1 opportunities (+20% on the inbound S1 run-rate).**

**Spend baseline (assumption A8, stated openly):** the extract has no spend data, so the paid baseline is a proxy: 1.83M Paid visits in Y2 → ~3.66M annualized × $5.50 blended cost/visit (B2B SaaS benchmark $4–8) ≈ **$20M paid run-rate**. Every downstream dollar scales linearly with this assumption — directionally robust anywhere in the benchmark range.

**Where the $3M goes:**

| Allocation | $ | Rationale (evidence) |
|---|---:|---|
| Quarterly **Fin brand moments** (launch-grade campaigns, events, PR) | $1.5M | The Sep '25 moment: 5.7× sustained Fin-surface lift, +20% S1 q/q (Q4) |
| **EMEA brand program** (SB/MM focus) | $0.9M | Pipeline share already matches traffic share at 7.3% S1; SB/MM convert at 8.8–11.8% (Q5) |
| **APAC activation diagnostic + localized brand test** | $0.3M | Fix the 17%-traffic→3%-S1 leak before scaling (Q5) |
| **Organic/content + Powered By recovery** investigation | $0.3M | Organic = 30.5 conv/1k (best); PB collapse = −72% of free reach (Q2/Q3) |

**Guardrails (pre-empting the VP Demand Gen):** cut only *unbranded* paid capture — keep a branded-search defense floor; the cut is 15% of the *least efficient marginal* spend (Paid efficiency already fell 24% as volume doubled, so the marginal dollar is the cheapest to give up); stage-gate quarterly against leading indicators (warm visits, warm intent visits) with agreed rollback triggers.

**Zero-cost accelerators:** (1) fix UTM/attribution capture — 99.6% of MQLs are channel-blind, which handicaps *every* channel's case, including paid; (2) enrich the 17% Unknown-segment MQLs — recovered routing is free pipeline.

**Expected return:** recovering **half** of the warm-traffic decline (conservative — the Apr–May '26 +3.8% YoY shows recovery is already starting) implies +1,666 inbound MQLs per 26 weeks; at the current 8.6% S1 rate ≈ **+285 S1 opportunities/year, +20% vs the 1,440/yr run-rate**. Sensitivity: at the old 6.5% S1 rate, +215/yr; full recovery at current rate, +570/yr.

---

## Assumption log

| # | Assumption | Rationale / risk |
|---|---|---|
| A1 | "Warm"/brand = Direct + Organic | Direct = brand recall; Organic for an established brand is mostly branded queries. Risk: some Organic is generic-keyword SEO (capture-ish). Sensitivity: Organic alone is the *most* efficient channel, so the warm-quality conclusion survives any split. |
| A2 | Powered By excluded from the Mindshare Index, tracked separately | Mar '25 structural break (−72%) would dominate the composite; cause unknown (program/tracking). |
| A3 | YoY = matched 26-week windows (Dec 2 '24–May 26 '25 vs Dec 1 '25–May 25 '26) | Only fully overlapping seasonal windows in a 78-week extract; avoids partial-quarter artifacts. |
| A4 | Brand-sourced pipeline = `sales_motion = 'inbound'` only | Outbound is SDR-driven prospecting, not mindshare. |
| A5 | High-intent web conversion = demo form + contact sales + successful signup | These mint core MQLs (Demo/Trial/Contact Sales), which convert at 8.1% vs 1.7% for non-core. |
| A6 | k-anonymity NULLs (<10 entities) treated as 0 | Conservative undercount; affects small cells (LATAM, Unknown region) most. |
| A7 | Marketing surfaces exclude Product Login, Support & Help Center, Legal, Changelog, Developers | Existing-customer traffic would inflate Direct's denominator and isn't prospect mindshare. |
| A8 | Paid cost proxy = $5.50/visit (B2B SaaS blended benchmark $4–8) | No spend data in extract. All $ figures scale linearly; recommendation is expressed as a % shift so it survives any CPC. Replace with actual spend on day one. |
| A9 | Web high-intent events ≈ MQL channel mix proxy | Necessary because UTM attribution is 99.6% unknown; cross-checked against funnel composition (Q4). |
| A10 | Sep–Nov '25 treated as a brand-investment natural experiment | Before/after on adjacent quarters; not a controlled test — confounds possible (seasonality, product news). Stated as coincident evidence, not proof. |

## Known limitations (would address with warehouse access)

- No spend data → channel ROI is proxied, not measured. First ask: marketing spend by channel × month.
- No referral channel breakout (folded into Other) and no brand-vs-generic split inside Organic → would split via Search Console data.
- Last-touch 90-day attribution undercredits brand by construction → propose a first-touch / multi-touch view once UTM capture is fixed.
- MQL table lacks channel linkage (only the broken UTM table joins them) → the single most valuable instrumentation fix.
- Engagement *speed* ("faster engagement" in the prompt) is not measurable at weekly grain; engaged-rate is the available proxy (Contact Sales 50.6% vs Nurture 7.8%).
