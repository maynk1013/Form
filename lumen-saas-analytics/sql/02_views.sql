-- Usage with a next-month churn flag.
-- The flag is a refresh-time label for analysis. It is not a source-system field.
-- Months that have no following month in the warehouse are left null so they
-- are not counted as retained.

CREATE VIEW vw_usage_health AS
SELECT
  u.account_id,
  u.month_start,
  u.active_users,
  u.events,
  u.adoption_score,
  s.plan_id,
  s.mrr,
  s.movement,
  CASE
    WHEN date(u.month_start, '+1 month') > (SELECT MAX(month_start) FROM fact_subscription_month)
      THEN NULL
    WHEN n.movement = 'Churn' THEN 1
    ELSE 0
  END AS churned_next_month
FROM fact_usage_monthly AS u
JOIN fact_subscription_month AS s
  ON s.account_id = u.account_id
 AND s.month_start = u.month_start
LEFT JOIN fact_subscription_month AS n
  ON n.account_id = u.account_id
 AND n.month_start = date(u.month_start, '+1 month');

CREATE VIEW vw_subscription AS
SELECT
  s.subscription_month_id,
  s.account_id,
  s.month_start,
  s.plan_id,
  s.seats,
  s.mrr,
  s.prior_mrr,
  s.movement,
  a.account_name,
  a.industry,
  a.region,
  a.employee_band,
  a.signup_date,
  a.channel_id,
  p.plan_name,
  p.tier_rank,
  p.monthly_price_per_seat,
  c.channel_name,
  c.channel_group
FROM fact_subscription_month AS s
JOIN dim_account AS a ON a.account_id = s.account_id
JOIN dim_plan AS p ON p.plan_id = s.plan_id
JOIN dim_channel AS c ON c.channel_id = a.channel_id;
