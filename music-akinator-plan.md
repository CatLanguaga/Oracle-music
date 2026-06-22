# Plan de Implementación: Akinator Musical (El Oráculo)

## Visión del Producto

Una figura mística (vudú, oráculo, chamán musical) que hace preguntas de sí/no
para adivinar la canción que el usuario tiene en mente. Cada pregunta reduce
el pool de candidatos usando el mismo algoritmo de Akinator: máxima ganancia
de información por pregunta. Si el oráculo no conoce la canción, el usuario
puede sugerirla y así alimenta la base de datos colaborativamente.

---

## El Algoritmo de Akinator (Entender Esto Primero)

Akinator no es magia. Es un árbol de decisión probabilístico con selección
de pregunta por ganancia de información (Information Gain / Entropía de Shannon).

### Cómo funciona paso a paso:

```
Estado inicial:
  - Pool de candidatos: todas las canciones en la DB
  - Probabilidad de cada canción: 1 / N (uniforme)

Por cada turno:
  1. Calcular cuál pregunta divide el pool actual más cerca de 50/50
     (esa pregunta tiene la máxima información ganada)
  2. Hacer esa pregunta al usuario
  3. El usuario responde: Sí / No / Probablemente / Probablemente no / No sé
  4. Actualizar probabilidades con Bayes:
     - Sí:            P(canción | respuesta) ∝ P(canción) × P(Sí | canción)
     - No:            P(canción | respuesta) ∝ P(canción) × (1 - P(Sí | canción))
     - Probablemente: peso parcial (0.7)
     - No sé:         no filtra nada, peso neutro (0.5)
  5. Si alguna canción supera 85% de probabilidad → hacer la suposición
  6. Si no → repetir desde paso 1 con el pool reducido

Convergencia típica: 15–25 preguntas para un pool de 10,000 canciones
```

### La Clave: Cómo se Representa una Canción

Cada canción es un **vector de atributos**. Cada atributo es la probabilidad
de que la respuesta a una pregunta sea "Sí" para esa canción:

```json
{
  "track_id": "spotify:track:abc123",
  "title": "Bohemian Rhapsody",
  "artist": "Queen",
  "attributes": {
    "is_rock":              1.0,
    "has_male_vocals":      1.0,
    "is_a_band":            1.0,
    "released_before_1990": 1.0,
    "released_before_2000": 1.0,
    "is_fast_tempo":        0.5,
    "is_sad_mood":          0.4,
    "is_romantic":          0.2,
    "has_guitar":           1.0,
    "has_piano":            1.0,
    "is_in_english":        1.0,
    "is_famous":            1.0,
    "is_electronic":        0.0,
    "has_rap":              0.0,
    "is_longer_than_5min":  1.0,
    "won_grammy":           0.0,
    "is_a_ballad":          0.6,
    "from_uk":              1.0
  }
}
```

Los valores no son binarios: son probabilidades (0.0–1.0) para manejar
canciones ambiguas ("¿es rápida? más o menos...").

---

## Stack Técnico

| Capa | Tecnología | Justificación |
|---|---|---|
| Backend | **FastAPI** | Async, familiar |
| Algoritmo | **Python puro + NumPy** | El algoritmo es matemática, no necesita ML framework |
| Base de datos | **PostgreSQL** | Canciones + atributos + sesiones de juego |
| Atributos automáticos | **Spotify Audio Features + Last.fm tags** | Alimentan el vector automáticamente |
| Atributos por IA | **Claude API** | Para atributos semánticos que Spotify no da (mood, temática, letra) |
| Cache del algoritmo | **Redis** | Pool de candidatos por sesión, preguntas pre-calculadas |
| Generación de imagen share | **Pillow** | Imagen del resultado al estilo Akinator |
| Frontend | **React + TailwindCSS + Framer Motion** | Animaciones para el personaje místico |
| Personaje | **Lottie o SVG animado** | La figura de vudú reacciona a las respuestas |
| Deployment | **Railway** | |

---

## Arquitectura

