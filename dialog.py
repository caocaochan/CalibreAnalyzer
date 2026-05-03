"""
Analysis results dialog — displays Chinese character and word statistics,
HSK coverage, and optional Anki deck comparison for known-unit analysis.
"""

from qt.core import (
    QAbstractItemView, QAbstractTableModel, QApplication, QComboBox, QDialog,
    QFileDialog, QFont, QFrame, QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QModelIndex, QObject,
    QProgressBar, QPushButton, QScrollArea, QSize, QSortFilterProxyModel,
    QTableView, QTabWidget, QTextEdit, QThread, Qt, QVBoxLayout, QWidget,
    pyqtSignal,
)


class _AnalysisRowsTableModel(QAbstractTableModel):
    def __init__(self, rows, columns, item_font_size, parent=None):
        super().__init__(parent)
        self._rows = rows
        self._columns = columns
        self._item_font_size = item_font_size

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._columns)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._columns[section]["title"]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = self._rows[index.row()]
        column = self._columns[index.column()]
        key = column["key"]
        value = row.get(key, "")

        if role == Qt.ItemDataRole.DisplayRole:
            if key in ("rank", "length"):
                return str(value)
            if key == "count":
                return f"{value:,}"
            if key == "hsk_level":
                return f"HSK {value}" if value != "—" else "—"
            return value

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(column.get("alignment", Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))

        if role == Qt.ItemDataRole.FontRole:
            if key == "item":
                return QFont("Microsoft YaHei", self._item_font_size)
            if key == "hsk_level":
                return QFont("Microsoft YaHei", 9)
        return None

    def row_item(self, row_index):
        return self._rows[row_index]["item"]


class _ContainsFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_text = ""

    def set_filter_text(self, text):
        self._filter_text = text.strip()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self._filter_text:
            return True
        model = self.sourceModel()
        return self._filter_text in model.row_item(source_row)


class _WordAnalysisWorker(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, analysis_key, book_text, book_format):
        super().__init__()
        self.analysis_key = analysis_key
        self.book_text = book_text
        self.book_format = book_format

    def run(self):
        try:
            from calibre_plugins.chinese_character_analyzer.analysis_cache import (
                load_word_analysis, save_word_analysis,
            )
            from calibre_plugins.chinese_character_analyzer.analyzer import (
                PkusegSegmenter, analyze_words, hydrate_cached_word_analysis,
            )
            from calibre_plugins.chinese_character_analyzer.runtime_manager import RUNTIME_VERSION

            self.progress.emit("cache_lookup")
            cached = load_word_analysis(self.analysis_key, self.book_format, RUNTIME_VERSION)
            if cached is not None:
                self.progress.emit("ready")
                self.finished.emit({
                    "cache_hit": True,
                    "stats": hydrate_cached_word_analysis(cached),
                })
                return

            segmenter = PkusegSegmenter()
            stats = analyze_words(
                self.book_text,
                segmenter=segmenter,
                progress_callback=self.progress.emit,
            )
            save_word_analysis(self.analysis_key, self.book_format, RUNTIME_VERSION, stats)
            self.progress.emit("ready")
            self.finished.emit({
                "cache_hit": False,
                "stats": stats,
            })
        except Exception as e:
            self.failed.emit(str(e))


