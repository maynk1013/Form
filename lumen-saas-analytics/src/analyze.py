"""Run the SQL question pack, draw charts, and write the executive memo."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import AS_OF_MONTH, TTM_START
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
    token = AS_OF_MONTH.isoformat()
    frames: dict[str, pd.DataFrame] = {}
    for path in sorted(SQL_DIR.glob("*.sql")):
        frame = pd.read_sql_query(path.read_text().replace("__AS_OF_MONTH__", token), conn)
        frame.to_csv(out_dir / f"{path.stem}.csv", index=False)
        frames[path.stem] = frame
    return frames


def _style() -> None:
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
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1000:
        return f"${value / 1000:.0f}k"
    return f"${value:.0f}"


def _save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _waterfall(latest: pd.Series, path: Path) -> None:
    """Movements only. Beginning and ending are close to $4M, so a stacked
    waterfall hides the $10k–$130k steps. The title carries the two totals."""
    labels = ["New", "Expansion", "Reactivation", "Contraction", "Churn"]
    values = [
        float(latest.new_mrr),
        float(latest.expansion_mrr),
        float(latest.reactivation_mrr),
        -float(latest.contraction_mrr),
        -float(latest.churned_mrr),
    ]
    colors = [TEAL, TEAL, TEAL, CORAL, CORAL]
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.bar(labels, values, color=colors, width=0.72)
    ax.axhline(0, color=NAVY, linewidth=0.8)
    span = max(abs(value) for value in values) or 1.0
    for index, value in enumerate(values):
        text = _money_axis(abs(value), 0)
        text = f"+{text}" if value >= 0 else f"-{text}"
        offset = span * 0.04
        ax.text(
            index,
            value + offset if value >= 0 else value - offset,
            text,
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=9,
            color=NAVY,
        )
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_money_axis))
    ax.set_ylim(-span * 1.35, span * 1.35)
    month_label = pd.Timestamp(str(latest.month_start)).strftime("%B %Y")
    ax.set_title(
        f"{month_label} movements  ·  beginning {_money_axis(float(latest.beginning_mrr), 0)}"
        f"  ·  ending {_money_axis(float(latest.ending_mrr), 0)}"
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, path)


def _charts(frames: dict[str, pd.DataFrame], chart_dir: Path) -> dict[str, str]:
    _style()
    chart_dir.mkdir(parents=True, exist_ok=True)
    notes: dict[str, str] = {}
    bridge = frames["01_mrr_bridge"]

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    positions = np.arange(len(bridge))
    ax.plot(positions, bridge["ending_mrr"], color=TEAL, linewidth=2.2)
    ax.fill_between(positions, bridge["ending_mrr"], color=TEAL, alpha=0.12)
    ax.set_xticks(positions[::3])
    ax.set_xticklabels(bridge["month_start"].astype(str).str.slice(0, 7).iloc[::3], rotation=45, ha="right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(_money_axis))
    ax.set_title("Ending MRR")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, chart_dir / "mrr_trend.png")
    notes["mrr_trend.png"] = "Ending MRR includes expansion and excludes churned accounts. It is not a sum of every historical month."

    _waterfall(bridge.iloc[-1], chart_dir / "mrr_waterfall.png")
    notes["mrr_waterfall.png"] = "Teal adds MRR and coral removes it. Beginning and ending are in the title because those totals are about $4M and the steps are not."

    cohort = frames["05_cohort_retention"]
    view = cohort[(cohort["cohort_month"] >= "2024-10-01") & (cohort["tenure_month"] <= 12)].copy()
    pivot = (
        view.pivot(index="cohort_month", columns="tenure_month", values="logo_retention")
        .sort_index()
        .sort_index(axis=1)
    )
    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    image = np.ma.masked_invalid(pivot.to_numpy(dtype=float))
    heatmap = ax.imshow(image, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([str(int(col)) for col in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([str(idx)[:7] for idx in pivot.index], fontsize=8)
    ax.set_xlabel("Months since signup")
    ax.set_title("Logo retention by signup month")
    fig.colorbar(heatmap, ax=ax, fraction=0.046, pad=0.04)
    _save(fig, chart_dir / "cohort_retention.png")
    notes["cohort_retention.png"] = "Each cell is logos still paying divided by the original cohort. Blank cells have not happened yet."

    usage = frames["06_usage_quartile_churn"]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.bar(usage["usage_band"], usage["next_month_churn_rate"], color=[CORAL, GOLD, TEAL, NAVY])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _pos: f"{value * 100:.1f}%"))
    ax.set_title("Chance of churning next month, by this month's adoption quartile")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, chart_dir / "usage_churn.png")
    notes["usage_churn.png"] = "Quartiles are ranked inside each month. Q1 is the lowest adoption score."

    plans = frames["03_plan_churn"]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.bar(plans["plan_name"], plans["monthly_logo_churn"], color=NAVY)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _pos: f"{value * 100:.1f}%"))
    ax.set_title("Pooled monthly logo churn by plan, trailing 12 months")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, chart_dir / "plan_churn.png")
    notes["plan_churn.png"] = "This is churn events divided by account-months that started the month active. It is not 12-month logo retention."

    channel = frames["08_cac_by_channel"].merge(frames["09_channel_retention_m6"], on="channel_name")
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    ax.scatter(channel["cac"], channel["logo_retention_m6"], s=80, color=TEAL)
    for row in channel.itertuples(index=False):
        ax.annotate(row.channel_name, (row.cac, row.logo_retention_m6), textcoords="offset points", xytext=(6, 4), fontsize=9)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(_money_axis))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _pos: f"{value * 100:.0f}%"))
    ax.set_xlabel("Blended CAC")
    ax.set_ylabel("Logo still paying at month 6")
    ax.set_title("Acquisition cost against six-month retention")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, chart_dir / "channel_cac_retention.png")
    notes["channel_cac_retention.png"] = "CAC is channel spend divided by signups. Retention uses only cohorts that have had six months."

    return notes


def _export_power_bi(conn: sqlite3.Connection, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    exports = {
        "dim_date": "SELECT * FROM dim_date ORDER BY full_date",
        "dim_plan": "SELECT * FROM dim_plan ORDER BY tier_rank",
        "dim_channel": "SELECT * FROM dim_channel ORDER BY channel_id",
        "dim_account": "SELECT * FROM dim_account ORDER BY account_id",
        "fact_subscription_month": "SELECT * FROM fact_subscription_month ORDER BY month_start, account_id",
        "fact_usage": "SELECT * FROM vw_usage_health ORDER BY month_start, account_id",
        "fact_ticket": "SELECT * FROM fact_ticket ORDER BY opened_date, ticket_id",
        "fact_marketing_spend": "SELECT * FROM fact_marketing_spend ORDER BY month_start, channel_id",
    }
    money_columns = {"mrr", "prior_mrr", "spend", "monthly_price_per_seat"}
    for name, sql in exports.items():
        frame = pd.read_sql_query(sql, conn)
        for column in frame.columns:
            if column in money_columns:
                frame[column] = frame[column].round(2)
        frame.to_csv(out_dir / f"{name}.csv", index=False)


def _trailing_twelve(conn: sqlite3.Connection) -> pd.DataFrame:
    start = pd.read_sql_query(
        """
        SELECT account_id, mrr AS mrr_start
        FROM fact_subscription_month
        WHERE month_start = ? AND mrr > 0
        """,
        conn,
        params=(TTM_START.isoformat(),),
    )
    end = pd.read_sql_query(
        """
        SELECT account_id, mrr AS mrr_end
        FROM fact_subscription_month
        WHERE month_start = ?
        """,
        conn,
        params=(AS_OF_MONTH.isoformat(),),
    )
    merged = start.merge(end, on="account_id", how="left")
    merged["mrr_end"] = merged["mrr_end"].fillna(0.0)
    starting = float(merged["mrr_start"].sum())
    ending = float(merged["mrr_end"].sum())
    kept = float(np.minimum(merged["mrr_end"], merged["mrr_start"]).sum())
    return pd.DataFrame([{
        "window_start": TTM_START.isoformat(),
        "window_end": AS_OF_MONTH.isoformat(),
        "starting_logos": int(len(merged)),
        "retained_logos": int((merged["mrr_end"] > 0).sum()),
        "starting_mrr": round(starting, 2),
        "ending_mrr_of_cohort": round(ending, 2),
        "grr_mrr": round(kept, 2),
        "nrr": round(ending / starting, 4),
        "grr": round(kept / starting, 4),
        "logo_retention": round(float((merged["mrr_end"] > 0).mean()), 4),
    }])


def _forecast(bridge: pd.DataFrame) -> pd.DataFrame:
    recent = bridge.tail(6)
    expansion_rate = float((recent["expansion_mrr"] / recent["beginning_mrr"]).mean())
    contraction_rate = float((recent["contraction_mrr"] / recent["beginning_mrr"]).mean())
    churn_rate = float((recent["churned_mrr"] / recent["beginning_mrr"]).mean())
    new_mrr = float(recent["new_mrr"].mean())
    reactivation_mrr = float(recent["reactivation_mrr"].mean())
    ending = float(bridge.iloc[-1]["ending_mrr"])
    last = pd.Timestamp(str(bridge.iloc[-1]["month_start"]))
    rows = []
    for step in range(1, 4):
        beginning = ending
        expansion = beginning * expansion_rate
        contraction = beginning * contraction_rate
        churn = beginning * churn_rate
        ending = beginning + new_mrr + reactivation_mrr + expansion - contraction - churn
        future = last + pd.DateOffset(months=step)
        rows.append({
            "month_start": future.strftime("%Y-%m-%d"),
            "forecast_ending_mrr": round(ending, 2),
            "method": "carry forward the last six months of new MRR and of expansion, contraction, and churn as a share of beginning MRR",
        })
    return pd.DataFrame(rows)


def analyze(db_path: Path) -> None:
    output = ROOT / "outputs"
    output.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        frames = run_sql_folder(conn, output / "sql")
        mart = pd.read_sql_query("SELECT * FROM vw_subscription", conn)
        counts = pd.read_sql_query(
            """
            SELECT
              (SELECT COUNT(*) FROM dim_account) AS accounts,
              (SELECT COUNT(*) FROM fact_subscription_month) AS subscription_rows,
              (SELECT COUNT(*) FROM fact_ticket) AS tickets,
              (SELECT MIN(month_start) FROM fact_subscription_month) AS first_month,
              (SELECT MAX(month_start) FROM fact_subscription_month) AS last_month
            """,
            conn,
        ).iloc[0]
        ttm = _trailing_twelve(conn)
        _export_power_bi(conn, ROOT / "powerbi" / "data")
    finally:
        conn.close()

    mart.to_csv(output / "subscription_mart.csv", index=False)
    ttm.to_csv(ROOT / "powerbi" / "data" / "metric_trailing_twelve_months.csv", index=False)
    ttm.to_csv(output / "metric_trailing_twelve_months.csv", index=False)

    bridge = frames["01_mrr_bridge"].copy()
    identity = (
        bridge["beginning_mrr"] + bridge["new_mrr"] + bridge["reactivation_mrr"] + bridge["expansion_mrr"]
        - bridge["contraction_mrr"] - bridge["churned_mrr"] - bridge["ending_mrr"]
    ).abs().max()
    if identity > 0.05:
        raise RuntimeError(f"Published bridge does not tie out (gap {identity}).")

    forecast = _forecast(bridge)
    forecast.to_csv(output / "mrr_forecast.csv", index=False)
    notes = _charts(frames, output / "charts")

    latest = bridge.iloc[-1]
    year_ago = bridge[bridge["month_start"] == "2025-09-01"].iloc[0]
    yoy = float(latest.ending_mrr) / float(year_ago.ending_mrr) - 1
    quick_denom = float(latest.contraction_mrr + latest.churned_mrr)
    quick = float(latest.new_mrr + latest.reactivation_mrr + latest.expansion_mrr) / quick_denom if quick_denom else float("inf")
    nrr = float(ttm.iloc[0]["nrr"])
    grr = float(ttm.iloc[0]["grr"])
    logo_retention = float(ttm.iloc[0]["logo_retention"])

    plans = frames["03_plan_churn"].sort_values("monthly_logo_churn")
    worst_plan = plans.iloc[-1]
    best_plan = plans.iloc[0]
    usage = frames["06_usage_quartile_churn"].set_index("usage_quartile")
    q1 = float(usage.loc[1, "next_month_churn_rate"])
    q4 = float(usage.loc[4, "next_month_churn_rate"])
    tickets = frames["07_tickets_before_churn"].set_index("churn_within_60_days")
    channel = frames["08_cac_by_channel"].merge(frames["09_channel_retention_m6"], on=["channel_name", "channel_group"])
    expensive = channel.sort_values("cac", ascending=False).iloc[0]
    sticky = channel.sort_values("logo_retention_m6", ascending=False).iloc[0]
    concentration = frames["10_account_concentration"].iloc[0]
    industries = frames["04_industry_scorecard"].sort_values("monthly_logo_churn")
    snapshot = frames["02_plan_snapshot"]

    if quick >= 2:
        quick_words = "New, reactivation, and expansion dollars cover the month's losses more than twice over."
    elif quick >= 1:
        quick_words = "New, reactivation, and expansion dollars still cover contraction and churn."
    else:
        quick_words = "Losses are larger than new and expansion dollars."

    bullets = [
        (
            f"Ending MRR in September 2026 is {money(float(latest.ending_mrr))}, {pct(yoy)} versus September 2025. "
            f"ARR on that ending balance is {money(float(latest.ending_mrr) * 12)}."
        ),
        (
            f"The October 2025 cohort of paying accounts finished September 2026 at {pct(nrr)} net revenue retention "
            f"and {pct(grr)} gross revenue retention. Logo retention for that same group is {pct(logo_retention)}. "
            + (
                "Expansion more than replaced the revenue that contracted or churned."
                if nrr >= 1
                else "Expansion did not replace the revenue that contracted or churned."
            )
        ),
        (
            f"In September, the quick ratio was {quick:.2f}. {quick_words} "
            f"The quick ratio counts new logos. The cohort NRR above does not. "
            f"Pooled monthly logo churn is {pct(float(worst_plan.monthly_logo_churn))} on {worst_plan.plan_name} "
            f"and {pct(float(best_plan.monthly_logo_churn))} on {best_plan.plan_name}."
        ),
        (
            f"Accounts in the lowest adoption quartile churned the next month at {pct(q1)}, "
            f"against {pct(q4)} in the highest quartile ({q1 / q4:.1f}×). "
            f"Accounts that churned within 60 days were already opening "
            f"{float(tickets.loc[1, 'avg_tickets']):.2f} tickets a month, versus "
            f"{float(tickets.loc[0, 'avg_tickets']):.2f} for accounts that stayed."
        ),
        (
            f"{expensive.channel_name} costs {money(float(expensive.cac))} per logo and keeps "
            f"{pct(float(expensive.logo_retention_m6))} of matured logos at month 6. "
            f"{sticky.channel_name} keeps {pct(float(sticky.logo_retention_m6))} at a CAC of {money(float(sticky.cac))}. "
            f"The ten largest accounts are {pct(float(concentration.top_10_mrr_share))} of ending MRR."
        ),
    ]

    actions = [
        (
            f"Treat {worst_plan.plan_name} churn as an onboarding problem, not a discounting problem. "
            f"Its pooled monthly logo churn is {pct(float(worst_plan.monthly_logo_churn))} "
            f"against {pct(float(best_plan.monthly_logo_churn))} on {best_plan.plan_name}. "
            "A price cut on the plan that already stays would not touch the logos that are leaving."
        )
    ]
    if q4 > 0 and q1 >= q4 * 1.5:
        actions.append(
            f"Page the account team when adoption falls into the bottom quartile. "
            f"Those accounts churn the next month at {pct(q1)}, against {pct(q4)} for the top quartile. "
            "The signal is already in the usage table. It does not need a new model to be useful."
        )
    else:
        actions.append(
            f"Adoption quartile is a weak separator this close ({pct(q1)} versus {pct(q4)}). "
            "Do not staff a health-score program on it until the gap is wider."
        )
    qualified = channel[
        (channel["channel_name"] != expensive.channel_name)
        & (channel["logo_retention_m6"] >= float(expensive.logo_retention_m6) + 0.08)
        & (channel["cac"] < float(expensive.cac))
    ].sort_values("cac")
    if not qualified.empty:
        pick = qualified.iloc[0]
        actions.append(
            f"Move the next increment of budget from {expensive.channel_name} toward {pick.channel_name}. "
            f"{expensive.channel_name} costs {money(float(expensive.cac))} per logo and keeps "
            f"{pct(float(expensive.logo_retention_m6))} at month 6. {pick.channel_name} keeps "
            f"{pct(float(pick.logo_retention_m6))} and costs {money(float(pick.cac))}. "
            f"{sticky.channel_name} retains slightly more ({pct(float(sticky.logo_retention_m6))}) but costs {money(float(sticky.cac))}."
            if pick.channel_name != sticky.channel_name
            else (
                f"Move the next increment of budget from {expensive.channel_name} toward {pick.channel_name}. "
                f"{expensive.channel_name} costs {money(float(expensive.cac))} per logo and keeps "
                f"{pct(float(expensive.logo_retention_m6))} at month 6. {pick.channel_name} keeps "
                f"{pct(float(pick.logo_retention_m6))} and costs {money(float(pick.cac))}."
            )
        )
    else:
        actions.append(
            f"Keep the channel mix. The most expensive channel, {expensive.channel_name}, is not also a weaker retainer than the cheaper ones."
        )

    forecast_bits = ", ".join(
        f"{str(row.month_start)[:7]} {money(row.forecast_ending_mrr)}" for row in forecast.itertuples(index=False)
    )
    footnotes = [
        "Synthetic data for a portfolio project. Lumen Workspace is fictional.",
        f"Window: {counts['first_month']} to {counts['last_month']}. {int(counts['accounts']):,} accounts, {int(counts['subscription_rows']):,} account-months, {int(counts['tickets']):,} tickets.",
        "Ending MRR is the sum of mrr on the close month. Churn rows are stored at mrr 0 so the bridge can see the lost dollars. Do not count rows to count customers.",
        "Trailing-twelve-month NRR follows the accounts that were paying in October 2025 and values them again in September 2026, with churned accounts at zero. GRR caps each account at its starting MRR so expansion does not help the ratio.",
        "Monthly NRR in the DAX file is a different measure: one month of movement divided by that month's beginning MRR. Do not compare it with the trailing-twelve-month figure.",
        f"The highest pooled monthly logo churn by industry is {industries.iloc[-1]['industry']} at {pct(float(industries.iloc[-1]['monthly_logo_churn']))}. The lowest is {industries.iloc[0]['industry']} at {pct(float(industries.iloc[0]['monthly_logo_churn']))}.",
        f"Baseline MRR path if the last six months of rates repeat: {forecast_bits}. It assumes new-logo dollars stay flat in absolute terms and that expansion, contraction, and churn stay a constant share of beginning MRR.",
        "Power BI Desktop is Windows-only. The CSV model and DAX are in powerbi/. This HTML report is the view that opens on a Mac.",
    ]
    kpis = [
        ("Ending MRR", money(float(latest.ending_mrr)), "September 2026 close"),
        ("MRR vs last year", pct(yoy), "September 2026 vs September 2025"),
        ("Net revenue retention", pct(nrr), "Oct 2025 cohort, valued Sep 2026"),
        ("Gross revenue retention", pct(grr), "Same cohort, expansion capped"),
        ("Logo retention", pct(logo_retention), "Same cohort, still paying"),
        ("Quick ratio", f"{quick:.2f}", "September: added MRR / lost MRR"),
    ]
    plan_rows = [
        [row.plan_name, f"{int(row.logos):,}", money(row.ending_mrr), money(row.arpa), f"{row.avg_seats:.1f}"]
        for row in snapshot.itertuples(index=False)
    ]
    channel_rows = [
        [
            row.channel_name,
            money(row.spend),
            f"{int(row.new_logos):,}",
            money(row.cac),
            pct(row.logo_retention_m6),
        ]
        for row in channel.sort_values("cac", ascending=False).itertuples(index=False)
    ]
    tables = [
        ("Close by plan", ["Plan", "Logos", "Ending MRR", "ARPA", "Avg seats"], plan_rows),
        ("Channels", ["Channel", "Spend", "New logos", "CAC", "Still paying at month 6"], channel_rows),
    ]
    chart_notes = [(name, notes[name]) for name in [
        "mrr_trend.png",
        "mrr_waterfall.png",
        "cohort_retention.png",
        "usage_churn.png",
        "plan_churn.png",
        "channel_cac_retention.png",
    ]]
    exec_charts = [
        ("charts/mrr_trend.png", "Ending MRR", notes["mrr_trend.png"]),
        ("charts/mrr_waterfall.png", "September bridge", notes["mrr_waterfall.png"]),
        ("charts/cohort_retention.png", "Who is still here", notes["cohort_retention.png"]),
        ("charts/usage_churn.png", "Adoption before churn", notes["usage_churn.png"]),
    ]
    write_findings(
        output / "FINDINGS.md",
        "Lumen Workspace — subscription review",
        "September 2026",
        kpis,
        bullets,
        actions,
        chart_notes,
        tables,
        footnotes,
    )
    write_html(
        output / "executive_report.html",
        "Lumen subscription review",
        "SaaS analytics  ·  closed September 2026",
        "Ending MRR is the live book. Net revenue retention follows one cohort for twelve months. The two numbers answer different questions.",
        kpis,
        bullets,
        actions,
        exec_charts,
        tables,
        footnotes,
    )
    print(
        f"Ending MRR {money(float(latest.ending_mrr))}  |  YoY {pct(yoy)}  |  NRR {pct(nrr)}  |  GRR {pct(grr)}  |  quick {quick:.2f}"
    )
    print(f"Wrote {output / 'executive_report.html'}")
