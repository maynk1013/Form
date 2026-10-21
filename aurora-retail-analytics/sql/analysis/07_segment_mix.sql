-- Question: How do Consumer, Corporate, and Home Office differ on value and returns?
-- Grain: customer segment. AOV uses distinct orders.

SELECT
  segment,
  COUNT(DISTINCT customer_id) AS customers,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(net_revenue), 2) AS net_revenue,
  ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin,
  ROUND(SUM(net_revenue) / COUNT(DISTINCT order_id), 2) AS aov,
  ROUND(AVG(is_returned), 4) AS line_return_rate
FROM vw_sales_enriched
GROUP BY segment
ORDER BY net_revenue DESC;
