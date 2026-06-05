import os

import config as config

from src.tools.backup_tool import (
    BackupConfig, BackupWorker, detect_vcs
)

from datetime import date

from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PyQt6.QtCore import Qt, QThread, QModelIndex
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QGroupBox, QRadioButton, QProgressBar,
    QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem,
    QHeaderView,
)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

ITEM_TYPE_ROLE   = Qt.ItemDataRole.UserRole + 1
ITEM_TYPE_FOLDER = "folder"
CHECKED_ROLE     = Qt.ItemDataRole.UserRole + 2   # bool, replaces Qt checkstate

COL_ARROW = 0
COL_TREE  = 1
COL_EXTS  = 2

INDENT   = 20
CB_SIZE  = 16
CB_MARG  = 4


def _scan_extensions(folder: str) -> list[str]:
    exts: set[str] = set()
    try:
        for dirpath, dirnames, filenames in os.walk(folder):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext:
                    exts.add(ext)
    except PermissionError:
        pass
    return sorted(exts)


# ──────────────────────────────────────────────────────────────────────────────
# Arrow delegate
# ──────────────────────────────────────────────────────────────────────────────

class ArrowDelegate(QStyledItemDelegate):

    def __init__(self, tree, theme_manager=None):
        super().__init__(tree)
        self._tree = tree
        self._tm   = theme_manager

    def paint(self, painter, option, index):
        # Background – drawn manually using the app palette
        painter.save()
        painter.fillRect(option.rect, option.palette.alternateBase()
                         if option.features & option.ViewItemFeature.Alternate
                         else option.palette.base())
        painter.restore()

        item = self._tree.itemFromIndex(index)
        if not item or item.data(COL_TREE, ITEM_TYPE_ROLE) != ITEM_TYPE_FOLDER:
            return

        # check for subfolder children
        has_sub = any(
            item.child(i).data(COL_TREE, ITEM_TYPE_ROLE) == ITEM_TYPE_FOLDER
            for i in range(item.childCount())
        )
        if not has_sub:
            try:
                path = item.data(COL_TREE, Qt.ItemDataRole.UserRole) or ""
                has_sub = any(
                    e.is_dir() and not e.name.startswith(".")
                    for e in os.scandir(path)
                )
            except Exception:
                pass
        if not has_sub:
            return

        painter.save()
        color = QColor(self._tm.color_line() if self._tm else "#4cc2ee")
        painter.setPen(color)
        f = QFont()
        f.setPointSize(8)
        painter.setFont(f)
        painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter,
                         "▼" if item.isExpanded() else "▶")
        painter.restore()


# ──────────────────────────────────────────────────────────────────────────────
# Tree + checkbox delegate
# ──────────────────────────────────────────────────────────────────────────────

