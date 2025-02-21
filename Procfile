web: gunicorn drillflow.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A drillflow worker -l INFO
bot: python manage.py runbot 