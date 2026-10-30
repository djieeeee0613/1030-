from datetime import datetime
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from DB import execute, fetch_all

router = APIRouter()
templates = Jinja2Templates(directory='templates')

@router.get('/')
def index(request: Request):
    events = fetch_all("SELECT * FROM events WHERE status = 'open' ORDER BY event_date")
    return templates.TemplateResponse(request=request, name='events.html', context={'events': events})

@router.get('/events/new')
def new_event(request: Request):
    return templates.TemplateResponse(request=request, name='event_form.html')

@router.post('/events')
def create_event(title: str = Form(..., max_length=100), event_date: datetime = Form(...), description: str = Form(''), location: str = Form('', max_length=150)):
    if not title.strip():
        raise HTTPException(status_code=422, detail='請輸入活動名稱')
    execute('INSERT INTO events (title, description, location, event_date) VALUES (%s, %s, %s, %s)', (title.strip(), description.strip(), location.strip(), event_date))
    return RedirectResponse('/', status_code=303)
