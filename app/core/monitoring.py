from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from .config import settings

# Метрики
REQUEST_COUNT = Counter(
    'http_request_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users_total',
    'Number of active users'
)

DB_CONNECTION_POOL = Gauge(
    'db_connection_pool',
    'Database connection pool statistics',
    ['state']
)

def setup_monitoring(app):
    # Sentry для отслеживания ошибок
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0
    )
    
    # Prometheus метрики
    Instrumentator().instrument(app).expose(app) 