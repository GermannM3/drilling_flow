web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
worker: celery -A drillflow worker -l INFO
bot: python manage.py runbot