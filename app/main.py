from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.logger import setup_logging
from .routers import orders, contractors, auth, geo, webapp
from .core.health_check import router as health_router
from .core.config import settings

# Настройка логирования
logger = setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(health_router, tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(contractors.router, prefix="/api/contractors", tags=["contractors"])
app.include_router(geo.router, prefix="/api/geo", tags=["geo"])
app.include_router(webapp.router, tags=["webapp"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up DrillFlow API")

@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": settings.VERSION,
        "environment": settings.ENV
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"} 