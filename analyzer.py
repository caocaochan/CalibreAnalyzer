"""
Core analysis logic.
Identifies Chinese characters, segments Chinese words, and computes stats.
"""

from collections import Counter


class SegmentationError(RuntimeError):
    """Raised when the configured word segmenter cannot be used."""


# Chinese / CJK punctuation and common symbols to exclude
_PUNCTUATION = set(
    "\u3000\u3001\u3002\u3003\u3008\u3009\u300a\u300b\u300c\u300d\u300e\u300f"
    "\u3010\u3011\u3014\u3015\u3016\u3017\u3018\u3019\u301a\u301b\u301c\u301d"
    "\u301e\u301f\ufe4f\ufe50\ufe51\ufe52\ufe54\ufe55\ufe56\ufe57\ufe59\ufe5a"
    "\ufe5b\ufe5c\ufe5d\ufe5e\ufe5f\ufe60\ufe61\ufe63\ufe68\ufe6a\ufe6b"
    "\uff01\uff02\uff03\uff04\uff05\uff08\uff09\uff0a\uff0c\uff0e\uff0f"
    "\uff1a\uff1b\uff1f\uff20\uff3b\uff3d\uff3e\uff5b\uff5d\uff5e"
    "\u2018\u2019\u201c\u201d\u2026\u2014\u2013\u00b7\u2022"
    "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r"
)


def _import_hsk_data():
    try:
        from calibre_plugins.chinese_character_analyzer import hsk_data
    except ImportError:
        import hsk_data
    return hsk_data


def is_cjk_ideograph(char):
    """Return True if the character is a CJK Unified Ideograph."""
    cp = ord(char)
    return (
        (0x4E00 <= cp <= 0x9FFF)        # CJK Unified Ideographs
        or (0x3400 <= cp <= 0x4DBF)     # CJK Extension A
        or (0x20000 <= cp <= 0x2A6DF)   # CJK Extension B
        or (0x2A700 <= cp <= 0x2B73F)   # CJK Extension C
        or (0x2B740 <= cp <= 0x2B81F)   # CJK Extension D
        or (0x2B820 <= cp <= 0x2CEAF)   # CJK Extension E
        or (0x2CEB0 <= cp <= 0x2EBEF)   # CJK Extension F
        or (0xF900 <= cp <= 0xFAFF)     # CJK Compat Ideographs
        or (0x2F800 <= cp <= 0x2FA1F)   # CJK Compat Ideographs Supp
    )


def contains_cjk_ideograph(text):
    """Return True if any character in text is a CJK ideograph."""
    return any(is_cjk_ideograph(ch) for ch in text)


def is_punctuation_or_space(text):
    """Return True if text contains only punctuation/whitespace characters."""
    return bool(text) and all(ch in _PUNCTUATION for ch in text)


def extract_cjk_characters(text):
    """Return all CJK ideographs from text, excluding punctuation."""
    return [ch for ch in text if is_cjk_ideograph(ch) and ch not in _PUNCTUATION]


def normalize_coverage_payload(coverage, items_key):
    """Convert set-based HSK coverage into a serializable list-based payload."""
    per_level = {}
    for level, info in coverage["per_level"].items():
        per_level[level] = {
            "count": info["count"],
            "pct": info["pct"],
            "items": sorted(info[items_key]),
        }

    return {
        "per_level": per_level,
        "cumulative": coverage["cumulative"],
        "not_in_hsk": sorted(coverage["not_in_hsk"]),
        "not_in_hsk_count": coverage["not_in_hsk_count"],
        "not_in_hsk_pct": coverage["not_in_hsk_pct"],
    }


def _sorted_frequency(counter):
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def _build_frequency_rows(frequency, hsk_level_getter):
    rows = []
    for rank, (item, count) in enumerate(frequency.items(), start=1):
        rows.append({
            "rank": rank,
            "item": item,
            "count": count,
            "length": len(item),
            "hsk_level": hsk_level_getter(item),
        })
    return rows


def _build_length_buckets(unique_words):
    buckets = {
        "1": {"count": 0, "pct": 0.0},
        "2": {"count": 0, "pct": 0.0},
        "3": {"count": 0, "pct": 0.0},
        "4+": {"count": 0, "pct": 0.0},
    }
    total_unique = len(unique_words)
    for word in unique_words:
        label = _length_bucket_label(word)
        buckets[label]["count"] += 1
    for info in buckets.values():
        info["pct"] = (info["count"] / total_unique * 100) if total_unique else 0.0
    return buckets


def _counts_from_rows(rows):
    return {row["item"]: row["count"] for row in rows}


def _average_weighted_word_length(rows, total_words):
    if not total_words:
        return 0.0
    weighted_total = sum(row["length"] * row["count"] for row in rows)
    return weighted_total / total_words


def analyze_characters(text):
    """
    Analyze a text string and return a dict with:
      - total_chars: count of all CJK ideographs (excluding punctuation)
      - unique_count: number of distinct CJK ideographs
      - unique_chars: sorted list of unique CJK ideographs
      - frequency: dict mapping each unique char to its count, sorted desc
      - frequency_rows: normalized row data for model-backed tables
    """
    chars = extract_cjk_characters(text)
    freq = Counter(chars)
    frequency = _sorted_frequency(freq)

    hsk_data = _import_hsk_data()

    return {
        "total_chars": len(chars),
        "unique_count": len(freq),
        "unique_chars": sorted(freq.keys()),
        "frequency": frequency,
        "counts_by_item": dict(frequency),
        "frequency_rows": _build_frequency_rows(
            frequency,
            lambda item: hsk_data.HSK_CHAR_TO_LEVEL.get(item, "—"),
        ),
    }


