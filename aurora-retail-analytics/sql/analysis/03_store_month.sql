-- Question: Which stores are ahead of the monthly revenue plan?
-- Grain: store-month, including months with no sales, so a quiet store
-- cannot disappear from attainment.
-- Attainment = net revenue / revenue target. Do not average the rates.

SELECT
  sp.store_id,
  sp.store_name,
  sp.city,
  sp.state,
  sp.region,
  sp.month_start,
  COALESCE(sa.net_revenue, 0) AS net_revenue,
  COALESCE(sa.gross_profit, 0) AS gross_profit,
  COALESCE(sa.orders, 0) AS orders,
  COALESCE(sa.units, 0) AS units,
  COALESCE(sa.returned_lines, 0) AS returned_lines,
  COALESCE(sa.lines, 0) AS lines,
  t.revenue_target,
  ROUND(COALESCE(sa.net_revenue, 0) / t.revenue_target, 4) AS target_attainment
FROM (
  SELECT
    s.store_id,
    s.store_name,
    s.city,
    s.state,
    s.region,
    m.month_start
  FROM dim_store AS s
  CROSS JOIN (
    SELECT DISTINCT date(full_date, 'start of month') AS month_start
    FROM dim_date
    WHERE full_date BETWEEN '__SALES_START__' AND '__SALES_END__'
  ) AS m
) AS sp
JOIN fact_store_target AS t
  ON t.store_id = sp.store_id
 AND t.month_start = sp.month_start
LEFT JOIN (
  SELECT
    store_id,
    date(order_date, 'start of month') AS month_start,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    COUNT(DISTINCT order_id) AS orders,
    SUM(quantity) AS units,
    SUM(is_returned) AS returned_lines,
    COUNT(*) AS lines
  FROM vw_sales_lines
  GROUP BY store_id, date(order_date, 'start of month')
) AS sa
  ON sa.store_id = sp.store_id
 AND sa.month_start = sp.month_start
ORDER BY sp.month_start, sp.store_id;
