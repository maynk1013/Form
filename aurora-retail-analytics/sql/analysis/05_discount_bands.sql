-- Question: Do deeper discounts pay for themselves after margin and returns?
-- Grain: order line, banded by the discount booked on that line.
-- avg_quantity shows whether the discount bought extra units.

SELECT
  CASE
    WHEN discount_rate = 0 THEN '0% full price'
    WHEN discount_rate <= 0.10 THEN '1-10%'
    WHEN discount_rate <= 0.20 THEN '11-20%'
    ELSE '21%+'
  END AS discount_band,
  CASE
    WHEN discount_rate = 0 THEN 1
    WHEN discount_rate <= 0.10 THEN 2
    WHEN discount_rate <= 0.20 THEN 3
    ELSE 4
  END AS band_order,
  COUNT(*) AS lines,
  ROUND(SUM(net_revenue), 2) AS net_revenue,
  ROUND(SUM(gross_profit), 2) AS gross_profit,
  ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin,
  ROUND(AVG(is_returned), 4) AS line_return_rate,
  ROUND(AVG(quantity), 2) AS avg_quantity
FROM vw_sales_lines
GROUP BY 1, 2
ORDER BY band_order;
