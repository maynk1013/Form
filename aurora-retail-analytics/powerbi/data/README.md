# Power BI source files

Import each CSV as its own table. Do not append them into one table.

| File | Grain |
| --- | --- |
| `dim_date.csv` | one calendar day, 2024-01-01 through 2026-12-31 |
| `dim_store.csv` | one store |
| `dim_product.csv` | one SKU |
| `dim_customer.csv` | one purchasing customer, with the RFM snapshot |
| `fact_sales.csv` | one order line, with additive money columns already resolved |
| `fact_store_target.csv` | one store-month revenue target |

`dim_customer.csv` is the only enriched dimension. RFM columns are a snapshot through the latest order date. Rerun `python run.py` to refresh them.

Build steps, relationships, and page layouts are in `../BUILD.md`.
