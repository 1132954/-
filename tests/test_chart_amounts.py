import tempfile
import unittest
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from storage import append_expense, make_expense
from visualization import create_pie_chart


class ChartAmountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "expenses.csv"

    def test_category_amounts_and_total_use_exact_saved_values(self):
        for amount, category in [("0.10", "餐飲"), ("0.20", "餐飲"), ("1234.56", "交通")]:
            append_expense(make_expense("2026-11-18", amount, category), self.path)
        original = self.path.read_bytes()
        figure = create_pie_chart(self.path)
        self.addCleanup(plt.close, figure)
        labels = {text.get_text() for text in figure.axes[0].texts}
        self.assertEqual(labels, {"餐飲\n金額 0.30", "交通\n金額 1,234.56"})
        self.assertEqual(figure.axes[0].get_title(), "支出類別分布\n總支出：1,234.86")
        self.assertEqual(self.path.read_bytes(), original)

    def test_single_category_shows_amount_and_total(self):
        append_expense(make_expense("2026-11-18", "85", "餐飲"), self.path)
        figure = create_pie_chart(self.path)
        self.addCleanup(plt.close, figure)
        self.assertEqual([text.get_text() for text in figure.axes[0].texts], ["餐飲\n金額 85.00"])
        self.assertEqual(figure.axes[0].get_title(), "支出類別分布\n總支出：85.00")


if __name__ == "__main__":
    unittest.main()
