-- Question: How much of ending MRR sits in the ten largest accounts?
-- Close month, active logos only.

WITH snap AS (
  SELECT account_id, mrr
  FROM fact_subscription_month
  WHERE month_start = '__AS_OF_MONTH__'
    AND mrr > 0
),
ranked AS (
  SELECT
    mrr,
    ROW_NUMBER() OVER (ORDER BY mrr DESC, account_id) AS revenue_rank,
    SUM(mrr) OVER () AS total_mrr
  FROM snap
)
SELECT
  ROUND(SUM(CASE WHEN revenue_rank <= 10 THEN mrr ELSE 0 END) / MAX(total_mrr), 4) AS top_10_mrr_share,
  ROUND(MAX(total_mrr), 2) AS ending_mrr,
  COUNT(*) AS active_logos
FROM ranked;
