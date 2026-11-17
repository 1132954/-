"""成員 A：支出輸入模組。"""

import argparse
from datetime import date
from pathlib import Path

from storage import DEFAULT_DATA_PATH, append_expense, make_expense


def run_input(path: Path = DEFAULT_DATA_PATH) -> None:
    print("\n新增支出（日期處輸入 q 返回／結束；日期留空使用今天）")
    while True:
        try:
            date_text = input("日期 YYYY-MM-DD：").strip()
            if date_text.lower() == "q":
                return
            amount = input("金額：")
            category = input("類別（例如餐飲、交通）：")
            notes = input("備註（可留空）：")
            expense = make_expense(date_text or date.today().isoformat(), amount, category, notes)
            append_expense(expense, path)
        except (ValueError, OSError) as exc:
            print(f"無法儲存：{exc}")
            continue
        except (EOFError, KeyboardInterrupt):
            print("\n已結束輸入。")
            return
        print(f"已儲存：{expense.date} / {expense.category} / {expense.amount:.2f}")
        print(f"資料位置：{Path(path).resolve()}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="輸入並儲存多筆支出")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="CSV 檔案路徑")
    run_input(parser.parse_args().data)


if __name__ == "__main__":
    main()