```
[Frontend React]
  → usuario dice "Tengo una canción en mente"
  → GET /oracle/session → session_id + primera pregunta
  → usuario responde (Sí / No / Probablemente / No sé)
  → POST /oracle/answer → siguiente pregunta o suposición
  → si el oráculo adivina: pantalla de resultado compartible
  → si falla o el usuario dice "No es correcto":
      → formulario de sugerencia: "¿Cuál era la canción?"
      → POST /oracle/suggest → guarda en cola de moderación

[Backend - Motor del Oráculo]
  OracleSession:
    - pool actual: lista de (track_id, probabilidad)
    - historial de respuestas
    - preguntas ya hechas (no repetir)
  
  Por cada respuesta:
    1. Actualizar probabilidades (Bayesian update)
    2. Seleccionar siguiente pregunta (máximo Information Gain)
    3. Si max_prob > 0.85 → hacer suposición
    4. Si quedan <5 candidatos → hacer suposición del más probable
    5. Si >25 preguntas sin convergencia → rendirse con gracia

[Base de Datos de Canciones]
  - Alimentada inicialmente con top tracks de Spotify por género
  - Atributos automáticos: Spotify Audio Features + Last.fm tags
  - Atributos semánticos: generados por Claude (mood, temática de letra)
  - Atributos crowdsourced: cuando usuarios sugieren o validan atributos

[Cola de Sugerencias]
  - Canciones nuevas sugeridas por usuarios
  - Panel de moderación para aprobar + asignar atributos automáticamente
  - Claude enriquece automáticamente los atributos de la canción sugerida
```

---

## Los Atributos: El Corazón del Sistema

### Categorías de Preguntas

```python
QUESTION_CATEGORIES = {
    # Género musical
    "genre": [
        "¿Es una canción de rock?",
        "¿Es electrónica o dance?",
        "¿Es pop?",
        "¿Tiene elementos de hip-hop o rap?",
        "¿Es jazz o blues?",
        "¿Es música clásica o instrumental?",
        "¿Es reggaetón o música latina?",
        "¿Es metal o heavy metal?",
        "¿Es R&B o soul?",
        "¿Es country o folk?",
    ],
    
    # Época
    "era": [
        "¿Fue lanzada antes del año 2000?",
        "¿Fue lanzada en los años 90?",
        "¿Fue lanzada en los años 80?",
        "¿Fue lanzada después del 2010?",
        "¿Es una canción reciente (últimos 3 años)?",
    ],
    
    # Artista
    "artist": [
        "¿El artista es un grupo o banda?",
        "¿El vocalista principal es mujer?",
        "¿El artista es de habla inglesa?",
        "¿El artista es latinoamericano?",
        "¿El artista es solo (no tiene banda)?",
        "¿Hay más de un artista en la canción (feat.)?",
    ],
    
    # Energía y tempo
    "energy": [
        "¿Es una canción rápida y energética?",
        "¿Es una balada o canción lenta?",
        "¿Es buena para bailar?",
        "¿Es relajante o tranquila?",
        "¿Tiene mucha percusión o batería prominente?",
    ],
    
    # Mood y temática
    "mood": [
        "¿Es una canción triste o melancólica?",
        "¿Es una canción de amor o romántica?",
        "¿Es una canción alegre o positiva?",
        "¿Habla de desamor o ruptura?",
        "¿Tiene un tono agresivo o rebelde?",
        "¿Es una canción bailable y festiva?",
    ],
    
    # Instrumentación
    "instruments": [
        "¿Tiene guitarra eléctrica prominente?",
        "¿Tiene piano como instrumento principal?",
        "¿Es principalmente electrónica (sintetizadores)?",
        "¿Tiene sección de cuerdas (violines, etc.)?",
        "¿Es principalmente acústica?",
    ],
    
    # Fama y contexto
    "fame": [
        "¿Es una canción muy famosa y conocida por casi todos?",
        "¿Aparece en alguna película o serie conocida?",
        "¿Fue número 1 en algún país?",
        "¿Tiene más de 500 millones de streams en Spotify?",
    ],
    
    # Letra
    "lyrics": [
        "¿Tiene letra en español?",
        "¿Tiene letra en inglés?",
        "¿Es instrumental (sin letra)?",
        "¿Mezcla dos idiomas?",
    ],
    
    # Duración
    "duration": [
        "¿Dura más de 5 minutos?",
        "¿Dura menos de 3 minutos?",
    ]
}
```

