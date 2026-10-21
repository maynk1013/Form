-- Question: What does the live book look like at the close, by plan?
-- Active logos only. Churn rows in the close month have mrr of 0 and are excluded.
-- ARPA is ending MRR / logos. Do not average a stored ARPA.

SELECT
  p.plan_name,
  p.tier_rank,
  COUNT(*) AS logos,
  ROUND(SUM(s.mrr), 2) AS ending_mrr,
  ROUND(AVG(s.seats), 1) AS avg_seats,
  ROUND(SUM(s.mrr) / COUNT(*), 2) AS arpa
FROM fact_subscription_month AS s
JOIN dim_plan AS p ON p.plan_id = s.plan_id
WHERE s.month_start = '__AS_OF_MONTH__'
  AND s.mrr > 0
GROUP BY p.plan_name, p.tier_rank
ORDER BY p.tier_rank;
