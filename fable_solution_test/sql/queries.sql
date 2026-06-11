-- ===========================================================================
-- Mindshare Take-Home — Snowflake-equivalent queries
-- ===========================================================================
-- These mirror the pandas logic in analysis.py, written against the weekly
-- extract tables (same grain as the CSVs). On production they would target
-- INTERCOM_PROD.CORE_GTM.FCT_WEB_VISITS / PRIVATE_GTM_ANALYTICS.PRV_MQL_ENGAGEMENT
-- with is_prospect_visit = TRUE AND is_included_visit = TRUE.
--
-- Window definitions used throughout (seasonally matched 26-week windows):
--   Y1 = 2024-12-02 .. 2025-05-26
--   Y2 = 2025-12-01 .. 2026-05-25
-- "Warm" = attribution_channel_group IN ('Direct','Organic')
-- "Marketing surfaces" = visit_path_category NOT IN ('Product Login',
--   'Support & Help Center','Legal & Compliance','Changelog','Developers')
-- ===========================================================================

-- ---------------------------------------------------------------------------
-- Q1: Composite Mindshare Index (monthly; each component indexed to window
--     mean = 100; weights 50% awareness / 30% intent / 20% pipeline)
-- ---------------------------------------------------------------------------
WITH monthly AS (
  SELECT
    DATE_TRUNC('month', week_start)                                   AS month,
    SUM(IFF(attribution_channel_group IN ('Direct','Organic')
            AND visit_path_category NOT IN ('Product Login','Support & Help Center',
                'Legal & Compliance','Changelog','Developers'),
            unique_cookies, 0))                                       AS awareness_cookies,
    SUM(IFF(attribution_channel_group IN ('Direct','Organic'),
            pricing_page_visits + demo_page_visits, 0))               AS intent_visits
  FROM web_visits_weekly
  GROUP BY 1
),
pipeline AS (
  SELECT DATE_TRUNC('month', week_start) AS month,
         SUM(total_mqls)                 AS core_inbound_mqls
  FROM mql_funnel_weekly
  WHERE sales_motion = 'inbound' AND core_noncore = 'core'
  GROUP BY 1
)
SELECT m.month,
       0.5 * (awareness_cookies / AVG(awareness_cookies) OVER () * 100)
     + 0.3 * (intent_visits     / AVG(intent_visits)     OVER () * 100)
     + 0.2 * (core_inbound_mqls / AVG(core_inbound_mqls) OVER () * 100)
       AS mindshare_index
FROM monthly m JOIN pipeline p USING (month)
ORDER BY 1;

