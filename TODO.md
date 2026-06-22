# TODO — Akinator Musical (Nyota)

Fases ordenadas por dependencia. No saltar adelante sin cerrar fase previa.
Regla: **cerebro antes que cara**. Engine funciona → después UI bonita.

---

## Fase 0 — Bootstrap del Proyecto ✅

Setup base, sin lógica todavía.

- [x] `git init` + `.gitignore` (Python, Node, .env, __pycache__, node_modules, *.npy, .claude/)
- [x] Estructura de directorios (`backend/{core,enrichment,api,scripts,db,seeds}`, `frontend/`)
- [x] `backend/requirements.txt` con dependencias (Python 3.12)
- [x] `backend/.env.example` (Spotify, Last.fm, Anthropic, DATABASE_URL, REDIS_URL, JWT)
- [x] `docker-compose.yml` (postgres + redis) — reservado para Coolify, no usado en dev
- [x] `README.md` con setup local
- [x] Virtualenv (Python 3.12.10) + instalar deps
- [x] **Dev sin docker:** SQLite (`aiosqlite`) + `fakeredis` in-memory
- [x] `backend/config.py` (pydantic-settings) — switch dev/prod por env vars
- [x] `backend/main.py` con `/health`
- [x] `scripts/check_infra.py` — smoke test DB + cache (dev y prod)
- [x] Push inicial a `origin/main` (https://github.com/CatLanguaga/Oracle-music)

**Done:** `uvicorn backend.main:app` levanta y `GET /health` responde 200.
Para prod (Coolify) basta cambiar `DATABASE_URL`/`REDIS_URL` en env.

---

## Fase 1 — Schema + Modelos de Datos ✅

Tablas vacías. Sin datos aún.

- [x] Schema SQL: `tracks`, `attributes`, `track_attributes`, `questions`, `game_sessions` (audit), `suggested_tracks`, `attribute_votes`
- [x] SQLAlchemy models en `backend/db/models.py` (async, declarative 2.0)
- [x] Alembic configurado (async, `render_as_batch` para SQLite), migración inicial aplicada
- [x] Seed de `attributes` (57 claves canónicas en `seeds/attributes.py`)
- [x] Seed de `questions` (56 preguntas en `seeds/questions.py`)
- [x] `scripts/seed_db.py` idempotente

**Done:** `alembic upgrade head` ok + `attributes=57 questions=56`.

---

## Fase 2 — Seed del Catálogo de Canciones

Sin esto no hay juego. **Bloqueante para Fase 4.**

- [ ] `enrichment/spotify_enricher.py`: cliente Spotipy + import por playlist/chart
- [ ] `enrichment/lastfm_enricher.py`: cliente HTTP Last.fm + map tags → atributos
- [ ] `enrichment/claude_enricher.py`: prompt + parse JSON de atributos semánticos
- [ ] `scripts/import_spotify_charts.py`: importa top tracks por género
- [ ] `scripts/enrich_batch.py`: corre los 3 enrichers en orden y persiste vectores
- [ ] Caché de respuestas de API en disco (evitar pagar 2 veces durante dev)
- [ ] **Meta:** 2000 tracks con vectores completos

**Done cuando:** `SELECT COUNT(*) FROM tracks WHERE attribute_count > 20` ≥ 2000.

---

## Fase 3 — Oracle Engine (Consola)

Algoritmo aislado. CLI loop, sin HTTP.

- [ ] `core/attribute_matrix.py`: carga tracks → `numpy.ndarray` (N_tracks × N_attrs)
- [ ] `core/oracle_engine.py`: init, `update_probabilities` (vectorizado), `get_top_candidate`, `should_guess`
- [ ] `core/question_selector.py`: Information Gain / distance-from-0.5
- [ ] Podado: drop candidatos con prob < 0.001
- [ ] Reglas de parada: prob > 0.85 / candidatos < 5 / preguntas > 25
- [ ] `scripts/play_console.py`: REPL para jugar manual
- [ ] Tests: convergencia en ≤20 preguntas para 10 canciones famosas conocidas

**Done cuando:** Bohemian Rhapsody, Despacito, Smells Like Teen Spirit, etc. son adivinadas en consola en ≤20 preguntas.

---

## Fase 4 — API REST

Engine detrás de HTTP. Sin frontend aún.

- [ ] `core/session_manager.py`: serialize/deserialize vector probs ↔ Redis (TTL 30min)
- [ ] JWT session token (python-jose), firmado, contiene `session_id`
- [ ] `api/oracle.py`: `POST /oracle/session`, `POST /oracle/answer`, `POST /oracle/give-up`, `POST /oracle/confirm`
- [ ] `api/suggest.py`: `POST /oracle/suggest`
- [ ] Logging por sesión (qué preguntas, qué respuestas, convergencia, resultado)
- [ ] Tests curl/httpie de flujo completo

**Done cuando:** flujo completo de partida vía `curl` termina en guess correcto.

---

## Fase 5 — Frontend Mínimo

Funcional, feo. Solo botones.

- [ ] Vite + React + TS + Tailwind
- [ ] `hooks/useOracleSession.ts`: maneja JWT + fetch al backend
- [ ] `QuestionCard.tsx`: pregunta + 5 botones (Sí / Probablemente / No sé / Probablemente no / No)
- [ ] `GuessReveal.tsx`: muestra track guess con portada Spotify + confirmar/rechazar
- [ ] `ResultScreen.tsx`: correcto / incorrecto
- [ ] `SuggestionForm.tsx`: sugerir track cuando oráculo falla

**Done cuando:** partida completa jugable en browser.

---

## Fase 6 — Personaje Nyota

Capa visual. El producto se vuelve memorable acá.

- [ ] Diseño Nyota (Lottie o SVG con estados: thinking/yes/no/guessing/correct/wrong/surrender)
- [ ] `OracleCharacter.tsx`: state machine de animaciones
- [ ] Frases narrativas del plan (`ORACLE_RESPONSES`)
- [ ] Framer Motion en transiciones de pregunta
- [ ] Sound design opcional (cristal, notas musicales)

**Done cuando:** Nyota reacciona distinto a cada estado y se siente vivo.

---

## Fase 7 — Sharing

- [ ] `api/share.py`: genera PNG con Pillow (template del plan)
- [ ] Botones share: Twitter/X, WhatsApp, copiar link
- [ ] OG tags para preview en redes
- [ ] URL única por partida (`/share/{session_id}`)

**Done cuando:** comparto en WhatsApp y se ve el preview con la imagen.

---

## Fase 8 — Sugerencias + Moderación

- [ ] Tabla `suggested_tracks` con estado pendiente/aprobado/rechazado
- [ ] Job background: Claude enriquece atributos de sugerencia → aprobación automática si supera umbral
- [ ] `api/moderation.py`: endpoints admin (list pending / approve / reject)
- [ ] Panel admin mínimo (HTML server-side está bien)
- [ ] Notificación al usuario cuando su sugerencia entra al pool (email opcional, o solo "tu track ahora vive en el grimorio")

**Done cuando:** sugerencia → enriquece → aparece en pool activo sin intervención manual.

---

## Fase 9 — Crowdsourcing de Atributos

- [ ] Al final de partida: mostrar 3-5 atributos del track adivinado para validar
- [ ] Tabla `attribute_votes` (track_id, attribute_key, user_session, value)
- [ ] Cron que consolida votos → actualiza `track_attributes` con promedio ponderado
- [ ] Gamificación básica: contador de validaciones por sesión

**Done cuando:** votos de usuarios mueven valores de atributos en DB.

---

## Fase 10 — Refinamiento + Observabilidad

Continuo. No tiene "done".

- [ ] Dashboard de partidas: rate de aciertos, preguntas promedio, drop-off
- [ ] Detectar preguntas con yes_prob ≈ 0 o ≈ 1 en histórico → retirar
- [ ] Detectar preguntas top-discriminadoras → priorizar al inicio
- [ ] Detectar tracks que nunca son adivinados → flag para revisión de atributos
- [ ] Performance: profiling con 50k tracks
- [ ] Logs estructurados (JSON) + Sentry para errores

---

## Fase 11 — Deploy

- [ ] Dockerfile backend + frontend
- [ ] Railway: postgres + redis + backend + frontend
- [ ] Secrets en Railway env vars
- [ ] CI mínimo: lint + tests en push
- [ ] Dominio + HTTPS
- [ ] Rate limiting básico (FastAPI middleware)

**Done cuando:** URL pública funcionando + dominio custom.

---

## Gamificación (post-launch)

- [ ] Racha diaria
- [ ] Logros: "Mente de cristal" (≤8 preguntas), "El esquivo" (5 fallas seguidas), "Contribuidor" (10 sugerencias aprobadas)
- [ ] Leaderboard semanal de "escapes del oráculo"

---

## Riesgos a vigilar (del plan original)

- **Spotify Audio Features deprecado** → Last.fm + Claude como fuentes primarias desde Fase 2
- **Cold start** → lanzar con géneros limitados si catálogo < 2000
- **Atributos subjetivos** → confiar en 0.0–1.0 + crowdsourcing
- **Trampa visual** → no tocar Fase 6 hasta Fase 3 verde
