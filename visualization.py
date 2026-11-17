"""成員 B：讀取資料，依類別加總後產生圓餅圖。"""

import argparse
from decimal import Decimal
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager

from storage import DEFAULT_DATA_PATH, Expense, load_expenses


def category_totals(expenses: list[Expense]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for expense in expenses:
        totals[expense.category] = totals.get(expense.category, Decimal("0")) + expense.amount
    return totals


def create_pie_chart(path: Path = DEFAULT_DATA_PATH):
    """回傳 Figure；無資料則回傳 None，方便之後擴充或在其他介面重用。"""
    totals = category_totals(load_expenses(path))
    if not totals:
        return None
    installed = {font.name for font in font_manager.fontManager.ttflist}
    candidates = ["Microsoft JhengHei", "PingFang TC", "Heiti TC", "Noto Sans CJK TC",
                  "Noto Sans CJK JP", "WenQuanYi Zen Hei", "Arial Unicode MS"]
    family = next((name for name in candidates if name in installed), "DejaVu Sans")
    # 局部設定，避免改動其他模組的全域繪圖設定。
    with plt.rc_context({"font.family": family, "axes.unicode_minus": False}):
        figure, axes = plt.subplots(figsize=(7, 5.5), layout="constrained")
        axes.pie([float(value) for value in totals.values()], labels=list(totals),
                 startangle=90)
        axes.set_title("支出類別分布")
        axes.set_aspect("equal")
    return figure


def show_pie_chart(path: Path = DEFAULT_DATA_PATH) -> None:
    try:
        figure = create_pie_chart(path)
    except (ValueError, OSError) as exc:
        print(f"無法產生圖表：{exc}")
        return
    if figure is None:
        print("目前沒有支出資料，請先新增支出。")
        return
    print("已產生圓餅圖，關閉圖表視窗後可繼續操作。")
    plt.show()
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="依支出類別顯示圓餅圖")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="CSV 檔案路徑")
    show_pie_chart(parser.parse_args().data)


if __name__ == "__main__":
    main()
