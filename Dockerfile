FROM python:3.11-slim

WORKDIR /app

# Cache deps separately from app code so code-only changes skip the pip install layer
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip && pip install -r backend/requirements.txt

COPY backend /app/backend

# Railway injects $PORT at runtime
CMD gunicorn --chdir backend "app:create_app()" --bind 0.0.0.0:$PORT --timeout 300 --workers 2
