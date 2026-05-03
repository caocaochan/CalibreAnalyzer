"""
Persistent cache helpers for expensive word-mode analysis results.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone


PLUGIN_IMPORT_NAME = "chinese_character_analyzer"
CACHE_SCHEMA_VERSION = 1


def _default_cache_root():
    try:
        from calibre.utils.config import config_dir
    except ImportError:
        config_dir = os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(config_dir, "plugins", PLUGIN_IMPORT_NAME, "analysis-cache")


def get_cache_root(base_dir=None):
    if base_dir is not None:
        return base_dir
    return _default_cache_root()


def build_analysis_key(text, book_format):
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{digest}:{(book_format or '').upper()}"


def build_cache_key(analysis_key, book_format, runtime_version, schema_version=CACHE_SCHEMA_VERSION):
    source = "|".join((
        analysis_key or "",
        (book_format or "").upper(),
        str(schema_version),
        runtime_version,
    ))
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _cache_path(analysis_key, book_format, runtime_version, base_dir=None):
    cache_key = build_cache_key(analysis_key, book_format, runtime_version)
    root = get_cache_root(base_dir)
    return os.path.join(root, cache_key[:2], f"{cache_key}.json")


def _serialize_word_stats(stats, analysis_key, book_format, runtime_version):
    return {
        "schema_version": CACHE_SCHEMA_VERSION,
        "analysis_key": analysis_key,
        "runtime_version": runtime_version,
        "format": (book_format or "").upper(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": dict(stats["summary"]),
        "frequency_rows": [dict(row) for row in stats["frequency_rows"]],
        "hsk_groups": json.loads(json.dumps(stats["hsk_groups"])),
        "length_buckets": json.loads(json.dumps(stats["length_buckets"])),
    }


def save_word_analysis(analysis_key, book_format, runtime_version, stats, base_dir=None):
    record = _serialize_word_stats(stats, analysis_key, book_format, runtime_version)
    path = _cache_path(analysis_key, book_format, runtime_version, base_dir=base_dir)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, separators=(",", ":"))
    return record


def load_word_analysis(analysis_key, book_format, runtime_version, base_dir=None):
    path = _cache_path(analysis_key, book_format, runtime_version, base_dir=base_dir)
    if not os.path.isfile(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as fh:
            record = json.load(fh)
    except (OSError, ValueError):
        return None

    if record.get("schema_version") != CACHE_SCHEMA_VERSION:
        return None
    if record.get("analysis_key") != analysis_key:
        return None
    if record.get("runtime_version") != runtime_version:
        return None
    if record.get("format") != (book_format or "").upper():
        return None
    if "summary" not in record or "frequency_rows" not in record or "hsk_groups" not in record:
        return None
    return record