class TreeLineDelegate(QStyledItemDelegate):

    def __init__(self, tree, theme_manager=None):
        super().__init__(tree)
        self._tree = tree
        self._tm   = theme_manager

    def _line_color(self):
        return QColor(self._tm.color_line() if self._tm else "#4cc2ee")

    def _text_color(self):
        return QColor(self._tm.color_text() if self._tm else "#ffffff")

    def _depth(self, item):
        d, p = 0, item.parent()
        while p:
            d += 1
            p = p.parent()
        return d

    def _is_last(self, item):
        parent = item.parent()
        siblings = (
            [self._tree.topLevelItem(i) for i in range(self._tree.topLevelItemCount())]
            if parent is None else
            [parent.child(i) for i in range(parent.childCount())]
        )
        return siblings[-1] is item if siblings else True

    def _cb_rect(self, option, depth):
        mid_y = option.rect.top() + option.rect.height() // 2
        x_cb  = option.rect.left() + depth * INDENT + CB_MARG
        y_cb  = mid_y - CB_SIZE // 2
        return option.rect.__class__(x_cb, y_cb, CB_SIZE, CB_SIZE)

    def paint(self, painter, option, index):
        item = self._tree.itemFromIndex(index)
        if not item or index.column() != COL_TREE:
            super().paint(painter, option, index)
            return

        # 1. Background – drawn manually using the app palette
        painter.save()
        painter.fillRect(option.rect, option.palette.alternateBase()
                         if option.features & option.ViewItemFeature.Alternate
                         else option.palette.base())
        painter.restore()

        depth = self._depth(item)
        mid_y = option.rect.top() + option.rect.height() // 2
        top_y = option.rect.top()
        bot_y = option.rect.bottom()
        x0    = option.rect.left()

        # 2. Tree lines
        if depth > 0:
            painter.save()
            painter.setPen(QPen(self._line_color(), 1))
            x_vert  = x0 + (depth - 1) * INDENT + INDENT // 2
            is_last = self._is_last(item)
            painter.drawLine(x_vert, mid_y, x_vert + 10, mid_y)
            painter.drawLine(x_vert, top_y, x_vert, mid_y if is_last else bot_y)
            anc, lvl = item.parent(), 1
            while anc and anc.parent() is not None:
                if not self._is_last(anc):
                    ax = x0 + (depth - 1 - lvl) * INDENT + INDENT // 2
                    painter.drawLine(ax, top_y, ax, bot_y)
                anc, lvl = anc.parent(), lvl + 1
            painter.restore()

        # 3. Checkbox (our own, no Qt native)
        cb = self._cb_rect(option, depth)
        checked = bool(item.data(COL_TREE, CHECKED_ROLE))
        painter.save()
        checked_col = QColor(self._tm.color_checked() if self._tm else "#00f091")
        if checked:
            painter.setPen(QPen(checked_col, 2))
            painter.setBrush(QBrush(checked_col))
        else:
            painter.setPen(QPen(self._line_color(), 2))
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
        painter.drawRoundedRect(cb, 3, 3)
        painter.restore()

        # 4. Text – use palette text color (auto theme-aware)
        x_text    = cb.right() + CB_MARG + 2
        text_rect = option.rect.__class__(x_text, option.rect.top(),
                                          option.rect.right() - x_text,
                                          option.rect.height())
        painter.save()
        painter.setPen(option.palette.text().color())
        painter.setFont(option.font)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter,
                         item.text(COL_TREE))
        painter.restore()

    def editorEvent(self, event, model, option, index):
        from PyQt6.QtCore import QEvent
        item = self._tree.itemFromIndex(index)
        if not item or index.column() != COL_TREE:
            return False
        if item.data(COL_TREE, ITEM_TYPE_ROLE) != ITEM_TYPE_FOLDER:
            return False
        if event.type() == QEvent.Type.MouseButtonRelease:
            depth = self._depth(item)
            cb    = self._cb_rect(option, depth)
            if cb.contains(event.pos()):
                cur = bool(item.data(COL_TREE, CHECKED_ROLE))
                item.setData(COL_TREE, CHECKED_ROLE, not cur)
                # trigger itemChanged manually
                self._tree._on_checked_changed(item, not cur)
                self._tree.viewport().update()
                return True
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Extension chip row
# ──────────────────────────────────────────────────────────────────────────────

class ExtChipRow(QWidget):

    def __init__(self, extensions):
        super().__init__()
        self._checks: dict[str, QCheckBox] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(10)
        for ext in extensions:
            cb = QCheckBox(ext)
            cb.setChecked(True)
            cb.setStyleSheet("font-size: 11px; font-weight: normal;")
            self._checks[ext] = cb
            layout.addWidget(cb)
        layout.addStretch()

    def excluded(self) -> set[str]:
        return {ext for ext, cb in self._checks.items() if not cb.isChecked()}


# ──────────────────────────────────────────────────────────────────────────────
# Folder tree widget
# ──────────────────────────────────────────────────────────────────────────────

