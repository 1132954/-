"""v0.5 的共同入口；A、B 模組仍可分別執行。"""

import argparse
from pathlib import Path

from input_module import run_delete, run_edit, run_input
from query_expenses import run_query
from storage import DEFAULT_DATA_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description="簡易記帳工具 v0.5")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="CSV 檔案路徑")
    path = parser.parse_args().data
    print("簡易記帳工具 v0.5")
    while True:
        print("\n1. 新增支出\n2. 修改既有支出\n3. 刪除既有支出\n4. 顯示類別圓餅圖\n5. 查詢支出（日期／類別）\n0. 結束")
        try:
            choice = input("請選擇：").strip()
            if choice == "1":
                run_input(path)
            elif choice == "2":
                run_edit(path)
            elif choice == "3":
                run_delete(path)
            elif choice == "4":
                from visualization import show_pie_chart
                show_pie_chart(path)
            elif choice == "5":
                run_query(path)
            elif choice == "0":
                print("已結束。")
                return
            else:
                print("請輸入 1、2、3、4、5 或 0。")
        except (EOFError, KeyboardInterrupt):
            print("\n已結束。")
            return


if __name__ == "__main__":
    main()
