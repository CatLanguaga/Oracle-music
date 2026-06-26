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

- [x] `enrichment/spotify_enricher.py`: Spotipy + `fetch_artist_top_tracks` (editorial playlists bloqueadas para Client Credentials)
- [x] `enrichment/lastfm_enricher.py`: httpx + map tags → atributos
- [x] `enrichment/gemini_enricher.py`: prompt + parse JSON + retry/fallback
- [x] `enrichment/deterministic.py`: era/duration/featuring desde metadata Spotify
- [x] `scripts/import_artists.py`: seed de ~150 artistas → top 10 tracks
- [x] `scripts/enrich_batch.py`: deterministic + lastfm + gemini, prioridad por fuente
- [x] Caché en `.cache/enrichment/{spotify,lastfm,gemini}/*.json`
- [~] **Meta:** 2000 tracks con vectores completos
  - Actual: 1228/1960 (62.7%) ready. Rerun partials background corriendo.
  - Cuello: Pollinations devuelve dicts pequeños ~25% bajo concurrencia. Aceptable para prototipo.

**Done cuando:** `SELECT COUNT(*) FROM tracks WHERE attribute_count > 20` ≥ 2000. (Pendiente: +100 artistas si necesario)

---

## Fase 3 — Oracle Engine (Consola) ✅

Algoritmo aislado. CLI loop, sin HTTP.

- [x] `core/attribute_matrix.py`: carga tracks → `numpy.ndarray` (N_tracks × N_attrs), missing=0.5
- [x] `core/oracle_engine.py`: init, `update` Bayesian, `top_candidate`, `top_k`, `should_guess`
- [x] `core/question_selector.py`: distance-from-0.5 (Σ p(t)·M[t,j]−0.5)
- [x] Podado: relativo a uniforme (0.01/N) — fix vs constante absoluta
- [x] Reglas de parada: prob > 0.85 / candidatos ≤ 5 / preguntas ≥ 25
- [x] `scripts/play_console.py`: REPL interactivo
- [x] Test simulado: `scripts/test_oracle_convergence.py` → **10/10 aciertos, avg 16 preguntas** (9/10 en ≤20)
- [x] Optimización convergencia: likelihood beta=2, prune dual (uniforme + top), guess threshold 0.5 + dominancia 0.25

**Done:** 10/10 canciones adivinadas. Avg 16 preguntas, 9/10 ≤20 (Shape of You único en 25).

---

## Fase 4 — API REST ✅

Engine detrás de HTTP. Sin frontend aún.

- [x] `core/session_manager.py`: serialize/deserialize vector probs ↔ Redis (TTL 30min)
- [x] JWT session token (python-jose), firmado, contiene `session_id`
- [x] `api/oracle.py`: `POST /oracle/session`, `POST /oracle/answer`, `POST /oracle/give-up`, `POST /oracle/confirm`
- [x] `api/suggest.py`: `POST /oracle/suggest`
- [x] Logging por sesión (qué preguntas, qué respuestas, convergencia, resultado)
- [x] `scripts/test_api_flow.py` end-to-end vía httpx ASGITransport (3/5 wins en sample random, avg 22q)

**Done:** flujo completo POST /session → /answer×N → /confirm via ASGI, audit row escrito en `game_sessions`.

---

## Fase 5 — Frontend Mínimo 🟡 (beta, falta smoke en browser)

Funcional con diseño beta (Tarot Editorial × Kenya Hara). Vive en `frontend/app/`.

- [x] Vite + React + TS + Tailwind v4 (proxy `/oracle` → `localhost:8000`)
- [x] Design tokens portados desde `frontend/prototype/index.html` (paper/ink/vermilion, Cormorant Garamond + Inter, engraved frame)
- [x] `src/types.ts` + `src/api.ts`: schemas espejo + fetch wrapper con JWT bearer
- [x] `hooks/useOracleSession.ts`: state machine idle/loading/question/guess/result/error
- [x] `components/NyotaGlyph.tsx`: SVG line-art (ojo + luna) con estado thinking
- [x] `components/WelcomeScreen.tsx`: invocación inicial
- [x] `components/QuestionCard.tsx`: 5 botones + keyboard 1–5 + progress
- [x] `components/GuessReveal.tsx`: track card con portada + top-k + confirm/reject
- [x] `components/ResultScreen.tsx`: correcto (stats) vs incorrecto (suggest form)
- [x] `components/SuggestionForm.tsx`: POST /oracle/suggest
- [x] `App.tsx`: orquesta fases del hook
- [ ] Smoke en browser: partida completa con backend levantado

**Done cuando:** partida completa jugable en browser.

---

