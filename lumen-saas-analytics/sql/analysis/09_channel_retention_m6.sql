-- Question: Which channels still have the logo six months later?
-- Cohorts that have not had six months yet are excluded, so a recent paid push
-- cannot look loyal just because it has not had time to churn.

SELECT
  ch.channel_name,
  ch.channel_group,
  COUNT(*) AS matured_logos,
  SUM(CASE WHEN COALESCE(s.mrr, 0) > 0 THEN 1 ELSE 0 END) AS retained_logos,
  ROUND(AVG(CASE WHEN COALESCE(s.mrr, 0) > 0 THEN 1.0 ELSE 0.0 END), 4) AS logo_retention_m6
FROM dim_account AS a
JOIN dim_channel AS ch ON ch.channel_id = a.channel_id
LEFT JOIN fact_subscription_month AS s
  ON s.account_id = a.account_id
 AND s.month_start = date(date(a.signup_date, 'start of month'), '+6 months')
WHERE date(a.signup_date, 'start of month') <= date('__AS_OF_MONTH__', '-6 months')
GROUP BY ch.channel_name, ch.channel_group
ORDER BY logo_retention_m6 DESC;
