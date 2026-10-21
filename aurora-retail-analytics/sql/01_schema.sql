-- Aurora Home & Living warehouse schema (SQLite).
-- Grain of fact_sales is one order line.
-- Money inputs stay on the fact because selling price can change over time.
-- Ratios are not stored. See sql/02_views.sql and docs/metric-definitions.md.

PRAGMA foreign_keys = ON;

CREATE TABLE dim_date (
  date_key INTEGER PRIMARY KEY,
  full_date TEXT NOT NULL UNIQUE,
  year INTEGER NOT NULL,
  quarter INTEGER NOT NULL,
  month INTEGER NOT NULL,
  month_name TEXT NOT NULL,
  year_month TEXT NOT NULL,
  day INTEGER NOT NULL,
  day_name TEXT NOT NULL,
  day_of_week INTEGER NOT NULL,
  week_of_year INTEGER NOT NULL,
  is_weekend INTEGER NOT NULL CHECK (is_weekend IN (0, 1))
);

CREATE TABLE dim_store (
  store_id INTEGER PRIMARY KEY,
  store_name TEXT NOT NULL,
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  region TEXT NOT NULL,
  opened_date TEXT NOT NULL,
  sq_ft INTEGER NOT NULL
);

CREATE TABLE dim_product (
  product_id INTEGER PRIMARY KEY,
  sku TEXT NOT NULL UNIQUE,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL,
  subcategory TEXT NOT NULL,
  unit_cost REAL NOT NULL CHECK (unit_cost >= 0),
  list_price REAL NOT NULL CHECK (list_price > 0)
);

CREATE TABLE dim_customer (
  customer_id INTEGER PRIMARY KEY,
  customer_name TEXT NOT NULL,
  segment TEXT NOT NULL CHECK (segment IN ('Consumer', 'Corporate', 'Home Office')),
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  region TEXT NOT NULL,
  first_order_date TEXT NOT NULL
);

CREATE TABLE fact_sales (
  sales_line_id INTEGER PRIMARY KEY,
  order_id TEXT NOT NULL,
  order_date TEXT NOT NULL,
  store_id INTEGER NOT NULL REFERENCES dim_store (store_id),
  product_id INTEGER NOT NULL REFERENCES dim_product (product_id),
  customer_id INTEGER NOT NULL REFERENCES dim_customer (customer_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_list_price REAL NOT NULL CHECK (unit_list_price > 0),
  discount_rate REAL NOT NULL CHECK (discount_rate >= 0 AND discount_rate < 1),
  unit_cost REAL NOT NULL CHECK (unit_cost >= 0),
  is_returned INTEGER NOT NULL CHECK (is_returned IN (0, 1))
);

CREATE TABLE fact_store_target (
  store_id INTEGER NOT NULL REFERENCES dim_store (store_id),
  month_start TEXT NOT NULL,
  revenue_target REAL NOT NULL CHECK (revenue_target > 0),
  PRIMARY KEY (store_id, month_start)
);

CREATE INDEX idx_fact_sales_order_date ON fact_sales (order_date);
CREATE INDEX idx_fact_sales_store ON fact_sales (store_id);
CREATE INDEX idx_fact_sales_product ON fact_sales (product_id);
CREATE INDEX idx_fact_sales_customer ON fact_sales (customer_id);
CREATE INDEX idx_fact_sales_order ON fact_sales (order_id);
