"""
Anki .apkg file parser.
Extracts note fields from .apkg files (ZIP archives containing SQLite databases).
Supports:
  - collection.anki2  (Anki 2.0 — plain SQLite)
  - collection.anki21 (Anki 2.1 — plain SQLite)
  - collection.anki21b (Anki 2.1.50+ — zstd-compressed SQLite)
"""

import os
import sqlite3
import json
import zipfile
import tempfile
import re
import struct


# ── zstd decompression ──────────────────────────────────────────────────

# zstd magic number: 0xFD2FB528 (little-endian)
_ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"

# SQLite magic: "SQLite format 3\000"
_SQLITE_MAGIC = b"SQLite format 3\x00"


def _decompress_zstd(data):
    """
    Decompress zstd data. Tries multiple approaches:
    1. Calibre's bundled zstandard module
    2. pyzstd (if available)
    3. zstd (if available)
    """
    # Try calibre's bundled zstandard
    try:
        import zstandard
        dctx = zstandard.ZstdDecompressor()
        return dctx.decompress(data, max_output_size=500 * 1024 * 1024)
    except ImportError:
        pass

    # Try pyzstd
    try:
        import pyzstd
        return pyzstd.decompress(data)
    except ImportError:
        pass

    # Try zstd
    try:
        import zstd
        return zstd.decompress(data)
    except ImportError:
        pass

    raise ImportError(
        "Cannot decompress zstd data. This Anki deck uses the newer .anki21b format "
        "which requires zstd decompression. Please install the 'pyzstd' or 'zstandard' "
        "Python package, or try exporting from Anki in the legacy format "
        "(File → Export → check 'Legacy support')."
    )


def _ensure_sqlite(data):
    """
    If data starts with the zstd magic number, decompress it.
    Returns raw SQLite bytes.
    """
    if data[:4] == _ZSTD_MAGIC:
        data = _decompress_zstd(data)

    if data[:16] != _SQLITE_MAGIC:
        raise ValueError(
            "The extracted database is not a valid SQLite file. "
            "It may be a format this plugin doesn't support yet."
        )

    return data


# ── Main parser ─────────────────────────────────────────────────────────

def parse_apkg(apkg_path):
    """
    Parse an .apkg file and return:
      - field_names: dict mapping model_id -> list of field names
      - notes: list of dicts with keys 'model_id', 'fields' (dict of name->value)
    """
    with zipfile.ZipFile(apkg_path, "r") as zf:
        names = zf.namelist()

        # Find the SQLite database inside the zip (prefer newest format)
        db_name = None
        for candidate in ("collection.anki21b", "collection.anki21", "collection.anki2"):
            if candidate in names:
                db_name = candidate
                break

        if db_name is None:
            raise ValueError(
                "Could not find a collection database inside the .apkg file. "
                f"Archive contents: {', '.join(names[:20])}"
            )

        raw_data = zf.read(db_name)

    # Handle zstd compression (anki21b files)
    raw_data = _ensure_sqlite(raw_data)

    # Write to temp file for sqlite3
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp.write(raw_data)
        tmp_path = tmp.name

    try:
        return _read_db(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _read_db(db_path):
    """Read field names and notes from the extracted SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        field_names = {}  # model_id -> [field_name, ...]

        # ── Try newer schema first (notetypes + fields tables) ──
        try:
            rows = conn.execute("SELECT id, name FROM notetypes").fetchall()
            for row in rows:
                mid = str(row["id"])
                flds = conn.execute(
                    "SELECT name FROM fields WHERE ntid=? ORDER BY ord", (row["id"],)
                ).fetchall()
                field_names[mid] = [f["name"] for f in flds]
        except sqlite3.OperationalError:
            pass

        # ── Fallback: classic 'col' table with JSON models ──
        if not field_names:
            try:
                col_row = conn.execute("SELECT models FROM col").fetchone()
                if col_row:
                    models = json.loads(col_row["models"])
                    for mid, model in models.items():
                        flds = sorted(model.get("flds", []), key=lambda f: f.get("ord", 0))
                        field_names[str(mid)] = [f["name"] for f in flds]
            except (sqlite3.OperationalError, json.JSONDecodeError):
                pass

        if not field_names:
            raise ValueError("Could not read note type definitions from the Anki database.")

        # ── Read all notes ──
        notes = []
        try:
            rows = conn.execute("SELECT mid, flds FROM notes").fetchall()
        except sqlite3.OperationalError:
            rows = []

        for row in rows:
            mid = str(row["mid"])
            raw_fields = row["flds"].split("\x1f")
            names = field_names.get(mid, [])

            fields = {}
            for i, value in enumerate(raw_fields):
                name = names[i] if i < len(names) else f"Field {i+1}"
                fields[name] = _strip_html(value)

            notes.append({"model_id": mid, "fields": fields})

        return field_names, notes

    finally:
        conn.close()


def _strip_html(text):
    """Remove HTML tags and decode entities from a field value."""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    return text.strip()


def extract_field_texts(notes, field_name):
    """Return cleaned, non-empty field texts for the selected Anki field."""
    texts = []
    for note in notes:
        value = note["fields"].get(field_name, "")
        if value:
            texts.append(value)
    return texts


def extract_characters_from_field(notes, field_name):
    """
    Given a list of notes and a field name, extract all unique CJK characters
    found across all notes in that field.
    Returns a set of characters.
    """
    from calibre_plugins.chinese_character_analyzer.analyzer import extract_cjk_characters

    chars = set()
    for value in extract_field_texts(notes, field_name):
        chars.update(extract_cjk_characters(value))
    return chars


def extract_words_from_field(notes, field_name, segmenter=None):
    """Return all unique segmented words found in the selected Anki field."""
    from calibre_plugins.chinese_character_analyzer.analyzer import extract_cjk_words

    words = set()
    for value in extract_field_texts(notes, field_name):
        words.update(extract_cjk_words(value, segmenter=segmenter))
    return words
