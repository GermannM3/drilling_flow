from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logger import setup_logging
from routers import orders, contractors, auth, geo, webapp

# Инициализация логгера
setup_logging()

app = FastAPI(title="DrillFlow API")

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(contractors.router)
app.include_router(orders.router)
app.include_router(geo.router)
app.include_router(webapp.router) 