import importlib
import pathlib
import sys
import types
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analyzer


def load_anki_connect():
    calibre_plugins_module = types.ModuleType("calibre_plugins")
    plugin_module = types.ModuleType("calibre_plugins.chinese_character_analyzer")
    plugin_module.__path__ = []

    sys.modules["calibre_plugins"] = calibre_plugins_module
    sys.modules["calibre_plugins.chinese_character_analyzer"] = plugin_module
    sys.modules["calibre_plugins.chinese_character_analyzer.analyzer"] = analyzer

    sys.modules.pop("anki_connect", None)
    return importlib.import_module("anki_connect")


class AnkiConnectTests(unittest.TestCase):
    def setUp(self):
        self.anki_connect = load_anki_connect()

    def tearDown(self):
        for name in (
            "anki_connect",
            "calibre_plugins",
            "calibre_plugins.chinese_character_analyzer",
            "calibre_plugins.chinese_character_analyzer.analyzer",
        ):
            sys.modules.pop(name, None)

    def test_get_all_field_names_returns_stable_empty_tuple(self):
        with mock.patch.object(self.anki_connect, "find_notes", return_value=[]):
            field_names, sample_notes, total_count = self.anki_connect.get_all_field_names(
                ["Default"]
            )

        self.assertEqual(field_names, [])
        self.assertEqual(sample_notes, [])
        self.assertEqual(total_count, 0)

    def test_get_all_field_names_preserves_field_order_and_total_count(self):
        sample_notes = [
            {
                "fields": {
                    "English": {"order": 1, "value": "hello"},
                    "Hanzi": {"order": 0, "value": "<b>你好</b>"},
                }
            },
            {
                "fields": {
                    "Pinyin": {"order": 2, "value": "ni hao"},
                    "English": {"order": 1, "value": "greeting"},
                }
            },
        ]

        with mock.patch.object(
            self.anki_connect, "find_notes", return_value=[11, 12, 13]
        ), mock.patch.object(
            self.anki_connect, "notes_info", return_value=sample_notes
        ):
            field_names, simplified_notes, total_count = self.anki_connect.get_all_field_names(
                ["Default"]
            )

        self.assertEqual(field_names, ["Hanzi", "English", "Pinyin"])
        self.assertEqual(
            simplified_notes,
            [
                {"fields": {"English": "hello", "Hanzi": "你好"}},
                {"fields": {"Pinyin": "ni hao", "English": "greeting"}},
            ],
        )
        self.assertEqual(total_count, 3)


if __name__ == "__main__":
    unittest.main()
