# Akinator Musical — Nyota

Oráculo que adivina canciones por preguntas sí/no. Bayesian update + Information Gain.

Ver [`music-akinator-plan.md`](./music-akinator-plan.md) (diseño) y [`TODO.md`](./TODO.md) (fases).

## Stack

- Backend: FastAPI + NumPy + Postgres + Redis
- Enrichment: Spotify + Last.fm + Claude
- Frontend: Vite + React + Tailwind + Framer Motion

## Setup local

Requiere: Python 3.11+, Docker, Node 20+.

**Dev local** usa SQLite + fakeredis. Docker queda reservado para Coolify.

```bash
# 1. Venv + deps
cd backend
py -3.12 -m venv .venv
source .venv/Scripts/activate    # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # editar con tus API keys

# 2. Smoke test infra (desde raíz del repo)
cd ..
python -m backend.scripts.check_infra

# 3. Migraciones + seed
alembic upgrade head
python -m backend.scripts.seed_db

# 4. Run API
uvicorn backend.main:app --reload
# → http://127.0.0.1:8000/health
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
