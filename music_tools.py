"""
tools/music_tools.py
Herramientas de conocimiento musical (sin API externa, conocimiento embebido).
"""

from langchain_core.tools import tool


# ── Mapas de teoría musical ──────────────────────────────────────────────────

CHORD_FORMULAS = {
    "major":       [0, 4, 7],
    "minor":       [0, 3, 7],
    "dim":         [0, 3, 6],
    "aug":         [0, 4, 8],
    "maj7":        [0, 4, 7, 11],
    "m7":          [0, 3, 7, 10],
    "7":           [0, 4, 7, 10],
    "m7b5":        [0, 3, 6, 10],
    "dim7":        [0, 3, 6, 9],
    "sus2":        [0, 2, 7],
    "sus4":        [0, 5, 7],
    "add9":        [0, 4, 7, 14],
    "maj9":        [0, 4, 7, 11, 14],
    "9":           [0, 4, 7, 10, 14],
    "m9":          [0, 3, 7, 10, 14],
    "13":          [0, 4, 7, 10, 14, 21],
}

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

SCALES = {
    "major":            [0, 2, 4, 5, 7, 9, 11],
    "natural_minor":    [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor":   [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor":    [0, 2, 3, 5, 7, 9, 11],
    "dorian":           [0, 2, 3, 5, 7, 9, 10],
    "phrygian":         [0, 1, 3, 5, 7, 8, 10],
    "lydian":           [0, 2, 4, 6, 7, 9, 11],
    "mixolydian":       [0, 2, 4, 5, 7, 9, 10],
    "locrian":          [0, 1, 3, 5, 6, 8, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues":            [0, 3, 5, 6, 7, 10],
    "whole_tone":       [0, 2, 4, 6, 8, 10],
    "diminished":       [0, 2, 3, 5, 6, 8, 9, 11],
}

GENRE_PROGRESSIONS = {
    "jazz": {
        "ii-V-I (major)":    ["Dm7", "G7", "Cmaj7"],
        "ii-V-i (minor)":    ["Dm7b5", "G7", "Cm7"],
        "rhythm changes":    ["Bbmaj7", "G7", "Cm7", "F7"],
        "coltrane changes":  ["Cmaj7", "Abmaj7", "Emaj7", "Cmaj7"],
        "blues (jazz)":      ["Bb7", "Eb7", "Bb7", "Bb7", "Eb7", "Edim7", "Bb7", "G7", "Cm7", "F7", "Bb7", "F7"],
    },
    "blues": {
        "12-bar blues":      ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "V7"],
        "quick change":      ["I7", "IV7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "V7"],
        "minor blues":       ["Im7", "Im7", "Im7", "Im7", "IVm7", "IVm7", "Im7", "Im7", "bVII7", "bVI7", "Im7", "Im7"],
    },
    "pop": {
        "I-V-vi-IV":         ["C", "G", "Am", "F"],
        "vi-IV-I-V":         ["Am", "F", "C", "G"],
        "I-IV-V":            ["C", "F", "G"],
        "50s progression":   ["C", "Am", "F", "G"],
    },
    "rock": {
        "power chord classic":  ["I5", "IV5", "V5"],
        "I-bVII-IV":            ["A", "G", "D"],
        "minor rock":           ["Am", "G", "F", "E"],
        "12-bar rock":          ["A7", "A7", "A7", "A7", "D7", "D7", "A7", "A7", "E7", "D7", "A7", "E7"],
    },
    "flamenco": {
        "Phrygian cadence":  ["Am", "G", "F", "E"],
        "soleares":          ["Am", "G", "F", "E", "Am"],
        "Andalusian cadence": ["Am", "G", "F", "E"],
    },
    "bossa nova": {
        "classic":           ["Cmaj7", "Dm7", "G7", "Cmaj7"],
        "girl from ipanema": ["Fmaj7", "G7", "Gm7", "C7", "Fmaj7", "Gbmaj7"],
    },
    "funk": {
        "groove vamp":       ["E7#9", "E7#9"],
        "minor funk":        ["Dm7", "G7sus4"],
        "classic":           ["I7", "IV7"],
    },
}


def _note_index(note: str) -> int:
    note = note.strip().capitalize()
    if note in NOTES:
        return NOTES.index(note)
    # handle flats → sharps
    flats = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
    return NOTES.index(flats.get(note, note))


# ── Tools ────────────────────────────────────────────────────────────────────

@tool
def get_chord_notes(root: str, chord_type: str) -> str:
    """
    Devuelve las notas de un acorde dado una tónica y un tipo de acorde.

    Args:
        root: Nota raíz del acorde (ej: 'C', 'F#', 'Bb')
        chord_type: Tipo de acorde (ej: 'major', 'minor', 'm7', 'maj7', '7', 'dim7', 'sus4')

    Returns:
        String con las notas del acorde y su construcción interválica.
    """
    chord_type = chord_type.lower().strip()
    if chord_type not in CHORD_FORMULAS:
        available = ", ".join(CHORD_FORMULAS.keys())
        return f"Tipo de acorde '{chord_type}' no reconocido. Disponibles: {available}"

    try:
        root_idx = _note_index(root)
    except (KeyError, ValueError):
        return f"Nota raíz '{root}' no reconocida. Usa: {', '.join(NOTES)}"

    intervals = CHORD_FORMULAS[chord_type]
    notes = [NOTES[(root_idx + i) % 12] for i in intervals]
    interval_names = {0:"R", 1:"b2", 2:"2", 3:"b3", 4:"3", 5:"4", 6:"b5/aug4",
                      7:"5", 8:"aug5/b6", 9:"6", 10:"b7", 11:"7", 14:"9", 21:"13"}
    named = [f"{NOTES[(root_idx+i)%12]}({interval_names.get(i%12 if i<12 else i,'?')})" for i in intervals]

    return (
        f"🎸 Acorde: {root} {chord_type}\n"
        f"   Notas: {' - '.join(notes)}\n"
        f"   Construcción: {' | '.join(named)}\n"
        f"   Intervalos semitono: {intervals}"
    )


@tool
def get_scale_notes(root: str, scale_type: str) -> str:
    """
    Devuelve las notas de una escala dada una tónica y tipo de escala.

    Args:
        root: Nota raíz (ej: 'A', 'D#', 'Gb')
        scale_type: Tipo de escala (ej: 'major', 'natural_minor', 'dorian', 'blues', 'pentatonic_minor')

    Returns:
        Notas de la escala con grados.
    """
    scale_type = scale_type.lower().strip()
    if scale_type not in SCALES:
        available = ", ".join(SCALES.keys())
        return f"Escala '{scale_type}' no encontrada. Disponibles: {available}"

    try:
        root_idx = _note_index(root)
    except (KeyError, ValueError):
        return f"Nota '{root}' no reconocida."

    intervals = SCALES[scale_type]
    notes = [NOTES[(root_idx + i) % 12] for i in intervals]
    degree_names = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]

    degrees = [f"{degree_names[n]}={note}" for n, note in enumerate(notes)]

    return (
        f"🎼 Escala: {root} {scale_type}\n"
        f"   Notas: {' - '.join(notes)}\n"
        f"   Grados: {' | '.join(degrees)}"
    )


@tool
def get_genre_progressions(genre: str) -> str:
    """
    Devuelve progresiones de acordes típicas de un género musical.

    Args:
        genre: Género musical (jazz, blues, pop, rock, flamenco, bossa_nova, funk)

    Returns:
        Lista de progresiones típicas del género con sus acordes.
    """
    genre = genre.lower().strip().replace(" ", "_").replace("-", "_")
    # aliases
    aliases = {"bossa": "bossa nova", "bossanova": "bossa nova", "bossa_nova": "bossa nova"}
    genre = aliases.get(genre, genre)

    if genre not in GENRE_PROGRESSIONS:
        available = ", ".join(GENRE_PROGRESSIONS.keys())
        return f"Género '{genre}' no encontrado. Disponibles: {available}"

    progressions = GENRE_PROGRESSIONS[genre]
    lines = [f"🎵 Progresiones de {genre.upper()}:\n"]
    for name, chords in progressions.items():
        lines.append(f"  • {name}: {' → '.join(chords)}")

    return "\n".join(lines)


@tool
def transpose_chord_progression(chords: str, semitones: int) -> str:
    """
    Transpone una progresión de acordes un número de semitonos.

    Args:
        chords: Acordes separados por comas o espacios (ej: 'Dm7, G7, Cmaj7')
        semitones: Número de semitonos a transponer (positivo = subir, negativo = bajar)

    Returns:
        La misma progresión transpuesta.
    """
    import re
    chord_list = re.split(r"[,\s]+", chords.strip())
    transposed = []

    for chord in chord_list:
        if not chord:
            continue
        # Extraer la nota raíz (1 o 2 caracteres: nota + posible sostenido/bemol)
        match = re.match(r"^([A-Ga-g][#b]?)(.*)", chord)
        if not match:
            transposed.append(chord)
            continue
        root, suffix = match.groups()
        try:
            root_idx = _note_index(root)
            new_idx = (root_idx + semitones) % 12
            transposed.append(NOTES[new_idx] + suffix)
        except Exception:
            transposed.append(chord)

    direction = "↑" if semitones > 0 else "↓"
    return (
        f"🔀 Transposición {direction}{abs(semitones)} semitonos:\n"
        f"   Original:    {' → '.join(chord_list)}\n"
        f"   Transpuesto: {' → '.join(transposed)}"
    )


@tool
def get_modes_info(mode: str) -> str:
    """
    Proporciona información detallada sobre un modo musical (modos gregorianos).

    Args:
        mode: Nombre del modo (ionian, dorian, phrygian, lydian, mixolydian, aeolian, locrian)

    Returns:
        Descripción del modo, su sonoridad, acordes típicos y usos.
    """
    modes_info = {
        "ionian": {
            "alias": "Mayor",
            "intervals": [0,2,4,5,7,9,11],
            "feel": "Brillante, alegre, estable",
            "use": "Música pop, clásica, himnos",
            "chords": ["Imaj7", "IIm7", "IIIm7", "IVmaj7", "V7", "VIm7", "VIIm7b5"],
            "artists": "Bach, The Beatles (Hey Jude), Elton John",
        },
        "dorian": {
            "alias": "Menor con 6ª mayor",
            "intervals": [0,2,3,5,7,9,10],
            "feel": "Modal, jazz, funky, oscuro pero esperanzador",
            "use": "Jazz (So What - Miles Davis), funk, rock progresivo",
            "chords": ["Im7", "IIm7", "bIIImaj7", "IV7", "Vm7", "VIm7b5", "bVIImaj7"],
            "artists": "Miles Davis, Santana, Pink Floyd",
        },
        "phrygian": {
            "alias": "Menor con 2ª menor",
            "intervals": [0,1,3,5,7,8,10],
            "feel": "Oscuro, español, flamenco, metal",
            "use": "Flamenco, metal extremo, música española",
            "chords": ["Im7", "bIImaj7", "bIII7", "IVm7", "Vm7b5", "bVImaj7", "bVIIm7"],
            "artists": "Paco de Lucía, Metallica (intro riffs), Carlos Santana",
        },
        "lydian": {
            "alias": "Mayor con #4",
            "intervals": [0,2,4,6,7,9,11],
            "feel": "Etéreo, onírico, flotante, misterioso",
            "use": "Música de película (John Williams), jazz moderno",
            "chords": ["Imaj7", "II7", "IIIm7", "#IVm7b5", "Vmaj7", "VIm7", "VIIm7"],
            "artists": "Joe Satriani, John Williams (Star Wars), Steve Vai",
        },
        "mixolydian": {
            "alias": "Mayor con 7ª menor",
            "intervals": [0,2,4,5,7,9,10],
            "feel": "Blues, rock, groove, relajado",
            "use": "Rock, blues, música celta, country",
            "chords": ["I7", "IIm7", "IIIm7b5", "IVmaj7", "Vm7", "VIm7", "bVIImaj7"],
            "artists": "The Beatles (Norwegian Wood), Grateful Dead, AC/DC",
        },
        "aeolian": {
            "alias": "Menor natural",
            "intervals": [0,2,3,5,7,8,10],
            "feel": "Melancólico, oscuro, introspectivo",
            "use": "Rock, pop (baladas), clásica",
            "chords": ["Im7", "IIm7b5", "bIIImaj7", "IVm7", "Vm7", "bVImaj7", "bVII7"],
            "artists": "Led Zeppelin, Radiohead, Nirvana",
        },
        "locrian": {
            "alias": "Menor con 2ª y 5ª menores",
            "intervals": [0,1,3,5,6,8,10],
            "feel": "Muy oscuro, inestable, tenso",
            "use": "Metal extremo, jazz moderno (raramente en tónica)",
            "chords": ["Im7b5", "bIImaj7", "bIIIm7", "IVm7", "bVmaj7", "bVI7", "bVIIm7"],
            "artists": "Bjork, John Petrucci (Dream Theater)",
        },
    }

    mode = mode.lower().strip()
    if mode not in modes_info:
        available = ", ".join(modes_info.keys())
        return f"Modo '{mode}' no encontrado. Disponibles: {available}"

    info = modes_info[mode]
    return (
        f"🎵 Modo {mode.capitalize()} ({info['alias']})\n\n"
        f"   Intervalos:  {info['intervals']}\n"
        f"   Sonoridad:   {info['feel']}\n"
        f"   Uso típico:  {info['use']}\n"
        f"   Acordes:     {' | '.join(info['chords'])}\n"
        f"   Artistas ref: {info['artists']}"
    )
