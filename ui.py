"""
UI action that adds a toolbar button and triggers the analysis dialog.
"""

from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import error_dialog

# get_icons is injected by calibre's plugin loader for zipped plugins
try:
    load_translations()
except NameError:
    pass

try:
    get_icons
except NameError:
    def get_icons(name, plugin_name=None):
        from qt.core import QIcon
        return QIcon()


class ChineseAnalyzerAction(InterfaceAction):
    name = "Chinese Character Analyzer"
    action_spec = ("Chinese Character Analyzer", None, "Analyze Chinese text in a book by character or word", None)

    def genesis(self):
        icon = get_icons("images/icon.png", "Chinese Character Analyzer")
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.run_analysis)

    def run_analysis(self):
        rows = self.gui.current_view().selectionModel().selectedRows()
        if not rows:
            return error_dialog(
                self.gui,
                "No book selected",
                "Please select a book to analyze.",
                show=True,
            )

        book_id = self.gui.library_view.model().id(rows[0])
        db = self.gui.current_db.new_api

        # Try to get text from available formats (prefer EPUB, then TXT, then others)
        fmts = db.formats(book_id)
        if not fmts:
            fmts = ()
        # formats() returns a tuple of uppercase format strings like ('EPUB', 'TXT')
        available = set(fmts)
        text = None

        preferred_order = ["EPUB", "TXT", "AZW3", "MOBI", "HTML", "HTM", "HTMLZ"]
        chosen_fmt = None
        for fmt in preferred_order:
            if fmt in available:
                chosen_fmt = fmt
                break

        if chosen_fmt is None:
            # Fall back to first available format
            if available:
                chosen_fmt = list(available)[0]
            else:
                return error_dialog(
                    self.gui,
                    "No formats",
                    "This book has no downloadable formats.",
                    show=True,
                )

        text = self._extract_text(db, book_id, chosen_fmt)

        if not text or not text.strip():
            return error_dialog(
                self.gui,
                "No text extracted",
                f"Could not extract text from the {chosen_fmt} format of this book.",
                show=True,
            )

        title = db.field_for("title", book_id)
        authors = db.field_for("authors", book_id)
        author_str = ", ".join(authors) if authors else "Unknown"

        from calibre_plugins.chinese_character_analyzer.analysis_cache import build_analysis_key
        from calibre_plugins.chinese_character_analyzer.analyzer import analyze_characters
        stats = analyze_characters(text)
        analysis_key = build_analysis_key(text, chosen_fmt)

        from calibre_plugins.chinese_character_analyzer.dialog import AnalysisDialog
        dlg = AnalysisDialog(self.gui, title, author_str, chosen_fmt, text, stats, analysis_key=analysis_key)
        dlg.exec()

    def _decode_text_bytes(self, raw):
        for encoding in ("utf-8", "gb18030", "gbk", "gb2312", "big5"):
            try:
                return raw.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        return raw.decode("utf-8", errors="replace")

    def _extract_text(self, db, book_id, fmt):
        """Extract plain text from a book format."""
        import os
        import tempfile

        raw = db.format(book_id, fmt)
        if raw is None:
            return None

        # Write to a temp file so we can use calibre's conversion pipeline
        suffix = "." + fmt.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name

        try:
            if fmt == "TXT":
                return self._decode_text_bytes(raw)

            elif fmt in ("EPUB", "AZW3", "MOBI", "HTMLZ"):
                return self._extract_via_calibre(tmp_path, fmt)

            elif fmt in ("HTML", "HTM"):
                from calibre.utils.cleantext import clean_ascii_chars
                from calibre.ebooks.BeautifulSoup import BeautifulSoup
                html = self._decode_text_bytes(raw)
                soup = BeautifulSoup(html)
                return soup.get_text()

            else:
                return self._extract_via_calibre(tmp_path, fmt)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _extract_via_calibre(self, path, fmt):
        """Use calibre's conversion infrastructure to extract text."""
        import os
        import tempfile

        try:
            from calibre.ebooks.conversion.plumber import Plumber
            from calibre.utils.logging import Log

            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as out:
                out_path = out.name

            log = Log()
            plumber = Plumber(path, out_path, log)
            plumber.run()

            with open(out_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception:
            # Fallback: try to just open the file and strip HTML
            try:
                from calibre.ebooks.BeautifulSoup import BeautifulSoup
                from zipfile import ZipFile

                if fmt == "EPUB":
                    text_parts = []
                    with ZipFile(path, "r") as zf:
                        for name in zf.namelist():
                            if name.endswith((".xhtml", ".html", ".htm", ".xml")):
                                data = zf.read(name).decode("utf-8", errors="replace")
                                soup = BeautifulSoup(data)
                                text_parts.append(soup.get_text())
                    return "\n".join(text_parts)
            except Exception:
                pass
            return None
        finally:
            try:
                os.unlink(out_path)
            except (OSError, UnboundLocalError):
                pass
