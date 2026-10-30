"""活動報名平台（使用端）

用 uv 管理（套件寫在 pyproject.toml）：
    uv sync            安裝套件（第一次或套件有更新時）
    uv run main.py     啟動
瀏覽器開：  http://localhost:3000
"""
import os

import psycopg
from flask import Flask, render_template

from route import register_routes

app = Flask(__name__, template_folder="template")

WEEK = "一二三四五六日"


@app.template_filter("fmt_date")
def fmt_date(dt):
    """2026/11/15（日）19:00"""
    return f"{dt:%Y/%m/%d}（{WEEK[dt.weekday()]}）{dt:%H:%M}"


@app.template_filter("pad")
def pad(n):
    return f"{int(n):02d}"


register_routes(app)


@app.errorhandler(404)
def not_found(_e):
    return render_template("error.html", title="找不到頁面", message="找不到這個頁面。"), 404


@app.errorhandler(psycopg.Error)
def db_error(e):
    app.logger.exception(e)
    return render_template(
        "error.html",
        title="系統暫時無法使用",
        message="無法連線資料庫。請確認 PostgreSQL 服務已啟動、已建立 ruins_events 並匯入 database.sql，且 DB.py 的密碼正確。",
        detail=str(e).strip(),
    ), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "3000")), debug=False)
