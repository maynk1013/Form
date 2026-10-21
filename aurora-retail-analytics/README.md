# Aurora Home & Living — retail analytics

Commercial review for a fictional 12-store home retailer, closed through **30 September 2026**. The question is simple: where did net revenue and gross profit actually come from, which stores are off the plan, and which discounts are buying nothing but returns.

The project is a star schema in SQLite, a SQL question pack, a Python pipeline that checks the math and writes an executive memo, and a Power BI model you can build from the exported CSVs.

## Open the result

After the pipeline has been run once, open:

- [`outputs/executive_report.html`](outputs/executive_report.html) in a browser
- [`outputs/FINDINGS.md`](outputs/FINDINGS.md) for the same memo in Markdown
- `data/aurora.db` in any SQLite client

```bash
sqlite3 data/aurora.db < sql/analysis/05_discount_bands.sql
```

Power BI Desktop does not run on macOS. The report that opens on this Mac is the HTML memo. The Power BI build is in [`powerbi/BUILD.md`](powerbi/BUILD.md): star-schema CSVs, DAX measures, a theme, and page-by-page layout. Build it in Power BI Desktop on Windows, or publish through the Power BI service.

## Run it

```bash
cd aurora-retail-analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
python -m unittest discover -s tests -v
```

`python run.py` deletes and rebuilds `data/aurora.db`, reruns every query in `sql/analysis`, rewrites `powerbi/data/*.csv`, and refreshes the charts and the memo. The draw uses seed 42.

## How the pieces fit

```mermaid
flowchart LR
  gen[Python generator] --> db[(SQLite warehouse)]
  db --> sql[SQL question pack]
  sql --> memo[Executive memo and charts]
  db --> csv[Power BI star schema]
  csv --> pbi[Power BI model and DAX]
```

| Path | What it is |
| --- | --- |
| `sql/01_schema.sql` | Dimensions, facts, keys |
| `sql/02_views.sql` | Additive money columns and the RFM snapshot |
| `sql/analysis/` | One business question per file |
| `src/generate.py` | Synthetic commercial activity |
| `src/warehouse.py` | Load plus the checks that block a bad database |
| `src/analyze.py` | Charts, forecast baseline, memo |
| `powerbi/` | Model guide, DAX, theme, CSV extracts |
| `docs/` | Dictionary, metric definitions, methodology |
| `tests/test_warehouse.py` | Money identity, returns, keys, targets |

## Model choices worth keeping

- **Facts store inputs. Views store additive money.** Margin, AOV, return rate, attainment, and growth are ratios of sums. They are measures, not columns you average.
- **Returned lines stay in the fact** with `is_returned = 1`, positive quantity, and zero net revenue. The refund is `returned_amount`. It is not subtracted a second time.
- **The date table starts in 2024** even though sales start in 2025, so prior-year measures return blank instead of breaking.
- **Comparable growth is January–September against January–September.** Comparing full-year 2025 with a partial 2026 would punish the current year.
- **Customer region is not store region.** A relationship between them would mix “where they live” with “where the sale rang.”
- **RFM is a pipeline snapshot.** A date slicer in Power BI should not pretend to rescore it. Use the Net Revenue measure by segment when the page is filtered.
- **Targets are a plan, not a percent of actuals.** Store demand and store plan shares are separate inputs, so a store can miss for the whole window.

Metric formulas: [`docs/metric-definitions.md`](docs/metric-definitions.md). What the generator is allowed to bake in: [`docs/methodology.md`](docs/methodology.md).

## Stack

Python 3, pandas, matplotlib, SQLite, and Power BI (DAX + star schema). No warehouse server is required. The SQL is ordinary and moves to Postgres with almost no change; watch `julianday` in the RFM view if you do that.
