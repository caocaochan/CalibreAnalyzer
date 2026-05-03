"""
AnkiConnect client — communicates with a running Anki instance via the
AnkiConnect add-on's HTTP API (default: http://127.0.0.1:8765).

Requires:
  - Anki running in the background
  - AnkiConnect add-on installed (code 2055492159)
"""

import json
import re

from calibre_plugins.chinese_character_analyzer.analyzer import (
    extract_cjk_characters,
    extract_cjk_words,
)

_DEFAULT_URL = "http://127.0.0.1:8765"
_API_VERSION = 6
_BATCH_SIZE = 100  # notesInfo batch size to avoid huge single requests


class AnkiConnectError(Exception):
    """Raised when AnkiConnect returns an error or is unreachable."""
    pass


def _request(action, params=None, url=_DEFAULT_URL):
    """
    Send a request to the AnkiConnect API and return the result.
    Uses urllib so we don't add any external dependencies.
    """
    from urllib.request import urlopen, Request
    from urllib.error import URLError

    payload = {"action": action, "version": _API_VERSION}
    if params:
        payload["params"] = params

    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except URLError as e:
        raise AnkiConnectError(
            "Could not connect to Anki.\n\n"
            "Make sure Anki is running and the AnkiConnect add-on is installed "
            "(Tools → Add-ons → Get Add-ons → code 2055492159).\n\n"
            f"Details: {e}"
        )
    except Exception as e:
        raise AnkiConnectError(f"AnkiConnect request failed: {e}")

    if body.get("error"):
        raise AnkiConnectError(f"AnkiConnect error: {body['error']}")

    return body.get("result")


def ping(url=_DEFAULT_URL):
    """Return True if AnkiConnect is reachable."""
    try:
        _request("version", url=url)
        return True
    except AnkiConnectError:
        return False


def deck_names(url=_DEFAULT_URL):
    """Return a list of all deck names."""
    return _request("deckNames", url=url)


def model_field_names(model_name, url=_DEFAULT_URL):
    """Return the list of field names for a given note type (model)."""
    return _request("modelFieldNames", params={"modelName": model_name}, url=url)


def find_notes(query, url=_DEFAULT_URL):
    """Return a list of note IDs matching an Anki search query."""
    return _request("findNotes", params={"query": query}, url=url)


def notes_info(note_ids, url=_DEFAULT_URL):
    """
    Return detailed info for the given note IDs.
    Batches requests to avoid oversized payloads.
    """
    all_notes = []
    for i in range(0, len(note_ids), _BATCH_SIZE):
        batch = note_ids[i : i + _BATCH_SIZE]
        result = _request("notesInfo", params={"notes": batch}, url=url)
        if result:
            all_notes.extend(result)
    return all_notes


def _strip_html(text):
    """Remove HTML tags and decode common entities."""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    return text.strip()


# ── Query builders ──────────────────────────────────────────────────────

# Known-ness filter presets:  (label, query_fragment)
# The query fragment is appended to the deck filter.
KNOWN_FILTERS = [
    ("All cards", ""),
    ("Reviewed (not new)", "-is:new"),
    ("Young + Mature (interval ≥1 day)", "prop:ivl>=1"),
    ("Mature only (interval ≥21 days)", "prop:ivl>=21"),
]


def build_query(deck_names_list, known_filter_query=""):
    """
    Build an Anki search query that matches notes in any of the given decks,
    with an optional filter for card maturity.
    """
    if not deck_names_list:
        raise AnkiConnectError("No decks selected.")

    # Combine decks with OR — each deck name is quoted
    deck_parts = []
    for name in deck_names_list:
        escaped = name.replace('"', '\\"')
        deck_parts.append(f'"deck:{escaped}"')

    if len(deck_parts) == 1:
        query = deck_parts[0]
    else:
        query = "(" + " OR ".join(deck_parts) + ")"

    if known_filter_query:
        query += " " + known_filter_query

    return query


def _extract_field_texts_from_notes(notes, field_name):
    texts = []
    for note in notes:
        fields = note.get("fields", {})
        field_data = fields.get(field_name, {})
        raw_value = field_data.get("value", "") if isinstance(field_data, dict) else ""
        clean = _strip_html(raw_value)
        if clean:
            texts.append(clean)
    return texts


def fetch_field_texts(deck_names_list, field_name, known_filter_query="",
                      url=_DEFAULT_URL, progress_callback=None):
    """
    Fetch cleaned field texts from the selected decks and field.
    Returns (texts, note_count).
    """
    if progress_callback:
        progress_callback("Building search query…")

    query = build_query(deck_names_list, known_filter_query)

    if progress_callback:
        progress_callback("Finding notes in Anki…")

    note_ids = find_notes(query, url=url)
    if not note_ids:
        return [], 0

    if progress_callback:
        progress_callback(f"Fetching {len(note_ids):,} notes…")

    notes = notes_info(note_ids, url=url)

    if progress_callback:
        progress_callback("Extracting field text…")

    return _extract_field_texts_from_notes(notes, field_name), len(notes)


def fetch_known_characters(deck_names_list, field_name, known_filter_query="",
                           url=_DEFAULT_URL, progress_callback=None):
    """
    High-level helper: fetch notes from the selected decks, extract CJK
    characters from the specified field, and return:
      - known_chars: set of unique CJK characters
      - note_count: total number of notes examined

    progress_callback(message) is called with status strings if provided.
    """
    texts, note_count = fetch_field_texts(
        deck_names_list,
        field_name,
        known_filter_query=known_filter_query,
        url=url,
        progress_callback=progress_callback,
    )
    known = set()
    for text in texts:
        known.update(extract_cjk_characters(text))
    return known, note_count


def fetch_known_words(deck_names_list, field_name, known_filter_query="",
                      url=_DEFAULT_URL, progress_callback=None, segmenter=None):
    """Fetch unique segmented words from the selected decks and field."""
    texts, note_count = fetch_field_texts(
        deck_names_list,
        field_name,
        known_filter_query=known_filter_query,
        url=url,
        progress_callback=progress_callback,
    )
    known = set()
    for text in texts:
        known.update(extract_cjk_words(text, segmenter=segmenter))
    return known, note_count


def get_all_field_names(deck_names_list, url=_DEFAULT_URL):
    """
    Fetch a small sample of notes from the given decks and collect all
    field names across all note types encountered.
    Returns (field_names_list, sample_notes) where sample_notes is a list
    of dicts with a 'fields' key for preview purposes.
    """
    query = build_query(deck_names_list)
    note_ids = find_notes(query, url=url)
    if not note_ids:
        return [], []

    # Fetch a sample for preview + all unique model field names
    sample_ids = note_ids[:20]
    sample_notes = notes_info(sample_ids, url=url)

    # Collect field names in order of appearance, preserving order
    all_fields = []
    seen = set()
    for note in sample_notes:
        # Sort fields by their "order" key to get correct ordering
        fields = note.get("fields", {})
        sorted_names = sorted(fields.keys(), key=lambda k: fields[k].get("order", 0))
        for name in sorted_names:
            if name not in seen:
                all_fields.append(name)
                seen.add(name)

    # Convert sample notes to a simpler format for the preview dialog
    simple_notes = []
    for note in sample_notes:
        fields = note.get("fields", {})
        simple = {}
        for fname, fdata in fields.items():
            simple[fname] = _strip_html(fdata.get("value", "") if isinstance(fdata, dict) else "")
        simple_notes.append({"fields": simple})

    return all_fields, simple_notes, len(note_ids)
