# Metric definitions

Grain of the sales fact is one order line. Ratios are not additive. In Power BI and in SQL, compute them as a ratio of sums after filters are applied. Never average a margin column.

| Metric | Formula | Notes |
| --- | --- | --- |
| List revenue | `quantity × unit_list_price`, rounded to cents | Includes returned lines. This is the sticker value, not money kept. |
| Kept list revenue | List revenue on lines that were not returned, else 0 | Denominator for discount rate. |
| Discount amount | Kept list revenue × discount rate, rounded to cents | Zero on returned lines. |
| Net revenue | Kept list revenue − discount amount | Returned lines contribute 0. This is the revenue number. |
| COGS | `quantity × unit_cost` on kept lines, else 0 | Returned goods are treated as restocked, so the cost comes back. |
| Gross profit | Net revenue − COGS | Identity is checked to the cent in `tests/test_warehouse.py`. |
| Gross margin | Gross profit / net revenue | Blank when revenue is 0. |
| Orders | Distinct `order_id` | An order with a mix of kept and returned lines still counts once. |
| AOV | Net revenue / orders | A fully returned order lowers AOV because it stays in the count with zero revenue. |
| Line return rate | Returned lines / lines | This is not an order-level return rate. |
| Returned amount | The refund on returned lines | Not subtracted again. Net revenue is already zero on those lines. |
| Revenue target | Store-month plan from `fact_store_target` | Independent of actuals. See methodology. |
| Plan attainment | Net revenue / revenue target | Sum both sides first. Do not average monthly attainment. |
| Comparable YTD | January–September of each year | Full-year 2025 is not compared with a partial 2026. |
| YoY % | (current − prior) / prior | Prior year uses the date table, including 2024 dates that have no sales, so 2025 prior-year cards stay blank instead of looking like a data error. |
| Recency | Days between the customer's last order and the latest order in the warehouse | 5 is the most recent quintile. |
| Frequency | Distinct orders | 5 is the highest quintile. |
| Monetary | Net revenue | 5 is the highest quintile. |
| RFM segment | Rule in `sql/02_views.sql` | Snapshot. It does not change when a Power BI slicer changes. |

### RFM rules

Evaluated in this order:

1. Champions — R, F, and M all 4 or 5
2. Loyal — R at least 3 and F at least 4
3. Big spenders — R at least 3 and M at least 4
4. Promising — R at least 4 and F at most 2
5. At risk — R at most 2, and F or M at least 3
6. Hibernating — R at most 2
7. Needs attention — everyone else who has purchased

`dim_customer` contains only customers with at least one order in the window.