-- ---------------------------------------------------------------------------
-- Q2a: YoY trend — matched 26-week windows, by channel
-- ---------------------------------------------------------------------------
SELECT attribution_channel_group,
       SUM(IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26', total_visits, 0)) AS y1_visits,
       SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25', total_visits, 0)) AS y2_visits,
       ROUND(y2_visits / NULLIF(y1_visits,0) * 100 - 100, 1)                       AS yoy_pct
FROM web_visits_weekly
GROUP BY 1 ORDER BY y1_visits DESC;

-- Q2b: Warm-channel YoY by region
SELECT region,
       SUM(IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26', total_visits, 0)) AS y1,
       SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25', total_visits, 0)) AS y2,
       ROUND(y2 / NULLIF(y1,0) * 100 - 100, 1)                                     AS yoy_pct
FROM web_visits_weekly
WHERE attribution_channel_group IN ('Direct','Organic') AND region <> 'Unknown'
GROUP BY 1 ORDER BY y1 DESC;

-- Q2c: Inbound funnel YoY
SELECT
  SUM(IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26', total_mqls, 0))      AS y1_mqls,
  SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25', total_mqls, 0))      AS y2_mqls,
  SUM(IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26', s1_conversions, 0))  AS y1_s1,
  SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25', s1_conversions, 0))  AS y2_s1,
  ROUND(y1_s1 / NULLIF(y1_mqls,0) * 100, 1)                                      AS y1_s1_rate,
  ROUND(y2_s1 / NULLIF(y2_mqls,0) * 100, 1)                                      AS y2_s1_rate
FROM mql_funnel_weekly
WHERE sales_motion = 'inbound';

-- Q2d: Warm intent-visit YoY (pricing + demo page visits, warm channels only)
SELECT
  SUM(IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26',
          pricing_page_visits + demo_page_visits, 0)) AS y1_intent_visits,
  SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25',
          pricing_page_visits + demo_page_visits, 0)) AS y2_intent_visits,
  ROUND(y2_intent_visits / NULLIF(y1_intent_visits,0) * 100 - 100, 1) AS yoy_pct
FROM web_visits_weekly
WHERE attribution_channel_group IN ('Direct','Organic');

-- Q2e: Trend significance — OLS slope of weekly warm visits, three windows.
--      REGR_SLOPE(y, x) is the least-squares slope; t is a 0-based week index.
--      (Weekly data is autocorrelated, so treat the slope directionally and
--       lean on the matched-window YoY above as the robust check.)
WITH wk AS (
  SELECT week_start,
         SUM(total_visits)                              AS warm_visits,
         ROW_NUMBER() OVER (ORDER BY week_start) - 1     AS t
  FROM web_visits_weekly
  WHERE attribution_channel_group IN ('Direct','Organic')
  GROUP BY week_start
)
SELECT 'full 78 wks'              AS window, ROUND(REGR_SLOPE(warm_visits, t),1) AS slope_visits_per_wk FROM wk
UNION ALL
SELECT 'excl. first 13 wks',      ROUND(REGR_SLOPE(warm_visits, t),1) FROM wk WHERE t >= 13
UNION ALL
SELECT 'last 26 wks',             ROUND(REGR_SLOPE(warm_visits, t),1) FROM wk WHERE t >= (SELECT MAX(t) FROM wk) - 25;

-- Q2f: Recent recovery — matched Apr 1 .. late-May weeks, 2025 vs 2026
SELECT
  SUM(IFF(week_start BETWEEN '2025-04-01' AND '2025-05-26', total_visits, 0)) AS apr_may_2025,
  SUM(IFF(week_start BETWEEN '2026-04-01' AND '2026-05-25', total_visits, 0)) AS apr_may_2026,
  ROUND(apr_may_2026 / NULLIF(apr_may_2025,0) * 100 - 100, 1)                 AS yoy_pct
FROM web_visits_weekly
WHERE attribution_channel_group IN ('Direct','Organic');

-- ---------------------------------------------------------------------------
-- Q3: Channel role — visit share vs high-intent-conversion share, efficiency
-- ---------------------------------------------------------------------------
WITH ch AS (
  SELECT attribution_channel_group AS channel,
         SUM(total_visits)   AS visits,
         SUM(unique_cookies) AS cookies,
         SUM(demo_form_submits + contact_sales_submits + successful_signups) AS high_intent
  FROM web_visits_weekly
  WHERE visit_path_category NOT IN ('Product Login','Support & Help Center',
        'Legal & Compliance','Changelog','Developers')
  GROUP BY 1
)
SELECT channel,
       ROUND(visits     / SUM(visits)     OVER () * 100, 1) AS visit_share_pct,
       ROUND(high_intent / SUM(high_intent) OVER () * 100, 1) AS conv_share_pct,
       ROUND(high_intent / cookies * 1000, 1)                 AS conv_per_1k_cookies
FROM ch ORDER BY visit_share_pct DESC;

-- Q3b: Paid diminishing returns (efficiency Y1 vs Y2)
SELECT
  IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26', 'Y1', 'Y2') AS window_label,
  SUM(total_visits) AS visits,
  SUM(demo_form_submits + contact_sales_submits + successful_signups) AS high_intent,
  ROUND(high_intent / visits * 1000, 1) AS conv_per_1k_visits
FROM web_visits_weekly
WHERE attribution_channel_group = 'Paid'
  AND (week_start BETWEEN '2024-12-02' AND '2025-05-26'
    OR week_start BETWEEN '2025-12-01' AND '2026-05-25')
GROUP BY 1;

-- Q3c: Visit-share shift by channel, Y1 vs Y2 (marketing surfaces only)
WITH win AS (
  SELECT attribution_channel_group AS channel,
         IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26', 'Y1', 'Y2') AS window_label,
         SUM(total_visits) AS visits
  FROM web_visits_weekly
  WHERE visit_path_category NOT IN ('Product Login','Support & Help Center',
        'Legal & Compliance','Changelog','Developers')
    AND (week_start BETWEEN '2024-12-02' AND '2025-05-26'
      OR week_start BETWEEN '2025-12-01' AND '2026-05-25')
  GROUP BY 1, 2
)
SELECT channel, window_label,
       ROUND(visits / SUM(visits) OVER (PARTITION BY window_label) * 100, 1) AS visit_share_pct
FROM win ORDER BY channel, window_label;

-- ---------------------------------------------------------------------------
-- Q4a: UTM attribution coverage (the broken-instrumentation finding)
-- ---------------------------------------------------------------------------
SELECT utm_source_category,
       SUM(total_mqls) AS mqls,
       ROUND(SUM(total_mqls) / SUM(SUM(total_mqls)) OVER () * 100, 1) AS share_pct,
       ROUND(SUM(s1_count) / NULLIF(SUM(total_mqls),0) * 100, 1)      AS s1_rate_pct
FROM utm_source_weekly
GROUP BY 1 ORDER BY mqls DESC;

-- Q4b: Inbound MQL quality by type / core flag / motion
SELECT mql_type, core_noncore,
       SUM(total_mqls) AS mqls,
       ROUND(SUM(engaged_mqls)   / NULLIF(SUM(total_mqls),0) * 100, 1) AS engaged_rate_pct,
       ROUND(SUM(s1_conversions) / NULLIF(SUM(total_mqls),0) * 100, 1) AS s1_rate_pct
FROM mql_funnel_weekly
WHERE sales_motion = 'inbound'
GROUP BY 1, 2 ORDER BY mqls DESC;

-- Q4b2: Inbound core vs non-core (quality cut on its own)
SELECT core_noncore,
       SUM(total_mqls)      AS mqls,
       SUM(s1_conversions)  AS s1,
       ROUND(SUM(s1_conversions) / NULLIF(SUM(total_mqls),0) * 100, 1) AS s1_rate_pct
FROM mql_funnel_weekly
WHERE sales_motion = 'inbound'
GROUP BY 1 ORDER BY mqls DESC;

-- Q4b3: Inbound vs outbound (outbound is SDR-driven, not mindshare)
SELECT sales_motion,
       SUM(total_mqls)      AS mqls,
       SUM(s1_conversions)  AS s1,
       ROUND(SUM(s1_conversions) / NULLIF(SUM(total_mqls),0) * 100, 1) AS s1_rate_pct
FROM mql_funnel_weekly
GROUP BY 1 ORDER BY mqls DESC;

-- Q4d: Weekly correlation — warm visits vs inbound core MQLs (brand drives base)
WITH wk_warm AS (
  SELECT week_start, SUM(total_visits) AS warm_visits
  FROM web_visits_weekly
  WHERE attribution_channel_group IN ('Direct','Organic')
  GROUP BY week_start
),
wk_core AS (
  SELECT week_start, SUM(total_mqls) AS core_mqls
  FROM mql_funnel_weekly
  WHERE sales_motion = 'inbound' AND core_noncore = 'core'
  GROUP BY week_start
)
SELECT ROUND(CORR(warm_visits, core_mqls), 2) AS corr_warm_core, COUNT(*) AS n_weeks
FROM wk_warm JOIN wk_core USING (week_start);

-- Q4c: Fin brand-moment natural experiment (Jun–Aug '25 vs Sep–Nov '25)
SELECT IFF(week_start < '2025-09-01', 'pre (Jun-Aug)', 'post (Sep-Nov)') AS period,
       SUM(total_mqls) AS inbound_mqls, SUM(s1_conversions) AS s1,
       ROUND(SUM(s1_conversions) / SUM(total_mqls) * 100, 1) AS s1_rate_pct
FROM mql_funnel_weekly
WHERE sales_motion = 'inbound' AND week_start BETWEEN '2025-06-01' AND '2025-11-30'
GROUP BY 1;

SELECT IFF(week_start < '2025-09-01', 'pre', 'post') AS period,
       ROUND(AVG(wk_visits)) AS avg_weekly_fin_visits
FROM (SELECT week_start, SUM(total_visits) AS wk_visits
      FROM web_visits_weekly
      WHERE visit_path_category LIKE 'Fin%'
      GROUP BY 1)
GROUP BY 1;

-- ---------------------------------------------------------------------------
-- Q5: Region opportunity map — warm traffic share vs inbound MQL / S1 share
-- ---------------------------------------------------------------------------
WITH traffic AS (
  SELECT region, SUM(total_visits) AS warm_visits
  FROM web_visits_weekly
  WHERE attribution_channel_group IN ('Direct','Organic') AND region <> 'Unknown'
  GROUP BY 1
),
pipe AS (
  SELECT region, SUM(total_mqls) AS mqls, SUM(s1_conversions) AS s1
  FROM mql_funnel_weekly
  WHERE sales_motion = 'inbound' AND region <> 'Unknown'
  GROUP BY 1
)
SELECT t.region,
       ROUND(warm_visits / SUM(warm_visits) OVER () * 100, 1) AS warm_traffic_share_pct,
       ROUND(mqls        / SUM(mqls)        OVER () * 100, 1) AS mql_share_pct,
       ROUND(s1          / SUM(s1)          OVER () * 100, 1) AS s1_share_pct,
       ROUND(s1 / NULLIF(mqls,0) * 100, 1)                    AS s1_rate_pct
FROM traffic t JOIN pipe p USING (region)
ORDER BY warm_traffic_share_pct DESC;

-- Q5b: Segment quality + YoY
SELECT company_reporting_segment,
       SUM(total_mqls) AS mqls,
       ROUND(SUM(s1_conversions) / NULLIF(SUM(total_mqls),0) * 100, 1) AS s1_rate_pct,
       SUM(IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26', total_mqls, 0)) AS mqls_y1,
       SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25', total_mqls, 0)) AS mqls_y2,
       ROUND(mqls_y2 / NULLIF(mqls_y1,0) * 100 - 100, 1)                         AS mql_yoy_pct
FROM mql_funnel_weekly
WHERE sales_motion = 'inbound'
GROUP BY 1 ORDER BY mqls DESC;

-- ---------------------------------------------------------------------------
-- Q6: FY27 recommendation math
--     No spend data in the extract (assumption A8): Paid budget is proxied
--     from Paid visits at a $5.50 CPC benchmark. The reallocation models a
--     15% Paid-budget shift into brand, expected to recover 50% of the
--     inbound-MQL decline (MQLs track warm traffic, see Q4d). 26-week windows
--     are annualized x2.
-- ---------------------------------------------------------------------------
WITH paid AS (
  SELECT SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25', total_visits, 0)) AS paid_y2_26wk
  FROM web_visits_weekly WHERE attribution_channel_group = 'Paid'
),
warm AS (
  SELECT SUM(IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26', total_visits, 0)) AS warm_y1,
         SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25', total_visits, 0)) AS warm_y2
  FROM web_visits_weekly WHERE attribution_channel_group IN ('Direct','Organic')
),
inb AS (
  SELECT SUM(IFF(week_start BETWEEN '2024-12-02' AND '2025-05-26', total_mqls, 0))     AS mql_y1,
         SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25', total_mqls, 0))     AS mql_y2,
         SUM(IFF(week_start BETWEEN '2025-12-01' AND '2026-05-25', s1_conversions, 0)) AS s1_y2
  FROM mql_funnel_weekly WHERE sales_motion = 'inbound'
)
SELECT
  paid_y2_26wk * 2                                                AS paid_annual_visits,
  ROUND(paid_y2_26wk * 2 * 5.50)                                  AS paid_budget_proxy_usd,
  ROUND(paid_y2_26wk * 2 * 5.50 * 0.15)                          AS shift_15pct_usd,
  ROUND(warm_y2 / NULLIF(warm_y1,0) * 100 - 100, 1)              AS warm_visit_yoy_pct,
  ROUND((mql_y1 - mql_y2) * 0.5)                                 AS mql_lift_26wk,
  ROUND((mql_y1 - mql_y2) * 0.5 * (s1_y2 / NULLIF(mql_y2,0)) * 2) AS s1_lift_annual,
  s1_y2 * 2                                                      AS s1_runrate_annual
FROM paid, warm, inb;
