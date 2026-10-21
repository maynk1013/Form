# Data dictionary

SQLite file: `data/aurora.db`. Power BI copies: `powerbi/data`.

## dim_date

One row per calendar day from 2024-01-01 through 2026-12-31. The extra year before sales start is there so prior-year time intelligence has dates to land on.

| Column | Meaning |
| --- | --- |
| date_key | `YYYYMMDD` integer key |
| full_date | ISO date. This is the date-table column. |
| year, quarter, month | Calendar parts. Fiscal year is the calendar year. |
| month_name | English month. Sort by `month`, not alphabetically. |
| year_month | `YYYY-MM`, safe to sort as text |
| day_name | Sort by `day_of_week` (Monday = 1) |
| is_weekend | Saturday or Sunday |

## dim_store

Twelve Aurora stores. All opened before the sales window, so every store is comparable for the full period. `sq_ft` is descriptive and is not used in a productivity KPI.

## dim_product

Thirty catalog SKUs. `unit_cost` and `list_price` are the current catalog. The fact also stores the cost and price used on the line, which is what margin uses.

## dim_customer

Purchasing customers only. `region` is where the customer lives, not where every order was rung. `first_order_date` is the earliest order in this window, not a lifetime start date from before January 2025.

RFM columns on the Power BI extract come from `vw_dim_customer`.

## fact_sales

One row per order line.

| Column | Meaning |
| --- | --- |
| order_id | Groups lines into a basket. Format `SO-100001`. |
| order_date | Register date. |
| quantity | Units on the line. Always positive, including returns. |
| discount_rate | Share taken off list price. `0.10` means 10% off. |
| is_returned | 1 if the line was refunded and restocked. |

Money columns live on `vw_sales_lines` and in `fact_sales.csv`. They are defined in `docs/metric-definitions.md`.

## fact_store_target

One row per store per month from January 2025 through September 2026. `revenue_target` is the net-revenue plan for that store-month. It is an input, not a calculation from actual sales.
