"""Seed list of artists for catalog import.

Each artist gives up to 10 top tracks via Spotify. 200 artists ≈ 2000 tracks.
Mix of eras / genres / languages to keep the Oracle balanced.
"""

SEED_ARTISTS: list[str] = [
    # ---- classic rock / 60s-70s ----
    "The Beatles", "Queen", "Led Zeppelin", "Pink Floyd", "The Rolling Stones",
    "David Bowie", "Fleetwood Mac", "Eagles", "Bob Dylan", "The Doors",
    "Jimi Hendrix", "Creedence Clearwater Revival", "The Who", "Lynyrd Skynyrd",
    "ABBA", "Elton John", "Stevie Wonder", "Simon & Garfunkel",
    # ---- 80s rock / pop ----
    "Michael Jackson", "Madonna", "Prince", "U2", "Bon Jovi", "AC/DC",
    "Guns N' Roses", "Bruce Springsteen", "Phil Collins", "Whitney Houston",
    "Tina Turner", "Dire Straits", "Toto", "Journey", "The Police",
    "Tears for Fears", "a-ha", "Duran Duran", "INXS", "Eurythmics",
    # ---- 90s rock / alt ----
    "Nirvana", "Pearl Jam", "Radiohead", "Oasis", "Red Hot Chili Peppers",
    "Foo Fighters", "Green Day", "Blur", "The Cranberries", "R.E.M.",
    "Soundgarden", "Alice in Chains", "Smashing Pumpkins", "Weezer",
    "Rage Against the Machine", "The Offspring", "Blink-182", "No Doubt",
    # ---- 90s pop / r&b ----
    "Spice Girls", "Backstreet Boys", "*NSYNC", "Britney Spears",
    "Mariah Carey", "Celine Dion", "TLC", "Destiny's Child", "Boyz II Men",
    "Shakira", "Ricky Martin",
    # ---- 2000s ----
    "Coldplay", "Linkin Park", "Eminem", "50 Cent", "Beyoncé", "Rihanna",
    "Justin Timberlake", "Christina Aguilera", "Alicia Keys", "Avril Lavigne",
    "Kelly Clarkson", "Maroon 5", "OneRepublic", "Black Eyed Peas",
    "System of a Down", "Muse", "Arctic Monkeys", "The Killers", "Franz Ferdinand",
    "Kanye West", "JAY-Z", "Outkast",
    # ---- 2010s pop / indie ----
    "Taylor Swift", "Adele", "Lady Gaga", "Bruno Mars", "Ed Sheeran",
    "Sam Smith", "Lorde", "Lana Del Rey", "Imagine Dragons", "The 1975",
    "Arctic Monkeys", "Vampire Weekend", "Tame Impala", "Mumford & Sons",
    "Florence + The Machine", "Hozier", "twenty one pilots",
    "Panic! at the Disco", "Fall Out Boy", "Paramore", "Lana Del Rey",
    # ---- modern pop / hip-hop ----
    "Drake", "Kendrick Lamar", "Travis Scott", "Post Malone", "The Weeknd",
    "Billie Eilish", "Doja Cat", "Olivia Rodrigo", "Dua Lipa", "Harry Styles",
    "Ariana Grande", "Selena Gomez", "Justin Bieber", "Halsey", "Sia",
    "Cardi B", "Nicki Minaj", "Megan Thee Stallion", "Lil Nas X", "SZA",
    "Frank Ocean", "Tyler, The Creator", "21 Savage", "Future",
    # ---- electronic ----
    "Daft Punk", "Calvin Harris", "David Guetta", "Avicii", "Skrillex",
    "Deadmau5", "Tiësto", "Martin Garrix", "The Chainsmokers", "Disclosure",
    "Gorillaz", "Massive Attack", "The Prodigy", "Chemical Brothers",
    # ---- metal ----
    "Metallica", "Iron Maiden", "Black Sabbath", "Megadeth", "Slayer",
    "Tool", "System of a Down", "Slipknot",
    # ---- latin / spanish ----
    "Bad Bunny", "J Balvin", "Karol G", "Daddy Yankee", "Ozuna",
    "Maluma", "Nicky Jam", "Rosalía", "Enrique Iglesias", "Marc Anthony",
    "Romeo Santos", "Aventura", "Juanes", "Manu Chao", "Café Tacvba",
    "Soda Stereo", "Gustavo Cerati", "Mecano", "Heroes del Silencio",
    "Joaquín Sabina", "Joan Manuel Serrat", "Alejandro Sanz", "Luis Miguel",
    "Vicente Fernández", "Selena", "Gloria Estefan",
    # ---- reggae / world ----
    "Bob Marley & The Wailers", "Bob Marley", "Damian Marley",
    # ---- jazz / soul ----
    "Frank Sinatra", "Ella Fitzgerald", "Louis Armstrong", "Miles Davis",
    "Nina Simone", "Amy Winehouse", "Norah Jones", "Aretha Franklin",
    "Ray Charles", "Marvin Gaye",
    # ---- country / folk ----
    "Johnny Cash", "Dolly Parton", "Willie Nelson", "Garth Brooks",
    "Shania Twain", "Taylor Swift",
    # ---- classical / cinematic ----
    "Hans Zimmer", "Ennio Morricone", "John Williams",
]

# Dedupe while preserving order
SEED_ARTISTS = list(dict.fromkeys(SEED_ARTISTS))
