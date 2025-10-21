#!/bin/bash

# Set default port if PORT environment variable is not set
PORT=${PORT:-8000}

# Start uvicorn with the port
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT