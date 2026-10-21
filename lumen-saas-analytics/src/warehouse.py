"""Create the SQLite warehouse and refuse to publish it if the bridge breaks."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.generate import generate

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"


def _insert(conn: sqlite3.Connection, table: str, columns: list[str], rows: list[tuple]) -> None:
    placeholders = ", ".join(["?"] * len(columns))
    column_list = ", ".join(columns)
    conn.executemany(
        f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})",
        rows,
    )


def assert_warehouse(conn: sqlite3.Connection) -> None:
    duplicate = conn.execute(
        """
        SELECT COUNT(*) FROM (
          SELECT account_id, month_start
          FROM fact_subscription_month
          GROUP BY 1, 2
          HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]
    if duplicate:
        raise RuntimeError("An account has two rows in the same month.")

    bad_movement = conn.execute(
        """
        SELECT COUNT(*) FROM fact_subscription_month
        WHERE (movement = 'New' AND NOT (prior_mrr = 0 AND mrr > 0))
           OR (movement = 'Reactivation' AND NOT (prior_mrr = 0 AND mrr > 0))
           OR (movement = 'Churn' AND NOT (prior_mrr > 0 AND mrr = 0))
           OR (movement = 'Expansion' AND NOT (mrr > prior_mrr AND prior_mrr > 0))
           OR (movement = 'Contraction' AND NOT (mrr > 0 AND mrr < prior_mrr))
           OR (movement = 'Retained' AND NOT (mrr = prior_mrr AND mrr > 0))
        """
    ).fetchone()[0]
    if bad_movement:
        raise RuntimeError(f"{bad_movement} subscription rows disagree with their movement label.")

    new_off_signup = conn.execute(
        """
        SELECT COUNT(*)
        FROM fact_subscription_month AS s
        JOIN dim_account AS a ON a.account_id = s.account_id
        WHERE s.movement = 'New'
          AND s.month_start != date(a.signup_date, 'start of month')
        """
    ).fetchone()[0]
    if new_off_signup:
        raise RuntimeError("A New logo is booked outside its signup month.")

    gap = conn.execute(
        """
        WITH months AS (
          SELECT
            SUM(prior_mrr)
              + SUM(CASE WHEN movement = 'New' THEN mrr ELSE 0 END)
              + SUM(CASE WHEN movement = 'Reactivation' THEN mrr ELSE 0 END)
              + SUM(CASE WHEN movement = 'Expansion' THEN mrr - prior_mrr ELSE 0 END)
              - SUM(CASE WHEN movement = 'Contraction' THEN prior_mrr - mrr ELSE 0 END)
              - SUM(CASE WHEN movement = 'Churn' THEN prior_mrr ELSE 0 END)
              - SUM(mrr) AS gap
          FROM fact_subscription_month
          GROUP BY month_start
        )
        SELECT MAX(ABS(gap)) FROM months
        """
    ).fetchone()[0]
    if gap is None or gap > 0.05:
        raise RuntimeError(f"MRR bridge does not tie out (gap {gap}).")

    missing_usage = conn.execute(
        """
        SELECT COUNT(*)
        FROM fact_subscription_month AS s
        LEFT JOIN fact_usage_monthly AS u
          ON u.account_id = s.account_id
         AND u.month_start = s.month_start
        WHERE u.account_id IS NULL
        """
    ).fetchone()[0]
    if missing_usage:
        raise RuntimeError(f"{missing_usage} subscription months have no usage row.")


def build_warehouse(db_path: Path, n_accounts: int | None = None, seed: int | None = None) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    kwargs = {}
    if n_accounts is not None:
        kwargs["n_accounts"] = n_accounts
    if seed is not None:
        kwargs["seed"] = seed
    tables = generate(**kwargs)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript((SQL_DIR / "01_schema.sql").read_text())
        _insert(
            conn,
            "dim_date",
            [
                "date_key", "full_date", "year", "quarter", "month", "month_name",
                "year_month", "day", "day_name", "day_of_week", "week_of_year", "is_weekend",
            ],
            tables["dim_date"],
        )
        _insert(conn, "dim_plan", ["plan_id", "plan_name", "monthly_price_per_seat", "tier_rank"], tables["dim_plan"])
        _insert(conn, "dim_channel", ["channel_id", "channel_name", "channel_group"], tables["dim_channel"])
        _insert(
            conn,
            "dim_account",
            ["account_id", "account_name", "industry", "region", "employee_band", "signup_date", "channel_id"],
            tables["dim_account"],
        )
        _insert(
            conn,
            "fact_subscription_month",
            ["subscription_month_id", "account_id", "month_start", "plan_id", "seats", "mrr", "prior_mrr", "movement"],
            tables["fact_subscription_month"],
        )
        _insert(
            conn,
            "fact_usage_monthly",
            ["account_id", "month_start", "active_users", "events", "adoption_score"],
            tables["fact_usage_monthly"],
        )
        _insert(
            conn,
            "fact_ticket",
            ["ticket_id", "account_id", "opened_date", "priority", "category", "resolution_hours", "csat"],
            tables["fact_ticket"],
        )
        _insert(
            conn,
            "fact_marketing_spend",
            ["spend_id", "month_start", "channel_id", "spend"],
            tables["fact_marketing_spend"],
        )
        conn.executescript((SQL_DIR / "02_views.sql").read_text())
        assert_warehouse(conn)
        conn.commit()
    finally:
        conn.close()
