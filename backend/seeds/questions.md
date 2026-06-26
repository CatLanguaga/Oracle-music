# Preguntas del Oráculo

Fuente canónica. `backend/scripts/seed_db.py` parsea este archivo a través de `backend/seeds/questions.py`.

**Convenciones:**

- `status`:
  - `active` — en uso, se carga en DB
  - `rephrasing` — texto en evaluación A/B (también se carga)
  - `draft` — borrador, no se carga aún
  - `retired` — no cargar, queda como histórico
- `rewrite` — reformulación propuesta pendiente de aprobación. Para aplicar: mover texto a la columna `text`, vaciar `rewrite`, dejar `status=active`.
- `notes` — diagnóstico o razón del estado actual.
- Tras editar este archivo, correr `python -m backend.scripts.seed_db` (idempotente sobre `(attribute_key, text_es)`).
- Pipes literales `|` dentro de celdas se escriben `\|`.

---

## genre

| key | text | status | rewrite | notes |
|---|---|---|---|---|
| is_rock | ¿Es una canción de rock? | active |  |  |
| is_pop | ¿Es una canción pop? | active |  |  |
| is_electronic | ¿Es una canción electrónica o de música para bailar en discoteca? | active |  | Reescrita 2026-06-26. Quitado EDM/techno (jerga). |
| is_hiphop_rap | ¿Es una canción de hip-hop o rap? | active |  | Reescrita 2026-06-26. Quitado "elementos de" (vago). |
| is_jazz_blues | ¿Es una canción de jazz o blues? | active |  | Reescrita 2026-06-26. Lenguaje simple. TODO Fase 5.1: considerar split is_jazz / is_blues.|
| is_classical | ¿Es música clásica? | active |  |  |
| is_latin | ¿Es música latina (reggaetón, salsa, bachata, cumbia, etc.)? | active |  | Reescrita 2026-06-26. |
| is_metal | ¿Es una canción de metal o heavy metal? | active |  | Reescrita 2026-06-26. Quitado thrash/death (jerga). |
| is_rnb_soul | ¿Es una canción de R&B o soul? | active |  | Reescrita 2026-06-26. Quitado neo-soul (jerga). |
| is_country_folk | ¿Es una canción de country o folk? | active |  | Reescrita 2026-06-26. Quitado "americana" (subgénero técnico). TODO Fase 5.1: split.|
| is_indie_alt | ¿Es una canción indie o de rock alternativo? | active |  | Reescrita 2026-06-26. |
| is_punk | ¿Es punk? | active |  |  |
| is_reggae | ¿Es reggae? | active |  |  |

## era

| key | text | status | rewrite | notes |
|---|---|---|---|---|
| released_before_2000 | ¿Fue lanzada antes del año 2000? | active |  |  |
| released_in_90s | ¿Fue lanzada en los años 90? | active |  |  |
| released_in_80s | ¿Fue lanzada en los años 80? | active |  |  |
| released_in_70s | ¿Fue lanzada en los años 70? | active |  |  |
| released_after_2010 | ¿Fue lanzada después del 2010? | active |  |  |
| released_recent_3y | ¿Es una canción reciente (últimos 3 años)? | active |  |  |

## artist

| key | text | status | rewrite | notes |
|---|---|---|---|---|
| artist_is_band | ¿El artista tiene más de un miembro (banda o grupo)? | active |  | Reescrita 2026-06-26. |
| artist_is_solo | ¿Es un artista solista (sin banda)? | retired |  | Retirada 2026-06-26: redundante con artist_is_band (engine infiere el inverso). Atributo en DB se mantiene.|
| vocalist_is_female | ¿La voz principal es de una mujer? | active |  |  |
| vocalist_is_male | ¿La voz principal es de un hombre? | retired |  | Retirada 2026-06-26: redundante con vocalist_is_female. Reincorporar si tratamos dúos mixtos como caso aparte.|
| artist_anglophone | ¿El artista canta principalmente en inglés? | active |  | Reescrita 2026-06-26. |
| artist_latin | ¿El artista es de un país hispanohablante? | active |  | Reescrita 2026-06-26. |
| artist_from_uk | ¿El artista es del Reino Unido? | active |  |  |
| artist_from_usa | ¿El artista es de Estados Unidos? | active |  |  |
| has_featuring | ¿Tiene un artista invitado (feat.)? | active |  |  |

## energy

| key | text | status | rewrite | notes |
|---|---|---|---|---|
| is_fast_tempo | ¿Es una canción rápida o acelerada? | active |  | Reescrita 2026-06-26. Quitado BPM (jerga técnica).|
| is_ballad | ¿Es una balada o canción lenta? | active |  |  |
| is_danceable | ¿Es buena para bailar? | active |  |  |
| is_chill | ¿Es relajante o tranquila? | active |  |  |
| has_strong_percussion | ¿Se escucha mucho la batería o percusión? | active |  | Reescrita 2026-06-26. Quitado "prominente". |

## mood

| key | text | status | rewrite | notes |
|---|---|---|---|---|
| is_sad_mood | ¿Es una canción triste o melancólica? | active |  |  |
| is_happy_mood | ¿Es una canción alegre o positiva? | active |  |  |
| is_romantic | ¿Es una canción de amor o romántica? | active |  |  |
| is_about_heartbreak | ¿Habla de desamor o ruptura? | active |  |  |
| is_rebellious | ¿Tiene un mensaje rebelde o de protesta? | active |  | Reescrita 2026-06-26. |
| is_party | ¿Es una canción festiva, de fiesta? | active |  |  |
| is_nostalgic | ¿Es una canción asociada a una época pasada o que evoca nostalgia? | active |  | Reescrita 2026-06-26. |

## instruments

| key | text | status | rewrite | notes |
|---|---|---|---|---|
| has_electric_guitar | ¿Se escucha mucho la guitarra eléctrica? | active |  | Reescrita 2026-06-26. Quitado "prominente". |
| has_piano | ¿El piano es el instrumento principal? | active |  | Reescrita 2026-06-26. |
| is_synth_driven | ¿Suenan sintetizadores en gran parte de la canción? | active |  | Reescrita 2026-06-26. Lenguaje simple.|
| has_strings | ¿Se escuchan violines u otros instrumentos de cuerda? | active |  | Reescrita 2026-06-26. Quitado "sección de cuerdas". |
| is_acoustic | ¿Es principalmente acústica? | active |  |  |
| is_instrumental | ¿Es instrumental (sin letra)? | active |  |  |

## fame

| key | text | status | rewrite | notes |
|---|---|---|---|---|
| is_very_famous | ¿Es una canción muy famosa, conocida por casi todos? | active |  |  |
| is_in_movie_or_series | ¿Aparece en alguna película o serie conocida? | active |  |  |
| was_number_one | ¿Fue número 1 en algún país? | active |  |  |
| has_famous_intro | ¿Tiene un intro icónico que reconocerías al instante? | active |  |  |
| is_cult_classic | ¿Es un clásico de culto? | active |  |  |

## lyrics

| key | text | status | rewrite | notes |
|---|---|---|---|---|
| lyrics_in_spanish | ¿Tiene letra en español? | active |  |  |
| lyrics_in_english | ¿Tiene letra en inglés? | active |  |  |
| lyrics_mixed_lang | ¿Mezcla dos o más idiomas? | active |  |  |

## duration

| key | text | status | rewrite | notes |
|---|---|---|---|---|
| is_longer_than_5min | ¿Dura más de 5 minutos? | active |  |  |
| is_shorter_than_3min | ¿Dura menos de 3 minutos? | active |  |  |