## Fase 5.1 — Hardening del Oráculo (post-smoke beta) 🔴

Hallazgos jugando la beta. Bloqueante antes de Fase 6.

### A. Preguntas mal formuladas (no son sí/no puras)

Problema: `«¿El artista es un grupo o banda?»` no es binaria — la negación no implica "solista" automáticamente. Confunde al jugador y a la inferencia.

- [ ] Auditar `backend/seeds/questions.py` línea por línea. Toda pregunta debe poder responderse con Sí/No sin ambigüedad
- [ ] Fix concretos:
  - `«¿El artista es un grupo o banda?»` → `«¿El artista es una banda (más de un miembro)?»`
  - Eliminar duplicados antagónicos: si existe `artist_is_band` no hace falta `artist_is_solo` como pregunta (el motor ya infiere lo contrario)
  - Revisar `vocalist_is_female` / `vocalist_is_male` (dúos mixtos = ambiguo) → reemplazar por `«¿Hay voz femenina prominente?»`
- [ ] Lint script: `scripts/lint_questions.py` que detecta patrones prohibidos ("o", "/", "uno de", comparativos) y falla CI
- [ ] Pasada Gemini sobre las 56 preguntas pidiendo reformulación si score de claridad < 0.8 (semilla para Fase 9.5.B)

### B. UI de respuestas: orden + jerarquía

Problema: orden actual mezcla certeza con sentido. Confuso visual.

- [ ] Reordenar botones en `QuestionCard.tsx`:
  ```
  1) Sí                 ← primary, full
  2) No                 ← accent, full
  3) No sé              ← ghost, full
  4) Probablemente no   ← default
  5) Probablemente sí   ← default
  ```
- [ ] Mapear teclas: `1=Sí, 2=No, 3=No sé, 4=Prob no, 5=Prob sí` (Y/N como flechas mentales arriba)
- [ ] Agrupar visualmente: Sí/No en bloque fuerte arriba, dudas abajo separadas por `<hr>` engraved
- [ ] Mobile: stack vertical, Sí/No agarran ancho completo

### C. Repetición entre partidas (falta variedad estilo Akinator real)

Problema: mismo set de top-discriminadoras → mismas 10 primeras preguntas todas las partidas. Aburrido.

- [ ] **Diversificación estocástica** en `core/question_selector.py`:
  - En vez de `argmax(score)`, hacer **softmax(score / τ)** con temperatura `τ` (config). `τ=0` = actual greedy. `τ=0.15` añade variedad sin sacrificar convergencia
  - Validar con `scripts/test_oracle_convergence.py` que avg preguntas no sube > 2
- [ ] **Penalización por sobreuso**: tabla `Question.ask_count` (ya existe Fase 10) — restar `λ · log(1 + ask_count / median_count)` al score. Preguntas vistas mucho bajan en ranking
- [ ] **Apertura por categoría rotatoria**: primera pregunta nunca repite categoría entre partidas consecutivas del mismo `session_id` o IP (cookie). Categorías: genre / era / mood / energy / artist
- [ ] **Akinator-style adaptación dentro de partida**: si jugador responde "No sé" 3+ veces seguidas en categoría X, evitar más preguntas de esa categoría el resto de la partida
- [ ] Métrica nueva en audit: % de overlap de preguntas entre 2 partidas consecutivas. Target < 60%

### D. Filtro / engine: edge cases tipo Bohemian Rhapsody

Problema: tracks con géneros híbridos (rock + ópera + balada) caen en zona muerta del Bayesian update porque ninguna pregunta los discrimina bien.

- [ ] Diagnóstico: log por sesión qué tracks quedan en top-10 final cuando falla. Cron: detectar tracks que **nunca** son adivinados (Fase 10 ya lo lista)
- [ ] Atributos compuestos faltantes — agregar al seed:
  - `is_multi_section` (cambia de género/tempo dentro de la misma canción)
  - `is_operatic_rock`, `is_progressive`
  - `has_choral_vocals`
  - `is_iconic` (top-100 históricos, ayuda como prior)
- [ ] **Prior por popularidad**: `spotify_popularity` ya en DB. Aplicar como prior inicial (canciones más conocidas tienen más prob de ser pensadas). Suaviza el caso "todos piensan en Bohemian Rhapsody pero ningún atributo lo distingue"
- [ ] **Beam search en últimos 5 candidatos**: cuando `candidates ≤ 10`, en vez de seguir seleccionando por entropía media, seleccionar pregunta que **discrimine entre top-5** específicamente (max varianza de M[t,j] sobre top-5, no sobre todo)
- [ ] **Fuzzy track matching** en sugerencias: cuando user sugiere "Bohemian Rhapsody" y existe en DB pero el oráculo no llegó, marcar como `near_miss` para auditar qué preguntas faltaron

