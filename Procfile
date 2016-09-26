web: gunicorn app:app
worker: celery worker -A tasks.cel -l INFO