#!/bin/bash

# Get number of workers from environment variable or use a default
WORKERS=${WORKERS:-4}
TIMEOUT=${TIMEOUT:-120}

# Start Gunicorn with appropriate settings
exec gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout $TIMEOUT \
    --access-logfile - \
    --error-logfile - \
    --log-level info 