### Cómo se Asignan los Atributos Automáticamente

**Fuente 1 — Spotify Audio Features (automático):**
```python
audio_features = spotify.audio_features(track_id)
# Mapeamos los valores numéricos a atributos semánticos:
attributes["is_fast_tempo"]       = 1.0 if features["tempo"] > 120 else 0.0
attributes["is_danceable"]        = features["danceability"]      # 0.0-1.0
attributes["is_energetic"]        = features["energy"]            # 0.0-1.0
attributes["is_acoustic"]         = features["acousticness"]      # 0.0-1.0
attributes["is_instrumental"]     = features["instrumentalness"]  # 0.0-1.0
attributes["is_happy_mood"]       = features["valence"]           # 0.0-1.0
attributes["is_loud"]             = 1.0 if features["loudness"] > -5 else 0.0
```

**Fuente 2 — Last.fm Tags (automático):**
```python
# Last.fm tiene tags crowdsourced por track: "rock", "90s", "sad", "british"
tags = lastfm.get_track_tags(artist, title)
# Mapear tags → atributos:
"rock" in tags         → attributes["is_rock"] = 1.0
"90s" in tags          → attributes["released_in_90s"] = 1.0
"female vocalist" in   → attributes["has_female_vocals"] = 1.0
```

**Fuente 3 — Claude (atributos semánticos difíciles):**
```
Prompt: "Para la canción '{title}' de '{artist}', responde en JSON
con probabilidad 0.0-1.0 para cada atributo:
- is_about_love, is_about_heartbreak, is_about_party,
- is_rebellious_tone, is_nostalgic, has_famous_intro,
- is_from_movie_or_series, is_cult_classic"
```

**Fuente 4 — Crowdsourcing:**
Cuando un usuario juega, al final puede validar o corregir atributos:
"¿Estás de acuerdo con esta descripción de la canción?" Los votos acumulados
ajustan los valores de los atributos.

---

## El Algoritmo en Código

```python
import numpy as np
from typing import List, Dict

class OracleEngine:
    def __init__(self, session_id: str):
        # Cargar todas las canciones con sus vectores de atributos
        self.candidates: Dict[str, float] = {}   # track_id → probabilidad
        self.asked_questions: set = set()
        
    def initialize(self, all_tracks: List[dict]):
        n = len(all_tracks)
        for track in all_tracks:
            self.candidates[track["id"]] = 1.0 / n   # uniforme inicial
    
    def select_next_question(self, questions: List[dict]) -> dict:
        """
        Selecciona la pregunta con máxima ganancia de información.
        La mejor pregunta es la que divide el pool actual más cerca de 50/50.
        """
        best_question = None
        best_score = float('inf')  # queremos el más cercano a 0.5
        
        for question in questions:
            if question["id"] in self.asked_questions:
                continue
            
            attr = question["attribute_key"]
            
            # Suma ponderada: ¿qué fracción del pool diría "Sí"?
            total_prob = sum(self.candidates.values())
            yes_prob = sum(
                prob * self._get_attr(track_id, attr)
                for track_id, prob in self.candidates.items()
            ) / total_prob
            
            # La pregunta perfecta tiene yes_prob = 0.5
            distance_from_ideal = abs(yes_prob - 0.5)
            
            if distance_from_ideal < best_score:
                best_score = distance_from_ideal
                best_question = question
        
        return best_question
    
    def update_probabilities(self, question: dict, answer: str):
        """Actualización bayesiana según la respuesta del usuario."""
        attr = question["attribute_key"]
        
        # Pesos por tipo de respuesta
        WEIGHTS = {
            "yes":           lambda p: p,           # P(canción) × P(Sí|canción)
            "probably_yes":  lambda p: p * 0.7 + (1 - p) * 0.3,
            "dont_know":     lambda p: 0.5,         # No da información
            "probably_no":   lambda p: (1 - p) * 0.7 + p * 0.3,
            "no":            lambda p: 1 - p,        # P(canción) × (1 - P(Sí|canción))
        }
        
        weight_fn = WEIGHTS[answer]
        
        new_probs = {}
        for track_id, current_prob in self.candidates.items():
            attr_prob = self._get_attr(track_id, attr)  # P(Sí|canción)
            new_probs[track_id] = current_prob * weight_fn(attr_prob)
        
        # Renormalizar
        total = sum(new_probs.values())
        self.candidates = {k: v / total for k, v in new_probs.items()}
        self.asked_questions.add(question["id"])
    
    def get_top_candidate(self) -> tuple:
        """Retorna (track_id, probabilidad) del candidato más probable."""
        return max(self.candidates.items(), key=lambda x: x[1])
    
    def should_guess(self) -> bool:
        top_id, top_prob = self.get_top_candidate()
        return top_prob > 0.85
```

---

## El Personaje: El Oráculo

### Identidad Visual

- **Nombre:** Nyota (o "El Oráculo de las Melodías")
- **Estética:** figura vudú / chamán / oráculo — túnica oscura, ojos brillantes,
  cristales o notas musicales flotando alrededor
- **Reacciones animadas según el estado:**
  - Preguntando → postura pensativa, cristal girando
  - Usuario responde "Sí" → reacción de "ajá", se inclina hacia adelante
  - Usuario responde "No" → niega, cristal cambia de color
  - A punto de adivinar → se ilumina, energía creciente, suspense
  - Adivina bien → celebración, notas musicales explosivas
  - Falla → confundido, avergonzado, "los espíritus me han fallado hoy"
  - No conoce la canción → reverencia, "enséñame, mortal"

### Frases del Oráculo (Respuestas Narrativas)

```python
ORACLE_RESPONSES = {
    "thinking":    ["Los espíritus consultan...", "Siento la vibración musical...", 
                    "Las notas me hablan..."],
    "guessing":    ["¡Los espíritus lo saben!", "La melodía se revela ante mí..."],
    "correct":     ["¡LO SABÍA! Mis poderes son infalibles.",
                    "Los espíritus nunca mienten. 😏"],
    "wrong":       ["Imposible... los espíritus me han traicionado.",
                    "Esta canción escapa a mis visiones... por ahora."],
    "surrender":   ["Me rindo ante tu elección, mortal. ¿Qué canción era?",
                    "Los espíritus guardan silencio ante esta melodía."],
    "no_db":       ["Esta canción no existe en mi grimorio. Enséñamela."],
}
```

---

## Fases de Implementación

### Fase 0 — Construir la Base de Datos (Paralela a todo)

- [ ] Script para importar top 500 tracks por género de Spotify (rock, pop, reggaetón,
  jazz, electrónica, hip-hop, metal, latin, R&B, clásica)
- [ ] Asignar atributos automáticos: Spotify Audio Features + géneros del artista
- [ ] Enrichment con Last.fm tags por track
- [ ] Claude genera atributos semánticos para los primeros 1,000 tracks
- [ ] **Meta inicial: 5,000 canciones con vectores de atributos completos**

### Fase 1 — Motor del Algoritmo (2 semanas)

- [ ] Modelo de datos: canciones + atributos + preguntas
- [ ] `OracleEngine`: inicialización, selección de pregunta, actualización bayesiana
- [ ] Endpoint `POST /oracle/session` → inicia sesión, retorna primera pregunta
- [ ] Endpoint `POST /oracle/answer` → procesa respuesta, retorna siguiente pregunta o suposición
- [ ] Endpoint `GET /oracle/give-up` → el oráculo se rinde, pide la canción al usuario
- [ ] Tests del algoritmo: verificar convergencia en <20 preguntas para canciones conocidas

