# --- Stage 1: build the React app -------------------------------------------
FROM node:20-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/ ./
# build:prod loads frontend/.env.production (PUBLIC_URL, REACT_APP_*), which
# are baked into the bundle. Plain `npm run build` is intentionally disabled.
RUN npm run build:prod

# --- Stage 2: Django app ------------------------------------------------------
FROM python:3.14-trixie

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements/ requirements/
RUN python -m pip install -r requirements/production.txt

COPY . .

# Django reads the React build from frontend_build/ (REACT_APP_DIR in
# config/settings/base.py): index.html as a template, static/ as a static dir.
COPY --from=frontend /app/frontend/build ./frontend_build

# Bake in the non-secret FSDH config as the .env file django-environ reads at
# startup. Real secrets are injected at container runtime via docker-compose's
# `environment:` block, which takes precedence over anything in this file.
COPY .env.fsdh .env

# The baked .env selects production settings, which require a secret key even
# though collectstatic never uses it. This throwaway value exists only for this
# build step and is not persisted in the image environment.
RUN DJANGO_SECRET_KEY=build-time-only-not-a-secret python manage.py collectstatic --noinput

EXPOSE 8080
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3"]
