# Methodology

Lumen Workspace is fictional. The generator simulates each account one month at a time so the MRR bridge is an identity, not a formatting trick.

`random.Random(42)` drives the draw. `python run.py` rebuilds it.

## What is structural

- **A latent trait** on each account. A higher trait raises the adoption score and lowers the monthly chance of churn. Low adoption and churn therefore move together. The usage-quartile query is where that either shows up or does not.
- **Plan, size, and channel.** Starter and the 1–20 employee band churn faster. Enterprise and the 501+ band churn slower. Paid Search multiplies churn hazard by 1.28. Organic multiplies it by 0.82. The first two months after a start or a reactivation are riskier.
- **Early tenure is not the signup month.** The signup month itself does not roll the churn dice. The next two months do, at 1.5× hazard.
- **Expansion and contraction** are more likely when the trait is high or low. If a change would not actually move MRR, the row stays Retained. Movement labels are derived from the dollars, then checked.
- **Reactivation** can happen from the third month after churn, with a higher chance for a high trait, on a plan one tier down.
- **Tickets** are more likely when the adoption score is low, and somewhat more likely for Enterprise and in a churn month. The "tickets before churn" result is that association. It is not a separate rule that dumps tickets onto future churners.
- **Spend** differs by channel and drifts up about 0.8% a month. Logo counts are not forced to match spend, so CAC is an outcome.

## What this is not

- It is not a billing-system extract.
- Trailing-twelve-month NRR is one cohort, October 2025 to September 2026. It is not the average of twelve monthly NRR figures.
- The MRR forecast carries forward the last six months of rates. It does not know about a price change or a launch that has not happened.
- There is no cash collection, no tax, and no contracted multi-year ARR. ARR in the report is ending MRR times 12.

## Checks

`src/warehouse.py` will not keep a database where a movement label disagrees with the dollars, a New logo falls outside the signup month, the bridge fails, an account has two rows in one month, or a subscription month has no usage row. `tests/test_warehouse.py` runs the same checks on a 50-account draw.
