import os

bind = "0.0.0.0:8000"
workers = int(os.getenv("GUNICORN_WORKERS", 6))
threads = int(os.getenv("GUNICORN_THREADS", 1))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 7200))
loglevel = os.getenv("GUNICORN_LOGLEVEL", "info")
accesslog = "-"
errorlog = "-"