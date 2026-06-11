"""
Mindshare Take-Home — Senior GTM Data Analyst (Intercom / Fin)
===============================================================
Single reproducible analysis script. Reads the three weekly-grain tables
(exported from the source workbook into ./data/), computes every number cited
in ANALYSIS.md and the slide deck, and writes:

  outputs/   - computed tables (CSV), one per analysis step
  figures/   - brand-styled charts used in the slides

Equivalent Snowflake SQL for each step lives in sql/queries.sql.

Key methodology decisions (full assumption log in ANALYSIS.md):
  * "Warm" / brand channels = Direct + Organic. Powered By is brand REACH
    (free impressions) but is reported separately because of a structural
    break in Mar 2025.
  * YoY comparisons use the two seasonally matched 26-week windows the data
    allows: Y1 = Dec 2 2024 - May 26 2025, Y2 = Dec 1 2025 - May 25 2026.
  * Brand-sourced pipeline = sales_motion = 'inbound' only (outbound is
    SDR-driven and does not reflect mindshare).
  * High-intent web conversions = demo_form_submits + contact_sales_submits
    + successful_signups (the web events that mint Core MQLs).
  * "Marketing surfaces" excludes Product Login, Support & Help Center,
    Legal & Compliance, Changelog, Developers (existing-customer traffic).
  * NULL-suppressed cells (<10 entities, k-anonymity) are treated as 0:
    conservative undercount, affects small cells only.

Run:  python analysis.py   (from fable_solution_test/)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "outputs")
FIG = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

# ---------------------------------------------------------------- branding --
# Intercom-style palette (near-black ink, Intercom blue, supporting neutrals)
INK = "#081D34"      # near-black navy ink
BLUE = "#0057FF"     # Intercom primary blue
LIGHTBLUE = "#7FA7FF"
GRAY = "#9AA5B1"
LIGHT = "#E8ECF1"
RED = "#E0457B"      # alert accent (Fin gradient pink)
TEAL = "#00A39B"
GOLD = "#F0A202"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK, "axes.edgecolor": LIGHT, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK,
    "axes.grid": True, "grid.color": LIGHT, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.size": 11,
})

# ------------------------------------------------------------------- load ---
web = pd.read_csv(os.path.join(DATA, "web_visits_weekly.csv"), parse_dates=["week_start"])
mql = pd.read_csv(os.path.join(DATA, "mql_funnel_weekly.csv"), parse_dates=["week_start"])
utm = pd.read_csv(os.path.join(DATA, "utm_source_weekly.csv"), parse_dates=["week_start"])

NUM_WEB = ["total_visits", "unique_cookies", "marketing_site_pageviews", "pricing_page_visits",
           "demo_page_visits", "blog_visits", "cta_clicks", "demo_form_submits",
           "contact_sales_submits", "signup_visits", "successful_signups"]
web[NUM_WEB] = web[NUM_WEB].fillna(0)  # k-anonymity NULLs -> 0 (assumption A6)

WARM = ["Direct", "Organic"]
Y1 = ("2024-12-02", "2025-05-26")   # 26 ISO weeks
Y2 = ("2025-12-01", "2026-05-25")   # 26 ISO weeks, seasonally matched
NON_MKT = ["Product Login", "Support & Help Center", "Legal & Compliance", "Changelog", "Developers"]
DISCOVERY = None  # awareness uses all marketing surfaces from warm channels

web["high_intent"] = web.demo_form_submits + web.contact_sales_submits + web.successful_signups
mkt = web[~web.visit_path_category.isin(NON_MKT)].copy()
warm = web[web.attribution_channel_group.isin(WARM)]
inb = mql[mql.sales_motion == "inbound"]

def win(df, w):
    return df[df.week_start.between(*w)]

print("=" * 70)
print("Q1/Q2 - MINDSHARE INDEX & TREND")
print("=" * 70)

# -------------------------------------------------- Q1: mindshare index -----
# Composite monthly index: Awareness 50% (warm unique cookies, marketing
# surfaces), Intent 30% (warm pricing+demo page visits), Brand-sourced
# pipeline 20% (inbound core MQLs). Each component indexed to full-window
# mean = 100, then weighted.
warm_mkt = mkt[mkt.attribution_channel_group.isin(WARM)]
mo_aware = warm_mkt.groupby(pd.Grouper(key="week_start", freq="MS")).unique_cookies.sum()
mo_intent = warm.groupby(pd.Grouper(key="week_start", freq="MS")).apply(
    lambda d: d.pricing_page_visits.sum() + d.demo_page_visits.sum())
mo_pipe = inb[inb.core_noncore == "core"].groupby(
    pd.Grouper(key="week_start", freq="MS")).total_mqls.sum()

idx = pd.DataFrame({"awareness": mo_aware, "intent": mo_intent, "pipeline": mo_pipe}).iloc[:18]
idx_n = idx / idx.mean() * 100
idx_n["mindshare_index"] = 0.5 * idx_n.awareness + 0.3 * idx_n.intent + 0.2 * idx_n.pipeline
idx_n.round(1).to_csv(os.path.join(OUT, "q1_mindshare_index_monthly.csv"))
print("\nMindshare index (monthly, window mean=100):")
print(idx_n.mindshare_index.round(1).to_string())

# -------------------------------------------------- Q2: YoY trend -----------
rows = []
for name, df, col in [
    ("Warm visits (Direct+Organic)", warm, "total_visits"),
    ("Warm unique cookies", warm, "unique_cookies"),
    ("Warm intent visits (pricing+demo)", warm, None),
    ("Paid visits", web[web.attribution_channel_group == "Paid"], "total_visits"),
    ("Powered By visits", web[web.attribution_channel_group == "Powered By"], "total_visits"),
]:
    if col is None:
        a = win(df, Y1).pricing_page_visits.sum() + win(df, Y1).demo_page_visits.sum()
        b = win(df, Y2).pricing_page_visits.sum() + win(df, Y2).demo_page_visits.sum()
    else:
        a, b = win(df, Y1)[col].sum(), win(df, Y2)[col].sum()
    rows.append([name, a, b, round((b / a - 1) * 100, 1)])
for name, col in [("Inbound MQLs", "total_mqls"), ("Inbound S1 conversions", "s1_conversions")]:
    a, b = win(inb, Y1)[col].sum(), win(inb, Y2)[col].sum()
    rows.append([name, a, b, round((b / a - 1) * 100, 1)])
yoy = pd.DataFrame(rows, columns=["metric", "Y1_Dec24_May25", "Y2_Dec25_May26", "yoy_pct"])
yoy.to_csv(os.path.join(OUT, "q2_yoy_summary.csv"), index=False)
print("\nYoY (matched 26-week windows):\n", yoy.to_string(index=False))

# S1 rate improvement
s1r1 = win(inb, Y1).s1_conversions.sum() / win(inb, Y1).total_mqls.sum() * 100
s1r2 = win(inb, Y2).s1_conversions.sum() / win(inb, Y2).total_mqls.sum() * 100
print(f"\nInbound MQL->S1 rate: Y1 {s1r1:.1f}% -> Y2 {s1r2:.1f}%")

# Warm visits YoY by region
a = win(warm[warm.region != "Unknown"], Y1).groupby("region").total_visits.sum()
b = win(warm[warm.region != "Unknown"], Y2).groupby("region").total_visits.sum()
reg_yoy = pd.DataFrame({"Y1": a, "Y2": b, "yoy_pct": ((b / a - 1) * 100).round(1)})
reg_yoy.to_csv(os.path.join(OUT, "q2_warm_visits_yoy_by_region.csv"))
print("\nWarm visits YoY by region:\n", reg_yoy.to_string())

# Trend significance: OLS slope on weekly warm visits, three windows
warm_wk = warm.groupby("week_start").total_visits.sum().sort_index()

def ols_slope(y):
    """OLS slope + t-stat (NB: weekly data is autocorrelated; t-stats are
    optimistic - used directionally, with matched-window YoY as the robust check)."""
    y = np.asarray(y, dtype=float)
    x = np.arange(len(y))
    X = np.column_stack([np.ones(len(y)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ beta
    se = np.sqrt(e @ e / (len(y) - 2) / ((x - x.mean()) ** 2).sum())
    return beta[1], beta[1] / se

slopes = pd.DataFrame(
    [["full 78 wks", *ols_slope(warm_wk)],
     ["excl. first 13 wks (elevated start)", *ols_slope(warm_wk.iloc[13:])],
     ["last 26 wks", *ols_slope(warm_wk.iloc[-26:])]],
    columns=["window", "slope_visits_per_wk", "t_stat"]).round(1)
slopes.to_csv(os.path.join(OUT, "q2_warm_trend_slopes.csv"), index=False)
print("\nWarm weekly trend slopes:\n", slopes.to_string(index=False))

# Recent recovery: Apr 1 - May 25 matched weeks YoY
r1 = warm[warm.week_start.between("2025-04-01", "2025-05-26")].total_visits.sum()
r2 = warm[warm.week_start.between("2026-04-01", "2026-05-25")].total_visits.sum()
print(f"\nWarm visits Apr-May: 2025 {r1:,} -> 2026 {r2:,} ({(r2/r1-1)*100:+.1f}%)  <- recovery signal")

print("\n" + "=" * 70)
print("Q3 - CHANNEL ROLE ANALYSIS (marketing surfaces)")
print("=" * 70)

g = mkt.groupby("attribution_channel_group").agg(
    visits=("total_visits", "sum"), cookies=("unique_cookies", "sum"),
    high_intent=("high_intent", "sum"), pricing=("pricing_page_visits", "sum"))
g["visit_share_pct"] = (g.visits / g.visits.sum() * 100).round(1)
g["conv_share_pct"] = (g.high_intent / g.high_intent.sum() * 100).round(1)
g["conv_per_1k_cookies"] = (g.high_intent / g.cookies * 1000).round(1)
g["role"] = ["Awareness (brand recall)", "Hybrid (best efficiency)", "Mixed long-tail",
             "Capture", "Awareness (brand reach)"]
g.to_csv(os.path.join(OUT, "q3_channel_roles.csv"))
print("\n", g[["visit_share_pct", "conv_share_pct", "conv_per_1k_cookies", "role"]].to_string())

# Paid diminishing returns
pd_ = web[web.attribution_channel_group == "Paid"]
for lab, w in [("Y1", Y1), ("Y2", Y2)]:
    d = win(pd_, w)
    print(f"Paid {lab}: visits {d.total_visits.sum():,}  high-intent {d.high_intent.sum():,}"
          f"  rate {d.high_intent.sum()/d.total_visits.sum()*1000:.1f}/1k")

# Visit-share shift Y1 -> Y2
for lab, w in [("Y1", Y1), ("Y2", Y2)]:
    s = win(mkt, w).groupby("attribution_channel_group").total_visits.sum()
    print(f"{lab} visit share %: ", dict((s / s.sum() * 100).round(1)))

print("\n" + "=" * 70)
print("Q4 - QUALITY OF MINDSHARE TRAFFIC")
print("=" * 70)

# UTM attribution coverage (the broken-instrumentation finding)
u = utm.groupby("utm_source_category")[["total_mqls", "s1_count"]].sum()
u["share_pct"] = (u.total_mqls / u.total_mqls.sum() * 100).round(1)
u["s1_rate_pct"] = (u.s1_count / u.total_mqls * 100).round(1)
u.to_csv(os.path.join(OUT, "q4_utm_coverage.csv"))
print("\nUTM source coverage (dim_leads.utm_source_last):\n", u.to_string())

# Funnel quality cuts (inbound)
q = inb.groupby("core_noncore")[["total_mqls", "s1_conversions"]].sum()
q["s1_rate_pct"] = (q.s1_conversions / q.total_mqls * 100).round(1)
print("\nInbound core vs non-core:\n", q.to_string())

t = inb.groupby("mql_type")[["total_mqls", "engaged_mqls", "s1_conversions"]].sum()
t["s1_rate_pct"] = (t.s1_conversions / t.total_mqls * 100).round(1)
t["engaged_rate_pct"] = (t.engaged_mqls / t.total_mqls * 100).round(1)
t = t.sort_values("total_mqls", ascending=False)
t.to_csv(os.path.join(OUT, "q4_mql_type_quality.csv"))
print("\nInbound quality by MQL type:\n", t.to_string())

mo_ = mql.groupby("sales_motion")[["total_mqls", "s1_conversions"]].sum()
mo_["s1_rate_pct"] = (mo_.s1_conversions / mo_.total_mqls * 100).round(1)
print("\nInbound vs outbound:\n", mo_.to_string())

# Weekly correlation: warm visits vs inbound core MQLs (brand drives the base)
wk_warm = warm.groupby("week_start").total_visits.sum()
wk_core = inb[inb.core_noncore == "core"].groupby("week_start").total_mqls.sum()
both = pd.concat([wk_warm, wk_core], axis=1, keys=["warm", "core"]).dropna()
r = both.warm.corr(both.core)
print(f"\nWeekly corr(warm visits, inbound core MQLs) = {r:.2f} (n={len(both)})")

# Natural experiment: Fin brand moment Sep-Nov 2025 vs Jun-Aug 2025
fin = web[web.visit_path_category.str.startswith("Fin")].groupby("week_start").total_visits.sum()
pre_fin, post_fin = fin[fin.index < "2025-09-01"], fin[fin.index >= "2025-09-01"]
pre = inb[inb.week_start.between("2025-06-01", "2025-08-31")]
post = inb[inb.week_start.between("2025-09-01", "2025-11-30")]
exp = pd.DataFrame({
    "period": ["Jun-Aug 2025 (pre)", "Sep-Nov 2025 (post)"],
    "fin_page_visits_wkly_avg": [round(fin["2025-06-01":"2025-08-31"].mean()),
                                 round(fin["2025-09-01":"2025-11-30"].mean())],
    "inbound_mqls": [pre.total_mqls.sum(), post.total_mqls.sum()],
    "s1_conversions": [pre.s1_conversions.sum(), post.s1_conversions.sum()],
    "s1_rate_pct": [round(pre.s1_conversions.sum() / pre.total_mqls.sum() * 100, 1),
                    round(post.s1_conversions.sum() / post.total_mqls.sum() * 100, 1)]})
exp.to_csv(os.path.join(OUT, "q4_fin_launch_experiment.csv"), index=False)
print("\nFin brand-moment natural experiment:\n", exp.to_string(index=False))
print(f"Fin-surface weekly visits: {pre_fin.mean():,.0f} pre-Sep -> {post_fin.mean():,.0f} after "
      f"({post_fin.mean()/pre_fin.mean():.1f}x, sustained through May 2026)")

print("\n" + "=" * 70)
print("Q5 - REGION / SEGMENT OPPORTUNITY MAP")
print("=" * 70)

w_ = warm[warm.region != "Unknown"]
i_ = inb[inb.region != "Unknown"]
ts = w_.groupby("region").total_visits.sum(); ts = (ts / ts.sum() * 100).round(1)
ms = i_.groupby("region").total_mqls.sum(); ms = (ms / ms.sum() * 100).round(1)
ss = i_.groupby("region").s1_conversions.sum(); ss = (ss / ss.sum() * 100).round(1)
sr = (i_.groupby("region").s1_conversions.sum() / i_.groupby("region").total_mqls.sum() * 100).round(1)
reg = pd.DataFrame({"warm_traffic_share_pct": ts, "inbound_mql_share_pct": ms,
                    "s1_share_pct": ss, "s1_rate_pct": sr})
reg.to_csv(os.path.join(OUT, "q5_region_gap.csv"))
print("\nRegion: warm traffic share vs pipeline share:\n", reg.to_string())

seg = inb.groupby("company_reporting_segment")[["total_mqls", "s1_conversions"]].sum()
seg["s1_rate_pct"] = (seg.s1_conversions / seg.total_mqls * 100).round(1)
segy = []
for s in ["ENT", "MM", "SB", "VSB", "Unknown"]:
    d = inb[inb.company_reporting_segment == s]
    segy.append([s, win(d, Y1).total_mqls.sum(), win(d, Y2).total_mqls.sum()])
segy = pd.DataFrame(segy, columns=["segment", "mqls_Y1", "mqls_Y2"]).set_index("segment")
seg = seg.join(segy)
seg["mql_yoy_pct"] = ((seg.mqls_Y2 / seg.mqls_Y1 - 1) * 100).round(1)
seg.to_csv(os.path.join(OUT, "q5_segment_quality.csv"))
print("\nSegment quality + YoY:\n", seg.to_string())

print("\n" + "=" * 70)
print("Q6 - FY27 RECOMMENDATION MATH")
print("=" * 70)

# Spend proxy (no spend data in extract - assumption A8, CPC benchmark $5.50)
CPC = 5.50
paid_y2 = win(web[web.attribution_channel_group == "Paid"], Y2).total_visits.sum()
paid_annual_visits = paid_y2 * 2
paid_budget_proxy = paid_annual_visits * CPC
shift = 0.15 * paid_budget_proxy
print(f"Paid visits Y2 (26wk) {paid_y2:,} -> annualized {paid_annual_visits:,}")
print(f"Paid budget proxy @ ${CPC:.2f}/visit = ${paid_budget_proxy/1e6:.1f}M; 15% shift = ${shift/1e6:.1f}M")

# Expected lift: recover half the warm-traffic decline in FY27
warm_y1, warm_y2 = win(warm, Y1).total_visits.sum(), win(warm, Y2).total_visits.sum()
mql_y1, mql_y2 = win(inb, Y1).total_mqls.sum(), win(inb, Y2).total_mqls.sum()
s1rate_y2 = win(inb, Y2).s1_conversions.sum() / win(inb, Y2).total_mqls.sum()
recover_frac = 0.5
mql_lift_26wk = (mql_y1 - mql_y2) * recover_frac          # MQLs track warm traffic (r above)
s1_lift_annual = mql_lift_26wk * s1rate_y2 * 2
s1_runrate_annual = win(inb, Y2).s1_conversions.sum() * 2
print(f"Warm visits decline Y1->Y2: {warm_y1:,} -> {warm_y2:,} ({(warm_y2/warm_y1-1)*100:.1f}%)")
print(f"Recovering {recover_frac:.0%} of the inbound-MQL decline = +{mql_lift_26wk:,.0f} MQLs/26wk")
print(f"At current S1 rate {s1rate_y2*100:.1f}% = +{s1_lift_annual:,.0f} S1 opps/yr "
      f"(+{s1_lift_annual/s1_runrate_annual*100:.0f}% vs run-rate {s1_runrate_annual:,.0f}/yr)")

# ================================================================ FIGURES ===
def style_ax(ax, title):
    ax.set_title(title, fontsize=13, fontweight="bold", color=INK, loc="left", pad=12)

# --- fig1: warm vs paid weekly visits (4-wk rolling) with annotations -------
fig, ax = plt.subplots(figsize=(10.5, 4.6))
wk_paid = web[web.attribution_channel_group == "Paid"].groupby("week_start").total_visits.sum()
ax.plot(wk_warm.rolling(4).mean() / 1000, color=BLUE, lw=2.5, label="Brand / warm (Direct + Organic)")
ax.plot(wk_paid.rolling(4).mean() / 1000, color=RED, lw=2.5, label="Paid")
ax.axvspan(pd.Timestamp("2025-09-01"), pd.Timestamp("2025-11-30"), color=BLUE, alpha=0.07)
ax.annotate("Fin brand moment\n(Sep–Nov ’25)", xy=(pd.Timestamp("2025-10-10"), 95),
            ha="center", fontsize=9.5, color=INK)
ax.annotate("Paid +103% YoY", xy=(pd.Timestamp("2026-02-15"), 78), color=RED, fontsize=10, fontweight="bold")
ax.annotate("Warm −25% YoY", xy=(pd.Timestamp("2025-06-01"), 58), color=BLUE, fontsize=10, fontweight="bold")
ax.set_ylabel("Weekly visits (000s, 4-wk avg)")
ax.legend(frameon=False, loc="upper right", fontsize=10)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b ’%y"))
style_ax(ax, "Brand traffic eroded while Paid doubled — capture is crowding out creation")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_warm_vs_paid.png"), dpi=200); plt.close(fig)

# --- fig2: channel role map — visit share vs conversion share ---------------
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
order = ["Powered By", "Direct", "Organic", "Other", "Paid"]
gx = g.loc[order]
x = np.arange(len(order))
axes[0].bar(x - 0.2, gx.visit_share_pct, 0.38, color=LIGHTBLUE, label="Share of visits")
axes[0].bar(x + 0.2, gx.conv_share_pct, 0.38, color=BLUE, label="Share of high-intent conversions")
axes[0].set_xticks(x); axes[0].set_xticklabels(order, fontsize=9.5)
axes[0].set_ylabel("% of total"); axes[0].legend(frameon=False, fontsize=9)
style_ax(axes[0], "Reach vs conversion share by channel")
colors = [GRAY, GRAY, BLUE, GRAY, RED]
axes[1].bar(order, gx.conv_per_1k_cookies, color=colors)
for i, v in enumerate(gx.conv_per_1k_cookies):
    axes[1].text(i, v + 0.6, f"{v:.0f}", ha="center", fontsize=10, fontweight="bold")
axes[1].set_ylabel("High-intent conversions / 1k visitors")
axes[1].tick_params(axis="x", labelsize=9.5)
style_ax(axes[1], "Organic converts 1.7× better than Paid")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig2_channel_roles.png"), dpi=200); plt.close(fig)

# --- fig3: region gap — warm traffic share vs MQL / S1 share ----------------
fig, ax = plt.subplots(figsize=(6.4, 4.0))
order_r = ["NAMER", "EMEA", "APAC", "LATAM"]
rg = reg.loc[order_r]
x = np.arange(len(order_r))
ax.bar(x - 0.27, rg.warm_traffic_share_pct, 0.26, color=LIGHTBLUE, label="Warm traffic share")
ax.bar(x, rg.inbound_mql_share_pct, 0.26, color=BLUE, label="Inbound MQL share")
ax.bar(x + 0.27, rg.s1_share_pct, 0.26, color=INK, label="S1 share")
ax.set_xticks(x); ax.set_xticklabels(order_r)
ax.set_ylabel("% of total"); ax.legend(frameon=False, fontsize=9)
ax.annotate("activation gap", xy=(2.0, 19), ha="center", fontsize=9, color=RED, fontweight="bold")
ax.annotate("activation gap", xy=(3.0, 9), ha="center", fontsize=9, color=RED, fontweight="bold")
style_ax(ax, "APAC & LATAM: awareness without activation")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig3_region_gap.png"), dpi=200); plt.close(fig)

# --- fig4: Fin natural experiment -------------------------------------------
fig, ax = plt.subplots(figsize=(6.4, 4.0))
finw = fin.rolling(4).mean()
ax.fill_between(finw.index, finw / 1000, color=BLUE, alpha=0.15)
ax.plot(finw / 1000, color=BLUE, lw=2.2, label="Fin-surface visits (000s/wk)")
ax.axvline(pd.Timestamp("2025-09-01"), color=RED, lw=1.4, ls="--")
ax.annotate("Fin launch moment", xy=(pd.Timestamp("2025-09-08"), 42), fontsize=9.5, color=RED)
ax.annotate("5.7× sustained lift", xy=(pd.Timestamp("2026-01-01"), 27), fontsize=10,
            fontweight="bold", color=INK)
ax.set_ylabel("Weekly Fin-page visits (000s, 4-wk avg)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b ’%y"))
style_ax(ax, "Proof brand works: the Sep ’25 Fin moment")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig4_fin_experiment.png"), dpi=200); plt.close(fig)

# --- fig5: mindshare index ----------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 3.6))
ax.plot(idx_n.index, idx_n.mindshare_index, color=BLUE, lw=2.5, marker="o", ms=4)
ax.axhline(100, color=GRAY, lw=1, ls=":")
ax.set_ylabel("Mindshare Index (window mean = 100)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b ’%y"))
style_ax(ax, "Composite Mindshare Index: 50% awareness · 30% intent · 20% brand-sourced pipeline")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig5_mindshare_index.png"), dpi=200); plt.close(fig)

print("\nFigures written to figures/, tables to outputs/. Done.")
