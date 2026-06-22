# Akinator Musical — Nyota

Oráculo que adivina canciones por preguntas sí/no. Bayesian update + Information Gain.

Ver [`music-akinator-plan.md`](./music-akinator-plan.md) (diseño) y [`TODO.md`](./TODO.md) (fases).

## Stack

- Backend: FastAPI + NumPy + Postgres + Redis
- Enrichment: Spotify + Last.fm + Claude
- Frontend: Vite + React + Tailwind + Framer Motion

## Setup local

Requiere: Python 3.11+, Docker, Node 20+.

```bash
# 1. Levantar infra
docker compose up -d

# 2. Backend env
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows bash; en Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # editar con tus claves

# 3. Smoke test infra
python scripts/check_infra.py
```

## Estructura

```
backend/
  core/         # oracle_engine, question_selector, attribute_matrix, session_manager
  enrichment/   # spotify, lastfm, claude
  api/          # oracle, suggest, share, moderation
  scripts/      # import_spotify_charts, enrich_batch, check_infra, play_console
  db/           # models, alembic
  seeds/        # questions.py, attributes.py
frontend/       # Vite + React (Fase 5)
docker-compose.yml
```

## Estado actual

Fase 0 — bootstrap. Ver `TODO.md`.
