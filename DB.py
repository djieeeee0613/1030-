"""資料庫連線與所有 SQL 查詢（PostgreSQL）。

連線設定預設為本機 PostgreSQL（使用者 postgres、資料庫 ruins_events）。
密碼請改下面的 password，或設定環境變數 DB_PASSWORD；
其他也可用環境變數覆蓋：DB_HOST / DB_PORT / DB_USER / DB_NAME
"""
import os

import psycopg
from psycopg.rows import dict_row

CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456"),  # ← 裝 PostgreSQL 時設定的 postgres 密碼
    "dbname": os.getenv("DB_NAME", "ruins_events"),
}

INT_MAX = 2**31 - 1  # events.event_id 是 INT，過大的編號直接視為不存在


def _run(sql, args=None, fetch=True):
    with psycopg.connect(**CONFIG, row_factory=dict_row, autocommit=True) as conn:
        cur = conn.execute(sql, args)
        return cur.fetchall() if fetch else cur.fetchone()


# ---- 活動 ----
def _events_by_status(status):
    return _run(
        """SELECT e.*, COUNT(r.registration_id) AS reg_count
             FROM events e
             LEFT JOIN registrations r ON r.event_id = e.event_id
            WHERE e.status = %s
            GROUP BY e.event_id
            ORDER BY e.event_date""",
        (status,),
    )


def get_open_events():
    """首頁：可報名的活動清單（含目前報名人數）"""
    return _events_by_status("open")


def get_closed_events():
    """首頁下方：已截止報名的活動（含報名人數）"""
    return _events_by_status("closed")


def get_event(event_id):
    """單一活動（不論是否截止）；不存在回傳 None"""
    if not 0 < event_id <= INT_MAX:
        return None
    rows = _run(
        """SELECT e.*,
                  (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.event_id) AS reg_count
             FROM events e
            WHERE e.event_id = %s""",
        (event_id,),
    )
    return rows[0] if rows else None


def set_event_status(event_id, status):
    """截止報名（closed）或重新開放（open）"""
    _run("UPDATE events SET status = %s WHERE event_id = %s RETURNING event_id",
         (status, event_id), fetch=False)


def get_open_event(event_id):
    """單一可報名活動；不存在或已截止回傳 None"""
    if not 0 < event_id <= INT_MAX:
        return None
    rows = _run(
        """SELECT e.*,
                  (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.event_id) AS reg_count
             FROM events e
            WHERE e.event_id = %s AND e.status = 'open'""",
        (event_id,),
    )
    return rows[0] if rows else None


# ---- 報名 ----
def has_registered(event_id, name, phone):
    """重複報名檢查：同一活動中「同名且同電話」視為重複"""
    rows = _run(
        """SELECT registration_id FROM registrations
            WHERE event_id = %s AND name = %s AND phone = %s""",
        (event_id, name, phone),
    )
    return bool(rows)


def get_event_registrations(event_id):
    """某活動的報名清單（依報名先後）"""
    return _run(
        """SELECT registration_id, name, phone, created_at
             FROM registrations
            WHERE event_id = %s
            ORDER BY created_at, registration_id""",
        (event_id,),
    )


def add_registration(event_id, name, phone):
    """新增報名，回傳新的 registration_id"""
    row = _run(
        """INSERT INTO registrations (event_id, name, phone)
           VALUES (%s, %s, %s) RETURNING registration_id""",
        (event_id, name, phone),
        fetch=False,
    )
    return row["registration_id"]


def get_registrations_by_phone(phone):
    """以電話查詢報名過的活動"""
    return _run(
        """SELECT r.registration_id, r.name, r.created_at,
                  e.event_id, e.title, e.location, e.event_date, e.status
             FROM registrations r
             JOIN events e ON e.event_id = r.event_id
            WHERE r.phone = %s
            ORDER BY e.event_date""",
        (phone,),
    )


def add_event(title, description, location, event_date):
    """新增活動（狀態預設 open，立即開放報名），回傳新的 event_id"""
    row = _run(
        """INSERT INTO events (title, description, location, event_date)
           VALUES (%s, %s, %s, %s) RETURNING event_id""",
        (title, description, location, event_date),
        fetch=False,
    )
    return row["event_id"]
