-- Question: What share of customers produces 80% of net revenue?
-- One row per customer with a running share. The Python report reads the
-- first row where cumulative_revenue_share crosses 0.80.

WITH cust AS (
  SELECT
    customer_id,
    ROUND(SUM(net_revenue), 2) AS net_revenue
  FROM vw_sales_lines
  GROUP BY customer_id
  HAVING net_revenue > 0
),
ranked AS (
  SELECT
    customer_id,
    net_revenue,
    ROW_NUMBER() OVER (ORDER BY net_revenue DESC, customer_id) AS rev_rank,
    COUNT(*) OVER () AS customers,
    SUM(net_revenue) OVER (ORDER BY net_revenue DESC, customer_id) AS cumulative_revenue,
    SUM(net_revenue) OVER () AS total_revenue
  FROM cust
)
SELECT
  rev_rank,
  customer_id,
  net_revenue,
  customers,
  ROUND(cumulative_revenue / total_revenue, 6) AS cumulative_revenue_share,
  ROUND(1.0 * rev_rank / customers, 6) AS customer_share
FROM ranked
ORDER BY rev_rank;
