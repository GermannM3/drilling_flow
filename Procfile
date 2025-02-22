web: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4
worker: celery -A worker worker -l INFO
bot: python -m bot.bot