-- Question: Does low adoption show up before next month's churn?
-- Quartiles are computed inside each month, so a quiet January is not compared
-- with a busy September. Q1 is the lowest adoption score.
-- The last warehouse month is excluded because it has no next month.

WITH scored AS (
  SELECT
    u.adoption_score,
    NTILE(4) OVER (PARTITION BY u.month_start ORDER BY u.adoption_score, u.account_id) AS usage_quartile,
    CASE WHEN n.movement = 'Churn' THEN 1 ELSE 0 END AS churned_next_month
  FROM fact_usage_monthly AS u
  JOIN fact_subscription_month AS s
    ON s.account_id = u.account_id
   AND s.month_start = u.month_start
   AND s.mrr > 0
  LEFT JOIN fact_subscription_month AS n
    ON n.account_id = u.account_id
   AND n.month_start = date(u.month_start, '+1 month')
  WHERE date(u.month_start, '+1 month') <= (SELECT MAX(month_start) FROM fact_subscription_month)
)
SELECT
  usage_quartile,
  CASE usage_quartile
    WHEN 1 THEN 'Q1 lowest'
    WHEN 2 THEN 'Q2'
    WHEN 3 THEN 'Q3'
    ELSE 'Q4 highest'
  END AS usage_band,
  COUNT(*) AS account_months,
  ROUND(AVG(churned_next_month), 4) AS next_month_churn_rate,
  ROUND(AVG(adoption_score), 1) AS avg_adoption
FROM scored
GROUP BY usage_quartile
ORDER BY usage_quartile;
