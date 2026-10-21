-- Question: Which 10 products contribute the most gross profit?
-- Ranked by profit, not revenue, so a high-revenue low-margin item does not win.

SELECT
  sku,
  product_name,
  category,
  ROUND(SUM(net_revenue), 2) AS net_revenue,
  ROUND(SUM(gross_profit), 2) AS gross_profit,
  ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin,
  ROUND(AVG(is_returned), 4) AS line_return_rate,
  SUM(quantity) AS units
FROM vw_sales_enriched
GROUP BY sku, product_name, category
ORDER BY gross_profit DESC
LIMIT 10;
