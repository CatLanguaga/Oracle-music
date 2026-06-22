"""Catálogo canónico de atributos. (key, category, description)."""

ATTRIBUTES: list[tuple[str, str, str]] = [
    # ---- genre ----
    ("is_rock", "genre", "Pertenece al género rock (clásico, alternativo, indie, etc)."),
    ("is_pop", "genre", "Pertenece al género pop."),
    ("is_electronic", "genre", "Electrónica, dance, EDM, house, techno."),
    ("is_hiphop_rap", "genre", "Hip-hop o rap."),
    ("is_jazz_blues", "genre", "Jazz o blues."),
    ("is_classical", "genre", "Música clásica u orquestal."),
    ("is_latin", "genre", "Reggaetón, salsa, bachata, cumbia u otra música latina."),
    ("is_metal", "genre", "Metal o heavy metal."),
    ("is_rnb_soul", "genre", "R&B o soul."),
    ("is_country_folk", "genre", "Country o folk."),
    ("is_indie_alt", "genre", "Indie o alternativo."),
    ("is_punk", "genre", "Punk o post-punk."),
    ("is_reggae", "genre", "Reggae."),

    # ---- era ----
    ("released_before_2000", "era", "Lanzada antes del año 2000."),
    ("released_in_90s", "era", "Lanzada en los años 90."),
    ("released_in_80s", "era", "Lanzada en los años 80."),
    ("released_in_70s", "era", "Lanzada en los años 70."),
    ("released_after_2010", "era", "Lanzada después de 2010."),
    ("released_recent_3y", "era", "Lanzada en los últimos 3 años."),

    # ---- artist ----
    ("artist_is_band", "artist", "El artista es un grupo o banda."),
    ("artist_is_solo", "artist", "Es un artista solista."),
    ("vocalist_is_female", "artist", "La voz principal es femenina."),
    ("vocalist_is_male", "artist", "La voz principal es masculina."),
    ("artist_anglophone", "artist", "El artista es de un país de habla inglesa."),
    ("artist_latin", "artist", "El artista es latinoamericano o español."),
    ("artist_from_uk", "artist", "El artista es del Reino Unido."),
    ("artist_from_usa", "artist", "El artista es de Estados Unidos."),
    ("has_featuring", "artist", "Tiene un artista invitado (feat.)."),

    # ---- energy ----
    ("is_fast_tempo", "energy", "Tempo rápido (>120 BPM)."),
    ("is_ballad", "energy", "Es una balada o canción lenta."),
    ("is_danceable", "energy", "Buena para bailar."),
    ("is_chill", "energy", "Relajante, tranquila."),
    ("is_energetic", "energy", "Alta energía."),
    ("has_strong_percussion", "energy", "Percusión o batería prominente."),

    # ---- mood ----
    ("is_sad_mood", "mood", "Triste o melancólica."),
    ("is_happy_mood", "mood", "Alegre o positiva."),
    ("is_romantic", "mood", "Sobre amor o romántica."),
    ("is_about_heartbreak", "mood", "Sobre desamor o ruptura."),
    ("is_rebellious", "mood", "Tono agresivo o rebelde."),
    ("is_party", "mood", "Festiva o de fiesta."),
    ("is_nostalgic", "mood", "Genera nostalgia."),

    # ---- instruments ----
    ("has_electric_guitar", "instruments", "Guitarra eléctrica prominente."),
    ("has_piano", "instruments", "Piano como instrumento principal."),
    ("is_synth_driven", "instruments", "Dominada por sintetizadores."),
    ("has_strings", "instruments", "Tiene sección de cuerdas (violines, etc.)."),
    ("is_acoustic", "instruments", "Principalmente acústica."),
    ("is_instrumental", "instruments", "Sin letra (instrumental)."),

    # ---- fame ----
    ("is_very_famous", "fame", "Muy famosa, conocida por casi todos."),
    ("is_in_movie_or_series", "fame", "Aparece en alguna película o serie conocida."),
    ("was_number_one", "fame", "Fue número 1 en algún país."),
    ("has_famous_intro", "fame", "Tiene un intro icónico/reconocible."),
    ("is_cult_classic", "fame", "Clásico de culto."),

    # ---- lyrics ----
    ("lyrics_in_spanish", "lyrics", "Letra en español."),
    ("lyrics_in_english", "lyrics", "Letra en inglés."),
    ("lyrics_mixed_lang", "lyrics", "Mezcla dos o más idiomas."),

    # ---- duration ----
    ("is_longer_than_5min", "duration", "Dura más de 5 minutos."),
    ("is_shorter_than_3min", "duration", "Dura menos de 3 minutos."),
]
