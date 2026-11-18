import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from input_module import run_edit
from storage import append_expense, load_expenses, make_expense, update_expense


class EditExpenseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "expenses.csv"
        self.rows = [make_expense("2026-11-17", "85", "餐飲", '早餐, "加蛋"\n外帶'),
                     make_expense("2026-11-17", "120", "交通", "火車")]
        for row in self.rows:
            append_expense(row, self.path)

    def run_flow(self, inputs):
        with patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(io.StringIO()) as output:
            run_edit(self.path)
        return output.getvalue()

    def test_update_only_selected_record_and_round_trip_notes(self):
        updated = make_expense("2026-11-18", "90.50", "早餐", '備註, "中文"\n第二行')
        update_expense(0, updated, self.path)
        self.assertEqual(load_expenses(self.path), [updated, self.rows[1]])

    def test_invalid_index_preserves_file(self):
        original = self.path.read_bytes()
        for index in [-1, 2, 99]:
            with self.subTest(index=index), self.assertRaises(IndexError):
                update_expense(index, self.rows[0], self.path)
        self.assertEqual(self.path.read_bytes(), original)

    def test_invalid_update_preserves_file(self):
        from dataclasses import replace
        from decimal import Decimal
        original = self.path.read_bytes()
        with self.assertRaises(ValueError):
            update_expense(0, replace(self.rows[0], amount=Decimal("-1")), self.path)
        self.assertEqual(self.path.read_bytes(), original)

    def test_atomic_replace_failure_preserves_file_and_cleans_temp(self):
        original = self.path.read_bytes()
        with patch("storage.os.replace", side_effect=PermissionError("locked")):
            with self.assertRaises(PermissionError):
                update_expense(0, self.rows[1], self.path)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), ["expenses.csv"])

    def test_stale_selection_is_rejected(self):
        snapshot = load_expenses(self.path)
        append_expense(make_expense("2026-11-18", "10", "其他"), self.path)
        original = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "資料已變更"):
            update_expense(0, self.rows[1], self.path, expected_expenses=snapshot)
        self.assertEqual(self.path.read_bytes(), original)

    def test_interactive_edit_keeps_blanks_and_clears_notes(self):
        output = self.run_flow(["1", "", "95.50", "", "-", "q"])
        rows = load_expenses(self.path)
        self.assertEqual(rows[0], make_expense("2026-11-17", "95.50", "餐飲", ""))
        self.assertEqual(rows[1], self.rows[1])
        self.assertIn("已更新", output)

    def test_cancel_and_invalid_amount_do_not_change_data(self):
        original = self.path.read_bytes()
        self.run_flow(["q"])
        self.assertEqual(self.path.read_bytes(), original)
        self.run_flow(["1", "", "-1", "", "", "q"])
        self.assertEqual(self.path.read_bytes(), original)

    def test_no_records_and_interrupted_entry(self):
        self.path.unlink()
        self.assertIn("沒有任何既有支出", self.run_flow([]))
        self.assertFalse(self.path.exists())
        append_expense(self.rows[0], self.path)
        original = self.path.read_bytes()
        self.run_flow(["1", EOFError()])
        self.assertEqual(self.path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
