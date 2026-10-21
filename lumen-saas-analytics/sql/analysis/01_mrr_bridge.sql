-- Question: Does ending MRR equal beginning plus the movements?
-- Grain: month. Expansion and contraction are the dollar change, not the new MRR.
-- beginning_mrr is SUM(prior_mrr). New and reactivated logos contribute prior_mrr of 0.

SELECT
  month_start,
  ROUND(SUM(prior_mrr), 2) AS beginning_mrr,
  ROUND(SUM(CASE WHEN movement = 'New' THEN mrr ELSE 0 END), 2) AS new_mrr,
  ROUND(SUM(CASE WHEN movement = 'Reactivation' THEN mrr ELSE 0 END), 2) AS reactivation_mrr,
  ROUND(SUM(CASE WHEN movement = 'Expansion' THEN mrr - prior_mrr ELSE 0 END), 2) AS expansion_mrr,
  ROUND(SUM(CASE WHEN movement = 'Contraction' THEN prior_mrr - mrr ELSE 0 END), 2) AS contraction_mrr,
  ROUND(SUM(CASE WHEN movement = 'Churn' THEN prior_mrr ELSE 0 END), 2) AS churned_mrr,
  ROUND(SUM(mrr), 2) AS ending_mrr,
  SUM(CASE WHEN movement = 'New' THEN 1 ELSE 0 END) AS new_logos,
  SUM(CASE WHEN movement = 'Reactivation' THEN 1 ELSE 0 END) AS reactivated_logos,
  SUM(CASE WHEN movement = 'Churn' THEN 1 ELSE 0 END) AS churned_logos,
  SUM(CASE WHEN prior_mrr > 0 THEN 1 ELSE 0 END) AS beginning_logos,
  SUM(CASE WHEN mrr > 0 THEN 1 ELSE 0 END) AS ending_logos
FROM fact_subscription_month
GROUP BY month_start
ORDER BY month_start;
