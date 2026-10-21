-- Question: Are weekend baskets different from weekday baskets?
-- Day type comes from the date dimension, not from a hardcoded list of dates.

SELECT
  CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(net_revenue), 2) AS net_revenue,
  ROUND(SUM(net_revenue) / COUNT(DISTINCT order_id), 2) AS aov,
  ROUND(AVG(is_returned), 4) AS line_return_rate
FROM vw_sales_enriched
GROUP BY day_type
ORDER BY day_type;
