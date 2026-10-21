"""Regression checks for the subscription bridge. They do not need a server."""

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
        self.db_path = Path(self.temp.name) / "lumen.db"
        build_warehouse(self.db_path, n_accounts=50, seed=7)
        self.conn = sqlite3.connect(self.db_path)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def test_bridge_ties_out_every_month(self):
        gap = self.conn.execute(
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
        self.assertLessEqual(gap, 0.05)

    def test_churn_rows_carry_the_lost_mrr_and_zero_ending(self):
        bad = self.conn.execute(
            """
            SELECT COUNT(*) FROM fact_subscription_month
            WHERE movement = 'Churn' AND (mrr != 0 OR prior_mrr <= 0)
            """
        ).fetchone()[0]
        self.assertEqual(bad, 0)

    def test_usage_covers_every_subscription_month(self):
        missing = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM fact_subscription_month AS s
            LEFT JOIN fact_usage_monthly AS u
              ON u.account_id = s.account_id AND u.month_start = s.month_start
            WHERE u.account_id IS NULL
            """
        ).fetchone()[0]
        self.assertEqual(missing, 0)

    def test_every_account_starts_with_a_new_logo(self):
        missing = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM dim_account AS a
            LEFT JOIN fact_subscription_month AS s
              ON s.account_id = a.account_id
             AND s.movement = 'New'
             AND s.month_start = date(a.signup_date, 'start of month')
            WHERE s.account_id IS NULL
            """
        ).fetchone()[0]
        self.assertEqual(missing, 0)


if __name__ == "__main__":
    unittest.main()