### Fase 2 — Frontend + Personaje (2 semanas)

- [ ] Diseño del personaje Nyota (Lottie animation o SVG con estados)
- [ ] UI de pregunta-respuesta: 5 botones (Sí / Probablemente / No sé / Probablemente no / No)
- [ ] Animaciones de reacción del personaje por respuesta
- [ ] Pantalla de suposición: "¿Es... [canción]?" con portada de Spotify
- [ ] Pantalla de resultado: correcto / incorrecto con animación correspondiente
- [ ] Formulario de sugerencia cuando el oráculo falla o no conoce la canción

### Fase 3 — Sharing y Sugerencias (1 semana)

- [ ] Imagen compartible: "Nyota me adivinó el pensamiento en 12 preguntas" con historial de respuestas
- [ ] Botones de share: Twitter/X, WhatsApp, copiar
- [ ] Cola de sugerencias: canción + artista + atributos básicos del usuario
- [ ] Panel de moderación: revisar sugerencias, enriquecer con Claude, aprobar
- [ ] Notificación al usuario cuando su sugerencia fue añadida ("¡Nyota ya conoce tu canción!")

### Fase 4 — Crowdsourcing de Atributos (1–2 semanas)

- [ ] Al final de cada partida, mostrar 3–5 atributos de la canción que el oráculo
  pensó y pedir al usuario que los valide o corrija
- [ ] Sistema de votación: los atributos con más votos de la comunidad se consolidan
- [ ] Gamificación: puntos por validar atributos, "Contribuidor del Oráculo"
- [ ] Leaderboard de contribuidores más activos

### Fase 5 — Refinamiento del Algoritmo (Continuo)

- [ ] Logs de cada partida: qué preguntas se hicieron, cuándo convergió, si fue correcta
- [ ] Detectar preguntas inútiles (que nunca discriminan bien) y retirarlas
- [ ] Detectar preguntas muy efectivas y priorizarlas al inicio
- [ ] Añadir preguntas nuevas basadas en los atributos donde el algoritmo falla más

---

## Desafíos Técnicos

### 1. El Cold Start: Sin Datos No Hay Juego

**Problema:** el algoritmo es tan bueno como su base de datos. Con 100 canciones
funciona bien. Con 10,000 funciona espectacularmente. Construir esa base toma tiempo.  
**Solución:**
- Lanzar con géneros limitados: "Solo funciona con Rock, Pop y Reggaetón por ahora"
- Usar Spotify Charts (top 50 semanal por país) para importar las canciones más conocidas primero
- Priorizar canciones famosas: el 80% de los usuarios pensará en canciones conocidas
- Crecer el catálogo gradualmente con las sugerencias de usuarios

### 2. Atributos Ambiguos o Subjetivos

**Problema:** "¿Es una canción triste?" depende del oyente. Para unos Bohemian Rhapsody
es épica, para otros es trágica. Los atributos no son binarios objetivos.  
**Solución:** Esto es exactamente por qué los atributos son probabilidades (0.0–1.0),
no binarios. Un valor de 0.5 significa "ambiguo". El sistema maneja incertidumbre
nativamente. Adicionalmente, el crowdsourcing promedia los votos de muchos usuarios,
que da una distribución real de cómo la gente percibe la canción.

### 3. Canciones con el Mismo Nombre de Artistas Distintos

**Problema:** "Shape of You" de Ed Sheeran y una cover de Shape of You de un artista
desconocido se llaman igual. El algoritmo puede confundirse.  
**Solución:** el identificador interno es `spotify_track_id`, no el nombre.
En la pantalla de suposición se muestra artista + álbum + portada para ser inequívoco.

### 4. Performance: El Algoritmo con 50,000 Canciones

**Problema:** calcular la ganancia de información para 150 preguntas × 50,000 canciones
por cada turno es O(preguntas × canciones). Puede ser lento.  
**Solución:**
- Pre-calcular matrices de atributos como arrays NumPy sparse (vectorizado)
- La actualización bayesiana se vuelve una multiplicación de vectores: O(N)
- Cachear en Redis el estado de la sesión (vector de probabilidades actual)
- Podado agresivo: eliminar candidatos con probabilidad <0.001 del pool activo

