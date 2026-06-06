import os

import config as config

from src.utils import open_folder
from src.tools.backup_tool import BackupConfig, BackupWorker, detect_vcs

from ui.widgets import FolderPickerWidget, ProgressWidget

from PyQt6.QtGui import (
    QPen,
    QFont,
    QColor,
    QBrush,
)
from PyQt6.QtCore import (
    Qt,
    QThread,
    QModelIndex,
)
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QGroupBox,
    QCheckBox,
    QHeaderView,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QRadioButton,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QStyledItemDelegate,
)


# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

ITEM_TYPE_ROLE   = Qt.ItemDataRole.UserRole + 1
ITEM_TYPE_FOLDER = "folder"
CHECKED_ROLE     = Qt.ItemDataRole.UserRole + 2

COL_ARROW = 0
COL_TREE  = 1
COL_EXTS  = 2

INDENT  = 20
CB_SIZE = 16
CB_MARG = 4


def _scan_extensions(folder: str) -> list[str]:
    exts: set[str] = set()

    try:
        for _, dirnames, filenames in os.walk(folder):
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
        painter.save()
        painter.fillRect(option.rect, option.palette.alternateBase()
                         if option.features & option.ViewItemFeature.Alternate
                         else option.palette.base())
        painter.restore()

        item = self._tree.itemFromIndex(index)
        if not item or item.data(COL_TREE, ITEM_TYPE_ROLE) != ITEM_TYPE_FOLDER:
            return

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

        cb      = self._cb_rect(option, depth)
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
        self._tm        = None
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

    def expand_all(self):   self.expandAll()
    def collapse_all(self): self.collapseAll()

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

        title = QLabel("Create Backup")
        title.setObjectName("title")
        layout.addWidget(title)

        # ----- Source -----
        src_group = QGroupBox("Source")
        src_layout = QVBoxLayout(src_group)
        default_src = config.get("hamilton_folder") or ""
        self.folder_widget = FolderPickerWidget(default_src)
        self.folder_widget.folder_input.textChanged.connect(self._on_src_changed)
        src_layout.addWidget(self.folder_widget)
        self.vcs_label = QLabel("Version Control Software: -")
        self.vcs_label.setObjectName("systemInfo")
        src_layout.addWidget(self.vcs_label)
        layout.addWidget(src_group)

        # ----- Tree -----
        tree_group = QGroupBox("Folder Tree")
        tree_layout = QVBoxLayout(tree_group)
        self.tree = FolderTreeWidget()
        self.tree.set_theme_manager(self._tm)
        self.tree.setMinimumHeight(180)
        self.tree.setToolTip(
            "If Version-Control-Software is detected, all versioned files are always included.\n"
            "Check folders to also copy them completely  -  "
            "uncheck file types to exclude them."
        )
        tree_layout.addWidget(self.tree)

        tree_btn_row = QHBoxLayout()
        for label, slot in [
            ("Check all",   self.tree.check_all),
            ("Uncheck all", self.tree.uncheck_all),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("btnSecondary")
            btn.clicked.connect(slot)
            tree_btn_row.addWidget(btn)
        tree_btn_row.addStretch()
        for label, slot in [
            ("Unfold all", self.tree.expand_all),
            ("Fold all",   self.tree.collapse_all),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("btnSecondary")
            btn.clicked.connect(slot)
            tree_btn_row.addWidget(btn)
        tree_layout.addLayout(tree_btn_row)
        layout.addWidget(tree_group)

        # ----- Options -----
        opt_group = QGroupBox("Backup Options")
        opt_layout = QHBoxLayout(opt_group)
        self.rb_folder = QRadioButton("Copy as folder")
        self.rb_zip    = QRadioButton("Create ZIP archive")
        self.rb_folder.setChecked(True)
        name_label = QLabel("Optional name:")
        name_label.setStyleSheet("font-weight: normal; font-size: 13px;")
        name_label.setFixedWidth(110)
        self.backup_name_input = QLineEdit()
        self.backup_name_input.setPlaceholderText("e.g. pre_SAT  ->  2026-06-02_pre_SAT")
        opt_layout.addWidget(self.rb_folder)
        opt_layout.addWidget(self.rb_zip)
        opt_layout.addStretch()
        opt_layout.addWidget(name_label)
        opt_layout.addWidget(self.backup_name_input)
        layout.addWidget(opt_group)

        # ----- Destination -----
        dest_group = QGroupBox("Destination")
        dest_layout = QVBoxLayout(dest_group)
        self.dest_widget = FolderPickerWidget(config.get("output_folder") or "")
        dest_layout.addWidget(self.dest_widget)
        layout.addWidget(dest_group)

        layout.addStretch()

        # ----- Progress -----
        self.progress = ProgressWidget("Copying")
        layout.addWidget(self.progress)

        # ----- Buttons -----
        self.btn_open = QPushButton("Open Output Folder")
        self.btn_open.setObjectName("btnSecondary")
        self.btn_open.setFixedHeight(36)
        self.btn_open.clicked.connect(self._open_output_folder)
        layout.addWidget(self.btn_open)

        self.btn_start = QPushButton("Start Backup")
        self.btn_start.setFixedHeight(36)
        self.btn_start.clicked.connect(self._start_or_abort)
        layout.addWidget(self.btn_start)

        if default_src and os.path.isdir(default_src):
            self._load_tree(default_src, silent=True)

    def _on_src_changed(self, path: str):
        if os.path.isdir(path):
            self._load_tree(path)

    def _load_tree(self, path: str, silent: bool = False):
        self._vcs = detect_vcs(path)
        labels = {"svn": "SVN", "git": "Git", "none": "No VCS detected"}
        self.vcs_label.setText(f"Version Control Software: {labels[self._vcs]}")
        self.tree.load(path)
        if not silent:
            self.logger.info(f"Backup source loaded: {path} ({self._vcs})")

    def _start(self):
        src  = self.folder_widget.get_folder().strip()
        dest = self.dest_widget.get_folder().strip()

        if not src or not os.path.isdir(src):
            self.logger.warning("Backup: invalid source folder")
            return
        if not dest or not os.path.isdir(dest):
            self.logger.warning("Backup: invalid destination folder")
            return

        full_dirs = self.tree.get_full_dirs()

        from datetime import date
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

        self._worker = BackupWorker(cfg, self.logger)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._thread.started.connect(self._worker.run)

        self.btn_start.setText("Abort")
        self.btn_start.setObjectName("btnSecondary")
        self.btn_start.setStyle(self.btn_start.style())  # force style refresh
        self.progress.reset()
        self._thread.start()
        self.logger.info("Backup started.")

    def _on_progress(self, msg: str):
        if not msg.startswith("PROGRESS:"):
            return
        try:
            _, cur, total, _ = msg.split(":", 3)
            self.progress.update(int(cur), int(total))
        except Exception:
            pass

    def _start_or_abort(self):
        if self.btn_start.text() == "Abort":
            self._abort()
        else:
            self._start()

    def _abort(self):
        if self._worker:
            self._worker.abort()
        self.logger.warning("Backup abort requested.")

    def _open_output_folder(self):
        dest = self.dest_widget.get_folder().strip()
        if not dest or not os.path.isdir(dest):
            self.logger.warning("Output folder not set or does not exist.")
            return
        open_folder(dest)

    def _on_finished(self, success: bool, summary: str):
        self._thread.quit()
        self._thread.wait()
        self.btn_start.setText("Start Backup")
        self.btn_start.setObjectName("")
        self.btn_start.setStyle(self.btn_start.style())  # force style refresh
        self.progress.finish()
        if not success:
            self.logger.error(f"Backup failed: {summary}")
