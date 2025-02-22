from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, database
from .routers import orders, contractors, auth, geo

app = FastAPI(title="DrillFlow API")

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(contractors.router, prefix="/api/contractors", tags=["contractors"])
app.include_router(geo.router, prefix="/api/geo", tags=["geo"]) 