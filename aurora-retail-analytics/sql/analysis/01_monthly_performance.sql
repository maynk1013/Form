-- Question: How did revenue, margin, basket size, and returns move each month?
-- Grain: calendar month. Orders are distinct inside the month, so summing
-- orders across months equals company orders (an order has one date).

SELECT
  d.year,
  d.month,
  d.year_month,
  d.month_name,
  ROUND(SUM(v.net_revenue), 2) AS net_revenue,
  ROUND(SUM(v.gross_profit), 2) AS gross_profit,
  ROUND(SUM(v.gross_profit) / NULLIF(SUM(v.net_revenue), 0), 4) AS gross_margin,
  COUNT(DISTINCT v.order_id) AS orders,
  ROUND(SUM(v.net_revenue) / COUNT(DISTINCT v.order_id), 2) AS aov,
  SUM(v.quantity) AS units,
  ROUND(AVG(v.is_returned), 4) AS line_return_rate,
  ROUND(SUM(v.discount_amount), 2) AS discount_amount,
  ROUND(SUM(v.discount_amount) / NULLIF(SUM(v.kept_list_revenue), 0), 4) AS discount_rate
FROM vw_sales_lines AS v
JOIN dim_date AS d ON d.full_date = v.order_date
GROUP BY d.year, d.month, d.year_month, d.month_name
ORDER BY d.year_month;
