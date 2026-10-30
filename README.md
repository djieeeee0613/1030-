# 活動報名平台

以 FastAPI、Jinja2 和 PostgreSQL 實作活動新增、報名和名單查詢。

## 本機設定

需要已安裝 uv、Python 3.9 以上及已啟動的 PostgreSQL。以下指令在此專案資料夾中執行：

```bash
uv sync
createdb ruins_events
psql -d ruins_events -f database.sql
```

上述資料庫指令使用目前系統帳號連線；請依本機 PostgreSQL 的帳號及密碼調整。若有專用帳號，設定連線網址，例如：

```bash
export DATABASE_URL='postgresql://使用者名稱:密碼@localhost:5432/ruins_events'
```

若未設定 `DATABASE_URL`，程式會使用 `postgresql://localhost/ruins_events`。密碼不要提交到 Git。

啟動伺服器：

```bash
uv run uvicorn main:app --reload
```

使用瀏覽器開啟 http://127.0.0.1:8000，按「新增活動」建立活動，接著可以報名和查看名單。`database.sql` 不會自動刪除資料，亦不包含範例資料。

此基本款沒有登入或權限控制，任何能連線的人都可新增活動及查看報名者姓名和電話；只適合本機或受信任的教學環境，公開前需加入授權及隱私保護。

執行測試：

```bash
uv run python -m unittest discover -s tests -v
```

使用 `uv add 套件名稱` 新增套件，並將 `pyproject.toml` 和 `uv.lock` 一起提交至 Git。
