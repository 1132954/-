# 簡易記帳工具 v0.1

軟體工程導論 Assignment 1 的共同基礎版本。使用 Python 輸入支出、儲存 CSV，並依各類別的**金額合計**產生圓餅圖。

## v0.1 功能

- 連續新增多筆支出：日期、金額、類別、選填備註。
- 日期留空使用今天；金額必須大於零且最多兩位小數。
- 支出追加至 CSV，重新啟動後資料仍保留。
- 讀取 CSV，依類別加總並顯示基本圓餅圖。
- 輸入與視覺化模組可以獨立執行，也可由共同選單啟動。

## 環境設定

需要 **Python 3.10 以上**。圖表視窗請在有桌面介面的電腦執行，例如本機 VS Code 的終端機。

```bash
git clone https://github.com/1132954/-.git expense-tracker
cd expense-tracker
python -m venv .venv
```

啟用虛擬環境（依作業系統擇一）：

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bat
:: Windows 命令提示字元 CMD
.venv\Scripts\activate.bat
```

```bash
# macOS / Linux
source .venv/bin/activate
```

安裝套件：

```bash
python -m pip install -r requirements.txt
```

如果系統的 Python 指令是 `python3`，請將上述建立環境的 `python` 改成 `python3`。虛擬環境啟用後可使用 `python`。

## 執行方式

### 共同入口

```bash
python main.py
```

選單：`1` 新增支出、`2` 顯示圓餅圖、`0` 結束。

輸入範例：

```text
日期 YYYY-MM-DD：2026-11-17
金額：85
類別（例如餐飲、交通）：餐飲
備註（可留空）：早餐
```

每筆儲存後可以繼續新增。**在下一筆的日期欄位輸入 `q`**，返回主選單；關閉圓餅圖視窗後也會回到選單。

### 成員 A：只執行輸入模組

```bash
python input_module.py
```

### 成員 B：只執行視覺化模組

```bash
python visualization.py
```

預設資料位置是專案內的 `data/expenses.csv`，首次新增時自動建立。這個檔案不會提交到 Git，以免兩人的個人記帳資料互相覆蓋。

三個入口皆支援 `--data` 指定其他 CSV。例如用同一份練習資料執行：

```bash
python input_module.py --data data/practice.csv
python visualization.py --data data/practice.csv
python main.py --data data/practice.csv
```

若要保存自己的記帳資料，請另外備份 CSV；`data/practice.csv` 等自訂路徑請自行確認是否要提交。

## 不需輸入即可看範例

```bash
python visualization.py --data data/sample_expenses.csv
```

範例共 7 筆支出：餐飲 300、交通 200、娛樂 350、生活用品 200，總計 1,050。

![範例支出類別圓餅圖](docs/sample_pie_chart.png)

程式會自動選用常見中文字型。Windows 通常使用 Microsoft JhengHei，macOS 使用 PingFang TC；Linux 建議安裝 Noto Sans CJK。若中文顯示方框，請安裝中文字型後重新啟動程式。

## 模組與共用介面

| 檔案 | 負責範圍 |
| --- | --- |
| `main.py` | 共同選單入口 |
| `input_module.py` | A：輸入支出與呼叫儲存介面 |
| `visualization.py` | B：類別統計與圖表 |
| `storage.py` | 共用：CSV 格式、讀取與追加儲存 |
| `data/sample_expenses.csv` | 可提交的固定範例資料 |
| `tests/test_baseline.py` | 基礎版本的整合檢查 |

CSV 欄位固定依序為：

```csv
date,amount,category,notes
2026-11-17,85.00,餐飲,早餐
```

- `date`：日期，`YYYY-MM-DD`。
- `amount`：正數金額，最多兩位小數；以 Decimal 運算，寫入 CSV 時固定兩位小數。
- `category`：非空白的類別文字。
- `notes`：可空白；含逗號、引號或換行時由 CSV 模組自動處理。
- CSV 使用 UTF-8 BOM，方便試算表軟體辨識中文。

A 透過 `make_expense(...)` 建立資料，再呼叫 `append_expense(expense, path)`。B 透過 `load_expenses(path)` 取得 `list[Expense]`；`category_totals(...)` 回傳各類別總金額，`create_pie_chart(path)` 回傳 Figure，無資料時回傳 None。

變更共用欄位或介面前，兩位成員應先確認，避免輸入與視覺化模組讀寫不同格式。

## 後續協作方式

這次是共同起點；兩人的分支開發與合併紀錄，要從後續實際新增的功能建立。**一項功能、一條功能分支、一次合併、一個新版本**；同一項功能可以有多次有意義的 commit。

基本的金額與日期檢查已包含在 v0.1，因此後續可選真正新增的功能：

| 建議順序 | 負責人 | 一次新增的功能 | 分支範例 |
| --- | --- | --- | --- |
| v0.2 | A | 修改既有支出 | `feature/edit-expense` |
| v0.3 | B | 提供圖表 PNG 匯出操作 | `feature/export-chart` |
| v0.4 | A | 刪除指定支出 | `feature/delete-expense` |
| v0.5 | B | 依月份篩選圓餅圖 | `feature/monthly-chart` |

以上為待開發清單，尚未包含於本版本。專案看板可使用「待辦 → 開發中 → 待檢查 → 完成」。

開始一項功能時，先更新主線，再建立分支：

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/edit-expense
```

開發與測試後，提交這項功能的相關檔案並推送分支：

```bash
git add input_module.py storage.py README.md tests/
git commit -m "feat: allow editing an existing expense"
git push -u origin feature/edit-expense
```

請依實際修改內容調整檔案清單與提交訊息。每人使用自己的 Git 姓名與電子郵件提交，保留真實貢獻紀錄。

另一位成員檢查後，執行整合。以下指令也適用於分支由另一台裝置推送到相同儲存庫的情況：

```bash
git switch main
git pull --ff-only origin main
git fetch origin
git merge --no-ff origin/feature/edit-expense -m "Merge expense editing feature"
python -m unittest discover -s tests -v
git push origin main
```

`--no-ff` 會保留 merge commit，方便在分支圖看到合併。若出現衝突，先協調修正、完成合併並重新測試，再推送。兩人可以同時開發；每次整合完成後，下一項功能需以最新主線確認相容性。

## 驗證

```bash
python -m unittest discover -s tests -v
```

測試涵蓋 CSV 追加與重新讀取、中文及特殊字元、精確金額加總、無資料狀態、錯誤資料保護，以及依金額比例繪圖。測試在暫存目錄中執行，不會修改個人記帳資料。

最後繳交仍需由兩位成員完成：實際貢獻與分支合併紀錄、Insights → Network 截圖、展示影片與影片連結。本版本附上原始碼、執行說明、範例資料及範例圓餅圖。