```python
# Versión vectorizada (mucho más rápida):
import numpy as np

# attr_matrix[i][j] = P(atributo j = Sí | canción i)
attr_matrix = np.load("attr_matrix.npy")  # Shape: (N_songs, N_attrs)
probabilities = np.ones(N_songs) / N_songs

# Actualización bayesiana en una línea:
def update_yes(probabilities, attr_idx, attr_matrix):
    weights = attr_matrix[:, attr_idx]        # P(Sí|canción) para cada canción
    updated = probabilities * weights
    return updated / updated.sum()            # renormalizar
```

### 5. El Usuario Piensa en una Canción Rara o Muy Nueva

**Problema:** "¿Es una canción muy famosa?" — no. El algoritmo tiene más canciones
famosas y le cuesta convergir hacia canciones nicho.  
**Solución:** cuando el usuario responde "No" a múltiples preguntas de fama,
el algoritmo ajusta dinámicamente a priorizar canciones de baja popularidad en Spotify.
La popularidad de Spotify (`track.popularity`, 0–100) es otro atributo más del vector.

### 6. Sesiones de Juego en el Servidor

**Problema:** cada sesión de juego mantiene estado (probabilidades actuales, preguntas hechas).
Esto no puede vivir en el cliente o se puede manipular.  
**Solución:** el estado de la sesión (vector de probabilidades + historial) vive en Redis
con TTL de 30 minutos. La sesión tiene un `session_token` firmado con JWT para validar
que el cliente no modifica el estado.

---

## Imagen Compartible

```
┌──────────────────────────────────────┐
│  🔮 NYOTA - EL ORÁCULO MUSICAL       │
│                                      │
│  Nyota adivinó mi canción en         │
│  ✨ 14 preguntas ✨                   │
│                                      │
│  🎵 [Nombre de la canción]           │
│  👤 [Artista]                        │
│                                      │
│  S S N N S ? S S N S S N S S        │ ← S=Sí N=No ?=No sé
│                                      │
│  ¿Puedes escapar del Oráculo?        │
│  [url del juego]                     │
└──────────────────────────────────────┘
```

---

## Sistema de Sugerencias

Flujo cuando el oráculo falla o no reconoce la canción:

```
1. Usuario dice: "No, esa no es" o "Mi canción no está en tu base"

2. Nyota reacciona: "Los espíritus guardan silencio ante esta melodía.
   ¿Me enseñas qué canción era, para que mi grimorio crezca?"

3. Formulario de sugerencia:
   - Nombre de la canción (campo de texto + búsqueda en Spotify)
   - Artista
   - Opcional: responder 5 preguntas básicas sobre la canción
     ("¿Es rápida? ¿Tiene letra en inglés? ¿Es de los 90s?")

4. Backend:
   - Guarda en tabla `suggested_tracks` con estado "pendiente"
   - Lanza job en background: Claude enriquece automáticamente los atributos
   - Si pasa el umbral mínimo de atributos → aprobación automática
   - Si no → va a moderación manual

5. Cuando se aprueba:
   - Notificación al usuario: "¡Tu canción ya vive en el grimorio de Nyota!"
   - La canción entra al pool activo del algoritmo
```

---

## Gamificación y Retención

- **Racha diaria:** juega un round cada día, mantén tu racha
- **Logros del Oráculo:**
  - "Tú que todo lo ocultas": el oráculo tardó 20+ preguntas en adivinar
  - "Mente de cristal": adivinado en ≤8 preguntas
  - "Contribuidor del grimorio": sugirió 10+ canciones aprobadas
  - "El esquivo": 5 veces consecutivas que el oráculo falló
- **Leaderboard semanal:** quién escapó más veces al oráculo

---

## Estructura de Directorios

