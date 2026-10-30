# 1030-

## 活動報名平台（使用端）

### 執行方式（PostgreSQL + uv）
1. 啟動 PostgreSQL 服務（課堂 phpweb 環境的 `runStopDB.bat` 會「切換」服務：沒開就啟動、已開就停止）。
2. 開 Adminer（`runPHPWeb.bat` → http://localhost:9000/adminer.php?pgsql=&username=postgres），
   用 postgres 帳號登入，在 SQL command 執行：
   ```
   CREATE DATABASE ruins_events ENCODING 'UTF8' TEMPLATE template0;
   ```
3. 進入 `ruins_events` 資料庫，匯入 `database.sql`（建立兩張表與 3 個 demo 活動，可重複匯入）。
4. 在 `DB.py` 的 `CONFIG` 填入 postgres 密碼（或設定環境變數 `DB_PASSWORD`）。
5. 安裝套件並啟動：
   ```
   uv sync
   uv run main.py
   ```
6. 瀏覽器開 http://localhost:3000

沒有 uv 的話：`pip install uv`，或 Windows PowerShell 執行
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

> phpweb 資料夾請放在「路徑沒有中文」的位置（例如 `C:\phpweb`），否則 PHP 讀不到 php.ini，Adminer 會顯示 No extension。

### 專案結構
- `main.py` 啟動 Flask、註冊路由
- `DB.py` 資料庫連線與 SQL
- `route/` 路由（首頁與報名、我的報名）
- `template/` HTML 頁面
- `pyproject.toml`、`uv.lock` 套件設定與鎖定版本
