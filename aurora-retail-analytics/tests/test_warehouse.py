"""Regression checks for the retail warehouse. They do not need a server."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.warehouse import build_warehouse


class WarehouseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "aurora.db"
        build_warehouse(self.db_path, n_orders=400, n_customers=80, seed=7)
        self.conn = sqlite3.connect(self.db_path)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def test_every_line_keeps_the_money_identity(self):
        gap = self.conn.execute(
            "SELECT MAX(ABS(net_revenue - cogs - gross_profit)) FROM vw_sales_lines"
        ).fetchone()[0]
        self.assertLessEqual(gap, 0.02)

    def test_returned_lines_do_not_keep_revenue(self):
        leaked = self.conn.execute(
            """
            SELECT COUNT(*) FROM vw_sales_lines
            WHERE is_returned = 1 AND (net_revenue != 0 OR cogs != 0 OR gross_profit != 0)
            """
        ).fetchone()[0]
        self.assertEqual(leaked, 0)

    def test_buyers_have_rfm_scores(self):
        missing = self.conn.execute(
            """
            SELECT COUNT(*) FROM dim_customer AS c
            LEFT JOIN vw_customer_rfm AS r ON r.customer_id = c.customer_id
            WHERE r.customer_id IS NULL
            """
        ).fetchone()[0]
        self.assertEqual(missing, 0)

    def test_targets_cover_the_window(self):
        stores = self.conn.execute("SELECT COUNT(*) FROM dim_store").fetchone()[0]
        targets = self.conn.execute("SELECT COUNT(*) FROM fact_store_target").fetchone()[0]
        self.assertEqual(targets, stores * 21)

    def test_no_duplicate_product_on_an_order(self):
        dupes = self.conn.execute(
            """
            SELECT COUNT(*) FROM (
              SELECT order_id, product_id
              FROM fact_sales
              GROUP BY order_id, product_id
              HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]
        self.assertEqual(dupes, 0)


if __name__ == "__main__":
    unittest.main()
