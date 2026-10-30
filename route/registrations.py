"""查看我的報名：用連絡電話查詢報名過的活動"""
from flask import Blueprint, render_template, request

import DB
from route import PHONE_RE, normalize_phone

bp = Blueprint("registrations", __name__)


@bp.get("/registrations")
def my_registrations():
    raw_phone = request.args.get("phone", "").strip()
    phone = normalize_phone(raw_phone)
    rows = None
    error = None

    if raw_phone:
        if not PHONE_RE.match(phone):
            error = "連絡電話格式不正確，請輸入 8~13 位數字。"
        else:
            rows = DB.get_registrations_by_phone(phone)

    return render_template(
        "registrations.html",
        phone=raw_phone,
        rows=rows,
        error=error,
        new_id=request.args.get("new", type=int),
    )
