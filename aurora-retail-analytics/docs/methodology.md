# Methodology

Aurora Home & Living is fictional. The pipeline builds a complete retail warehouse so the SQL, the charts, and the Power BI model can be reviewed without a private extract.

`random.Random(42)` drives the generator. Rerunning `python run.py` rebuilds the same events on the same Python version. The forecast then uses NumPy only to fit a line through those results.

## What is structural, and what is noise

These patterns are built into the generator. The memo reports them only after measuring them. If a pattern is weak in a given run, the wording says so.

- **Calendar.** Order counts rise in November and December, dip in January, and are somewhat higher on weekends. A separate monthly trend of about 0.8% is applied from January 2025.
- **Discount economics.** Furniture is discounted more often and more deeply. Quantity barely responds. Return probability rises once the discount passes 20%, and again past 30%. The question in `sql/analysis/05_discount_bands.sql` is whether that trade is worth it.
- **Customers.** Corporate accounts get shallower discounts and return less often. Repeat purchasing is skewed, so a minority of customers can dominate revenue. That is a hypothesis the Pareto query tests.
- **Stores.** Demand weights and plan shares are different inputs. Miami and Denver are given more of the plan than their demand weight. Austin is given less. `COMPANY_MONTHLY_BASE` is chosen so the chain in total lands near the plan. The store shares are not fitted to each store's sales, which is why attainment still runs from the low 70s to above 130 percent. A store target is not a percentage of that store's actuals.
- **Returns.** A returned line keeps a positive quantity and `is_returned = 1`. Revenue and COGS on that line are zero. The refund is stored once as `returned_amount`.

## What this is not

- It is not a point-of-sale extract, and it should not be described as one.
- The forecast is a seasonal naive-plus-trend baseline. November and December each appear once in history. The band is one residual standard deviation, not a prediction interval from a formal model.
- RFM is a single snapshot. It will not move inside a Power BI date slicer.

## Checks

`src/warehouse.py` refuses to save the database if a foreign key is broken, a sale falls outside the closed window, gross profit does not equal net revenue minus COGS, an RFM score is outside 1–5, or any store-month is missing a target. `tests/test_warehouse.py` covers the identities on a smaller draw from the same generator.
