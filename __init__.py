"""
Chinese Character Analyzer — Calibre Plugin
Analyzes Chinese books and displays character and word statistics,
including HSK coverage and optional Anki comparison.
"""

from calibre.customize import InterfaceActionBase


class ChineseCharacterAnalyzerPlugin(InterfaceActionBase):
    name = "Chinese Character Analyzer"
    description = "Analyze Chinese books by character or word, with HSK coverage and Anki comparison."
    supported_platforms = ["windows", "osx", "linux"]
    author = "CaoCao"
    version = (1, 2, 1)
    minimum_calibre_version = (5, 0, 0)
    actual_plugin = "calibre_plugins.chinese_character_analyzer.ui:ChineseAnalyzerAction"

    def is_customizable(self):
        return False
