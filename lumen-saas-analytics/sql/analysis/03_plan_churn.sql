-- Question: Which plan loses logos fastest?
-- Pooled monthly logo churn over the trailing 12 months.
-- Denominator is account-months that entered the month with MRR, not a unique logo count.
-- This is not 12-month logo retention. That is computed on a fixed cohort in Python.

SELECT
  p.plan_name,
  p.tier_rank,
  SUM(CASE WHEN s.movement = 'Churn' THEN 1 ELSE 0 END) AS churned_logos,
  SUM(CASE WHEN s.prior_mrr > 0 THEN 1 ELSE 0 END) AS beginning_account_months,
  ROUND(
    1.0 * SUM(CASE WHEN s.movement = 'Churn' THEN 1 ELSE 0 END)
      / NULLIF(SUM(CASE WHEN s.prior_mrr > 0 THEN 1 ELSE 0 END), 0),
    4
  ) AS monthly_logo_churn
FROM fact_subscription_month AS s
JOIN dim_plan AS p ON p.plan_id = s.plan_id
WHERE s.month_start > date('__AS_OF_MONTH__', '-12 months')
  AND s.month_start <= '__AS_OF_MONTH__'
GROUP BY p.plan_name, p.tier_rank
ORDER BY p.tier_rank;