```
music-akinator/
├── backend/
│   ├── main.py
│   ├── core/
│   │   ├── oracle_engine.py       # El algoritmo bayesiano central
│   │   ├── question_selector.py   # Selección por Information Gain
│   │   ├── attribute_matrix.py    # Carga y vectorización NumPy
│   │   └── session_manager.py     # Estado de sesión en Redis
│   ├── enrichment/
│   │   ├── spotify_enricher.py    # Audio features → atributos
│   │   ├── lastfm_enricher.py     # Tags Last.fm → atributos
│   │   └── claude_enricher.py     # Atributos semánticos vía Claude
│   ├── api/
│   │   ├── oracle.py              # /session, /answer, /give-up
│   │   ├── suggest.py             # /suggest (canciones nuevas)
│   │   ├── share.py               # /share (imagen compartible)
│   │   └── moderation.py          # Panel de aprobación de sugerencias
│   ├── scripts/
│   │   ├── import_spotify_charts.py   # Seed inicial del catálogo
│   │   └── enrich_batch.py            # Enriquecer canciones en batch
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── OracleCharacter.tsx    # Personaje animado con estados
│   │   │   ├── QuestionCard.tsx       # Pregunta + 5 botones de respuesta
│   │   │   ├── GuessReveal.tsx        # "¿Es esta canción?" con portada
│   │   │   ├── ResultScreen.tsx       # Correcto / Incorrecto + share
│   │   │   └── SuggestionForm.tsx     # Sugerir canción nueva
│   │   ├── hooks/
│   │   │   └── useOracleSession.ts    # Estado de sesión en el frontend
│   │   └── App.tsx
│   └── package.json
└── docker-compose.yml
```

---

## Dependencias Backend

```txt
fastapi
uvicorn
numpy              # Vectorización del algoritmo
spotipy            # Catálogo + audio features
httpx              # Llamadas a Last.fm (sin SDK oficial)
anthropic          # Claude para enriquecer atributos semánticos
sqlalchemy
asyncpg
redis
pillow             # Imagen compartible
python-jose        # JWT para session tokens
rapidfuzz          # Matching de nombres en sugerencias
```

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Base de datos muy pequeña al lanzar → juego fácil de vencer | Alta | Alto | Lanzar con géneros limitados, seed agresivo con charts de Spotify |
| Atributos incorrectos en canciones → algoritmo no converge | Alta | Alto | Crowdsourcing desde el día uno corrige errores naturalmente |
| Spotify Audio Features deprecado (ya pasó parcialmente) | Media | Medio | Last.fm + Claude como fuentes principales, Spotify como complemento |
| Usuario piensa en una canción rarísima → el oráculo siempre falla | Alta | Bajo | La derrota del oráculo es narrativamente entretenida + alimenta la DB |
| El algoritmo "atascado" haciendo preguntas inútiles | Media | Alto | Logs de partidas + análisis semanal de preguntas poco efectivas |
| Performance lenta con catálogo grande | Media | Medio | NumPy vectorizado desde el inicio, podado de candidatos con prob <0.001 |

---

## Orden de Ataque

1. **Primero:** construir el script de seed. Importar 2,000 canciones conocidas
   con sus atributos automáticos (Spotify + Last.fm). Sin esto no hay juego.

2. **Segundo:** implementar `OracleEngine` y probarlo en un script de consola.
   Jugar manualmente respondiendo preguntas y verificar que converge en <20 preguntas
   para canciones del catálogo. Iterar hasta que funcione bien.

3. **Tercero:** API de sesión completa (sin frontend). Testear con curl.

4. **Cuarto:** frontend mínimo (sin animaciones del personaje). Que el juego
   funcione en el browser con botones simples.

5. **Quinto:** el personaje animado. Es lo que hace el producto memorable pero
   no es el core funcional.

6. **Sexto:** sharing + sugerencias.

**La trampa de este proyecto es enamorarse del personaje animado antes de que
el algoritmo funcione. El oráculo más impresionante visualmente es inútil si
no adivina correctamente. Primero el cerebro, después la cara.**
