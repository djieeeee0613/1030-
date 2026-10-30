"""FastAPI + MySQL basic activity registration prototype."""
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import pymysql
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymysql.err import IntegrityError

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / '.env')
app = FastAPI(title='搖滾台中活動報名平台')
app.mount('/static', StaticFiles(directory=BASE / 'static'), name='static')
templates = Jinja2Templates(directory=str(BASE / 'templates'))


def conn():
    return pymysql.connect(host=os.getenv('DB_HOST', '127.0.0.1'),
        port=int(os.getenv('DB_PORT', '3306')), user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''), database=os.getenv('DB_NAME', 'ruins_events'),
        charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=False)


def fetchall(sql, params=()):
    with conn() as db:
        with db.cursor() as c:
            c.execute(sql, params)
            return c.fetchall()


def fetchone(sql, params=()):
    rows = fetchall(sql, params)
    return rows[0] if rows else None


def is_open(event):
    return event['status'] == 'open' and (event['registration_deadline'] is None or datetime.now() < event['registration_deadline'])


def get_event(event_id):
    item = fetchone('''SELECT e.*, COUNT(r.registration_id) AS participants FROM events e
                 LEFT JOIN registrations r ON r.event_id=e.event_id
                 WHERE e.event_id=%s GROUP BY e.event_id''', (event_id,))
    if not item:
        raise HTTPException(404, '找不到活動')
    item['can_register'] = is_open(item)
    return item


@app.get('/')
def index(request: Request):
    items = fetchall('''SELECT e.*, COUNT(r.registration_id) AS participants FROM events e
                     LEFT JOIN registrations r ON r.event_id=e.event_id
                     GROUP BY e.event_id ORDER BY e.event_date''')
    for item in items:
        item['can_register'] = is_open(item)
    return templates.TemplateResponse(request, 'index.html', {'events': items})


@app.get('/events/new')
def new_event(request: Request):
    return templates.TemplateResponse(request, 'new.html', {})


@app.post('/events')
def create_event(title: str = Form(...), description: str = Form(''), location: str = Form(''),
                 event_date: datetime = Form(...), registration_deadline: datetime = Form(...)):
    title = title.strip()
    if not title or registration_deadline >= event_date:
        return RedirectResponse('/events/new?error=' + quote('活動名稱不可空白，截止時間必須早於活動時間'), 303)
    with conn() as db:
        with db.cursor() as c:
            c.execute('''INSERT INTO events(title,description,location,event_date,registration_deadline)
                      VALUES (%s,%s,%s,%s,%s)''', (title,description.strip(),location.strip(),event_date,registration_deadline))
            event_id = c.lastrowid
        db.commit()
    return RedirectResponse(f'/events/{event_id}?msg=' + quote('活動建立成功'), 303)


@app.get('/events/{event_id}')
def detail(request: Request, event_id: int):
    return templates.TemplateResponse(request, 'detail.html', {'event': get_event(event_id)})


@app.post('/events/{event_id}/register')
def register(event_id: int, name: str = Form(...), phone: str = Form(...)):
    name, phone = name.strip(), phone.strip()
    if not name or not phone:
        return RedirectResponse(f'/events/{event_id}?error=' + quote('姓名與電話不得空白'), 303)
    # Row lock prevents closing the event midway through a registration transaction.
    with conn() as db:
        try:
            with db.cursor() as c:
                c.execute('SELECT * FROM events WHERE event_id=%s FOR UPDATE', (event_id,))
                event = c.fetchone()
                if not event:
                    raise HTTPException(404, '找不到活動')
                if not is_open(event):
                    return RedirectResponse(f'/events/{event_id}?error=' + quote('活動已截止報名'), 303)
                c.execute('INSERT INTO registrations(event_id,name,phone) VALUES (%s,%s,%s)', (event_id,name,phone))
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            if exc.args and exc.args[0] == 1062:
                return RedirectResponse(f'/events/{event_id}?error=' + quote('相同姓名與電話已報名這場活動'), 303)
            raise
    return RedirectResponse(f'/events/{event_id}?msg=' + quote('報名成功！'), 303)


@app.get('/events/{event_id}/registrations')
def registrations(request: Request, event_id: int):
    event = get_event(event_id)
    members = fetchall('SELECT name, phone, created_at FROM registrations WHERE event_id=%s ORDER BY created_at', (event_id,))
    return templates.TemplateResponse(request, 'registrations.html', {'event': event, 'members': members})


@app.post('/events/{event_id}/close')
def close(event_id: int):
    get_event(event_id)
    with conn() as db:
        with db.cursor() as c:
            c.execute("UPDATE events SET status='closed' WHERE event_id=%s", (event_id,))
        db.commit()
    return RedirectResponse(f'/events/{event_id}?msg=' + quote('報名已關閉'), 303)
