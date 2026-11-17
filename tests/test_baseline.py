"""驗證跨模組資料相容、追加儲存與圖表，而非只檢查個別實作細節。"""

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from storage import append_expense, load_expenses, make_expense
from visualization import category_totals, create_pie_chart


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "nested" / "expenses.csv"

    def test_append_round_trip_and_category_totals(self):
        rows = [make_expense("2026-11-17", "0.10", "餐飲", '早餐, "加蛋"\n外帶'),
                make_expense("2026-11-17", "0.20", "餐飲"),
                make_expense("2026-11-17", "120", "交通")]
        for row in rows:
            append_expense(row, self.path)
        self.assertEqual(load_expenses(self.path), rows)
        self.assertEqual(category_totals(load_expenses(self.path)),
                         {"餐飲": Decimal("0.30"), "交通": Decimal("120.00")})

    def test_empty_data_does_not_create_chart(self):
        self.assertEqual(load_expenses(self.path), [])
        self.assertIsNone(create_pie_chart(self.path))

    def test_invalid_csv_is_not_overwritten(self):
        self.path.parent.mkdir()
        bad_data = "date,amount,category,notes\n2026-11-17,oops,餐飲,\n"
        self.path.write_text(bad_data, encoding="utf-8")
        with self.assertRaises(ValueError):
            append_expense(make_expense("2026-11-17", "10", "交通"), self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), bad_data)

    def test_invalid_input_is_rejected(self):
        for values in [("2026-02-30", "10", "餐飲"), ("2026-11-17", "NaN", "餐飲"),
                       ("2026-11-17", "0", "餐飲"), ("2026-11-17", "-1", "餐飲"),
                       ("2026-11-17", "1.001", "餐飲"), ("2026-11-17", "10", " ")]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                make_expense(*values)

    def test_chart_uses_category_totals(self):
        for amount, category in [("10", "餐飲"), ("20", "餐飲"), ("30", "交通")]:
            append_expense(make_expense("2026-11-17", amount, category), self.path)
        figure = create_pie_chart(self.path)
        self.addCleanup(plt.close, figure)
        wedges = figure.axes[0].patches
        self.assertEqual(len(wedges), 2)
        self.assertAlmostEqual(wedges[0].theta2 - wedges[0].theta1, 180)
        output = Path(self.temp.name) / "chart.png"
        figure.savefig(output)
        self.assertGreater(output.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
