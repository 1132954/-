"""A 的 v0.5：依日期範圍與類別查詢既有支出，不修改 CSV。"""

import argparse
from datetime import date
from decimal import Decimal
from pathlib import Path

from storage import DEFAULT_DATA_PATH, Expense, load_expenses


def _parse_date(value: str | None, label: str) -> date | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        parsed = date.fromisoformat(text)
        if parsed.isoformat() != text:
            raise ValueError
        return parsed
    except ValueError as exc:
        raise ValueError(f"{label}請使用有效的 YYYY-MM-DD 日期。") from exc


def filter_expenses(expenses: list[Expense], start: str | None = None,
                    end: str | None = None, category: str | None = None) -> list[tuple[int, Expense]]:
    """條件採 AND；日期包含起訖日，回傳 CSV 中原本的 1-based 編號。"""
    start_date = _parse_date(start, "開始日期")
    end_date = _parse_date(end, "結束日期")
    if start_date and end_date and start_date > end_date:
        raise ValueError("開始日期不能晚於結束日期。")
    category_key = (category or "").strip().casefold()
    results = []
    for number, expense in enumerate(expenses, start=1):
        expense_date = date.fromisoformat(expense.date)
        if start_date and expense_date < start_date:
            continue
        if end_date and expense_date > end_date:
            continue
        if category_key and expense.category.casefold() != category_key:
            continue
        results.append((number, expense))
    return results


def query_file(path: Path = DEFAULT_DATA_PATH, start: str | None = None,
               end: str | None = None, category: str | None = None) -> list[tuple[int, Expense]]:
    return filter_expenses(load_expenses(path), start, end, category)


def print_results(results: list[tuple[int, Expense]]) -> None:
    print("\n=== 支出查詢結果 ===")
    if not results:
        print("沒有符合條件的支出。")
    for number, expense in results:
        notes = expense.notes.replace("\r", " ").replace("\n", " / ")
        print(f"原編號 {number} | {expense.date} | {expense.amount:.2f} | {expense.category} | {notes}")
    total = sum((expense.amount for _, expense in results), Decimal("0"))
    print(f"符合筆數：{len(results)}；金額合計：{total:.2f}")


def run_query(path: Path = DEFAULT_DATA_PATH) -> None:
    print("\n依日期／類別查詢；留空代表不限制，任何欄位輸入 :q 可返回。")
    while True:
        try:
            start = input("開始日期 YYYY-MM-DD（q 返回）：").strip()
            if start.casefold() in {"q", ":q"}:
                return
            end = input("結束日期 YYYY-MM-DD（可留空）：").strip()
            if end.casefold() == ":q":
                return
            category = input("類別（完全符合，留空查全部）：").strip()
            if category.casefold() == ":q":
                return
            print_results(query_file(path, start, end, category))
        except (ValueError, OSError) as exc:
            print(f"查詢失敗：{exc}")
        except (EOFError, KeyboardInterrupt):
            print("\n已結束查詢。")
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="v0.5：依日期範圍與類別查詢支出")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="CSV 檔案路徑")
    parser.add_argument("--start", help="開始日期 YYYY-MM-DD（含當日）")
    parser.add_argument("--end", help="結束日期 YYYY-MM-DD（含當日）")
    parser.add_argument("--category", help="類別名稱；英文忽略大小寫")
    args = parser.parse_args()
    if all(value is None for value in [args.start, args.end, args.category]):
        run_query(args.data)
        return
    try:
        print_results(query_file(args.data, args.start, args.end, args.category))
    except (ValueError, OSError) as exc:
        parser.exit(1, f"查詢失敗：{exc}\n")


if __name__ == "__main__":
    main()