class AnalysisDialog(QDialog):
    _WORD_STATUS_TEXT = {
        "cache_lookup": "Checking cached word analysis…",
        "segmenting": "Segmenting text into words…",
        "building_stats": "Building frequency and coverage stats…",
        "ready": "Word analysis ready.",
    }

    def __init__(self, parent, title, author, fmt, text, character_stats, analysis_key=None):
        super().__init__(parent)
        from calibre_plugins.chinese_character_analyzer.analysis_cache import build_analysis_key

        self.book_title = title
        self.book_text = text
        self.book_format = fmt
        self.analysis_key = analysis_key or build_analysis_key(text, fmt)
        self.character_stats = character_stats
        self.word_stats = None
        self.mode = "character"
        self.tabs = None
        self._anki_data = None
        self._tab_contexts = {}
        self._tab_role_order = []
        self._word_overview_label = None
        self._word_analysis_thread = None
        self._word_analysis_worker = None
        self._word_analysis_active = False
        self._word_analysis_status = ""
        self._word_cache_hit = False
        self._mode_hsk_text_cache = {}

        from calibre_plugins.chinese_character_analyzer.analyzer import normalize_coverage_payload
        from calibre_plugins.chinese_character_analyzer.hsk_data import hsk_coverage

        self.character_hsk = normalize_coverage_payload(
            hsk_coverage(character_stats["unique_chars"]),
            "chars",
        )

        self.setWindowTitle(f"Chinese Text Analysis — {title}")
        self.setMinimumSize(QSize(720, 520))
        self.resize(QSize(1040, 840))

        outer_layout = QVBoxLayout(self)
        outer_layout.setSpacing(0)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer_layout.addWidget(self.content_scroll)

        content = QWidget()
        self.content_scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setSpacing(6)
        layout.setContentsMargins(14, 10, 14, 10)

        header = QLabel(
            f"<span style='font-family: Microsoft YaHei; font-size: 13pt; font-weight: bold;'>{title}</span>"
            f"  <span style='color:gray; font-family: Microsoft YaHei; font-size: 9pt;'>{author} · {fmt}</span>"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        mode_label = QLabel("Analysis mode:")
        mode_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        mode_row.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Character", "character")
        self.mode_combo.addItem("Word", "word")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_row.addWidget(self.mode_combo)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        self.stats_widget = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_widget)
        self.stats_layout.setSpacing(6)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stats_widget)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.tabs.setMinimumHeight(460)
        layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()

        anki_connect_btn = QPushButton("Connect to Anki…")
        anki_connect_btn.setToolTip(
            "Connect to a running Anki instance via AnkiConnect to compare your known words or characters"
        )
        anki_connect_btn.clicked.connect(self._connect_anki)
        btn_layout.addWidget(anki_connect_btn)

        anki_btn = QPushButton("Import .apkg File…")
        anki_btn.setToolTip("Import an .apkg file to compare your known words or characters against this book")
        anki_btn.clicked.connect(self._import_anki)
        btn_layout.addWidget(anki_btn)

        btn_layout.addStretch()

        export_btn = QPushButton("Export to CSV…")
        export_btn.clicked.connect(self._export_csv)
        btn_layout.addWidget(export_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self._refresh_mode_ui()

    # ── Mode switching ──────────────────────────────────────────────────

    def _on_mode_changed(self, index):
        mode = self.mode_combo.itemData(index)
        if mode == self.mode:
            return

        if mode == "word" and not self._ensure_word_analysis_started():
            self.mode_combo.blockSignals(True)
            self.mode_combo.setCurrentIndex(self.mode_combo.findData(self.mode))
            self.mode_combo.blockSignals(False)
            return

        self.mode = mode
        self._refresh_mode_ui()

    def _ensure_word_analysis_started(self):
        if self.word_stats is not None or self._word_analysis_active:
            return True

        from calibre_plugins.chinese_character_analyzer.runtime_manager import (
            WordRuntimeCancelled, WordRuntimeError, current_platform_key,
            ensure_word_runtime, get_runtime_asset, runtime_download_available,
            runtime_is_installed,
        )

        if not runtime_is_installed():
            asset = get_runtime_asset()
            if asset is None:
                from calibre.gui2 import error_dialog
                error_dialog(
                    self,
                    "Word Mode Unavailable",
                    "Word mode is not available for this Calibre runtime yet "
                    f"({current_platform_key()}).",
                    show=True,
                )
                return False

            if not runtime_download_available():
                from calibre.gui2 import error_dialog
                error_dialog(
                    self,
                    "Word Mode Unavailable",
                    "Word mode runtime assets are missing from this build.",
                    show=True,
                )
                return False

            if not self._confirm_word_runtime_download(asset, current_platform_key()):
                return False

        try:
            ensure_word_runtime(parent=self, allow_download=True)
        except WordRuntimeCancelled:
            return False
        except WordRuntimeError as e:
            from calibre.gui2 import error_dialog
            error_dialog(self, "Word Mode Unavailable", str(e), show=True)
            return False

        self._start_word_analysis_worker()
        return True

    def _start_word_analysis_worker(self):
        if self._word_analysis_active:
            return

        self._word_analysis_status = "cache_lookup"
        self._word_analysis_active = True
        self._word_analysis_thread = QThread(self)
        self._word_analysis_worker = _WordAnalysisWorker(
            self.analysis_key,
            self.book_text,
            self.book_format,
        )
        self._word_analysis_worker.moveToThread(self._word_analysis_thread)
        self._word_analysis_thread.started.connect(self._word_analysis_worker.run)
        self._word_analysis_worker.progress.connect(self._on_word_analysis_progress)
        self._word_analysis_worker.finished.connect(self._on_word_analysis_finished)
        self._word_analysis_worker.failed.connect(self._on_word_analysis_failed)
        self._word_analysis_worker.finished.connect(self._word_analysis_thread.quit)
        self._word_analysis_worker.failed.connect(self._word_analysis_thread.quit)
        self._word_analysis_thread.finished.connect(self._word_analysis_worker.deleteLater)
        self._word_analysis_thread.finished.connect(self._on_word_analysis_thread_finished)
        self._word_analysis_thread.start()

    def _on_word_analysis_progress(self, status):
        self._word_analysis_status = status
        self._refresh_stats_panel()
        self._update_word_overview_message()

    def _on_word_analysis_finished(self, result):
        self._word_analysis_active = False
        self._word_cache_hit = result["cache_hit"]
        self.word_stats = result["stats"]
        self._word_analysis_status = "ready"
        self._mode_hsk_text_cache.pop("word", None)
        if self.mode == "word":
            self._refresh_stats_panel()
            self._update_tab_labels()
            self._update_word_overview_message()
            self._ensure_current_tab_built()

    def _on_word_analysis_failed(self, message):
        self._word_analysis_active = False
        self._word_analysis_status = ""
        from calibre.gui2 import error_dialog
        error_dialog(
            self,
            "Word Analysis Error",
            f"Could not analyze this book in word mode:\n{message}",
            show=True,
        )

        self.mode_combo.blockSignals(True)
        self.mode_combo.setCurrentIndex(self.mode_combo.findData("character"))
        self.mode_combo.blockSignals(False)
        self.mode = "character"
        self._refresh_mode_ui()

    def _on_word_analysis_thread_finished(self):
        self._word_analysis_thread = None
        self._word_analysis_worker = None

    def _confirm_word_runtime_download(self, asset, platform_key):
        from calibre.gui2 import question_dialog

        size = asset.get("size")
        if size:
            size_text = f"{size / (1024 * 1024):.1f} MB"
        else:
            size_text = "a pinned runtime bundle"

        packages = ", ".join(asset.get("packages", ()))
        message = (
            "<p>Word mode needs a one-time setup before it can segment text.</p>"
            f"<p><b>Runtime:</b> {platform_key}<br>"
            f"<b>Installed payload:</b> {size_text}</p>"
        )
        if packages:
            message += f"<p><b>Includes:</b> {packages}</p>"
        message += (
            "<p>The bundled runtime will be extracted into your Calibre profile, "
            "and future word analyses will run offline.</p>"
            "<p>Set it up now?</p>"
        )
        return question_dialog(self, "Install Word Mode", message)

    def _refresh_mode_ui(self):
        self._refresh_stats_panel()
        self._setup_tabs()

    def _refresh_stats_panel(self):
        self._clear_layout(self.stats_layout)
        if self.mode == "word" and self.word_stats is None:
            self.stats_layout.addWidget(self._build_loading_frame())
            return
        self._build_stats_panel()

    def _setup_tabs(self):
        self.tabs.blockSignals(True)
        self.tabs.clear()
        self._tab_contexts = {}
        self._tab_role_order = []
        self._word_overview_label = None

        if self.mode == "word":
            self._add_placeholder_tab("overview", "Overview", self._word_status_message())
            self._add_placeholder_tab("frequency", "Frequency", "Open this tab when the word analysis is ready.")
            self._add_placeholder_tab("hsk_detail", "HSK Level Detail", "Open this tab to generate the HSK detail view.")
        else:
            self._add_placeholder_tab("frequency", "Frequency", "Loading frequency table…")
            self._add_placeholder_tab("hsk_detail", "HSK Level Detail", "Loading HSK detail…")

        if self._anki_data is not None:
            self._add_placeholder_tab("anki", "Anki", "Open this tab to compare with your Anki data.")

        self.tabs.blockSignals(False)
        self._update_tab_labels()
        self._ensure_current_tab_built()

    def _add_placeholder_tab(self, role, title, message):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 0)

        label = QLabel(message)
        label.setWordWrap(True)
        label.setStyleSheet("color: gray;")
        layout.addWidget(label)
        layout.addStretch()

        self.tabs.addTab(widget, title)
        self._tab_role_order.append(role)
        self._tab_contexts[role] = {
            "widget": widget,
            "layout": layout,
            "built": role == "overview",
            "message_label": label,
        }
        if role == "overview":
            self._word_overview_label = label

    def _tab_index_for_role(self, role):
        try:
            return self._tab_role_order.index(role)
        except ValueError:
            return -1

    def _update_tab_labels(self):
        stats = self._current_stats()
        for role in self._tab_role_order:
            index = self._tab_index_for_role(role)
            if index < 0:
                continue
            if role == "overview":
                label = "Overview"
            elif role == "frequency":
                if stats is None:
                    label = "Frequency"
                elif self.mode == "word":
                    label = f"Frequency ({stats['unique_count']:,} words)"
                else:
                    label = f"Frequency ({stats['unique_count']:,} chars)"
            elif role == "anki":
                label = self._tab_contexts[role].get("tab_title", "Anki")
            else:
                label = "HSK Level Detail"
            self.tabs.setTabText(index, label)

    def _on_tab_changed(self, index):
        if index >= 0:
            self._ensure_current_tab_built(index)

    def closeEvent(self, event):
        self._shutdown_word_analysis_thread()
        super().closeEvent(event)

    def _ensure_current_tab_built(self, index=None):
        if index is None:
            index = self.tabs.currentIndex()
        if index < 0 or index >= len(self._tab_role_order):
            return

        role = self._tab_role_order[index]
        context = self._tab_contexts[role]
        if context["built"]:
            return

        if self.mode == "word" and self.word_stats is None:
            self._update_word_overview_message()
            return

        if role == "frequency":
            self._build_frequency_tab_content(context)
        elif role == "hsk_detail":
            self._build_hsk_detail_tab_content(context)
        elif role == "anki":
            self._build_anki_tab_content(context)

        context["built"] = True

    def _current_stats(self):
        if self.mode == "word":
            return self.word_stats
        return self.character_stats

    def _current_hsk(self):
        if self.mode == "word":
            return self.word_stats["hsk_groups"]
        return self.character_hsk

    def _current_total_count(self):
        stats = self._current_stats()
        if stats is None:
            return 0
        return stats["total_words"] if self.mode == "word" else stats["total_chars"]

    def _current_unique_items(self):
        stats = self._current_stats()
        if stats is None:
            return []
        return stats["unique_words"] if self.mode == "word" else stats["unique_chars"]

    def _current_counts(self):
        stats = self._current_stats()
        if stats is None:
            return {}
        return stats.get("counts_by_item", stats["frequency"])

    def _unit_label(self):
        return "Words" if self.mode == "word" else "Characters"

    def _unit_singular(self):
        return "Word" if self.mode == "word" else "Character"

    def _word_status_message(self):
        if not self._word_analysis_status:
            return "Preparing word mode…"
        message = self._WORD_STATUS_TEXT.get(self._word_analysis_status, self._word_analysis_status)
        if self._word_analysis_status == "ready" and self._word_cache_hit:
            return f"{message} Loaded from cache."
        return message

    def _update_word_overview_message(self):
        if self._word_overview_label is not None:
            self._word_overview_label.setText(self._word_status_message())

    # ── Top summary + coverage ──────────────────────────────────────────

    def _build_loading_frame(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            "QFrame { background: palette(alternate-base); border-radius: 6px; padding: 10px; }"
        )
        layout = QVBoxLayout(frame)
        layout.setSpacing(6)
        label = QLabel("<b>Word Mode</b>")
        label.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(label)

        status = QLabel(self._word_status_message())
        status.setWordWrap(True)
        status.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(status)
        return frame

    def _build_stats_panel(self):
        stats = self._current_stats()
        cards = QHBoxLayout()
        cards.setSpacing(10)

        total_label = "Total Words" if self.mode == "word" else "Total Characters"
        unique_label = "Unique Words" if self.mode == "word" else "Unique Characters"

        cards.addWidget(self._make_card(total_label, f"{self._current_total_count():,}"))
        cards.addWidget(self._make_card(unique_label, f"{stats['unique_count']:,}"))

        ratio = (stats["unique_count"] / self._current_total_count() * 100) if self._current_total_count() else 0
        cards.addWidget(self._make_card("Unique Ratio", f"{ratio:.1f}%"))

        if self.mode == "word":
            avg_len = stats["summary"]["avg_word_length"]
            cards.addWidget(self._make_card("Avg. Word Length", f"{avg_len:.2f}"))

        self.stats_layout.addLayout(cards)
        self.stats_layout.addWidget(self._build_hsk_frame())

        if self.mode == "word":
            self.stats_layout.addWidget(self._build_word_length_frame(stats["length_buckets"]))

    def _build_hsk_frame(self):
        from calibre_plugins.chinese_character_analyzer.hsk_data import (
            HSK_LEVEL_ORDER, HSK_WORD_LEVEL_ORDER,
        )

        coverage = self._current_hsk()
        level_order = HSK_WORD_LEVEL_ORDER if self.mode == "word" else HSK_LEVEL_ORDER
        title_text = "HSK Vocabulary Coverage" if self.mode == "word" else "HSK 3.0 Coverage"

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            "QFrame { background: palette(alternate-base); border-radius: 6px; padding: 4px; }"
        )
        inner = QVBoxLayout(frame)
        inner.setSpacing(2)
        inner.setContentsMargins(6, 3, 6, 3)

        title = QLabel(f"<b>{title_text}</b>")
        title.setFont(QFont("Microsoft YaHei", 9))
        inner.addWidget(title)

        bar_colors = [
            "#4CAF50", "#66BB6A", "#2196F3", "#42A5F5",
            "#FF9800", "#FFA726", "#E91E63",
        ]

        for i, level in enumerate(level_order):
            info = coverage["per_level"][level]
            cumulative = coverage["cumulative"][level]
            row = QHBoxLayout()
            row.setSpacing(6)

            if level == "1":
                label_text = "HSK 1"
            elif level == "7-9":
                label_text = "HSK 1–9"
            else:
                label_text = f"HSK 1–{level}"
            label = QLabel(label_text)
            label.setFixedWidth(80)
            label.setFont(QFont("Microsoft YaHei", 8, QFont.Weight.Bold))
            row.addWidget(label)

            bar = QProgressBar()
            bar.setRange(0, 1000)
            bar.setValue(int(cumulative["pct"] * 10))
            bar.setTextVisible(False)
            bar.setFixedHeight(12)
            bar.setStyleSheet(
                f"QProgressBar {{ border: 1px solid palette(mid); border-radius: 4px; background: palette(base); }}"
                f"QProgressBar::chunk {{ background: {bar_colors[i]}; border-radius: 3px; }}"
            )
            row.addWidget(bar, stretch=1)

            pct_label = QLabel(f"{cumulative['pct']:5.1f}%  ({cumulative['count']})")
            pct_label.setFixedWidth(126)
            pct_label.setFont(QFont("Microsoft YaHei", 8))
            row.addWidget(pct_label)

            new_label = QLabel(f"+{info['count']}")
            new_label.setFixedWidth(58)
            new_label.setFont(QFont("Microsoft YaHei", 8))
            new_label.setStyleSheet("color: gray;")
            new_label.setToolTip(
                f"This level alone adds {info['count']} {self._unit_label().lower()} ({info['pct']:.1f}%)"
            )
            row.addWidget(new_label)

            inner.addLayout(row)

        other_row = QHBoxLayout()
        other_row.setSpacing(6)
        other_label = QLabel("Other")
        other_label.setFixedWidth(80)
        other_label.setFont(QFont("Microsoft YaHei", 8, QFont.Weight.Bold))
        other_label.setStyleSheet("color: gray;")
        other_row.addWidget(other_label)

        other_bar = QProgressBar()
        other_bar.setRange(0, 1000)
        other_bar.setValue(int(coverage["not_in_hsk_pct"] * 10))
        other_bar.setTextVisible(False)
        other_bar.setFixedHeight(12)
        other_bar.setStyleSheet(
            "QProgressBar { border: 1px solid palette(mid); border-radius: 4px; background: palette(base); }"
            "QProgressBar::chunk { background: #9E9E9E; border-radius: 3px; }"
        )
        other_row.addWidget(other_bar, stretch=1)

        other_pct = QLabel(f"{coverage['not_in_hsk_pct']:5.1f}%  ({coverage['not_in_hsk_count']})")
        other_pct.setFixedWidth(126)
        other_pct.setFont(QFont("Microsoft YaHei", 8))
        other_pct.setStyleSheet("color: gray;")
        other_row.addWidget(other_pct)

        spacer = QLabel("")
        spacer.setFixedWidth(58)
        other_row.addWidget(spacer)
        inner.addLayout(other_row)
        return frame

    def _build_word_length_frame(self, buckets):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            "QFrame { background: palette(alternate-base); border-radius: 6px; padding: 4px; }"
        )
        layout = QVBoxLayout(frame)
        layout.setSpacing(4)
        layout.setContentsMargins(6, 3, 6, 3)

        title = QLabel("<b>Unique Word Lengths</b>")
        title.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(8)
        for bucket in ("1", "2", "3", "4+"):
            info = buckets[bucket]
            row.addWidget(self._make_small_card(
                f"{bucket} char" if bucket != "4+" else "4+ chars",
                f"{info['count']:,}",
                f"{info['pct']:.1f}%",
            ))
        layout.addLayout(row)
        return frame

    # ── Frequency + HSK detail tabs ────────────────────────────────────

    def _frequency_columns(self):
        if self.mode == "word":
            return [
                {"title": "Rank", "key": "rank", "alignment": Qt.AlignmentFlag.AlignCenter},
                {"title": "Word", "key": "item", "alignment": Qt.AlignmentFlag.AlignCenter},
                {"title": "Count", "key": "count", "alignment": Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter},
                {"title": "Length", "key": "length", "alignment": Qt.AlignmentFlag.AlignCenter},
                {"title": "HSK Level", "key": "hsk_level", "alignment": Qt.AlignmentFlag.AlignCenter},
            ]
        return [
            {"title": "Rank", "key": "rank", "alignment": Qt.AlignmentFlag.AlignCenter},
            {"title": "Character", "key": "item", "alignment": Qt.AlignmentFlag.AlignCenter},
            {"title": "Count", "key": "count", "alignment": Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter},
            {"title": "HSK Level", "key": "hsk_level", "alignment": Qt.AlignmentFlag.AlignCenter},
        ]

    def _anki_columns(self):
        if self.mode == "word":
            return [
                {"title": "#", "key": "rank", "alignment": Qt.AlignmentFlag.AlignCenter},
                {"title": "Word", "key": "item", "alignment": Qt.AlignmentFlag.AlignCenter},
                {"title": "Occurrences", "key": "count", "alignment": Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter},
                {"title": "Length", "key": "length", "alignment": Qt.AlignmentFlag.AlignCenter},
                {"title": "HSK Level", "key": "hsk_level", "alignment": Qt.AlignmentFlag.AlignCenter},
            ]
        return [
            {"title": "#", "key": "rank", "alignment": Qt.AlignmentFlag.AlignCenter},
            {"title": "Character", "key": "item", "alignment": Qt.AlignmentFlag.AlignCenter},
            {"title": "Occurrences", "key": "count", "alignment": Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter},
            {"title": "HSK Level", "key": "hsk_level", "alignment": Qt.AlignmentFlag.AlignCenter},
        ]

    def _create_table_view(self, model, proxy=None):
        view = QTableView()
        view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        view.verticalHeader().setVisible(False)
        view.setAlternatingRowColors(True)
        view.setModel(proxy if proxy is not None else model)

        stretch_column = 1
        header = view.horizontalHeader()
        for idx in range(model.columnCount()):
            mode = QHeaderView.ResizeMode.Stretch if idx == stretch_column else QHeaderView.ResizeMode.ResizeToContents
            header.setSectionResizeMode(idx, mode)
        return view

    def _build_frequency_tab_content(self, context):
        self._clear_layout(context["layout"])

        search_layout = QHBoxLayout()
        search_box = QLineEdit()
        search_box.setPlaceholderText(
            "Search words…" if self.mode == "word" else "Search characters…"
        )
        search_layout.addWidget(search_box)
        context["layout"].addLayout(search_layout)

        rows = self._current_stats()["frequency_rows"]
        model = _AnalysisRowsTableModel(rows, self._frequency_columns(), 14 if self.mode == "word" else 16, self)
        proxy = _ContainsFilterProxyModel(self)
        proxy.setSourceModel(model)
        search_box.textChanged.connect(proxy.set_filter_text)
        context["layout"].addWidget(self._create_table_view(model, proxy), stretch=1)

    def _build_hsk_detail_tab_content(self, context):
        self._clear_layout(context["layout"])

        cache_key = f"{self.mode}:{self._current_stats()['unique_count']}"
        text_value = self._mode_hsk_text_cache.get(cache_key)
        if text_value is None:
            from calibre_plugins.chinese_character_analyzer.hsk_data import (
                HSK_LEVEL_ORDER, HSK_WORD_LEVEL_ORDER,
            )

            coverage = self._current_hsk()
            level_order = HSK_WORD_LEVEL_ORDER if self.mode == "word" else HSK_LEVEL_ORDER
            label = "words" if self.mode == "word" else "chars"

            sections = []
            for level in level_order:
                info = coverage["per_level"][level]
                items = info["items"]
                cumulative = coverage["cumulative"][level]
                if items:
                    sections.append(
                        f"── HSK {level}  ({info['count']} {label}, {info['pct']:.1f}%  |  cumulative: {cumulative['pct']:.1f}%) ──\n"
                        + "  ".join(items)
                    )
                else:
                    sections.append(f"── HSK {level}  (0 {label}) ──\n(none)")

            not_in_hsk = coverage["not_in_hsk"]
            sections.append(
                f"── Not in HSK  ({coverage['not_in_hsk_count']} {label}, {coverage['not_in_hsk_pct']:.1f}%) ──\n"
                + ("  ".join(not_in_hsk) if not_in_hsk else "(none)")
            )
            text_value = "\n\n".join(sections)
            self._mode_hsk_text_cache[cache_key] = text_value

        text = QTextEdit()
        text.setReadOnly(True)
        text.setFont(QFont("Microsoft YaHei", 12))
        text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        text.setPlainText(text_value)
        context["layout"].addWidget(text, stretch=1)

    # ── AnkiConnect live connection ─────────────────────────────────────

    def _connect_anki(self):
        from calibre_plugins.chinese_character_analyzer.anki_connect import (
            AnkiConnectError, fetch_field_texts, ping,
        )

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        reachable = ping()
        QApplication.restoreOverrideCursor()

        if not reachable:
            from calibre.gui2 import error_dialog
            error_dialog(
                self, "Cannot Connect to Anki",
                "Could not reach AnkiConnect.\n\n"
                "Please make sure:\n"
                "  1. Anki is running\n"
                "  2. The AnkiConnect add-on is installed\n"
                "     (Tools → Add-ons → Get Add-ons → code 2055492159)\n"
                "  3. You have restarted Anki after installing the add-on",
                show=True,
            )
            return

        chooser = _AnkiConnectChooserDialog(self)
        if chooser.exec() != QDialog.DialogCode.Accepted:
            return

        selected_decks = chooser.selected_decks()
        chosen_field = chooser.selected_field()
        filter_query = chooser.selected_filter_query()
        if not selected_decks or not chosen_field:
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            texts, note_count = fetch_field_texts(selected_decks, chosen_field, filter_query)
        except AnkiConnectError as e:
            QApplication.restoreOverrideCursor()
            from calibre.gui2 import error_dialog
            error_dialog(self, "AnkiConnect Error", str(e), show=True)
            return
        finally:
            QApplication.restoreOverrideCursor()

        if not self._validate_anki_texts(texts, chosen_field):
            return

        self._set_anki_data(texts, chosen_field, note_count)

    # ── Anki .apkg file import ───────────────────────────────────────────

    def _import_anki(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Anki Deck (.apkg)",
            "",
            "Anki Packages (*.apkg);;All Files (*)",
        )
        if not path:
            return

        try:
            from calibre_plugins.chinese_character_analyzer.anki_parser import parse_apkg
            field_names, notes = parse_apkg(path)
        except Exception as e:
            from calibre.gui2 import error_dialog
            error_dialog(
                self, "Anki Import Error",
                f"Could not read the .apkg file:\n{e}",
                show=True,
            )
            return

        if not notes:
            from calibre.gui2 import error_dialog
            error_dialog(self, "Anki Import Error", "No notes found in this deck.", show=True)
            return

        all_fields = []
        seen = set()
        for _mid, names in field_names.items():
            for name in names:
                if name not in seen:
                    all_fields.append(name)
                    seen.add(name)

        if not all_fields:
            from calibre.gui2 import error_dialog
            error_dialog(self, "Anki Import Error", "No fields found in the deck.", show=True)
            return

        chooser = _FieldChooserDialog(self, all_fields, notes)
        if chooser.exec() != QDialog.DialogCode.Accepted:
            return

        chosen_field = chooser.selected_field()
        if not chosen_field:
            return

        from calibre_plugins.chinese_character_analyzer.anki_parser import extract_field_texts
        texts = extract_field_texts(notes, chosen_field)
        if not self._validate_anki_texts(texts, chosen_field):
            return

        self._set_anki_data(texts, chosen_field, len(notes))

    def _validate_anki_texts(self, texts, field_name):
        from calibre_plugins.chinese_character_analyzer.analyzer import extract_cjk_characters

        all_chars = set()
        for text in texts:
            all_chars.update(extract_cjk_characters(text))

        if all_chars:
            return True

        from calibre.gui2 import error_dialog
        error_dialog(
            self, "No Characters Found",
            f"No CJK characters found in the '{field_name}' field.",
            show=True,
        )
        return False

    def _set_anki_data(self, texts, field_name, note_count):
        self._anki_data = {
            "texts": texts,
            "field_name": field_name,
            "note_count": note_count,
            "known_cache": {},
            "unknown_rows_cache": {},
        }
        self._refresh_mode_ui()
        anki_index = self._tab_index_for_role("anki")
        if anki_index >= 0:
            self.tabs.setCurrentIndex(anki_index)

    def _build_anki_tab_content(self, context):
        self._clear_layout(context["layout"])

        known_units = self._get_known_units_for_mode()
        stats = self._current_stats()
        counts = self._current_counts()
        book_unique = set(self._current_unique_items())

        known_in_book = book_unique & known_units
        unknown_in_book = book_unique - known_units

        total_known_occ = sum(counts.get(item, 0) for item in known_in_book)
        total_occ = self._current_total_count()
        coverage_pct = (total_known_occ / total_occ * 100) if total_occ else 0
        unique_coverage_pct = (len(known_in_book) / len(book_unique) * 100) if book_unique else 0

        summary = QFrame()
        summary.setFrameShape(QFrame.Shape.StyledPanel)
        summary.setStyleSheet(
            "QFrame { background: palette(alternate-base); border-radius: 6px; padding: 5px; }"
        )
        summary_layout = QVBoxLayout(summary)
        summary_layout.setSpacing(4)

        info_label = QLabel(
            f"<b style='font-family: Microsoft YaHei;'>Anki Deck Analysis ({self._unit_singular()})</b>"
            f"<br><span style='color: gray;'>Field: \"{self._anki_data['field_name']}\" · "
            f"{self._anki_data['note_count']:,} notes · {len(known_units):,} unique known {self._unit_label().lower()}</span>"
        )
        info_label.setWordWrap(True)
        summary_layout.addWidget(info_label)

        cards = QHBoxLayout()
        cards.setSpacing(8)
        cards.addWidget(self._make_card("Text Coverage", f"{coverage_pct:.1f}%"))
        cards.addWidget(self._make_card("Known Unique", f"{len(known_in_book):,} / {len(book_unique):,}"))
        cards.addWidget(self._make_card("Unknown Unique", f"{len(unknown_in_book):,}"))
        summary_layout.addLayout(cards)

        summary_layout.addLayout(self._build_coverage_row("Text coverage", coverage_pct, "#26A69A"))
        summary_layout.addLayout(self._build_coverage_row("Unique coverage", unique_coverage_pct, "#42A5F5"))
        context["layout"].addWidget(summary)

        unit_label = "Unknown Words" if self.mode == "word" else "Unknown Characters"
        label = QLabel(
            f"<b>{unit_label}</b> — {len(unknown_in_book):,} {self._unit_label().lower()} "
            f"you haven't learned yet, sorted by frequency in this book:"
        )
        label.setWordWrap(True)
        label.setFont(QFont("Microsoft YaHei", 9))
        context["layout"].addWidget(label)

        cache_key = f"{self.mode}:{len(unknown_in_book)}:{stats['unique_count']}"
        rows = self._anki_data["unknown_rows_cache"].get(cache_key)
        if rows is None:
            unknown_sorted = sorted(unknown_in_book, key=lambda item: counts.get(item, 0), reverse=True)
            rows = []
            for rank, item in enumerate(unknown_sorted, start=1):
                rows.append({
                    "rank": rank,
                    "item": item,
                    "count": counts.get(item, 0),
                    "length": len(item),
                    "hsk_level": self._hsk_level_for_item(item),
                })
            self._anki_data["unknown_rows_cache"][cache_key] = rows

        model = _AnalysisRowsTableModel(rows, self._anki_columns(), 14 if self.mode == "word" else 16, self)
        context["layout"].addWidget(self._create_table_view(model), stretch=1)
        context["tab_title"] = f"Anki ({coverage_pct:.0f}% coverage)"
        self._update_tab_labels()

    def _get_known_units_for_mode(self):
        cache = self._anki_data["known_cache"]
        if self.mode in cache:
            return cache[self.mode]

        texts = self._anki_data["texts"]
        if self.mode == "word":
            from calibre_plugins.chinese_character_analyzer.analyzer import extract_cjk_words
            known_units = set()
            for text in texts:
                known_units.update(extract_cjk_words(text))
        else:
            from calibre_plugins.chinese_character_analyzer.analyzer import extract_cjk_characters
            known_units = set()
            for text in texts:
                known_units.update(extract_cjk_characters(text))

        cache[self.mode] = known_units
        return cache[self.mode]

    # ── Card / table helpers ────────────────────────────────────────────

    def _make_card(self, label, value):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(
            "QFrame { background: palette(alternate-base); border-radius: 6px; padding: 4px; }"
        )
        layout = QVBoxLayout(card)
        layout.setSpacing(1)
        layout.setContentsMargins(8, 4, 8, 4)

        value_label = QLabel(value)
        font = QFont("Segoe UI", 16, QFont.Weight.DemiBold)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        value_label.setFont(font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)

        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("color: gray; font-size: 8pt;")
        layout.addWidget(text_label)
        return card

    def _make_small_card(self, label, value, pct):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(
            "QFrame { background: palette(base); border-radius: 6px; padding: 4px; }"
        )
        layout = QVBoxLayout(card)
        layout.setSpacing(1)
        layout.setContentsMargins(6, 4, 6, 4)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        layout.addWidget(value_label)

        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setStyleSheet("color: gray; font-size: 8pt;")
        layout.addWidget(label_widget)

        pct_label = QLabel(pct)
        pct_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pct_label.setStyleSheet("color: gray; font-size: 7.5pt;")
        layout.addWidget(pct_label)
        return card

    def _build_coverage_row(self, label_text, pct, color):
        row = QHBoxLayout()
        row.setSpacing(6)

        label = QLabel(label_text)
        label.setFixedWidth(96)
        label.setFont(QFont("Microsoft YaHei", 8))
        row.addWidget(label)

        bar = QProgressBar()
        bar.setRange(0, 1000)
        bar.setValue(int(pct * 10))
        bar.setTextVisible(False)
        bar.setFixedHeight(14)
        bar.setStyleSheet(
            "QProgressBar { border: 1px solid palette(mid); border-radius: 5px; background: palette(base); }"
            f"QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}"
        )
        row.addWidget(bar, stretch=1)

        pct_label = QLabel(f"{pct:.1f}%")
        pct_label.setFixedWidth(56)
        pct_label.setFont(QFont("Microsoft YaHei", 8, QFont.Weight.Bold))
        row.addWidget(pct_label)
        return row

    def _hsk_level_for_item(self, item):
        from calibre_plugins.chinese_character_analyzer.hsk_data import HSK_CHAR_TO_LEVEL, HSK_WORD_TO_LEVEL
        if self.mode == "word":
            return HSK_WORD_TO_LEVEL.get(item, "—")
        return HSK_CHAR_TO_LEVEL.get(item, "—")

    def _display_hsk_level(self, item):
        level = self._hsk_level_for_item(item)
        return f"HSK {level}" if level != "—" else "—"

    def _export_csv(self):
        filename = (
            f"{self.book_title}_chinese_words.csv"
            if self.mode == "word"
            else f"{self.book_title}_chinese_chars.csv"
        )
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Analysis",
            filename,
            "CSV Files (*.csv)",
        )
        if not path:
            return

        import csv

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if self.mode == "word":
                writer.writerow(["Rank", "Word", "Count", "Length", "HSK Level"])
                for row in self.word_stats["frequency_rows"]:
                    writer.writerow([row["rank"], row["item"], row["count"], row["length"], self._display_hsk_level(row["item"])])
            else:
                writer.writerow(["Rank", "Character", "Count", "HSK Level"])
                for row in self.character_stats["frequency_rows"]:
                    writer.writerow([row["rank"], row["item"], row["count"], self._display_hsk_level(row["item"])])

        from calibre.gui2 import info_dialog
        unit_label = self._unit_label().lower()
        info_dialog(
            self,
            "Export complete",
            f"Exported {self._current_stats()['unique_count']:,} {unit_label} to:\n{path}",
            show=True,
        )

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            child_layout = item.layout()
            widget = item.widget()
            if child_layout is not None:
                self._clear_layout(child_layout)
            if widget is not None:
                widget.deleteLater()

    def _shutdown_word_analysis_thread(self):
        thread = self._word_analysis_thread
        if thread is None:
            return
        try:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        except RuntimeError:
            pass
        finally:
            self._word_analysis_thread = None
            self._word_analysis_worker = None


