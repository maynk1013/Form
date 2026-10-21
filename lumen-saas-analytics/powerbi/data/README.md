# Power BI source files

Import each CSV as its own table. Do not append them.

| File | Grain |
| --- | --- |
| `dim_date.csv` | one calendar day |
| `dim_plan.csv` | one plan |
| `dim_channel.csv` | one acquisition channel |
| `dim_account.csv` | one account |
| `fact_subscription_month.csv` | one account-month, including the churn month at mrr 0 |
| `fact_usage.csv` | one account-month, with `churned_next_month` |
| `fact_ticket.csv` | one support ticket |
| `fact_marketing_spend.csv` | one channel-month of spend |
| `metric_trailing_twelve_months.csv` | one published scorecard row, October 2025–September 2026 |

Leave `metric_trailing_twelve_months` disconnected. A date slicer must not change the official trailing-twelve-month NRR. Monthly NRR is a different measure and will not match it.

`churned_next_month` is null on the last month in the warehouse. Do not treat null as retained.
