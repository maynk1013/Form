"""Create the SQLite warehouse and refuse to publish it if checks fail."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.config import SALES_END, SALES_START
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
    """Raise if keys, windows, or money identities are broken."""
    orphan_sql = [
        """
        SELECT COUNT(*) FROM fact_sales AS f
        LEFT JOIN dim_store AS s ON s.store_id = f.store_id
        WHERE s.store_id IS NULL
        """,
        """
        SELECT COUNT(*) FROM fact_sales AS f
        LEFT JOIN dim_product AS p ON p.product_id = f.product_id
        WHERE p.product_id IS NULL
        """,
        """
        SELECT COUNT(*) FROM fact_sales AS f
        LEFT JOIN dim_customer AS c ON c.customer_id = f.customer_id
        WHERE c.customer_id IS NULL
        """,
        """
        SELECT COUNT(*) FROM fact_sales AS f
        LEFT JOIN dim_date AS d ON d.full_date = f.order_date
        WHERE d.date_key IS NULL
        """,
    ]
    for statement in orphan_sql:
        orphans = conn.execute(statement).fetchone()[0]
        if orphans:
            raise RuntimeError(f"Found {orphans} fact rows with a missing dimension key.")

    outside = conn.execute(
        """
        SELECT COUNT(*) FROM fact_sales
        WHERE order_date < ? OR order_date > ?
        """,
        (SALES_START.isoformat(), SALES_END.isoformat()),
    ).fetchone()[0]
    if outside:
        raise RuntimeError(f"{outside} sales fall outside the closed-month window.")

    money_gap = conn.execute(
        """
        SELECT MAX(ABS(net_revenue - cogs - gross_profit))
        FROM vw_sales_lines
        """
    ).fetchone()[0]
    if money_gap is None or money_gap > 0.02:
        raise RuntimeError(f"Gross profit does not equal net revenue minus COGS (gap {money_gap}).")

    bad_scores = conn.execute(
        """
        SELECT COUNT(*) FROM vw_customer_rfm
        WHERE r_score NOT BETWEEN 1 AND 5
           OR f_score NOT BETWEEN 1 AND 5
           OR m_score NOT BETWEEN 1 AND 5
        """
    ).fetchone()[0]
    if bad_scores:
        raise RuntimeError("RFM scores fell outside 1–5.")

    missing_targets = conn.execute(
        """
        WITH months AS (
          SELECT DISTINCT date(full_date, 'start of month') AS month_start
          FROM dim_date
          WHERE full_date BETWEEN ? AND ?
        )
        SELECT COUNT(*)
        FROM dim_store AS s
        CROSS JOIN months AS m
        LEFT JOIN fact_store_target AS t
          ON t.store_id = s.store_id
         AND t.month_start = m.month_start
        WHERE t.store_id IS NULL
        """,
        (SALES_START.isoformat(), SALES_END.isoformat()),
    ).fetchone()[0]
    if missing_targets:
        raise RuntimeError(f"{missing_targets} store-months have no revenue target.")


def build_warehouse(db_path: Path, n_orders: int | None = None, n_customers: int | None = None, seed: int | None = None) -> None:
    """Rebuild aurora.db from scratch."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    kwargs = {}
    if n_orders is not None:
        kwargs["n_orders"] = n_orders
    if n_customers is not None:
        kwargs["n_customers"] = n_customers
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
        _insert(
            conn,
            "dim_store",
            ["store_id", "store_name", "city", "state", "region", "opened_date", "sq_ft"],
            tables["dim_store"],
        )
        _insert(
            conn,
            "dim_product",
            ["product_id", "sku", "product_name", "category", "subcategory", "unit_cost", "list_price"],
            tables["dim_product"],
        )
        _insert(
            conn,
            "dim_customer",
            ["customer_id", "customer_name", "segment", "city", "state", "region", "first_order_date"],
            tables["dim_customer"],
        )
        _insert(
            conn,
            "fact_sales",
            [
                "sales_line_id", "order_id", "order_date", "store_id", "product_id",
                "customer_id", "quantity", "unit_list_price", "discount_rate", "unit_cost", "is_returned",
            ],
            tables["fact_sales"],
        )
        _insert(
            conn,
            "fact_store_target",
            ["store_id", "month_start", "revenue_target"],
            tables["fact_store_target"],
        )
        conn.executescript((SQL_DIR / "02_views.sql").read_text())
        assert_warehouse(conn)
        conn.commit()
    finally:
        conn.close()
