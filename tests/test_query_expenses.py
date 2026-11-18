import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from query_expenses import filter_expenses, print_results, query_file, run_query
from storage import append_expense, delete_expense, load_expenses, make_expense, update_expense


class QueryExpenseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "expenses.csv"
        self.rows = [make_expense("2026-10-31", "0.10", "餐飲", '早餐, "中文"\n外帶'),
                     make_expense("2026-11-01", "0.20", "餐飲"),
                     make_expense("2026-11-30", "10", "交通"),
                     make_expense("2026-12-01", "20", "Food"),
                     make_expense("2026-12-02", "30", "Seafood")]
        for row in self.rows:
            append_expense(row, self.path)

    def test_no_filters_preserve_all_records_and_order(self):
        self.assertEqual(filter_expenses(self.rows), list(enumerate(self.rows, start=1)))

    def test_date_range_includes_both_endpoints(self):
        self.assertEqual(query_file(self.path, "2026-11-01", "2026-11-30"),
                         [(2, self.rows[1]), (3, self.rows[2])])

    def test_single_date_boundaries(self):
        self.assertEqual(query_file(self.path, start="2026-11-30"),
                         [(3, self.rows[2]), (4, self.rows[3]), (5, self.rows[4])])
        self.assertEqual(query_file(self.path, end="2026-11-01"),
                         [(1, self.rows[0]), (2, self.rows[1])])

    def test_category_is_exact_and_case_insensitive(self):
        self.assertEqual(query_file(self.path, category=" food "), [(4, self.rows[3])])
        self.assertEqual(query_file(self.path, category="餐飲"), [(1, self.rows[0]), (2, self.rows[1])])

    def test_combined_conditions_preserve_original_number(self):
        self.assertEqual(query_file(self.path, "2026-11-01", "2026-11-30", "餐飲"),
                         [(2, self.rows[1])])

    def test_invalid_dates_and_reversed_ranges_are_rejected(self):
        cases = [("2026-02-29", None), (None, "2026-13-01"), ("20261101", None),
                 ("2026-1-1", None), ("abc", None), ("2026-12-01", "2026-11-01")]
        original = self.path.read_bytes()
        for start, end in cases:
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                query_file(self.path, start, end)
        self.assertEqual(self.path.read_bytes(), original)

    def test_result_summary_uses_precise_amounts(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            print_results(query_file(self.path, category="餐飲"))
        self.assertIn("符合筆數：2；金額合計：0.30", output.getvalue())
        self.assertIn("原編號 1", output.getvalue())

    def test_no_matches_display_zero(self):
        results = query_file(self.path, category="不存在的類別")
        self.assertEqual(results, [])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            print_results(results)
        self.assertIn("沒有符合條件", output.getvalue())
        self.assertIn("符合筆數：0；金額合計：0.00", output.getvalue())

    def test_missing_file_does_not_create_data(self):
        self.path.unlink()
        self.assertEqual(query_file(self.path), [])
        self.assertFalse(self.path.exists())

    def test_queries_never_rewrite_csv(self):
        original = self.path.read_bytes()
        query_file(self.path, category="餐飲")
        query_file(self.path, "2026-11-01", "2026-11-30")
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(load_expenses(self.path), self.rows)

    def test_interactive_query_and_cancel(self):
        original = self.path.read_bytes()
        with patch("builtins.input", side_effect=["2026-11-01", "2026-11-30", "餐飲", "q"]):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                run_query(self.path)
        self.assertIn("符合筆數：1；金額合計：0.20", output.getvalue())
        for inputs in [["", ":q"], ["", "", ":q"]]:
            with patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(io.StringIO()):
                run_query(self.path)
        self.assertEqual(self.path.read_bytes(), original)

    def test_invalid_interactive_input_and_eof_do_not_write(self):
        original = self.path.read_bytes()
        with patch("builtins.input", side_effect=["bad", "", "", "q"]):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                run_query(self.path)
        self.assertIn("查詢失敗", output.getvalue())
        with patch("builtins.input", side_effect=EOFError()), contextlib.redirect_stdout(io.StringIO()):
            run_query(self.path)
        self.assertEqual(self.path.read_bytes(), original)

    def test_query_reflects_existing_edit_and_delete_features(self):
        update_expense(1, make_expense("2026-11-03", "25", "交通"), self.path)
        delete_expense(0, self.path)
        original = self.path.read_bytes()
        results = query_file(self.path, "2026-11-01", "2026-11-30", "交通")
        self.assertEqual([number for number, _ in results], [1, 2])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            print_results(results)
        self.assertIn("符合筆數：2；金額合計：35.00", output.getvalue())
        self.assertEqual(self.path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