**Done cuando:**
- 0 preguntas ambiguas en `questions.py` (lint pasa)
- UI nueva orden + grouping en `QuestionCard`
- Test convergencia: 10 partidas con **<60% overlap** de preguntas y avg ≤ 18
- Bohemian Rhapsody + 5 tracks problemáticos adivinados consistentemente

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
- [ ] Job background: Gemini enriquece atributos de sugerencia → aprobación automática si supera umbral
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

## Fase 9.5 — Evolución adaptativa de preguntas/atributos

Catálogo de preguntas y atributos se afina solo con el uso. Depende de Fase 8 (panel moderación), Fase 9 (votos) y telemetría base de Fase 10 (`ask_count`/`yes_rate`).

### A. Detección de preguntas ambiguas

- [ ] Tabla `question_answers(session_id, question_id, variant_id?, value, created_at)` — log per-answer (necesario para varianza)
- [ ] Columna `Question.status: active|candidate|rephrasing|retired` + `Question.variance`
- [ ] Cron: marca `rephrasing` si `ask_count ≥ 50` AND `0.4 ≤ yes_rate ≤ 0.6` AND `variance > umbral`

### B. Rephrase auto vía Gemini (A/B testing)

- [ ] Tabla `question_variants(id, parent_question_id, text_es, status, ask_count, yes_rate, variance, gemini_score, created_at)`
- [ ] `gemini_enricher.propose_rephrasings(text, attr_key, attr_desc) → list[str]` (3 variantes + score self-eval 0–1) — reusa `_client()`/`_parse_json()`
- [ ] `question_selector`: epsilon-greedy (prob 0.3) sirve variante candidata cuando padre está `rephrasing`
- [ ] Promotor: si variante baja `|0.5 − yes_rate|` por margen `M` y reduce varianza → reemplaza texto base; original → `retired`

### C. Atributos nuevos desde sugerencias

- [ ] Tabla `proposed_attributes(key_raw, category_guess, source, occurrence_count, gemini_confidence, status, merged_into?)`
- [ ] Hook en pipeline de `SuggestedTrack` (Fase 8): tags/atributos no presentes en `attributes` → encolar
- [ ] Cron: si `occurrence_count ≥ 5` AND `gemini_confidence ≥ 0.7` → Gemini genera `description`, `category`, 1–2 preguntas candidatas
- [ ] Detección de sinónimos: Gemini propone `merged_into` (ej. `is_trap` → `is_hiphop_rap`) en vez de crear duplicado

### D. Aprobación híbrida

- [ ] `confidence_score = w1·gemini_score + w2·telemetry_signal` (pesos en `config.py`)
- [ ] Reglas: `≥ 0.85` auto-aplica · `0.5–0.85` cola admin · `< 0.5` descarta + log
- [ ] Tabla `change_audit_log(entity_type, entity_id, action, payload, confidence_score, actor, created_at)` — `actor = system | admin_id`

### E. API + admin

- [ ] `GET /admin/questions/pending` + `POST /admin/questions/{id}/approve|reject`
- [ ] `GET /admin/attributes/proposed` + `POST /admin/attributes/{key}/approve|reject|merge`
- [ ] Dos tabs nuevos en panel HTML server-side de Fase 8

### Archivos

- `backend/db/models.py`, migración Alembic nueva
- `backend/enrichment/gemini_enricher.py` (+ `propose_rephrasings`, `classify_proposed_attribute`)
- `backend/core/question_selector.py` (epsilon-greedy)
- `backend/core/question_evolution.py` (nuevo: `detect_ambiguous`, `trigger_rephrase`, `promote_variants`, `process_proposed_attributes`)
- `backend/api/oracle.py` (log `question_answers` en `/oracle/answer`)
- `backend/api/moderation.py` (endpoints nuevos)
- `backend/scripts/run_question_evolution.py`

**Done cuando:**
- Variante de pregunta sirve sin intervención admin y reemplaza base si gana A/B.
- Track sugerido con tag inédito (`is_phonk`) produce `Attribute` + `Question(candidate)` tras umbral.
- `change_audit_log` contiene filas con `actor=system`.

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

- **Spotify Audio Features deprecado** → Last.fm + Gemini como fuentes primarias desde Fase 2
- **Cold start** → lanzar con géneros limitados si catálogo < 2000
- **Atributos subjetivos** → confiar en 0.0–1.0 + crowdsourcing
- **Trampa visual** → no tocar Fase 6 hasta Fase 3 verde
