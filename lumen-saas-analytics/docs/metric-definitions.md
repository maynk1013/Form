# Metric definitions

The subscription fact is one row per account per month. The month an account churns is a row with `mrr = 0` and `movement = 'Churn'`. That row is how the lost dollars stay visible.

| Metric | Formula | Notes |
| --- | --- | --- |
| Ending MRR | Sum of `mrr` | Churn rows add nothing. This is the live book at month end. |
| Beginning MRR | Sum of `prior_mrr` | Equals last month's ending MRR. New and reactivated logos contribute 0. |
| New MRR | `mrr` where movement is New | First paid month. Booked in the signup month only. |
| Reactivation MRR | `mrr` where movement is Reactivation | A logo that had churned and came back. `prior_mrr` is 0. |
| Expansion MRR | `mrr - prior_mrr` where movement is Expansion | The increase, not the new MRR. |
| Contraction MRR | `prior_mrr - mrr` where movement is Contraction | A positive number. The bridge subtracts it. |
| Churned MRR | `prior_mrr` where movement is Churn | The dollars that left. Ending `mrr` on that row is 0. |
| Bridge | Beginning + New + Reactivation + Expansion − Contraction − Churned = Ending | Checked to the cent. If this is not true, stop and fix the grain. |
| ARR | Ending MRR × 12 | A run-rate, not contracted annual revenue. There is no multi-year contract table. |
| Active logos | Distinct accounts with `mrr > 0` | Never `COUNTROWS`. |
| Monthly logo churn | Churned logos / logos with `prior_mrr > 0` | A rate for that month. Pooling twelve months is an average weighted by beginning logos, not a twelve-month survival rate. |
| Monthly NRR | (Beginning + Expansion − Contraction − Churned) / Beginning | New logos are excluded. This is one month. |
| Monthly GRR | (Beginning − Contraction − Churned) / Beginning | Expansion is excluded. |
| Quick ratio | (New + Reactivation + Expansion) / (Contraction + Churned) | Above 1 means the month's additions covered the month's losses. |
| Trailing-twelve-month NRR | Ending MRR of the October 2025 paying accounts, measured in September 2026, divided by their October 2025 MRR | Churned or missing accounts count as 0. Expansion counts. This is the memo's NRR. |
| Trailing-twelve-month GRR | Same cohort, but each account's ending MRR is capped at its starting MRR | Expansion cannot paper over churn. |
| Logo retention (TTM) | Share of that October 2025 cohort with MRR still above 0 in September 2026 | Different from monthly logo churn. |
| Month-6 logo retention | Share of a signup cohort with MRR above 0 six months later | Cohorts younger than six months are excluded. |
| CAC | Channel spend / new logos from that channel | Blended. Organic has a cost because the model includes content and payroll-like spend, not only media invoices. |
| ARPA | Ending MRR / active logos | Not an average of an account-level ARPA column. |
| Next-month churn | Share of active account-months whose next row is Churn | The last month in the warehouse is excluded. |

### Why two NRR numbers exist

Monthly NRR answers "did this month's base grow before counting new logos?" Trailing-twelve-month NRR answers "what happened to the accounts we already had a year ago?" A dashboard that shows one of them under the other's name is wrong even when the arithmetic is right.
