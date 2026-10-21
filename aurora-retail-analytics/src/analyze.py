"""Run the SQL question pack, draw charts, and write the executive memo."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import SALES_END, SALES_START
from src.report import write_findings, write_html

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql" / "analysis"

NAVY = "#1B3A4B"
TEAL = "#1F7A8C"
GOLD = "#C4A35A"
CORAL = "#C44536"
SLATE = "#5C6B73"
GREEN = "#2E7D4F"


def money(value: float) -> str:
    sign = "-" if value < 0 else ""
    amount = abs(value)
    if amount >= 1_000_000:
        return f"{sign}${amount / 1_000_000:.2f}M"
    if amount >= 10_000:
        return f"{sign}${amount / 1_000:.1f}k"
    return f"{sign}${amount:,.0f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def run_sql_folder(conn: sqlite3.Connection, out_dir: Path) -> dict[str, pd.DataFrame]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tokens = {
        "__SALES_START__": SALES_START.isoformat(),
        "__SALES_END__": SALES_END.isoformat(),
    }
    frames: dict[str, pd.DataFrame] = {}
    for path in sorted(SQL_DIR.glob("*.sql")):
        sql = path.read_text()
        for key, value in tokens.items():
            sql = sql.replace(key, value)
        frame = pd.read_sql_query(sql, conn)
        frame.to_csv(out_dir / f"{path.stem}.csv", index=False)
        frames[path.stem] = frame
    return frames


def _style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#D9D3CB",
        "axes.labelcolor": NAVY,
        "xtick.color": SLATE,
        "ytick.color": SLATE,
        "text.color": NAVY,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.titleweight": "regular",
        "axes.titlesize": 13,
        "axes.labelsize": 10,
    })


def _money_axis(value: float, _pos: int) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1000:
        return f"${value / 1000:.0f}k"
    return f"${value:.0f}"


def _save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def forecast_revenue(monthly: pd.DataFrame) -> pd.DataFrame:
    """Seasonally adjusted linear trend. A baseline, not a planning system."""
    series = monthly.sort_values("year_month")
    observed = series["net_revenue"].to_numpy(dtype=float)
    month_numbers = series["month"].to_numpy(dtype=int)
    index = np.arange(len(observed), dtype=float)
    overall = float(observed.mean())
    factors: dict[int, float] = {}
    for month in range(1, 13):
        subset = observed[month_numbers == month]
        factors[month] = float(subset.mean() / overall) if len(subset) else 1.0
    seasonal = np.array([factors[int(month)] for month in month_numbers])
    slope, intercept = np.polyfit(index, observed / seasonal, 1)
    fitted = (intercept + slope * index) * seasonal
    sigma = float(np.std(observed - fitted, ddof=2))
    last = pd.Timestamp(str(series["year_month"].iloc[-1]) + "-01")
    rows = []
    for step in range(1, 4):
        future = last + pd.DateOffset(months=step)
        point = float((intercept + slope * (len(observed) - 1 + step)) * factors[int(future.month)])
        rows.append({
            "month_start": future.strftime("%Y-%m-%d"),
            "year_month": future.strftime("%Y-%m"),
            "forecast_net_revenue": round(point, 2),
            "forecast_low": round(point - sigma, 2),
            "forecast_high": round(point + sigma, 2),
            "method": "linear trend on seasonally adjusted monthly net revenue; band is +/- 1 residual standard deviation",
        })
    return pd.DataFrame(rows)


def _charts(frames: dict[str, pd.DataFrame], chart_dir: Path) -> dict[str, str]:
    _style()
    chart_dir.mkdir(parents=True, exist_ok=True)
    notes: dict[str, str] = {}

    store = frames["03_store_month"]
    by_month = (
        store.groupby("month_start", as_index=False)[["net_revenue", "revenue_target"]]
        .sum()
        .sort_values("month_start")
    )
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    positions = np.arange(len(by_month))
    ax.bar(positions, by_month["net_revenue"], color=TEAL, width=0.72, label="Net revenue")
    ax.plot(positions, by_month["revenue_target"], color=GOLD, marker="o", linewidth=2, label="Plan")
    ax.set_xticks(positions[::2])
    ax.set_xticklabels(by_month["month_start"].iloc[::2], rotation=45, ha="right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_money_axis))
    ax.set_title("Net revenue against the store plan")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, chart_dir / "monthly_revenue_vs_plan.png")
    notes["monthly_revenue_vs_plan.png"] = "Bars are net revenue. The gold line is the sum of store revenue targets."

    by_store = (
        store.groupby("store_name", as_index=False)[["net_revenue", "revenue_target"]]
        .sum()
    )
    by_store["attainment"] = by_store["net_revenue"] / by_store["revenue_target"]
    by_store = by_store.sort_values("attainment")
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    colors = [CORAL if value < 1 else TEAL for value in by_store["attainment"]]
    ax.barh(by_store["store_name"], by_store["attainment"], color=colors)
    ax.axvline(1, color=NAVY, linewidth=1)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _pos: f"{value * 100:.0f}%"))
    ax.set_title("Store revenue versus plan, January 2025–September 2026")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, chart_dir / "store_attainment.png")
    notes["store_attainment.png"] = "Attainment is total net revenue divided by total target, not an average of monthly rates."

    bands = frames["05_discount_bands"].sort_values("band_order")
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.bar(bands["discount_band"], bands["gross_margin"], color=NAVY, width=0.7)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _pos: f"{value * 100:.0f}%"))
    ax2 = ax.twinx()
    ax2.plot(bands["discount_band"], bands["line_return_rate"], color=CORAL, marker="o", linewidth=2)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _pos: f"{value * 100:.0f}%"))
    ax2.tick_params(axis="y", colors=CORAL)
    ax.set_title("Gross margin by discount band, with line return rate")
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    _save(fig, chart_dir / "discount_bands.png")
    notes["discount_bands.png"] = "Navy bars are gross margin. The coral line is the share of lines that were returned."

    rfm = frames["08_rfm_segments"].sort_values("net_revenue")
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.barh(rfm["rfm_segment"], rfm["net_revenue"], color=TEAL)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(_money_axis))
    ax.set_title("Net revenue by RFM segment")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, chart_dir / "rfm_revenue.png")
    notes["rfm_revenue.png"] = "RFM is scored once, through the latest order date in the warehouse."

    yoy = frames["02_yoy_comparable"]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.plot(yoy["month_name"], yoy["net_revenue_2025"], color=SLATE, marker="o", label="2025")
    ax.plot(yoy["month_name"], yoy["net_revenue_2026"], color=TEAL, marker="o", label="2026")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_money_axis))
    ax.set_title("Comparable months: January–September")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, chart_dir / "yoy_comparable.png")
    notes["yoy_comparable.png"] = "Same nine months in each year. October–December 2025 is excluded so the partial year cannot flatter 2025."

    category = frames["04_category_economics"].sort_values("gross_margin")
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.barh(category["category"], category["gross_margin"], color=GOLD)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _pos: f"{value * 100:.0f}%"))
    ax.set_title("Gross margin by category")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, chart_dir / "category_margin.png")
    notes["category_margin.png"] = "Margin is category gross profit divided by category net revenue."

    return notes


def _export_power_bi(conn: sqlite3.Connection, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    exports = {
        "dim_date": "SELECT * FROM dim_date ORDER BY full_date",
        "dim_store": "SELECT * FROM dim_store ORDER BY store_id",
        "dim_product": "SELECT * FROM dim_product ORDER BY product_id",
        "dim_customer": "SELECT * FROM vw_dim_customer ORDER BY customer_id",
        "fact_sales": "SELECT * FROM vw_sales_lines ORDER BY order_date, order_id, sales_line_id",
        "fact_store_target": "SELECT * FROM fact_store_target ORDER BY month_start, store_id",
    }
    money_columns = {
        "unit_cost", "list_price", "unit_list_price", "list_revenue", "kept_list_revenue",
        "discount_amount", "net_revenue", "cogs", "gross_profit", "returned_amount",
        "revenue_target", "monetary",
    }
    for name, sql in exports.items():
        frame = pd.read_sql_query(sql, conn)
        for column in frame.columns:
            if column in money_columns:
                frame[column] = frame[column].round(2)
        frame.to_csv(out_dir / f"{name}.csv", index=False)


def _pareto_share(pareto: pd.DataFrame) -> float:
    crossed = pareto[pareto["cumulative_revenue_share"] >= 0.80]
    if crossed.empty:
        return float("nan")
    return float(crossed.iloc[0]["customer_share"])


def analyze(db_path: Path) -> None:
    output = ROOT / "outputs"
    charts = output / "charts"
    sql_out = output / "sql"
    output.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        frames = run_sql_folder(conn, sql_out)
        mart = pd.read_sql_query("SELECT * FROM vw_sales_enriched", conn)
        counts = pd.read_sql_query(
            """
            SELECT
              (SELECT COUNT(*) FROM fact_sales) AS lines,
              (SELECT COUNT(DISTINCT order_id) FROM fact_sales) AS orders,
              (SELECT COUNT(*) FROM dim_customer) AS customers,
              (SELECT MIN(order_date) FROM fact_sales) AS first_order,
              (SELECT MAX(order_date) FROM fact_sales) AS last_order
            """,
            conn,
        ).iloc[0]
        _export_power_bi(conn, ROOT / "powerbi" / "data")
    finally:
        conn.close()

    mart.to_csv(output / "sales_mart.csv", index=False)
    forecast = forecast_revenue(frames["01_monthly_performance"])
    forecast.to_csv(output / "revenue_forecast.csv", index=False)
    notes = _charts(frames, charts)

    monthly = frames["01_monthly_performance"]
    yoy = frames["02_yoy_comparable"]
    store = frames["03_store_month"]
    category = frames["04_category_economics"]
    bands = frames["05_discount_bands"].sort_values("band_order")
    products = frames["06_top_products"]
    segments = frames["07_segment_mix"]
    rfm = frames["08_rfm_segments"]
    weekday = frames["09_weekday_weekend"].set_index("day_type")

    net_revenue = float(monthly["net_revenue"].sum())
    gross_profit = float(monthly["gross_profit"].sum())
    orders = int(monthly["orders"].sum())
    margin = gross_profit / net_revenue
    aov = net_revenue / orders
    returned_lines = float(store["returned_lines"].sum())
    lines = float(store["lines"].sum())
    return_rate = returned_lines / lines
    attainment = float(store["net_revenue"].sum() / store["revenue_target"].sum())

    rev_2025 = float(yoy["net_revenue_2025"].sum())
    rev_2026 = float(yoy["net_revenue_2026"].sum())
    yoy_growth = (rev_2026 - rev_2025) / rev_2025
    profit_2025 = float(yoy["gross_profit_2025"].sum())
    profit_2026 = float(yoy["gross_profit_2026"].sum())
    margin_2025 = profit_2025 / rev_2025
    margin_2026 = profit_2026 / rev_2026

    by_store = store.groupby("store_name", as_index=False)[["net_revenue", "revenue_target"]].sum()
    by_store["attainment"] = by_store["net_revenue"] / by_store["revenue_target"]
    worst = by_store.sort_values("attainment").iloc[0]
    best = by_store.sort_values("attainment").iloc[-1]

    full_price = bands[bands["discount_band"] == "0% full price"].iloc[0]
    deep = bands[bands["discount_band"] == "21%+"].iloc[0]
    margin_gap = float(full_price["gross_margin"] - deep["gross_margin"])

    nov = float(monthly.loc[monthly["month"] == 11, "net_revenue"].mean())
    jun = float(monthly.loc[monthly["month"] == 6, "net_revenue"].mean())
    best_category = category.sort_values("gross_profit", ascending=False).iloc[0]
    worst_returns = category.sort_values("line_return_rate", ascending=False).iloc[0]
    best_margin_category = category.sort_values("gross_margin", ascending=False).iloc[0]
    pareto = _pareto_share(frames["10_customer_pareto"])
    at_risk = rfm[rfm["rfm_segment"] == "At risk"]
    weekend_aov = float(weekday.loc["Weekend", "aov"])
    weekday_aov = float(weekday.loc["Weekday", "aov"])
    corporate = segments[segments["segment"] == "Corporate"].iloc[0]
    consumer = segments[segments["segment"] == "Consumer"].iloc[0]

    bullets = [
        (
            f"January–September net revenue moved from {money(rev_2025)} in 2025 to {money(rev_2026)} in 2026 "
            f"({pct(yoy_growth)}). Comparable gross margin moved from {pct(margin_2025)} to {pct(margin_2026)}."
        ),
        (
            f"November averages {money(nov)}, {nov / jun:.2f}× a typical June ({money(jun)}). "
            "The plan and the open-to-buy need that peak; a flat monthly budget will miss it."
        ),
        (
            f"{best_category['category']} contributes the most gross profit ({money(float(best_category['gross_profit']))}). "
            f"{best_margin_category['category']} has the highest margin ({pct(float(best_margin_category['gross_margin']))}). "
            f"{worst_returns['category']} has the highest line return rate ({pct(float(worst_returns['line_return_rate']))})."
        ),
        (
            f"Revenue is broad: the top {pct(pareto)} of customers account for 80% of net revenue. "
            f"Corporate is the better book, with AOV of {money(float(corporate['aov']))} versus "
            f"{money(float(consumer['aov']))} for Consumer, and a line return rate of "
            f"{pct(float(corporate['line_return_rate']))} versus {pct(float(consumer['line_return_rate']))}."
        ),
        (
            (
                f"Weekend AOV is {money(weekend_aov)} against {money(weekday_aov)} on weekdays. "
                if abs(weekend_aov - weekday_aov) / weekday_aov >= 0.08
                else f"Weekend and weekday baskets are close ({money(weekend_aov)} vs {money(weekday_aov)}), so day-of-week is not the lever. "
            )
            + f"{best['store_name']} reached {pct(float(best['attainment']))} of plan and "
            f"{worst['store_name']} reached {pct(float(worst['attainment']))}."
        ),
    ]

    actions = [
        (
            f"Reset the store plan before next year's lock. {best['store_name']} has produced "
            f"{money(float(best['net_revenue']))} on a {money(float(best['revenue_target']))} plan "
            f"({pct(float(best['attainment']))}). {worst['store_name']} has produced "
            f"{money(float(worst['net_revenue']))} against {money(float(worst['revenue_target']))} "
            f"({pct(float(worst['attainment']))}). Inventory and labor that follow the current plan "
            "will pile up in the stores that are not earning it."
        )
    ]
    if margin_gap >= 0.05:
        full_qty = float(full_price["avg_quantity"])
        deep_qty = float(deep["avg_quantity"])
        if deep_qty <= full_qty:
            quantity_clause = (
                f"Average quantity does not increase ({full_qty:.2f} units at full price, {deep_qty:.2f} at 21%+)."
            )
        else:
            quantity_clause = f"Average quantity only moves from {full_qty:.2f} to {deep_qty:.2f}."
        actions.append(
            f"Cap promotional depth at 20% and review every 21%+ offer. Full-price lines hold a "
            f"{pct(float(full_price['gross_margin']))} gross margin and a {pct(float(full_price['line_return_rate']))} "
            f"return rate. The 21%+ band falls to {pct(float(deep['gross_margin']))} margin and a "
            f"{pct(float(deep['line_return_rate']))} return rate. {quantity_clause} The discount is not buying a larger basket."
        )
    else:
        actions.append(
            f"Discount depth is not the main margin leak. Full-price margin is {pct(float(full_price['gross_margin']))} "
            f"and the 21%+ band is {pct(float(deep['gross_margin']))}, a gap of {pct(margin_gap)}."
        )
    if not at_risk.empty:
        risk = at_risk.iloc[0]
        actions.append(
            f"Put a win-back on the At risk segment before spending more to acquire lookalikes. "
            f"{int(risk['customers']):,} customers in that segment have already spent {money(float(risk['net_revenue']))}, "
            f"with an average recency of {float(risk['avg_recency_days']):.0f} days and {float(risk['avg_orders']):.1f} orders."
        )

    forecast_bits = ", ".join(
        f"{row.year_month} {money(row.forecast_net_revenue)}"
        for row in forecast.itertuples(index=False)
    )
    footnotes = [
        "Synthetic data for a portfolio project. Aurora Home & Living is fictional.",
        f"Window: {counts['first_order']} to {counts['last_order']}. {int(counts['lines']):,} lines, {int(counts['orders']):,} orders, {int(counts['customers']):,} customers.",
        "Net revenue excludes returned lines. Gross profit is net revenue minus COGS. Returned goods are treated as refunded and restocked.",
        "Year-to-date comparisons use January–September in both years.",
        "RFM scores are a snapshot through the latest order date and refresh only when the pipeline reruns.",
        f"Baseline forecast for the next three months: {forecast_bits}. Each month-of-year has only one or two history points, so November and December lean on a single prior season.",
        "Power BI Desktop is Windows-only. The CSV star schema, DAX, and build guide in powerbi/ are ready for Desktop or the Power BI service. This HTML report is the view that opens on a Mac.",
    ]

    kpis = [
        ("Net revenue", money(net_revenue), "Jan 2025–Sep 2026, after returns"),
        ("YTD growth", pct(yoy_growth), "Jan–Sep 2026 vs Jan–Sep 2025"),
        ("Gross margin", pct(margin), "Gross profit / net revenue"),
        ("Average order", money(aov), "Net revenue / orders"),
        ("Line return rate", pct(return_rate), "Returned lines / lines"),
        ("Plan attainment", pct(attainment), "Net revenue / store targets"),
    ]
    product_rows = [
        [
            row.product_name,
            row.category,
            money(row.net_revenue),
            money(row.gross_profit),
            pct(row.gross_margin),
            pct(row.line_return_rate),
        ]
        for row in products.itertuples(index=False)
    ]
    store_rows = []
    ranked_stores = by_store.sort_values("attainment")
    for row in ranked_stores.itertuples(index=False):
        store_rows.append([
            row.store_name,
            money(row.net_revenue),
            money(row.revenue_target),
            pct(row.attainment),
        ])
    tables = [
        (
            "Top 10 products by gross profit",
            ["Product", "Category", "Net revenue", "Gross profit", "Margin", "Return rate"],
            product_rows,
        ),
        (
            "Store scorecard",
            ["Store", "Net revenue", "Plan", "Attainment"],
            store_rows,
        ),
    ]
    chart_notes = [(name, notes[name]) for name in [
        "monthly_revenue_vs_plan.png",
        "store_attainment.png",
        "discount_bands.png",
        "rfm_revenue.png",
        "yoy_comparable.png",
        "category_margin.png",
    ]]
    exec_charts = [
        ("charts/monthly_revenue_vs_plan.png", "Revenue versus plan", notes["monthly_revenue_vs_plan.png"]),
        ("charts/store_attainment.png", "Where the plan is wrong", notes["store_attainment.png"]),
        ("charts/discount_bands.png", "Discount depth", notes["discount_bands.png"]),
        ("charts/rfm_revenue.png", "Customer value", notes["rfm_revenue.png"]),
    ]

    write_findings(
        output / "FINDINGS.md",
        "Aurora Home & Living — commercial review",
        "30 September 2026",
        kpis,
        bullets,
        actions,
        chart_notes,
        tables,
        footnotes,
    )
    write_html(
        output / "executive_report.html",
        "Aurora commercial review",
        "Retail analytics  ·  closed September 2026",
        "Twelve stores. Net revenue is after returns. The plan is the annual store target, not a restatement of actuals.",
        kpis,
        bullets,
        actions,
        exec_charts,
        tables,
        footnotes,
    )
    print(f"Net revenue {money(net_revenue)}  |  YTD {pct(yoy_growth)}  |  margin {pct(margin)}  |  attainment {pct(attainment)}")
    print(f"Wrote {output / 'executive_report.html'}")
