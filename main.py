from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import events, registrations

app = FastAPI(title='活動報名平台')
app.mount('/static', StaticFiles(directory='static'), name='static')
app.include_router(events.router)
app.include_router(registrations.router)
