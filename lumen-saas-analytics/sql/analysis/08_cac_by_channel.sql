-- Question: What does a new logo cost, by acquisition channel?
-- CAC = channel spend / new logos signed up in the same months.
-- This is a blended acquisition cost. It is not a paid-media CAC that excludes organic.

WITH new_logos AS (
  SELECT
    date(signup_date, 'start of month') AS month_start,
    channel_id,
    COUNT(*) AS new_logos
  FROM dim_account
  GROUP BY 1, 2
)
SELECT
  c.channel_name,
  c.channel_group,
  ROUND(SUM(m.spend), 2) AS spend,
  COALESCE(SUM(n.new_logos), 0) AS new_logos,
  ROUND(SUM(m.spend) / NULLIF(SUM(n.new_logos), 0), 2) AS cac
FROM fact_marketing_spend AS m
JOIN dim_channel AS c ON c.channel_id = m.channel_id
LEFT JOIN new_logos AS n
  ON n.month_start = m.month_start
 AND n.channel_id = m.channel_id
GROUP BY c.channel_name, c.channel_group
ORDER BY cac DESC;
