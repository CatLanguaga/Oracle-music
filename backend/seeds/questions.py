"""Preguntas iniciales. Cada una mapea a un attribute_key.

Una pregunta = un atributo. Varias preguntas pueden compartir attribute pero
en seed inicial es 1:1 para mantener cosas simples.
"""

# (attribute_key, text_es, category)
QUESTIONS: list[tuple[str, str, str]] = [
    # genre
    ("is_rock", "¿Es una canción de rock?", "genre"),
    ("is_pop", "¿Es una canción pop?", "genre"),
    ("is_electronic", "¿Es electrónica o dance?", "genre"),
    ("is_hiphop_rap", "¿Tiene elementos de hip-hop o rap?", "genre"),
    ("is_jazz_blues", "¿Es jazz o blues?", "genre"),
    ("is_classical", "¿Es música clásica?", "genre"),
    ("is_latin", "¿Es reggaetón o música latina?", "genre"),
    ("is_metal", "¿Es metal o heavy metal?", "genre"),
    ("is_rnb_soul", "¿Es R&B o soul?", "genre"),
    ("is_country_folk", "¿Es country o folk?", "genre"),
    ("is_indie_alt", "¿Es indie o alternativa?", "genre"),
    ("is_punk", "¿Es punk?", "genre"),
    ("is_reggae", "¿Es reggae?", "genre"),

    # era
    ("released_before_2000", "¿Fue lanzada antes del año 2000?", "era"),
    ("released_in_90s", "¿Fue lanzada en los años 90?", "era"),
    ("released_in_80s", "¿Fue lanzada en los años 80?", "era"),
    ("released_in_70s", "¿Fue lanzada en los años 70?", "era"),
    ("released_after_2010", "¿Fue lanzada después del 2010?", "era"),
    ("released_recent_3y", "¿Es una canción reciente (últimos 3 años)?", "era"),

    # artist
    ("artist_is_band", "¿El artista es un grupo o banda?", "artist"),
    ("artist_is_solo", "¿Es un artista solista (sin banda)?", "artist"),
    ("vocalist_is_female", "¿La voz principal es de una mujer?", "artist"),
    ("vocalist_is_male", "¿La voz principal es de un hombre?", "artist"),
    ("artist_anglophone", "¿El artista es de habla inglesa?", "artist"),
    ("artist_latin", "¿El artista es latinoamericano o español?", "artist"),
    ("artist_from_uk", "¿El artista es del Reino Unido?", "artist"),
    ("artist_from_usa", "¿El artista es de Estados Unidos?", "artist"),
    ("has_featuring", "¿Tiene un artista invitado (feat.)?", "artist"),

    # energy
    ("is_fast_tempo", "¿Es una canción rápida y energética?", "energy"),
    ("is_ballad", "¿Es una balada o canción lenta?", "energy"),
    ("is_danceable", "¿Es buena para bailar?", "energy"),
    ("is_chill", "¿Es relajante o tranquila?", "energy"),
    ("has_strong_percussion", "¿Tiene percusión o batería prominente?", "energy"),

    # mood
    ("is_sad_mood", "¿Es una canción triste o melancólica?", "mood"),
    ("is_happy_mood", "¿Es una canción alegre o positiva?", "mood"),
    ("is_romantic", "¿Es una canción de amor o romántica?", "mood"),
    ("is_about_heartbreak", "¿Habla de desamor o ruptura?", "mood"),
    ("is_rebellious", "¿Tiene un tono agresivo o rebelde?", "mood"),
    ("is_party", "¿Es una canción festiva, de fiesta?", "mood"),
    ("is_nostalgic", "¿Te genera nostalgia?", "mood"),

    # instruments
    ("has_electric_guitar", "¿Tiene guitarra eléctrica prominente?", "instruments"),
    ("has_piano", "¿Tiene piano como instrumento principal?", "instruments"),
    ("is_synth_driven", "¿Está dominada por sintetizadores?", "instruments"),
    ("has_strings", "¿Tiene sección de cuerdas (violines, etc.)?", "instruments"),
    ("is_acoustic", "¿Es principalmente acústica?", "instruments"),
    ("is_instrumental", "¿Es instrumental (sin letra)?", "instruments"),

    # fame
    ("is_very_famous", "¿Es una canción muy famosa, conocida por casi todos?", "fame"),
    ("is_in_movie_or_series", "¿Aparece en alguna película o serie conocida?", "fame"),
    ("was_number_one", "¿Fue número 1 en algún país?", "fame"),
    ("has_famous_intro", "¿Tiene un intro icónico que reconocerías al instante?", "fame"),
    ("is_cult_classic", "¿Es un clásico de culto?", "fame"),

    # lyrics
    ("lyrics_in_spanish", "¿Tiene letra en español?", "lyrics"),
    ("lyrics_in_english", "¿Tiene letra en inglés?", "lyrics"),
    ("lyrics_mixed_lang", "¿Mezcla dos o más idiomas?", "lyrics"),

    # duration
    ("is_longer_than_5min", "¿Dura más de 5 minutos?", "duration"),
    ("is_shorter_than_3min", "¿Dura menos de 3 minutos?", "duration"),
]
