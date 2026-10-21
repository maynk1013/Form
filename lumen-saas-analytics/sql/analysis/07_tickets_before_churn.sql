-- Question: Are accounts that churn within 60 days already opening more tickets?
-- An account-month is included only when the next two months exist in the warehouse,
-- so the close of the dataset is not labeled "stayed" just because time ran out.
-- Average tickets includes months with zero tickets. CSAT is averaged on months that had a ticket.

WITH acct_month AS (
  SELECT
    s.account_id,
    s.month_start,
    CASE
      WHEN EXISTS (
        SELECT 1
        FROM fact_subscription_month AS c
        WHERE c.account_id = s.account_id
          AND c.movement = 'Churn'
          AND c.month_start > s.month_start
          AND c.month_start <= date(s.month_start, '+2 months')
      ) THEN 1
      ELSE 0
    END AS churn_within_60_days
  FROM fact_subscription_month AS s
  WHERE s.mrr > 0
    AND date(s.month_start, '+2 months') <= '__AS_OF_MONTH__'
),
tix AS (
  SELECT
    account_id,
    date(opened_date, 'start of month') AS month_start,
    COUNT(*) AS tickets,
    AVG(csat) AS avg_csat
  FROM fact_ticket
  GROUP BY account_id, date(opened_date, 'start of month')
)
SELECT
  a.churn_within_60_days,
  COUNT(*) AS account_months,
  ROUND(AVG(COALESCE(t.tickets, 0)), 3) AS avg_tickets,
  ROUND(AVG(t.avg_csat), 3) AS avg_csat_when_ticketed
FROM acct_month AS a
LEFT JOIN tix AS t
  ON t.account_id = a.account_id
 AND t.month_start = a.month_start
GROUP BY a.churn_within_60_days
ORDER BY a.churn_within_60_days;
