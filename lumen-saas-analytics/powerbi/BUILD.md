# Build the Lumen report in Power BI

Power BI Desktop is a Windows application. On a Mac, open `outputs/executive_report.html`. Build this model in Power BI Desktop, or publish it through the Power BI service.

The close figures have to match `outputs/FINDINGS.md` before you format anything. `Bridge Check` has to be 0 on every month.

## 1. Load

1. File → Options → Data Load → turn **Auto date/time** off.
2. Import each CSV in `powerbi/data` as its own table.
3. Dates: `full_date`, `month_start`, `signup_date`, `opened_date`, `window_start`, `window_end`.
4. Money columns: Fixed decimal number.
5. Apply `powerbi/theme.json`.

## 2. Relationships

Many-to-one, single direction, fact to dimension.

| From | To |
| --- | --- |
| `fact_subscription_month[account_id]` | `dim_account[account_id]` |
| `fact_subscription_month[plan_id]` | `dim_plan[plan_id]` |
| `fact_subscription_month[month_start]` | `dim_date[full_date]` |
| `fact_usage[account_id]` | `dim_account[account_id]` |
| `fact_usage[month_start]` | `dim_date[full_date]` |
| `fact_usage[plan_id]` | `dim_plan[plan_id]` |
| `fact_ticket[account_id]` | `dim_account[account_id]` |
| `fact_ticket[opened_date]` | `dim_date[full_date]` |
| `fact_marketing_spend[channel_id]` | `dim_channel[channel_id]` |
| `fact_marketing_spend[month_start]` | `dim_date[full_date]` |
| `dim_account[channel_id]` | `dim_channel[channel_id]` |
| `dim_account[signup_date]` | `dim_date[full_date]` |

`metric_trailing_twelve_months` has no relationship. That is intentional.

Do not relate `fact_usage` to `fact_subscription_month` directly. They meet through account and date. A second relationship would be ambiguous.

Mark `dim_date` as a date table on `full_date`. Sort `month_name` by `month`. Sort `day_name` by `day_of_week`. Sort `plan_name` by `tier_rank`.

The subscription and usage facts only land on the first of each month. A filter on September still hits 1 September, so the monthly measure is correct. Put `year_month` on chart axes, not `day`.

## 3. Measures

Paste `measures.dax`.

`Monthly NRR` is one month of expansion, contraction, and churn divided by beginning MRR. The memo's NRR is `TTM NRR`, from the disconnected scorecard: the October 2025 paying cohort, valued again in September 2026. Both are right. They are not the same question.

`Bridge Check` should be blank or 0. If it is not, a movement column was filtered off while `mrr` was not.

## 4. Pages

**Executive.** Cards: Ending MRR, ARR, Ending MRR YoY %, TTM NRR, TTM GRR, TTM Logo Retention, Quick Ratio, Active Logos. Line chart of Ending MRR by `year_month`. Do not put a date slicer on this page if the TTM cards are on it, or add a note that those three cards ignore slicers.

**Bridge.** Clustered column of New MRR, Reactivation MRR, Expansion MRR, and minus Contraction MRR and Churned MRR, by `year_month`. Waterfall visual if your Desktop build has it, using the same measures. Card: Bridge Check.

**Cohorts.** This page is awkward in DAX because retention is a tenure calculation. Use the SQL result `outputs/sql/05_cohort_retention.csv` as a small imported table for the matrix, or rebuild the matrix from `fact_subscription_month` with a cohort column:

```dax
Cohort Month = DATE ( YEAR ( dim_account[signup_date] ), MONTH ( dim_account[signup_date] ), 1 )
```

Put that column on `dim_account`. Tenure is `DATEDIFF ( dim_account[Cohort Month], dim_date[full_date], MONTH )` used inside a measure, not as a calculated column that ignores filter context. Logo retention = Active Logos / the distinct accounts whose cohort is the row header. Check a cell against the SQL file before you trust the heatmap.

**Product health.** Bar of Next-Month Churn Rate by an adoption-quartile bucket. The quartile in the memo is ranked inside each month in SQL. A Power BI quartile across all history will not match it. For the matching visual, import `outputs/sql/06_usage_quartile_churn.csv` as a static table, or accept that the live quartile is a different cut and label it.

**Acquisition.** Table of channel, Marketing Spend, New Logos, Blended CAC. Scatter needs six-month retention from `outputs/sql/09_channel_retention_m6.csv`, because that cohort filter is fixed. Label the scatter as month-6 retention of matured cohorts, not as a live slicer.

## 5. Reconcile

With the date filter on September 2026 only:

- Ending MRR matches the memo.
- Bridge Check is 0.
- Active Logos matches the sum of logos in the plan table of the memo.
- TTM NRR matches the memo with no date filter, because that table is disconnected.

## 6. Refresh

`python run.py` rewrites the CSVs, including the one-row scorecard. Home → Refresh in Power BI.
