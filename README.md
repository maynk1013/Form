# Two analytics projects

Both are fictional, both are complete, and each one is its own folder in this repository.

| Folder | Company | Question |
| --- | --- | --- |
| `aurora-retail-analytics` | Aurora Home & Living, 12 stores | Where revenue and margin came from, which stores missed the plan, and which discounts only buy returns |
| `lumen-saas-analytics` | Lumen Workspace, B2B SaaS | Whether the existing book grew, which plan leaks logos, and which channel is expensive for the retention it buys |

Each project has:

- a SQLite star schema and a SQL file per business question
- a Python pipeline that rebuilds the data, checks the math, and writes charts
- an executive report you can open in a browser on this Mac (`outputs/executive_report.html`)
- a Power BI star schema, DAX measures, theme, and a page-by-page build guide

Power BI Desktop is Windows-only. The HTML report is what opens locally. The Power BI files are ready for Desktop or the Power BI service.

## Run

```bash
cd aurora-retail-analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Repeat inside `lumen-saas-analytics`.

## Open the reports

- [aurora-retail-analytics/outputs/executive_report.html](aurora-retail-analytics/outputs/executive_report.html)
- [lumen-saas-analytics/outputs/executive_report.html](lumen-saas-analytics/outputs/executive_report.html)

`.gitignore` leaves out the virtualenv and Python caches. The database, CSVs, and charts are committed so the report opens without rerunning the pipeline.

The data is synthetic. Nothing in either project is a real customer extract.
