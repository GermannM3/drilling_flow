from fastapi import FastAPI
from core.logger import setup_logging
from routers import orders, contractors, auth, geo, webapp

# Инициализация логгера
setup_logging()

app = FastAPI(title="DrillFlow API")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(contractors.router)
app.include_router(orders.router)
app.include_router(geo.router)
app.include_router(webapp.router) 