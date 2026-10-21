-- Question: Where is gross profit actually earned, and which category comes back?
-- Grain: product category. Margin is profit / revenue, not an average of line margins.

SELECT
  category,
  ROUND(SUM(net_revenue), 2) AS net_revenue,
  ROUND(SUM(gross_profit), 2) AS gross_profit,
  ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin,
  ROUND(AVG(is_returned), 4) AS line_return_rate,
  ROUND(SUM(discount_amount) / NULLIF(SUM(kept_list_revenue), 0), 4) AS discount_rate,
  SUM(quantity) AS units,
  COUNT(DISTINCT order_id) AS orders
FROM vw_sales_enriched
GROUP BY category
ORDER BY gross_profit DESC;
