-- Question: Is 2026 ahead of 2025 on a like-for-like calendar?
-- Only January–September is compared. Full-year 2025 is not compared with
-- a partial 2026.

SELECT
  d.month,
  d.month_name,
  ROUND(SUM(CASE WHEN d.year = 2025 THEN v.net_revenue ELSE 0 END), 2) AS net_revenue_2025,
  ROUND(SUM(CASE WHEN d.year = 2026 THEN v.net_revenue ELSE 0 END), 2) AS net_revenue_2026,
  ROUND(SUM(CASE WHEN d.year = 2025 THEN v.gross_profit ELSE 0 END), 2) AS gross_profit_2025,
  ROUND(SUM(CASE WHEN d.year = 2026 THEN v.gross_profit ELSE 0 END), 2) AS gross_profit_2026
FROM vw_sales_lines AS v
JOIN dim_date AS d ON d.full_date = v.order_date
WHERE d.month BETWEEN 1 AND 9
GROUP BY d.month, d.month_name
ORDER BY d.month;
