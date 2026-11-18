"""成員 A：支出輸入與修改模組。"""

import argparse
from datetime import date
from pathlib import Path

from storage import DEFAULT_DATA_PATH, append_expense, load_expenses, make_expense, update_expense


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


def run_edit(path: Path = DEFAULT_DATA_PATH) -> None:
    while True:
        try:
            expenses = load_expenses(path)
        except (ValueError, OSError) as exc:
            print(f"無法讀取資料：{exc}")
            return

        if not expenses:
            print("\n目前沒有任何既有支出可修改。")
            return

        print("\n=== 既有支出列表 ===")
        for idx, item in enumerate(expenses, start=1):
            note_display = f" ({item.notes})" if item.notes else ""
            print(f"{idx}. {item.date} | {item.category} | {item.amount:.2f}{note_display}")

        try:
            choice = input("\n請輸入要修改的編號（輸入 q 返回）：").strip()
            if choice.lower() == "q":
                return
            if not choice.isdigit() or not (1 <= int(choice) <= len(expenses)):
                print(f"請輸入 1 到 {len(expenses)} 之間的編號。")
                continue

            target_idx = int(choice) - 1
            current = expenses[target_idx]
            print("（直接按 Enter 代表保留原值；備註輸入 - 代表清空）")

            new_date = input(f"日期 [{current.date}]：").strip() or current.date
            new_amount = input(f"金額 [{current.amount:.2f}]：").strip() or str(current.amount)
            new_category = input(f"類別 [{current.category}]：").strip() or current.category
            raw_notes = input(f"備註 [{current.notes}]：").strip()
            new_notes = "" if raw_notes == "-" else (raw_notes or current.notes)

            updated = make_expense(new_date, new_amount, new_category, new_notes)
            update_expense(target_idx, updated, path, expected_expenses=expenses)
            print(f"已更新：{updated.date} / {updated.category} / {updated.amount:.2f}\n")
        except (ValueError, IndexError, OSError) as exc:
            print(f"修改失敗：{exc}")
        except (EOFError, KeyboardInterrupt):
            print("\n已結束修改。")
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="輸入或修改支出")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="CSV 檔案路徑")
    parser.add_argument("--edit", action="store_true", help="修改既有支出")
    args = parser.parse_args()
    (run_edit if args.edit else run_input)(args.data)


if __name__ == "__main__":
    main()
