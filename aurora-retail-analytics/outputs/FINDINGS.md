# Aurora Home & Living — commercial review

Closed through 30 September 2026. Figures are computed from the SQLite warehouse. The dataset is synthetic.

## Scorecard

| Metric | Value | Definition |
| --- | --- | --- |
| Net revenue | $14.93M | Jan 2025–Sep 2026, after returns |
| YTD growth | 12.3% | Jan–Sep 2026 vs Jan–Sep 2025 |
| Gross margin | 45.6% | Gross profit / net revenue |
| Average order | $622 | Net revenue / orders |
| Line return rate | 5.3% | Returned lines / lines |
| Plan attainment | 100.0% | Net revenue / store targets |

## What the numbers say

- January–September net revenue moved from $5.69M in 2025 to $6.38M in 2026 (12.3%). Comparable gross margin moved from 45.5% to 45.6%.
- November averages $1.04M, 1.59× a typical June ($651.6k). The plan and the open-to-buy need that peak; a flat monthly budget will miss it.
- Textiles contributes the most gross profit ($2.26M). Decor has the highest margin (56.1%). Furniture has the highest line return rate (12.1%).
- Revenue is broad: the top 43.3% of customers account for 80% of net revenue. Corporate is the better book, with AOV of $710 versus $574 for Consumer, and a line return rate of 2.7% versus 6.7%.
- Weekend and weekday baskets are close ($630 vs $618), so day-of-week is not the lever. South Congress House reached 133.3% of plan and Design District reached 72.7%.

## Actions

1. Reset the store plan before next year's lock. South Congress House has produced $1.39M on a $1.05M plan (133.3%). Design District has produced $977.6k against $1.34M (72.7%). Inventory and labor that follow the current plan will pile up in the stores that are not earning it.
2. Cap promotional depth at 20% and review every 21%+ offer. Full-price lines hold a 53.1% gross margin and a 4.0% return rate. The 21%+ band falls to 23.4% margin and a 16.7% return rate. Average quantity does not increase (1.70 units at full price, 1.49 at 21%+). The discount is not buying a larger basket.
3. Put a win-back on the At risk segment before spending more to acquire lookalikes. 552 customers in that segment have already spent $2.09M, with an average recency of 203 days and 5.7 orders.

## Charts

- `monthly_revenue_vs_plan.png` — Bars are net revenue. The gold line is the sum of store revenue targets.
- `store_attainment.png` — Attainment is total net revenue divided by total target, not an average of monthly rates.
- `discount_bands.png` — Navy bars are gross margin. The coral line is the share of lines that were returned.
- `rfm_revenue.png` — RFM is scored once, through the latest order date in the warehouse.
- `yoy_comparable.png` — Same nine months in each year. October–December 2025 is excluded so the partial year cannot flatter 2025.
- `category_margin.png` — Margin is category gross profit divided by category net revenue.

## Top 10 products by gross profit

| Product | Category | Net revenue | Gross profit | Margin | Return rate |
| --- | --- | --- | --- | --- | --- |
| Linen Sectional Sofa | Furniture | $1.89M | $635.6k | 33.7% | 11.9% |
| Jute Area Rug 8x10 | Textiles | $1.26M | $587.7k | 46.7% | 6.3% |
| Stonewashed Linen Duvet | Textiles | $755.7k | $437.5k | 57.9% | 5.1% |
| Oak Dining Table | Furniture | $1.21M | $433.0k | 35.8% | 12.6% |
| Arc Floor Lamp | Lighting | $778.0k | $428.8k | 55.1% | 4.2% |
| Percale Sheet Set | Textiles | $593.5k | $349.8k | 58.9% | 5.7% |
| Walnut Writing Desk | Furniture | $814.0k | $299.7k | 36.8% | 12.6% |
| Flatweave Hall Runner | Textiles | $584.0k | $293.9k | 50.3% | 5.3% |
| Wool Throw Blanket | Textiles | $473.5k | $285.1k | 60.2% | 5.2% |
| Boucle Lounge Chair | Furniture | $827.0k | $284.8k | 34.4% | 11.5% |

## Store scorecard

| Store | Net revenue | Plan | Attainment |
| --- | --- | --- | --- |
| Design District | $977.6k | $1.34M | 72.7% |
| LoHi Living | $959.7k | $1.19M | 80.3% |
| Inman Park Home | $943.2k | $1.12M | 84.2% |
| North Loop Goods | $776.8k | $821.4k | 94.6% |
| SoHo Residence | $1.56M | $1.64M | 95.2% |
| Knox Henderson | $1.28M | $1.27M | 101.0% |
| Pike Place Home | $1.38M | $1.34M | 102.3% |
| Newbury Home | $1.23M | $1.19M | 103.1% |
| Abbot Kinney Home | $1.47M | $1.42M | 103.3% |
| Mission Atelier | $1.47M | $1.27M | 116.2% |
| Lincoln Park Living | $1.49M | $1.27M | 117.5% |
| South Congress House | $1.39M | $1.05M | 133.3% |

## Notes

- Synthetic data for a portfolio project. Aurora Home & Living is fictional.
- Window: 2025-01-01 to 2026-09-30. 49,196 lines, 24,000 orders, 3,615 customers.
- Net revenue excludes returned lines. Gross profit is net revenue minus COGS. Returned goods are treated as refunded and restocked.
- Year-to-date comparisons use January–September in both years.
- RFM scores are a snapshot through the latest order date and refresh only when the pipeline reruns.
- Baseline forecast for the next three months: 2026-10 $752.8k, 2026-11 $1.13M, 2026-12 $1.25M. Each month-of-year has only one or two history points, so November and December lean on a single prior season.
- Power BI Desktop is Windows-only. The CSV star schema, DAX, and build guide in powerbi/ are ready for Desktop or the Power BI service. This HTML report is the view that opens on a Mac.
