-- Question: How much historical spend sits with customers who have gone quiet?
-- Snapshot through the latest order date. See vw_customer_rfm for the rules.
-- monetary is net revenue, so this is spend kept after returns.

SELECT
  rfm_segment,
  COUNT(*) AS customers,
  ROUND(SUM(monetary), 2) AS net_revenue,
  ROUND(AVG(recency_days), 1) AS avg_recency_days,
  ROUND(AVG(frequency), 2) AS avg_orders,
  ROUND(AVG(monetary), 2) AS avg_monetary
FROM vw_customer_rfm
GROUP BY rfm_segment
ORDER BY net_revenue DESC;
