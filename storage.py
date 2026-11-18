"""A、B 共用的 CSV 資料介面；金額以 Decimal 處理。"""

import csv
import os
import tempfile
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = ROOT / "data" / "expenses.csv"
FIELDS = ["date", "amount", "category", "notes"]


@dataclass(frozen=True)
class Expense:
    date: str
    amount: Decimal
    category: str
    notes: str = ""


def make_expense(date_text: str, amount_text: str, category: str, notes: str = "") -> Expense:
    """統一檢查輸入與 CSV，避免無效資料進入圓餅圖。"""
    try:
        normalized_date = date.fromisoformat(date_text.strip()).isoformat()
    except ValueError as exc:
        raise ValueError("日期請使用有效的 YYYY-MM-DD 格式。") from exc
    try:
        amount = Decimal(amount_text.strip())
        if not amount.is_finite() or amount <= 0:
            raise ValueError("金額必須是大於零的數字。")
        rounded = amount.quantize(Decimal("0.01"))
        if amount != rounded:
            raise ValueError("金額最多只能有兩位小數。")
    except InvalidOperation as exc:
        raise ValueError("金額請輸入有效數字，最多兩位小數。") from exc
    if not category.strip():
        raise ValueError("類別不能留空。")
    return Expense(normalized_date, rounded, category.strip(), notes.strip())


def load_expenses(path: Path = DEFAULT_DATA_PATH) -> list[Expense]:
    """不存在或空白的資料檔代表尚未有支出；格式錯誤則明確回報。"""
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        if reader.fieldnames != FIELDS:
            raise ValueError("CSV 欄位必須依序為：" + ",".join(FIELDS))
        expenses = []
        for row in reader:
            if None in row or any(row.get(field) is None for field in FIELDS):
                raise ValueError(f"CSV 第 {reader.line_num} 行的欄位數量不正確。")
            try:
                expenses.append(make_expense(*(row[field] for field in FIELDS)))
            except ValueError as exc:
                raise ValueError(f"CSV 第 {reader.line_num} 行：{exc}") from exc
    return expenses


def append_expense(expense: Expense, path: Path = DEFAULT_DATA_PATH) -> None:
    """只追加資料，不覆寫既有紀錄；先確認既有檔案可以正常讀取。"""
    path = Path(path)
    expense = make_expense(expense.date, str(expense.amount), expense.category, expense.notes)
    load_expenses(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow({"date": expense.date, "amount": f"{expense.amount:.2f}",
                         "category": expense.category, "notes": expense.notes})


def _write_expenses_atomically(expenses: list[Expense], path: Path) -> None:
    """先完成同目錄暫存檔，再替換 CSV；寫入失敗時保留原檔。"""
    validated = [make_expense(item.date, str(item.amount), item.category, item.notes)
                 for item in expenses]
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8-sig", newline="",
                                         dir=path.parent, prefix=f".{path.name}.",
                                         suffix=".tmp", delete=False) as handle:
            temp_path = Path(handle.name)
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            for item in validated:
                writer.writerow({"date": item.date, "amount": f"{item.amount:.2f}",
                                 "category": item.category, "notes": item.notes})
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def update_expense(index: int, updated: Expense, path: Path = DEFAULT_DATA_PATH,
                   *, expected_expenses: list[Expense] | None = None) -> None:
    """依 0-based 索引修改一筆；可檢查使用者選取後資料是否有變更。"""
    path = Path(path)
    expenses = load_expenses(path)
    if expected_expenses is not None and expenses != expected_expenses:
        raise ValueError("操作期間資料已變更，請重新選擇支出。")
    if not (0 <= index < len(expenses)):
        raise IndexError("找不到指定的支出項目。")
    expenses[index] = make_expense(updated.date, str(updated.amount), updated.category, updated.notes)
    _write_expenses_atomically(expenses, path)
