-- Additive line metrics and the customer RFM snapshot.
-- Gross profit is net revenue minus COGS after each component is rounded to cents.
-- Returned lines contribute zero revenue and zero COGS (refunded and restocked).
-- returned_amount is the refund, kept so return dollars are visible without
-- subtracting them twice from net revenue.

CREATE VIEW vw_sales_lines AS
SELECT
  sales_line_id,
  order_id,
  order_date,
  store_id,
  product_id,
  customer_id,
  quantity,
  unit_list_price,
  discount_rate,
  unit_cost,
  is_returned,
  list_revenue,
  kept_list_revenue,
  discount_amount,
  net_revenue,
  cogs,
  ROUND(net_revenue - cogs, 2) AS gross_profit,
  returned_amount
FROM (
  SELECT
    sales_line_id,
    order_id,
    order_date,
    store_id,
    product_id,
    customer_id,
    quantity,
    unit_list_price,
    discount_rate,
    unit_cost,
    is_returned,
    ROUND(quantity * unit_list_price, 2) AS list_revenue,
    CASE
      WHEN is_returned = 1 THEN 0
      ELSE ROUND(quantity * unit_list_price, 2)
    END AS kept_list_revenue,
    CASE
      WHEN is_returned = 1 THEN 0
      ELSE ROUND(ROUND(quantity * unit_list_price, 2) * discount_rate, 2)
    END AS discount_amount,
    CASE
      WHEN is_returned = 1 THEN 0
      ELSE ROUND(
        ROUND(quantity * unit_list_price, 2)
        - ROUND(ROUND(quantity * unit_list_price, 2) * discount_rate, 2),
        2
      )
    END AS net_revenue,
    CASE
      WHEN is_returned = 1 THEN 0
      ELSE ROUND(quantity * unit_cost, 2)
    END AS cogs,
    CASE
      WHEN is_returned = 1 THEN ROUND(
        ROUND(quantity * unit_list_price, 2)
        - ROUND(ROUND(quantity * unit_list_price, 2) * discount_rate, 2),
        2
      )
      ELSE 0
    END AS returned_amount
  FROM fact_sales
);

CREATE VIEW vw_sales_enriched AS
SELECT
  v.*,
  d.year,
  d.quarter,
  d.month,
  d.month_name,
  d.year_month,
  d.day_name,
  d.is_weekend,
  s.store_name,
  s.city AS store_city,
  s.state AS store_state,
  s.region AS store_region,
  p.sku,
  p.product_name,
  p.category,
  p.subcategory,
  c.customer_name,
  c.segment,
  c.region AS customer_region
FROM vw_sales_lines AS v
JOIN dim_date AS d ON d.full_date = v.order_date
JOIN dim_store AS s ON s.store_id = v.store_id
JOIN dim_product AS p ON p.product_id = v.product_id
JOIN dim_customer AS c ON c.customer_id = v.customer_id;

-- RFM is a snapshot through the latest order date in the warehouse.
-- Rebuild it by rerunning the pipeline. Do not treat the scores as live.
-- Recency score is inverted: 5 = most recent. Frequency and monetary: 5 = highest.
CREATE VIEW vw_customer_rfm AS
WITH metrics AS (
  SELECT
    customer_id,
    CAST(
      julianday((SELECT MAX(order_date) FROM fact_sales)) - julianday(MAX(order_date))
      AS INTEGER
    ) AS recency_days,
    COUNT(DISTINCT order_id) AS frequency,
    ROUND(SUM(
      CASE
        WHEN is_returned = 0 THEN
          ROUND(
            ROUND(quantity * unit_list_price, 2)
            - ROUND(ROUND(quantity * unit_list_price, 2) * discount_rate, 2),
            2
          )
        ELSE 0
      END
    ), 2) AS monetary
  FROM fact_sales
  GROUP BY customer_id
),
scored AS (
  SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    6 - NTILE(5) OVER (ORDER BY recency_days ASC, customer_id) AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC, customer_id) AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC, customer_id) AS m_score
  FROM metrics
)
SELECT
  customer_id,
  recency_days,
  frequency,
  monetary,
  r_score,
  f_score,
  m_score,
  CASE
    WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
    WHEN r_score >= 3 AND f_score >= 4 THEN 'Loyal'
    WHEN r_score >= 3 AND m_score >= 4 THEN 'Big spenders'
    WHEN r_score >= 4 AND f_score <= 2 THEN 'Promising'
    WHEN r_score <= 2 AND (f_score >= 3 OR m_score >= 3) THEN 'At risk'
    WHEN r_score <= 2 THEN 'Hibernating'
    ELSE 'Needs attention'
  END AS rfm_segment
FROM scored;

CREATE VIEW vw_dim_customer AS
SELECT
  c.customer_id,
  c.customer_name,
  c.segment,
  c.city,
  c.state,
  c.region,
  c.first_order_date,
  r.recency_days,
  r.frequency,
  r.monetary,
  r.r_score,
  r.f_score,
  r.m_score,
  r.rfm_segment
FROM dim_customer AS c
LEFT JOIN vw_customer_rfm AS r ON r.customer_id = c.customer_id;
