import pathlib
import sys
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analysis_cache
import analyzer
import hsk_data


class FakeSegmenter:
    def __init__(self, tokens):
        self._tokens = list(tokens)

    def segment(self, _text):
        return list(self._tokens)


class AnalysisCacheTests(unittest.TestCase):
    def test_build_cache_key_invalidates_on_inputs(self):
        analysis_key = analysis_cache.build_analysis_key("你好世界", "EPUB")
        base = analysis_cache.build_cache_key(analysis_key, "EPUB", "runtime-a")

        self.assertNotEqual(
            base,
            analysis_cache.build_cache_key(analysis_key, "TXT", "runtime-a"),
        )
        self.assertNotEqual(
            base,
            analysis_cache.build_cache_key(analysis_key, "EPUB", "runtime-b"),
        )
        self.assertNotEqual(
            base,
            analysis_cache.build_cache_key(analysis_key, "EPUB", "runtime-a", schema_version=99),
        )

    def test_cache_round_trip_and_hydration(self):
        tokens = [
            "今天", "天气", "很好", "今天", "我们", "一起", "学习", "中文",
            "学习", "中文", "。", "abc", "图书馆",
        ]
        stats = analyzer.analyze_words("ignored", segmenter=FakeSegmenter(tokens))

        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_key = analysis_cache.build_analysis_key("示例文本", "EPUB")
            saved = analysis_cache.save_word_analysis(
                analysis_key,
                "EPUB",
                "runtime-1",
                stats,
                base_dir=tmpdir,
            )
            loaded = analysis_cache.load_word_analysis(
                analysis_key,
                "EPUB",
                "runtime-1",
                base_dir=tmpdir,
            )

        self.assertIsNotNone(loaded)
        self.assertEqual(saved["summary"], loaded["summary"])
        self.assertEqual(saved["frequency_rows"], loaded["frequency_rows"])
        self.assertEqual(saved["length_buckets"], loaded["length_buckets"])

        hydrated = analyzer.hydrate_cached_word_analysis(loaded)
        self.assertEqual(stats["total_words"], hydrated["total_words"])
        self.assertEqual(stats["unique_count"], hydrated["unique_count"])
        self.assertEqual(stats["frequency_rows"], hydrated["frequency_rows"])
        self.assertEqual(stats["length_buckets"], hydrated["length_buckets"])
        self.assertEqual(stats["hsk_groups"], hydrated["hsk_groups"])

    def test_cached_and_uncached_word_analysis_match(self):
        tokens = (
            ["今天", "天气", "很好", "我们", "一起", "去", "图书馆", "学习", "中文"]
            + ["今天", "学习", "中文", "晚上", "回家", "做饭", "睡觉"]
        ) * 40
        uncached = analyzer.analyze_words("ignored", segmenter=FakeSegmenter(tokens))

        with tempfile.TemporaryDirectory() as tmpdir:
            analysis_key = analysis_cache.build_analysis_key("长篇小说片段", "EPUB")
            analysis_cache.save_word_analysis(
                analysis_key,
                "EPUB",
                "runtime-1",
                uncached,
                base_dir=tmpdir,
            )
            cached = analysis_cache.load_word_analysis(
                analysis_key,
                "EPUB",
                "runtime-1",
                base_dir=tmpdir,
            )

        restored = analyzer.hydrate_cached_word_analysis(cached)
        self.assertEqual(uncached["total_words"], restored["total_words"])
        self.assertEqual(uncached["unique_count"], restored["unique_count"])
        self.assertEqual(uncached["frequency_rows"], restored["frequency_rows"])
        self.assertEqual(uncached["length_buckets"], restored["length_buckets"])
        self.assertEqual(uncached["hsk_groups"], restored["hsk_groups"])
        self.assertEqual(uncached["unique_words"], restored["unique_words"])

    def test_character_reverse_lookup_map(self):
        self.assertEqual(hsk_data.HSK_CHAR_TO_LEVEL["一"], "1")
        self.assertEqual(hsk_data.HSK_CHAR_TO_LEVEL["黑"], "2")

    def test_filter_word_tokens_keeps_only_tokens_with_cjk(self):
        tokens = ["  ", "。", "abc", "今天", "abc中", "123", " 图书馆 "]
        self.assertEqual(
            analyzer.filter_word_tokens(tokens),
            ["今天", "abc中", "图书馆"],
        )

    def test_create_word_segmenter_selects_backend_class(self):
        self.assertIsInstance(
            analyzer.create_word_segmenter("jieba"),
            analyzer.JiebaSegmenter,
        )
        self.assertIsInstance(
            analyzer.create_word_segmenter("pkuseg"),
            analyzer.PkusegSegmenter,
        )

    def test_default_word_segmenter_tracks_configured_backend(self):
        analyzer._DEFAULT_WORD_SEGMENTER = None
        analyzer._DEFAULT_WORD_SEGMENTER_BACKEND = None

        with mock.patch.object(analyzer, "_get_word_backend_name", return_value="jieba"):
            segmenter = analyzer.get_default_word_segmenter()
            self.assertIsInstance(segmenter, analyzer.JiebaSegmenter)

        analyzer._DEFAULT_WORD_SEGMENTER = None
        analyzer._DEFAULT_WORD_SEGMENTER_BACKEND = None

        with mock.patch.object(analyzer, "_get_word_backend_name", return_value="pkuseg"):
            segmenter = analyzer.get_default_word_segmenter()
            self.assertIsInstance(segmenter, analyzer.PkusegSegmenter)

    def test_jieba_segmenter_produces_valid_word_stats(self):
        text = "我们一起学习中文123abc。今天也去图书馆。"
        stats = analyzer.analyze_words(
            text,
            segmenter=analyzer.JiebaSegmenter(),
        )

        self.assertGreater(stats["total_words"], 0)
        self.assertGreater(stats["unique_count"], 0)
        self.assertTrue(stats["unique_words"])
        self.assertTrue(
            all(analyzer.contains_cjk_ideograph(token) for token in stats["unique_words"])
        )


if __name__ == "__main__":
    unittest.main()
