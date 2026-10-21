# Build the Aurora report in Power BI

Power BI Desktop is a Windows application. On a Mac, open the executive report at `outputs/executive_report.html` and use the SQLite warehouse. Build this report in Power BI Desktop, or in the Power BI service from a machine that can publish it.

The numbers in the report should match `outputs/FINDINGS.md`. If they do not, a relationship or a filter is wrong. Fix that before formatting.

## 1. Load the model

1. File → Options → Data Load → turn off **Auto date/time**. The model has one date table.
2. Home → Get data → Text/CSV. Import each file in `powerbi/data` as its own table. Do not use Get data → Folder → Combine.
3. Set these column types:
   - `dim_date[full_date]` and `fact_sales[order_date]` and `fact_store_target[month_start]` and `dim_customer[first_order_date]` → Date
   - every money column → Fixed decimal number
   - `is_returned` and `is_weekend` → Whole number
4. View → Themes → Browse for themes → `powerbi/theme.json`.

## 2. Relationships

All relationships are many-to-one, single direction, from the fact to the dimension.

| From | To |
| --- | --- |
| `fact_sales[order_date]` | `dim_date[full_date]` |
| `fact_sales[store_id]` | `dim_store[store_id]` |
| `fact_sales[product_id]` | `dim_product[product_id]` |
| `fact_sales[customer_id]` | `dim_customer[customer_id]` |
| `fact_store_target[store_id]` | `dim_store[store_id]` |
| `fact_store_target[month_start]` | `dim_date[full_date]` |

`fact_store_target` only matches the first day of each month. A month filter on `dim_date` still hits that row, because the filter includes the first.

Do not create a relationship from `dim_customer[region]` to `dim_store`. Customer region is home region. Store region is where the register rang. They are different questions.

Mark `dim_date` as a date table on `full_date`.

Sort `month_name` by `month`. Sort `day_name` by `day_of_week`.

## 3. Measures

Create the measures in `measures.dax`. Do not drop `gross_margin` onto a visual and let Power BI average it. Margin, AOV, return rate, attainment, and year-over-year are measures.

## 4. Pages

**Executive.** Cards: Net Revenue, YTD Comparable YoY %, Gross Margin %, AOV, Line Return Rate, Plan Attainment. Clustered column chart of Net Revenue by `year_month`, with Revenue Target as a line. Slicers: year, region, segment.

**Stores.** Bar chart of Plan Attainment by `store_name`. Matrix: store, region, Net Revenue, Revenue Target, Plan Variance, Gross Margin %, AOV. A map is optional; city and state are on the store.

**Assortment.** Bar of Gross Profit by category. Scatter of Gross Margin % (x) against Line Return Rate (y), details = product name, size = Net Revenue. Table of the top products by Gross Profit.

**Discount and returns.** Bar of Gross Margin % by a calculated discount band, plus Line Return Rate as a line. The band is a calculated column on `fact_sales`:

```dax
Discount Band =
SWITCH (
    TRUE (),
    fact_sales[discount_rate] = 0, "0% full price",
    fact_sales[discount_rate] <= 0.10, "1-10%",
    fact_sales[discount_rate] <= 0.20, "11-20%",
    "21%+"
)
```

**Customers.** Bar of the additive `monetary` column is the snapshot. Prefer a measure of Net Revenue by `rfm_segment` so the page still responds to the date slicer. Donut of Net Revenue by segment. Table: segment, Customers, Orders, AOV, Line Return Rate.

## 5. Check against the warehouse

With no slicers other than the full window:

- Net Revenue equals the scorecard in `outputs/FINDINGS.md`.
- YTD Comparable YoY % uses January–September only. A card of plain YoY % on the full window is a different question and will not match that figure.
- Plan Attainment stays near the scorecard. If it explodes, the target table is being filtered by a fact that does not reach it, or the relationship to the date table is inactive.

## 6. Refresh

`python run.py` rewrites the CSVs. In Power BI, Home → Refresh. The RFM columns change only when that pipeline runs.
