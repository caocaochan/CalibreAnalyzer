import importlib
import pathlib
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def install_qt_stubs():
    qt_module = types.ModuleType("qt")
    qt_core = types.ModuleType("qt.core")

    class DummyBase:
        def __init__(self, *args, **kwargs):
            pass

    class QModelIndex:
        def isValid(self):
            return False

    class QFileDialog:
        @staticmethod
        def getSaveFileName(*args, **kwargs):
            return "", ""

    def pyqtSignal(*args, **kwargs):
        return object()

    qt_core.QAbstractItemView = DummyBase
    qt_core.QAbstractTableModel = DummyBase
    qt_core.QApplication = DummyBase
    qt_core.QComboBox = DummyBase
    qt_core.QDialog = DummyBase
    qt_core.QFileDialog = QFileDialog
    qt_core.QFont = DummyBase
    qt_core.QFrame = DummyBase
    qt_core.QGroupBox = DummyBase
    qt_core.QHBoxLayout = DummyBase
    qt_core.QHeaderView = DummyBase
    qt_core.QLabel = DummyBase
    qt_core.QLineEdit = DummyBase
    qt_core.QListWidget = DummyBase
    qt_core.QListWidgetItem = DummyBase
    qt_core.QModelIndex = QModelIndex
    qt_core.QObject = DummyBase
    qt_core.QProgressBar = DummyBase
    qt_core.QPushButton = DummyBase
    qt_core.QScrollArea = DummyBase
    qt_core.QSize = DummyBase
    qt_core.QSortFilterProxyModel = DummyBase
    qt_core.QTableView = DummyBase
    qt_core.QTabWidget = DummyBase
    qt_core.QTextEdit = DummyBase
    qt_core.QThread = DummyBase
    qt_core.QVBoxLayout = DummyBase
    qt_core.QWidget = DummyBase
    qt_core.Qt = types.SimpleNamespace(
        ItemDataRole=types.SimpleNamespace(
            DisplayRole=0,
            TextAlignmentRole=1,
            FontRole=2,
        ),
        Orientation=types.SimpleNamespace(Horizontal=0),
        AlignmentFlag=types.SimpleNamespace(
            AlignLeft=0,
            AlignVCenter=0,
        ),
    )
    qt_core.pyqtSignal = pyqtSignal

    sys.modules["qt"] = qt_module
    sys.modules["qt.core"] = qt_core


def install_calibre_gui_stubs():
    calibre_module = types.ModuleType("calibre")
    gui2_module = types.ModuleType("calibre.gui2")
    gui2_module.error_dialog = mock.Mock()
    gui2_module.info_dialog = mock.Mock()

    sys.modules["calibre"] = calibre_module
    sys.modules["calibre.gui2"] = gui2_module

    return gui2_module


def load_dialog_module():
    install_qt_stubs()
    gui2_module = install_calibre_gui_stubs()
    sys.modules.pop("dialog", None)
    return importlib.import_module("dialog"), gui2_module


class DialogLogicTests(unittest.TestCase):
    def setUp(self):
        self.dialog, self.gui2 = load_dialog_module()

    def tearDown(self):
        for name in ("dialog", "qt", "qt.core", "calibre", "calibre.gui2"):
            sys.modules.pop(name, None)

    def test_export_guard_blocks_word_mode_until_ready(self):
        dlg = self.dialog.AnalysisDialog.__new__(self.dialog.AnalysisDialog)
        dlg.mode = "word"
        dlg.word_stats = None

        with mock.patch.object(
            self.dialog.QFileDialog, "getSaveFileName", return_value=("ignored.csv", "CSV")
        ) as chooser:
            dlg._export_csv()

        chooser.assert_not_called()
        self.gui2.error_dialog.assert_called_once()

    def test_export_writes_csv_when_word_stats_exist(self):
        dlg = self.dialog.AnalysisDialog.__new__(self.dialog.AnalysisDialog)
        dlg.mode = "word"
        dlg.word_stats = {
            "unique_count": 1,
            "frequency_rows": [
                {"rank": 1, "item": "中文", "count": 2, "length": 2},
            ],
        }
        dlg.book_title = "sample"
        dlg.character_stats = {"frequency_rows": []}
        dlg._display_hsk_level = lambda _item: "HSK 1"

        with tempfile.TemporaryDirectory() as tmpdir:
            target = pathlib.Path(tmpdir) / "export.csv"
            with mock.patch.object(
                self.dialog.QFileDialog,
                "getSaveFileName",
                return_value=(str(target), "CSV"),
            ):
                dlg._export_csv()

            contents = target.read_text(encoding="utf-8-sig")

        self.assertIn("Rank,Word,Count,Length,HSK Level", contents)
        self.assertIn("1,中文,2,2,HSK 1", contents)
        self.gui2.error_dialog.assert_not_called()
        self.gui2.info_dialog.assert_called_once()


if __name__ == "__main__":
    unittest.main()