class _FieldChooserDialog(QDialog):
    """Dialog to let the user pick which Anki field contains the Chinese text."""

    def __init__(self, parent, field_names, notes):
        super().__init__(parent)
        self.setWindowTitle("Choose Anki Field")
        self.setMinimumWidth(450)
        self._field_names = field_names
        self._notes = notes

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = QLabel(
            "Select the field that contains the Chinese text you've learned.\n"
            "A preview of the first few values is shown below."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        combo_row = QHBoxLayout()
        combo_label = QLabel("Field:")
        combo_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        combo_row.addWidget(combo_label)

        self._combo = QComboBox()
        self._combo.addItems(field_names)
        self._combo.currentTextChanged.connect(self._update_preview)
        combo_row.addWidget(self._combo, stretch=1)
        layout.addLayout(combo_row)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(QFont("Microsoft YaHei", 11))
        self._preview.setMaximumHeight(180)
        layout.addWidget(self._preview)

        self._char_count_label = QLabel("")
        self._char_count_label.setStyleSheet("color: gray;")
        layout.addWidget(self._char_count_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Use This Field")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        self._update_preview(field_names[0] if field_names else "")

    def _update_preview(self, field_name):
        from calibre_plugins.chinese_character_analyzer.anki_parser import extract_characters_from_field

        previews = []
        for note in self._notes[:10]:
            value = note["fields"].get(field_name, "")
            if value:
                previews.append(value[:80] + ("…" if len(value) > 80 else ""))

        if previews:
            self._preview.setPlainText("\n".join(previews))
        else:
            self._preview.setPlainText("(no values found for this field)")

        chars = extract_characters_from_field(self._notes, field_name)
        self._char_count_label.setText(
            f"{len(chars):,} unique CJK characters found across {len(self._notes):,} notes"
        )

    def selected_field(self):
        return self._combo.currentText()


class _AnkiConnectChooserDialog(QDialog):
    """
    Dialog that lets the user pick deck(s), a field, and a known-ness filter
    when connecting to Anki via AnkiConnect.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Connect to Anki")
        self.setMinimumSize(QSize(520, 560))

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = QLabel(
            "Select the deck(s) containing your Chinese vocabulary, the field "
            "with the Chinese text, and how to define \"known\" cards."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        deck_group = QGroupBox("Decks")
        deck_layout = QVBoxLayout(deck_group)

        self._deck_list = QListWidget()
        self._deck_list.setAlternatingRowColors(True)
        self._deck_list.itemChanged.connect(self._on_deck_selection_changed)
        deck_layout.addWidget(self._deck_list)

        deck_btn_row = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all_decks)
        deck_btn_row.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all_decks)
        deck_btn_row.addWidget(deselect_all_btn)
        deck_btn_row.addStretch()
        deck_layout.addLayout(deck_btn_row)
        layout.addWidget(deck_group)

        filter_row = QHBoxLayout()
        filter_label = QLabel("Count as known:")
        filter_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        filter_row.addWidget(filter_label)

        from calibre_plugins.chinese_character_analyzer.anki_connect import KNOWN_FILTERS
        self._filter_combo = QComboBox()
        for label, _query in KNOWN_FILTERS:
            self._filter_combo.addItem(label)
        self._filter_combo.setCurrentIndex(0)
        filter_row.addWidget(self._filter_combo, stretch=1)
        layout.addLayout(filter_row)

        field_group = QGroupBox("Field containing Chinese text")
        field_layout = QVBoxLayout(field_group)

        self._field_combo = QComboBox()
        self._field_combo.currentTextChanged.connect(self._update_preview)
        field_layout.addWidget(self._field_combo)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(QFont("Microsoft YaHei", 11))
        self._preview.setMaximumHeight(140)
        field_layout.addWidget(self._preview)

        self._char_count_label = QLabel("")
        self._char_count_label.setStyleSheet("color: gray;")
        field_layout.addWidget(self._char_count_label)
        layout.addWidget(field_group)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self._status_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self._ok_btn = QPushButton("Analyze")
        self._ok_btn.setDefault(True)
        self._ok_btn.setEnabled(False)
        self._ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self._ok_btn)
        layout.addLayout(btn_layout)

        self._sample_notes = []
        self._total_note_count = 0
        self._populate_decks()

    def _populate_decks(self):
        from calibre_plugins.chinese_character_analyzer.anki_connect import (
            AnkiConnectError, deck_names,
        )

        try:
            names = deck_names()
        except AnkiConnectError as e:
            self._status_label.setText(f"Error: {e}")
            return

        if not names:
            self._status_label.setText("No decks found in Anki.")
            return

        names = sorted(names, key=lambda name: (name != "Default", name.lower()))
        for name in names:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self._deck_list.addItem(item)

        self._status_label.setText(
            f"{len(names)} deck(s) found. Select deck(s) to load fields."
        )

    def _select_all_decks(self):
        self._deck_list.blockSignals(True)
        for i in range(self._deck_list.count()):
            self._deck_list.item(i).setCheckState(Qt.CheckState.Checked)
        self._deck_list.blockSignals(False)
        self._load_fields()

    def _deselect_all_decks(self):
        self._deck_list.blockSignals(True)
        for i in range(self._deck_list.count()):
            self._deck_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        self._deck_list.blockSignals(False)
        self._on_decks_cleared()

    def _on_deck_selection_changed(self, _item):
        decks = self._get_checked_decks()
        if decks:
            self._load_fields()
        else:
            self._on_decks_cleared()

    def _on_decks_cleared(self):
        self._field_combo.blockSignals(True)
        self._field_combo.clear()
        self._field_combo.blockSignals(False)
        self._preview.clear()
        self._char_count_label.setText("")
        self._sample_notes = []
        self._total_note_count = 0
        self._ok_btn.setEnabled(False)
        self._status_label.setText("Select deck(s) to load fields.")

    def _get_checked_decks(self):
        checked = []
        for i in range(self._deck_list.count()):
            item = self._deck_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked.append(item.text())
        return checked

    def _load_fields(self):
        decks = self._get_checked_decks()
        if not decks:
            self._status_label.setText("Please select at least one deck first.")
            return

        from calibre_plugins.chinese_character_analyzer.anki_connect import (
            AnkiConnectError, get_all_field_names,
        )

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            field_names, sample_notes, total_count = get_all_field_names(decks)
        except AnkiConnectError as e:
            QApplication.restoreOverrideCursor()
            self._status_label.setText(f"Error: {e}")
            return
        finally:
            QApplication.restoreOverrideCursor()

        if not field_names:
            self._status_label.setText("No fields found in the selected deck(s).")
            return

        self._sample_notes = sample_notes
        self._total_note_count = total_count

        self._field_combo.blockSignals(True)
        self._field_combo.clear()
        self._field_combo.addItems(field_names)
        self._field_combo.blockSignals(False)

        best_idx = 0
        for i, name in enumerate(field_names):
            low = name.lower()
            if any(keyword in low for keyword in ("hanzi", "character", "chinese", "汉字", "字")):
                best_idx = i
                break
        self._field_combo.setCurrentIndex(best_idx)
        self._update_preview(field_names[best_idx])

        self._ok_btn.setEnabled(True)
        self._status_label.setText(
            f'Found {len(field_names)} field(s) across {total_count:,} notes. '
            f'Pick a field and click "Analyze".'
        )

    def _update_preview(self, field_name):
        if not field_name or not self._sample_notes:
            return

        from calibre_plugins.chinese_character_analyzer.analyzer import is_cjk_ideograph

        previews = []
        cjk_count = 0
        for note in self._sample_notes:
            value = note["fields"].get(field_name, "")
            if value:
                previews.append(value[:80] + ("…" if len(value) > 80 else ""))
            for ch in value:
                if is_cjk_ideograph(ch):
                    cjk_count += 1

        if previews:
            self._preview.setPlainText("\n".join(previews[:10]))
        else:
            self._preview.setPlainText("(no values found for this field)")

        has_cjk = "✓ Contains CJK characters" if cjk_count > 0 else "✗ No CJK characters found in sample"
        self._char_count_label.setText(
            f"Preview of {len(self._sample_notes)} notes — {has_cjk}"
        )

    def selected_decks(self):
        return self._get_checked_decks()

    def selected_field(self):
        return self._field_combo.currentText()

    def selected_filter_query(self):
        from calibre_plugins.chinese_character_analyzer.anki_connect import KNOWN_FILTERS
        idx = self._filter_combo.currentIndex()
        if 0 <= idx < len(KNOWN_FILTERS):
            return KNOWN_FILTERS[idx][1]
        return ""
