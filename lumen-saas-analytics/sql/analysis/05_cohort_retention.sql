-- Question: Of the logos that started in a month, what share are still paying N months later?
-- Active means mrr > 0. A cohort that has not reached a tenure has no row for it.
-- Do not fill those cells with zero.

WITH life AS (
  SELECT
    a.account_id,
    date(a.signup_date, 'start of month') AS cohort_month,
    s.month_start,
    (
      CAST(strftime('%Y', s.month_start) AS INTEGER) * 12
      + CAST(strftime('%m', s.month_start) AS INTEGER)
    ) - (
      CAST(strftime('%Y', date(a.signup_date, 'start of month')) AS INTEGER) * 12
      + CAST(strftime('%m', date(a.signup_date, 'start of month')) AS INTEGER)
    ) AS tenure_month
  FROM dim_account AS a
  JOIN fact_subscription_month AS s ON s.account_id = a.account_id
  WHERE s.mrr > 0
),
sizes AS (
  SELECT cohort_month, COUNT(DISTINCT account_id) AS cohort_size
  FROM life
  WHERE tenure_month = 0
  GROUP BY cohort_month
)
SELECT
  l.cohort_month,
  l.tenure_month,
  COUNT(DISTINCT l.account_id) AS active_logos,
  z.cohort_size,
  ROUND(1.0 * COUNT(DISTINCT l.account_id) / z.cohort_size, 4) AS logo_retention
FROM life AS l
JOIN sizes AS z ON z.cohort_month = l.cohort_month
WHERE l.tenure_month BETWEEN 0 AND 18
GROUP BY l.cohort_month, l.tenure_month
ORDER BY l.cohort_month, l.tenure_month;
