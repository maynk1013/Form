-- Question: Which industries hold the book, and which churn faster?
-- Ending MRR is the close month only, so it is not summed across the year.
-- Churn is the pooled monthly rate over the trailing 12 months.

WITH ending AS (
  SELECT
    a.industry,
    COUNT(*) AS logos,
    ROUND(SUM(s.mrr), 2) AS ending_mrr
  FROM fact_subscription_month AS s
  JOIN dim_account AS a ON a.account_id = s.account_id
  WHERE s.month_start = '__AS_OF_MONTH__'
    AND s.mrr > 0
  GROUP BY a.industry
),
churn AS (
  SELECT
    a.industry,
    ROUND(
      1.0 * SUM(CASE WHEN s.movement = 'Churn' THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN s.prior_mrr > 0 THEN 1 ELSE 0 END), 0),
      4
    ) AS monthly_logo_churn
  FROM fact_subscription_month AS s
  JOIN dim_account AS a ON a.account_id = s.account_id
  WHERE s.month_start > date('__AS_OF_MONTH__', '-12 months')
    AND s.month_start <= '__AS_OF_MONTH__'
  GROUP BY a.industry
)
SELECT
  e.industry,
  e.logos,
  e.ending_mrr,
  c.monthly_logo_churn
FROM ending AS e
JOIN churn AS c ON c.industry = e.industry
ORDER BY e.ending_mrr DESC;
