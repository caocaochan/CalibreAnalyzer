import importlib
import pathlib
import sys
import types
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def install_ui_stubs():
    calibre_module = types.ModuleType("calibre")
    gui2_module = types.ModuleType("calibre.gui2")
    actions_module = types.ModuleType("calibre.gui2.actions")
    utils_module = types.ModuleType("calibre.utils")
    cleantext_module = types.ModuleType("calibre.utils.cleantext")
    ebooks_module = types.ModuleType("calibre.ebooks")
    bs_module = types.ModuleType("calibre.ebooks.BeautifulSoup")

    class InterfaceAction:
        def __init__(self, *args, **kwargs):
            pass

    class BeautifulSoup:
        def __init__(self, html):
            self.html = html

        def get_text(self):
            return self.html.replace("<html>", "").replace("</html>", "").replace("<body>", "").replace("</body>", "")

    actions_module.InterfaceAction = InterfaceAction
    gui2_module.error_dialog = lambda *args, **kwargs: None
    cleantext_module.clean_ascii_chars = lambda text: text
    bs_module.BeautifulSoup = BeautifulSoup

    sys.modules["calibre"] = calibre_module
    sys.modules["calibre.gui2"] = gui2_module
    sys.modules["calibre.gui2.actions"] = actions_module
    sys.modules["calibre.utils"] = utils_module
    sys.modules["calibre.utils.cleantext"] = cleantext_module
    sys.modules["calibre.ebooks"] = ebooks_module
    sys.modules["calibre.ebooks.BeautifulSoup"] = bs_module


def load_ui_module():
    install_ui_stubs()
    sys.modules.pop("ui", None)
    return importlib.import_module("ui")


class FakeDb:
    def __init__(self, payload):
        self.payload = payload

    def format(self, _book_id, _fmt):
        return self.payload


class UITextExtractionTests(unittest.TestCase):
    def setUp(self):
        self.ui = load_ui_module()
        self.action = self.ui.ChineseAnalyzerAction.__new__(self.ui.ChineseAnalyzerAction)

    def tearDown(self):
        for name in (
            "ui",
            "calibre",
            "calibre.gui2",
            "calibre.gui2.actions",
            "calibre.utils",
            "calibre.utils.cleantext",
            "calibre.ebooks",
            "calibre.ebooks.BeautifulSoup",
        ):
            sys.modules.pop(name, None)

    def test_decode_text_bytes_handles_gb18030(self):
        raw = "中文内容".encode("gb18030")
        self.assertEqual(self.action._decode_text_bytes(raw), "中文内容")

    def test_decode_text_bytes_falls_back_safely(self):
        raw = b"\xff\xfe\xfa"
        self.assertEqual(self.action._decode_text_bytes(raw), raw.decode("utf-8", errors="replace"))

    def test_extract_text_decodes_html_using_shared_helper(self):
        html = "<html><body>中文页面</body></html>".encode("gbk")
        text = self.action._extract_text(FakeDb(html), 1, "HTML")
        self.assertIn("中文页面", text)


if __name__ == "__main__":
    unittest.main()