class FolderTreeWidget(QTreeWidget):

    def __init__(self):
        super().__init__()

        self.setColumnCount(3)
        self.setHeaderLabels(["", "Folder", "File types to include"])
        self.header().setSectionResizeMode(COL_ARROW, QHeaderView.ResizeMode.Fixed)
        self.header().setSectionResizeMode(COL_TREE,  QHeaderView.ResizeMode.Interactive)
        self.header().setSectionResizeMode(COL_EXTS,  QHeaderView.ResizeMode.Stretch)
        self.setColumnWidth(COL_ARROW, 24)
        self.setColumnWidth(COL_TREE,  220)

        self.setRootIsDecorated(False)
        self.setIndentation(0)
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.setStyleSheet(
            "QTreeWidget::item:hover { background: transparent; border: none; }"
            "QTreeWidget::item:hover:!selected { background: transparent; }"
            "QTreeWidget::item { border: none; }"
        )

        self._tm        = None   # set via set_theme_manager()
        self._arrow_del = ArrowDelegate(self)
        self._line_del  = TreeLineDelegate(self)
        self.setItemDelegateForColumn(COL_ARROW, self._arrow_del)
        self.setItemDelegateForColumn(COL_TREE,  self._line_del)

        self.clicked.connect(self._on_clicked)

    def set_theme_manager(self, tm):
        self._tm = tm
        self._arrow_del._tm = tm
        self._line_del._tm  = tm
        self.viewport().update()

    def load(self, root: str):
        self.clear()
        self._add_folders(None, root)
        self.collapseAll()

    def _add_folders(self, parent_item, folder: str):
        try:
            entries = sorted(
                [e for e in os.scandir(folder) if e.is_dir()],
                key=lambda e: e.name.lower()
            )
        except PermissionError:
            return

        for entry in entries:
            if entry.name.startswith(".") or entry.name in ("__pycache__", "node_modules"):
                continue

            item = QTreeWidgetItem(["", entry.name, ""])
            item.setData(COL_TREE, Qt.ItemDataRole.UserRole, entry.path)
            item.setData(COL_TREE, ITEM_TYPE_ROLE, ITEM_TYPE_FOLDER)
            item.setData(COL_TREE, CHECKED_ROLE, False)
            # NO setCheckState – we handle checks ourselves
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)

            if parent_item is None:
                self.addTopLevelItem(item)
            else:
                parent_item.addChild(item)

            self._add_folders(item, entry.path)

    def _on_clicked(self, index: QModelIndex):
        item = self.itemFromIndex(index)
        if not item:
            return
        if index.column() == COL_ARROW and item.data(COL_TREE, ITEM_TYPE_ROLE) == ITEM_TYPE_FOLDER:
            item.setExpanded(not item.isExpanded())
            self.viewport().update()

    def _on_checked_changed(self, item, checked: bool):
        if checked:
            self._insert_ext_row(item)
        else:
            self._remove_ext_row(item)

    def _insert_ext_row(self, folder_item):
        self._remove_ext_row(folder_item)
        path = folder_item.data(COL_TREE, Qt.ItemDataRole.UserRole)
        exts = _scan_extensions(path)
        if not exts:
            return
        chip_row = ExtChipRow(exts)
        self.setItemWidget(folder_item, COL_EXTS, chip_row)
        folder_item._chip_row = chip_row

    def _remove_ext_row(self, folder_item):
        self.removeItemWidget(folder_item, COL_EXTS)
        folder_item._chip_row = None

    def get_full_dirs(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        self._collect(self.invisibleRootItem(), result)
        return result

    def _collect(self, parent, result):
        for i in range(parent.childCount()):
            item = parent.child(i)
            if item.data(COL_TREE, ITEM_TYPE_ROLE) != ITEM_TYPE_FOLDER:
                continue
            if bool(item.data(COL_TREE, CHECKED_ROLE)):
                path     = item.data(COL_TREE, Qt.ItemDataRole.UserRole)
                chip_row = getattr(item, "_chip_row", None)
                result[path] = chip_row.excluded() if chip_row else set()
            self._collect(item, result)

    def expand_all(self):
        self.expandAll()

    def collapse_all(self):
        self.collapseAll()

    def check_all(self):
        self._set_all(self.invisibleRootItem(), True)

    def uncheck_all(self):
        self._set_all(self.invisibleRootItem(), False)

    def _set_all(self, parent, checked: bool):
        for i in range(parent.childCount()):
            item = parent.child(i)
            if item.data(COL_TREE, ITEM_TYPE_ROLE) != ITEM_TYPE_FOLDER:
                continue
            was = bool(item.data(COL_TREE, CHECKED_ROLE))
            item.setData(COL_TREE, CHECKED_ROLE, checked)
            if checked and not was:
                self._insert_ext_row(item)
                item.setExpanded(True)
            elif not checked:
                self._remove_ext_row(item)
            self._set_all(item, checked)
        self.viewport().update()


# ──────────────────────────────────────────────────────────────────────────────
# Backup Page
# ──────────────────────────────────────────────────────────────────────────────

class BackupPage(QWidget):

    def __init__(self, logger, theme_manager=None):
        super().__init__()
        self.logger  = logger
        self._tm     = theme_manager
        self._thread = None
        self._worker = None
        self._vcs    = "none"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("Create Backup")
        title.setObjectName("title")
        layout.addWidget(title)

        # ── Source ────────────────────────────────────────────────────
        src_group = QGroupBox("Source")
        src_v = QVBoxLayout(src_group)
        src_row = QHBoxLayout()
        default_src = config.get("hamilton_folder") or ""
        self.src_input = QLineEdit(default_src)
        self.src_input.setPlaceholderText("Select source folder...")
        btn_src = QPushButton("Browse")
        btn_src.clicked.connect(self._browse_src)
        src_row.addWidget(self.src_input)
        src_row.addWidget(btn_src)
        src_v.addLayout(src_row)
        self.vcs_label = QLabel("VCS: –")
        self.vcs_label.setObjectName("systemInfo")
        src_v.addWidget(self.vcs_label)
        layout.addWidget(src_group)

        # ── Folder tree ───────────────────────────────────────────────
        tree_group = QGroupBox("Additional full-copy folders")
        tree_v = QVBoxLayout(tree_group)

        self.tree = FolderTreeWidget()
        self.tree.set_theme_manager(self._tm)
        self.tree.setMinimumHeight(220)
        tree_v.addWidget(self.tree)

        tree_btn_row = QHBoxLayout()
        btn_check_all   = QPushButton("Check all")
        btn_check_all.setObjectName("btnSecondary")
        btn_check_all.clicked.connect(self.tree.check_all)

        btn_uncheck_all = QPushButton("Uncheck all")
        btn_uncheck_all.setObjectName("btnSecondary")
        btn_uncheck_all.clicked.connect(self.tree.uncheck_all)

        btn_expand_all  = QPushButton("Unfold all")
        btn_expand_all.setObjectName("btnSecondary")
        btn_expand_all.clicked.connect(self.tree.expand_all)

        btn_collapse_all = QPushButton("Fold all")
        btn_collapse_all.setObjectName("btnSecondary")
        btn_collapse_all.clicked.connect(self.tree.collapse_all)

        tree_btn_row.addWidget(btn_check_all)
        tree_btn_row.addWidget(btn_uncheck_all)
        tree_btn_row.addStretch()
        tree_btn_row.addWidget(btn_expand_all)
        tree_btn_row.addWidget(btn_collapse_all)

        tree_v.addLayout(tree_btn_row)
        layout.addWidget(tree_group)

        # ── Destination ───────────────────────────────────────────────
        dest_group = QGroupBox("Destination")
        dest_v = QVBoxLayout(dest_group)

        dest_row = QHBoxLayout()
        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("Select destination folder...")
        btn_dest = QPushButton("Browse")
        btn_dest.clicked.connect(self._browse_dest)
        dest_row.addWidget(self.dest_input)
        dest_row.addWidget(btn_dest)
        dest_v.addLayout(dest_row)

        fmt_row = QHBoxLayout()
        self.rb_folder = QRadioButton("Copy as folder")
        self.rb_zip    = QRadioButton("Create ZIP archive")
        self.rb_folder.setChecked(True)
        fmt_row.addWidget(self.rb_folder)
        fmt_row.addWidget(self.rb_zip)
        fmt_row.addStretch()
        dest_v.addLayout(fmt_row)

        name_row = QHBoxLayout()
        name_label = QLabel("Optional name:")
        name_label.setStyleSheet("font-weight: normal; font-size: 13px;")
        name_label.setFixedWidth(110)
        self.backup_name_input = QLineEdit()
        self.backup_name_input.setPlaceholderText("e.g. before_release")
        name_row.addWidget(name_label)
        name_row.addWidget(self.backup_name_input)
        dest_v.addLayout(name_row)

        layout.addWidget(dest_group)

        # ── Progress ──────────────────────────────────────────────────
        self.progress_widget = QWidget()
        prog_v = QVBoxLayout(self.progress_widget)
        prog_v.setContentsMargins(0, 4, 0, 0)
        prog_v.setSpacing(4)

        prog_top = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setTextVisible(False)
        self.progress_count = QLabel("Copying 0 of 0")
        self.progress_count.setStyleSheet("font-size: 12px; font-weight: normal;")
        self.progress_count.setFixedWidth(140)
        self.progress_pct = QLabel("0%")
        self.progress_pct.setStyleSheet("font-size: 12px; font-weight: normal;")
        self.progress_pct.setFixedWidth(36)
        prog_top.addWidget(self.progress_count)
        prog_top.addWidget(self.progress_bar)
        prog_top.addWidget(self.progress_pct)
        prog_v.addLayout(prog_top)

        self.progress_file = QLabel("")
        self.progress_file.setObjectName("systemInfo")
        self.progress_file.setStyleSheet("font-size: 11px; font-weight: normal;")
        prog_v.addWidget(self.progress_file)
        layout.addWidget(self.progress_widget)

        # ── Action buttons – full width, each on own row ───────────────
        self.btn_start = QPushButton("Start Backup")
        self.btn_start.setFixedHeight(36)
        self.btn_start.clicked.connect(self._start)
        layout.addWidget(self.btn_start)

        self.btn_abort = QPushButton("Abort")
        self.btn_abort.setObjectName("btnSecondary")
        self.btn_abort.setFixedHeight(36)
        self.btn_abort.setEnabled(False)
        self.btn_abort.clicked.connect(self._abort)
        layout.addWidget(self.btn_abort)

        if default_src and os.path.isdir(default_src):
            self._load_tree(default_src, silent=True)

    def _browse_src(self):
        path = QFileDialog.getExistingDirectory(self, "Select source folder")
        if path:
            self.src_input.setText(path)
            self._load_tree(path)

    def _browse_dest(self):
        path = QFileDialog.getExistingDirectory(self, "Select destination folder")
        if path:
            self.dest_input.setText(path)

    def _load_tree(self, path: str, silent: bool = False):
        self._vcs = detect_vcs(path)
        labels = {"svn": "SVN ✓", "git": "Git ✓", "none": "No VCS detected"}
        self.vcs_label.setText(f"VCS detected: {labels[self._vcs]}")
        self.tree.load(path)
        if not silent:
            self.logger.info(f"Backup source loaded: {path} ({self._vcs})")

    def _start(self):
        src  = self.src_input.text().strip()
        dest = self.dest_input.text().strip()

        if not src or not os.path.isdir(src):
            self.logger.warning("Backup: invalid source folder")
            return

        if not dest or not os.path.isdir(dest):
            self.logger.warning("Backup: invalid destination folder")
            return

        full_dirs = self.tree.get_full_dirs()

        date_str    = date.today().strftime("%Y-%m-%d")
        custom_name = self.backup_name_input.text().strip()
        backup_name = f"{date_str}_{custom_name}" if custom_name else date_str

        cfg = BackupConfig(
            src_root    = src,
            dest        = dest,
            to_zip      = self.rb_zip.isChecked(),
            vcs         = self._vcs,
            full_dirs   = full_dirs,
            backup_name = backup_name,
        )

        self._worker = BackupWorker(cfg)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._thread.started.connect(self._worker.run)
        self.btn_start.setEnabled(False)
        self.btn_abort.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_count.setText("Copying 0 of 0")
        self.progress_pct.setText("0%")
        self.progress_file.setText("")
        self._thread.start()
        self.logger.info("Backup started.")

    def _on_progress(self, msg: str):
        # parse "PROGRESS:current:total:filename" – don't log these
        if msg.startswith("PROGRESS:"):
            try:
                _, cur, total, fname = msg.split(":", 3)
                cur, total = int(cur), int(total)
                pct = int(cur / total * 100) if total > 0 else 0
                self.progress_bar.setValue(pct)
                self.progress_pct.setText(f"{pct}%")
                self.progress_count.setText(f"Copying {cur} of {total}")
                self.progress_file.setText(fname)
            except Exception:
                pass
        else:
            self.logger.info(msg)

    def _abort(self):
        if self._worker:
            self._worker.abort()
        self.logger.warning("Backup abort requested.")

    def _on_finished(self, success: bool, summary: str):
        self._thread.quit()
        self._thread.wait()
        self.btn_start.setEnabled(True)
        self.btn_abort.setEnabled(False)
        if success:
            self.logger.info(f"Backup complete: {summary}")
        else:
            self.logger.error(f"Backup failed: {summary}")