class PkusegSegmenter:
    """Lazy wrapper around pkuseg so character mode has no hard dependency."""

    def __init__(self):
        self._segmenter = None

    def _get_segmenter(self):
        if self._segmenter is None:
            try:
                from calibre_plugins.chinese_character_analyzer.runtime_manager import (
                    WordRuntimeError, ensure_word_runtime,
                )

                ensure_word_runtime(parent=None, allow_download=False)
            except WordRuntimeError as e:
                raise SegmentationError(str(e)) from e

            try:
                import pkuseg
            except ImportError as e:
                raise SegmentationError(
                    "Word mode runtime is installed, but 'pkuseg' could not be imported."
                ) from e

            try:
                self._segmenter = pkuseg.pkuseg()
            except Exception as e:
                raise SegmentationError(
                    "Could not initialize pkuseg for word segmentation."
                ) from e

        return self._segmenter

    def segment(self, text):
        return self._get_segmenter().cut(text)


_DEFAULT_WORD_SEGMENTER = None


def get_default_word_segmenter():
    global _DEFAULT_WORD_SEGMENTER
    if _DEFAULT_WORD_SEGMENTER is None:
        _DEFAULT_WORD_SEGMENTER = PkusegSegmenter()
    return _DEFAULT_WORD_SEGMENTER


def _normalize_analysis_token(token):
    token = token.strip()
    if not token:
        return None
    for char in token:
        if is_cjk_ideograph(char):
            return token
    return None


def filter_word_tokens(tokens):
    """
    Normalize raw segmented tokens down to analysis tokens.

    Rules:
      - drop empty/whitespace tokens
      - drop tokens that do not contain CJK ideographs
    """
    filtered = []
    for token in tokens:
        normalized = _normalize_analysis_token(token)
        if normalized is not None:
            filtered.append(normalized)
    return filtered


def extract_cjk_words(text, segmenter=None):
    """Return segmented word tokens from text according to the shared filter."""
    if segmenter is None:
        segmenter = get_default_word_segmenter()
    return filter_word_tokens(segmenter.segment(text))


def _length_bucket_label(token):
    length = len(token)
    if length >= 4:
        return "4+"
    return str(length)


def _build_word_analysis(words):
    freq = Counter(words)
    frequency = _sorted_frequency(freq)
    unique_words = sorted(freq.keys())

    hsk_data = _import_hsk_data()
    coverage = hsk_data.hsk_word_coverage(unique_words)
    hsk_groups = normalize_coverage_payload(coverage, "words")
    frequency_rows = _build_frequency_rows(
        frequency,
        lambda item: hsk_data.HSK_WORD_TO_LEVEL.get(item, "—"),
    )

    return {
        "total_words": len(words),
        "unique_count": len(freq),
        "unique_words": unique_words,
        "frequency": frequency,
        "counts_by_item": _counts_from_rows(frequency_rows),
        "frequency_rows": frequency_rows,
        "length_buckets": _build_length_buckets(unique_words),
        "hsk_word_coverage": hsk_groups,
        "hsk_groups": hsk_groups,
        "summary": {
            "total_words": len(words),
            "unique_count": len(freq),
            "avg_word_length": _average_weighted_word_length(frequency_rows, len(words)),
        },
    }


def hydrate_cached_word_analysis(payload):
    """Restore in-memory convenience fields from a cached word-analysis payload."""
    frequency_rows = list(payload["frequency_rows"])
    frequency = _counts_from_rows(frequency_rows)
    unique_words = sorted(frequency.keys())
    summary = dict(payload.get("summary", {}))

    stats = {
        "total_words": summary.get("total_words", 0),
        "unique_count": summary.get("unique_count", len(frequency_rows)),
        "unique_words": unique_words,
        "frequency": frequency,
        "counts_by_item": frequency,
        "frequency_rows": frequency_rows,
        "length_buckets": payload["length_buckets"],
        "hsk_word_coverage": payload["hsk_groups"],
        "hsk_groups": payload["hsk_groups"],
        "summary": {
            "total_words": summary.get("total_words", 0),
            "unique_count": summary.get("unique_count", len(frequency_rows)),
            "avg_word_length": summary.get(
                "avg_word_length",
                _average_weighted_word_length(frequency_rows, summary.get("total_words", 0)),
            ),
        },
    }
    return stats


def analyze_words(text, segmenter=None, progress_callback=None):
    """
    Analyze a text string in word mode and return a dict with:
      - total_words: total number of retained segmented words
      - unique_count: number of distinct words
      - unique_words: sorted list of unique words
      - frequency: dict mapping each unique word to its count, sorted desc
      - frequency_rows: normalized row data for model-backed tables
      - length_buckets: dict of unique-word counts by token length bucket
      - hsk_word_coverage: HSK coverage details for the unique words
    """
    if segmenter is None:
        segmenter = get_default_word_segmenter()

    if progress_callback is not None:
        progress_callback("segmenting")
    words = extract_cjk_words(text, segmenter)

    if progress_callback is not None:
        progress_callback("building_stats")
    return _build_word_analysis(words)


def analyze_chinese(text):
    """Backward-compatible alias for character analysis."""
    return analyze_characters(text)
