"""首頁活動清單、單一活動報名表單與送出報名"""
from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

import DB
from route import PHONE_RE, normalize_phone

bp = Blueprint("events", __name__)

NOT_FOUND_MSG = "找不到這個活動。"
CLOSED_MSG = "這個活動已截止報名，無法再報名。"


def _closed_page(event):
    return render_template("error.html", title="已截止報名",
                           message=f"「{event['title']}」{CLOSED_MSG}"), 403


@bp.get("/")
def home():
    events = DB.get_open_events()
    added = request.args.get("added", type=int)
    added_event = next((e for e in events if e["event_id"] == added), None) if added else None
    return render_template("home.html", events=events, closed_events=DB.get_closed_events(),
                           added_event=added_event)


@bp.get("/events/new")
def new_event_form():
    return render_template("new_event.html", values={}, error=None)


@bp.post("/events/new")
def new_event():
    values = {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "location": request.form.get("location", "").strip(),
        "event_date": request.form.get("event_date", "").strip(),
    }

    def fail(msg):
        return render_template("new_event.html", values=values, error=msg), 400

    if not values["title"] or len(values["title"]) > 100:
        return fail("請輸入活動名稱（最多 100 字）。")
    if not values["location"] or len(values["location"]) > 150:
        return fail("請輸入活動地點（最多 150 字）。")
    if len(values["description"]) > 1000:
        return fail("活動說明最多 1000 字。")
    try:
        event_date = datetime.fromisoformat(values["event_date"])
    except ValueError:
        return fail("請選擇正確的活動日期與時間。")
    if event_date <= datetime.now():
        return fail("活動日期必須是未來的時間。")

    new_id = DB.add_event(values["title"], values["description"], values["location"], event_date)
    return redirect(url_for("events.home", added=new_id))


@bp.get("/events/<int:event_id>")
def register_form(event_id):
    event = DB.get_event(event_id)
    if not event:
        return render_template("error.html", title="找不到頁面", message=NOT_FOUND_MSG), 404
    if event["status"] != "open":
        return _closed_page(event)
    return render_template("register.html", event=event, values={}, error=None)


@bp.post("/events/<int:event_id>/register")
def register(event_id):
    event = DB.get_event(event_id)
    if not event:
        return render_template("error.html", title="找不到頁面", message=NOT_FOUND_MSG), 404
    if event["status"] != "open":
        return _closed_page(event)

    name = request.form.get("name", "").strip()
    raw_phone = request.form.get("phone", "").strip()
    phone = normalize_phone(raw_phone)
    values = {"name": name, "phone": raw_phone}

    def fail(msg, code):
        return render_template("register.html", event=event, values=values, error=msg), code

    if not name or len(name) > 50:
        return fail("請輸入姓名（最多 50 字）。", 400)
    if not PHONE_RE.match(phone):
        return fail("連絡電話格式不正確，請輸入 8~13 位數字，例如 0912345678。", 400)
    if DB.has_registered(event_id, name, phone):
        return fail(f"「{name}」已經用這支電話報名過這場活動了，請勿重複報名。", 409)

    new_id = DB.add_registration(event_id, name, phone)
    return redirect(url_for("registrations.my_registrations", phone=phone, new=new_id))


# ---- 活動報名清單（顯示目前報名人數）與截止報名 ----
@bp.get("/events/<int:event_id>/registrations")
def event_registrations(event_id):
    event = DB.get_event(event_id)
    if not event:
        return render_template("error.html", title="找不到頁面", message=NOT_FOUND_MSG), 404
    return render_template(
        "event_registrations.html",
        event=event,
        rows=DB.get_event_registrations(event_id),
        changed=request.args.get("changed"),
    )


@bp.post("/events/<int:event_id>/close")
def close_event(event_id):
    return _set_status(event_id, "closed")


@bp.post("/events/<int:event_id>/reopen")
def reopen_event(event_id):
    return _set_status(event_id, "open")


def _set_status(event_id, status):
    if not DB.get_event(event_id):
        return render_template("error.html", title="找不到頁面", message=NOT_FOUND_MSG), 404
    DB.set_event_status(event_id, status)
    return redirect(url_for("events.event_registrations", event_id=event_id, changed=status))
