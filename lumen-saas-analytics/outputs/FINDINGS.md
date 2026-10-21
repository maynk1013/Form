# Lumen Workspace — subscription review

Closed through September 2026. Figures are computed from the SQLite warehouse. The dataset is synthetic.

## Scorecard

| Metric | Value | Definition |
| --- | --- | --- |
| Ending MRR | $4.35M | September 2026 close |
| MRR vs last year | 56.0% | September 2026 vs September 2025 |
| Net revenue retention | 96.4% | Oct 2025 cohort, valued Sep 2026 |
| Gross revenue retention | 87.5% | Same cohort, expansion capped |
| Logo retention | 81.3% | Same cohort, still paying |
| Quick ratio | 4.01 | September: added MRR / lost MRR |

## What the numbers say

- Ending MRR in September 2026 is $4.35M, 56.0% versus September 2025. ARR on that ending balance is $52.21M.
- The October 2025 cohort of paying accounts finished September 2026 at 96.4% net revenue retention and 87.5% gross revenue retention. Logo retention for that same group is 81.3%. Expansion did not replace the revenue that contracted or churned.
- In September, the quick ratio was 4.01. New, reactivation, and expansion dollars cover the month's losses more than twice over. The quick ratio counts new logos. The cohort NRR above does not. Pooled monthly logo churn is 8.9% on Starter and 0.5% on Enterprise.
- Accounts in the lowest adoption quartile churned the next month at 10.1%, against 0.5% in the highest quartile (19.1×). Accounts that churned within 60 days were already opening 0.89 tickets a month, versus 0.61 for accounts that stayed.
- Paid Search costs $14.2k per logo and keeps 70.2% of matured logos at month 6. Outbound keeps 83.7% at a CAC of $9,201. The ten largest accounts are 8.9% of ending MRR.

## Actions

1. Treat Starter churn as an onboarding problem, not a discounting problem. Its pooled monthly logo churn is 8.9% against 0.5% on Enterprise. A price cut on the plan that already stays would not touch the logos that are leaving.
2. Page the account team when adoption falls into the bottom quartile. Those accounts churn the next month at 10.1%, against 0.5% for the top quartile. The signal is already in the usage table. It does not need a new model to be useful.
3. Move the next increment of budget from Paid Search toward Content. Paid Search costs $14.2k per logo and keeps 70.2% at month 6. Content keeps 81.9% and costs $4,351. Outbound retains slightly more (83.7%) but costs $9,201.

## Charts

- `mrr_trend.png` — Ending MRR includes expansion and excludes churned accounts. It is not a sum of every historical month.
- `mrr_waterfall.png` — Teal adds MRR and coral removes it. Beginning and ending are in the title because those totals are about $4M and the steps are not.
- `cohort_retention.png` — Each cell is logos still paying divided by the original cohort. Blank cells have not happened yet.
- `usage_churn.png` — Quartiles are ranked inside each month. Q1 is the lowest adoption score.
- `plan_churn.png` — This is churn events divided by account-months that started the month active. It is not 12-month logo retention.
- `channel_cac_retention.png` — CAC is channel spend divided by signups. Retention uses only cohorts that have had six months.

## Close by plan

| Plan | Logos | Ending MRR | ARPA | Avg seats |
| --- | --- | --- | --- | --- |
| Starter | 119 | $68.3k | $574 | 14.7 |
| Growth | 107 | $227.9k | $2,130 | 23.9 |
| Scale | 144 | $1.01M | $6,983 | 39.0 |
| Enterprise | 143 | $3.05M | $21.3k | 53.4 |

## Channels

| Channel | Spend | New logos | CAC | Still paying at month 6 |
| --- | --- | --- | --- | --- |
| Paid Search | $2.21M | 155 | $14.2k | 70.2% |
| Outbound | $1.37M | 149 | $9,201 | 83.7% |
| Content | $639.6k | 147 | $4,351 | 81.9% |
| Partner | $478.1k | 128 | $3,735 | 78.0% |
| Organic | $261.1k | 141 | $1,852 | 77.3% |

## Notes

- Synthetic data for a portfolio project. Lumen Workspace is fictional.
- Window: 2023-01-01 to 2026-09-01. 720 accounts, 10,777 account-months, 7,030 tickets.
- Ending MRR is the sum of mrr on the close month. Churn rows are stored at mrr 0 so the bridge can see the lost dollars. Do not count rows to count customers.
- Trailing-twelve-month NRR follows the accounts that were paying in October 2025 and values them again in September 2026, with churned accounts at zero. GRR caps each account at its starting MRR so expansion does not help the ratio.
- Monthly NRR in the DAX file is a different measure: one month of movement divided by that month's beginning MRR. Do not compare it with the trailing-twelve-month figure.
- The highest pooled monthly logo churn by industry is Education at 4.8%. The lowest is Software at 2.0%.
- Baseline MRR path if the last six months of rates repeat: 2026-10 $4.48M, 2026-11 $4.61M, 2026-12 $4.74M. It assumes new-logo dollars stay flat in absolute terms and that expansion, contraction, and churn stay a constant share of beginning MRR.
- Power BI Desktop is Windows-only. The CSV model and DAX are in powerbi/. This HTML report is the view that opens on a Mac.
