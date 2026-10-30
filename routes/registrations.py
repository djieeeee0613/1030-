from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from DB import execute, fetch_all, fetch_one

router = APIRouter()
templates = Jinja2Templates(directory='templates')

def get_event(event_id):
    event = fetch_one('SELECT * FROM events WHERE event_id = %s', (event_id,))
    if not event:
        raise HTTPException(status_code=404, detail='找不到活動')
    return event

@router.get('/events/{event_id}/register')
def register_form(event_id: int, request: Request):
    event = get_event(event_id)
    if event['status'] != 'open':
        raise HTTPException(status_code=400, detail='此活動已截止報名')
    return templates.TemplateResponse(request=request, name='register.html', context={'event': event})

@router.post('/events/{event_id}/register')
def register(event_id: int, name: str = Form(..., max_length=50), phone: str = Form(..., max_length=20)):
    event = get_event(event_id)
    if event['status'] != 'open':
        raise HTTPException(status_code=400, detail='此活動已截止報名')
    if not name.strip() or not phone.strip():
        raise HTTPException(status_code=422, detail='請填寫姓名和聯絡電話')
    count = execute("INSERT INTO registrations (event_id, name, phone) SELECT event_id, %s, %s FROM events WHERE event_id = %s AND status = 'open'", (name.strip(), phone.strip(), event_id))
    if not count:
        raise HTTPException(status_code=400, detail='此活動已截止報名')
    return RedirectResponse('/?registered=1', status_code=303)

@router.get('/events/{event_id}/attendees')
def attendees(event_id: int, request: Request):
    event = get_event(event_id)
    registrations = fetch_all('SELECT name, phone, created_at FROM registrations WHERE event_id = %s ORDER BY created_at', (event_id,))
    return templates.TemplateResponse(request=request, name='attendees.html', context={'event': event, 'registrations': registrations})
