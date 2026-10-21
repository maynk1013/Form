# Data dictionary

SQLite file: `data/lumen.db`. Power BI copies: `powerbi/data`.

## dim_date

One row per day from 2022-01-01 through 2026-12-31. Subscription facts use the first of the month. Tickets and signups use the actual day. Both resolve to this table.

## dim_plan

Starter ($39 per seat), Growth ($89), Scale ($179), Enterprise ($399). `tier_rank` is the sort order and the upgrade path.

## dim_channel

Organic and Content are Owned. Partner is Partner. Paid Search and Outbound are Paid. Spend lives on the marketing fact, not on this dimension, because it changes every month.

## dim_account

One row per account. `industry`, `region`, and `employee_band` are attributes. They are not separate dimensions because nothing else references them. Channel is a dimension because marketing spend shares it. `signup_date` is the acquisition date. The first subscription month is the first of that month.

Employee bands are `1-20`, `21-100`, `101-500`, and `501+`.

## fact_subscription_month

One row per account per month from the signup month through the churn month, and again after a reactivation.

| Column | Meaning |
| --- | --- |
| month_start | First day of the month. |
| seats | Seats at month end. On a churn row, the seats they left with. |
| mrr | Price per seat × seats, or 0 if they churned. |
| prior_mrr | Last month's MRR, or 0 if they were not paying. |
| movement | New, Reactivation, Expansion, Contraction, Churn, or Retained. The label has to match the two money columns. The warehouse check enforces that. |

## fact_usage_monthly

One row for every subscription row, including the churn month. `adoption_score` is 5–98. `active_users` cannot exceed seats. The Power BI extract adds `churned_next_month` from `vw_usage_health`.

## fact_ticket

One support ticket. `csat` is 1–5. `resolution_hours` is time to resolve, not time open.

## fact_marketing_spend

One row per channel per month from January 2023 through September 2026.

## metric_trailing_twelve_months

A published scorecard, not a fact. One row. Window is fixed: 2025-10-01 through 2026-09-01.
