import os

import config as config

from src.tools.backup_creator import (
    BackupConfig, BackupWorker, detect_vcs, EXTRA_TYPES
)

from collections import defaultdict
from PyQt6.QtCore import Qt, QThread, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QGroupBox, QRadioButton, QProgressBar,
    QAbstractItemView, QSizePolicy,
)
from PyQt6.QtGui import QColor

# Role used to distinguish folder items from extension items
ITEM_TYPE_ROLE = Qt.ItemDataRole.UserRole + 1
ITEM_TYPE_FOLDER = "folder"
ITEM_TYPE_EXT    = "ext"


def _scan_extensions(folder: str) -> list[str]:
    """Returns sorted list of unique extensions found recursively in folder."""
    exts: set[str] = set()
    try:
        for dirpath, dirnames, filenames in os.walk(folder):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext:
                    exts.add(ext)
                else:
                    exts.add("(no extension)")
    except PermissionError:
        pass
    return sorted(exts)


# ──────────────────────────────────────────────────────────────────────────────
# Folder tree
# ──────────────────────────────────────────────────────────────────────────────

class FolderTreeWidget(QTreeWidget):

    def __init__(self):
        super().__init__()
        self.setHeaderLabel(
            "Check folders to copy completely  –  uncheck extensions to exclude them"
        )
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.itemChanged.connect(self._on_item_changed)
        self._updating = False

    def load(self, root: str):
        self._updating = True
        self.clear()
        self._add_folders(None, root)
        self.expandToDepth(0)
        self._updating = False

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

            item = QTreeWidgetItem([entry.name])
            item.setData(0, Qt.ItemDataRole.UserRole, entry.path)
            item.setData(0, ITEM_TYPE_ROLE, ITEM_TYPE_FOLDER)
            item.setCheckState(0, Qt.CheckState.Unchecked)
            item.setForeground(0, item.foreground(0))   # inherit theme color

            if parent_item is None:
                self.addTopLevelItem(item)
            else:
                parent_item.addChild(item)

            self._add_folders(item, entry.path)

    def _on_item_changed(self, item, column):
        if self._updating or column != 0:
            return
        item_type = item.data(0, ITEM_TYPE_ROLE)

        if item_type == ITEM_TYPE_FOLDER:
            self._updating = True
            if item.checkState(0) == Qt.CheckState.Checked:
                self._insert_ext_children(item)
            else:
                self._remove_ext_children(item)
            self._updating = False

        elif item_type == ITEM_TYPE_EXT:
            # update parent folder indicator
            self._updating = True
            self._update_folder_indicator(item.parent())
            self._updating = False

    def _insert_ext_children(self, folder_item):
        """Scan folder and add extension child items."""
        # Remove any existing ext children first
        self._remove_ext_children(folder_item)

        path = folder_item.data(0, Qt.ItemDataRole.UserRole)
        exts = _scan_extensions(path)

        if not exts:
            return

        for ext in exts:
            child = QTreeWidgetItem([ext])
            child.setData(0, Qt.ItemDataRole.UserRole, ext)
            child.setData(0, ITEM_TYPE_ROLE, ITEM_TYPE_EXT)
            child.setCheckState(0, Qt.CheckState.Checked)

            # Visually distinct from folder items
            from PyQt6.QtGui import QColor, QBrush, QFont
            child.setForeground(0, QBrush(QColor("#4cc2ee")))
            font = QFont()
            font.setPointSize(10)
            font.setItalic(True)
            child.setFont(0, font)
            # Tag-style prefix so it reads like a file type badge
            child.setText(0, f"  ›  {ext}")

            folder_item.addChild(child)

        folder_item.setExpanded(True)

    def _remove_ext_children(self, folder_item):
        """Remove all extension child items from a folder item."""
        to_remove = []
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.data(0, ITEM_TYPE_ROLE) == ITEM_TYPE_EXT:
                to_remove.append(child)
        for child in to_remove:
            folder_item.removeChild(child)

    def _update_folder_indicator(self, folder_item):
        """Set folder checkbox to checked/indeterminate based on ext selection."""
        if not folder_item:
            return
        ext_children = [
            folder_item.child(i) for i in range(folder_item.childCount())
            if folder_item.child(i).data(0, ITEM_TYPE_ROLE) == ITEM_TYPE_EXT
        ]
        if not ext_children:
            return
        checked = sum(1 for c in ext_children if c.checkState(0) == Qt.CheckState.Checked)
        if checked == len(ext_children):
            folder_item.setCheckState(0, Qt.CheckState.Checked)
        elif checked == 0:
            folder_item.setCheckState(0, Qt.CheckState.Unchecked)
        else:
            folder_item.setCheckState(0, Qt.CheckState.PartiallyChecked)

    # ── Public API ─────────────────────────────────────────────────────────

    def get_full_dirs(self) -> dict[str, set[str]]:
        """
        Returns {abs_path: set_of_excluded_extensions} for checked folders.
        Empty set = copy everything (no exclusions).
        """
        result: dict[str, set[str]] = {}
        self._collect(self.invisibleRootItem(), result)
        return result

    def _collect(self, parent, result):
        for i in range(parent.childCount()):
            item = parent.child(i)
            if item.data(0, ITEM_TYPE_ROLE) != ITEM_TYPE_FOLDER:
                continue
            state = item.checkState(0)
            if state in (Qt.CheckState.Checked, Qt.CheckState.PartiallyChecked):
                path = item.data(0, Qt.ItemDataRole.UserRole)
                excluded = set()
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.data(0, ITEM_TYPE_ROLE) == ITEM_TYPE_EXT:
                        if child.checkState(0) != Qt.CheckState.Checked:
                            excluded.add(child.data(0, Qt.ItemDataRole.UserRole))
                result[path] = excluded
            self._collect(item, result)

    def check_all(self):
        self._updating = True
        self._set_folders(self.invisibleRootItem(), Qt.CheckState.Checked)
        self._updating = False

    def uncheck_all(self):
        self._updating = True
        self._set_folders(self.invisibleRootItem(), Qt.CheckState.Unchecked)
        self._updating = False

    def _set_folders(self, parent, state):
        for i in range(parent.childCount()):
            item = parent.child(i)
            if item.data(0, ITEM_TYPE_ROLE) == ITEM_TYPE_FOLDER:
                old_state = item.checkState(0)
                item.setCheckState(0, state)
                if state == Qt.CheckState.Checked and old_state != Qt.CheckState.Checked:
                    self._insert_ext_children(item)
                elif state == Qt.CheckState.Unchecked:
                    self._remove_ext_children(item)
                self._set_folders(item, state)


# ──────────────────────────────────────────────────────────────────────────────
# Backup Page
# ──────────────────────────────────────────────────────────────────────────────

class BackupPage(QWidget):

    def __init__(self, logger):
        super().__init__()
        self.logger  = logger
        self._thread = None
        self._worker = None
        self._vcs    = "none"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("Make Backup")
        title.setObjectName("title")
        layout.addWidget(title)

        # ── Source ────────────────────────────────────────────────────
        src_group = QGroupBox("Source")
        src_v = QVBoxLayout(src_group)

        src_row = QHBoxLayout()
        default_src = config.get("hamilton_folder") or ""
        self.src_input = QLineEdit(default_src)
        self.src_input.setPlaceholderText("Select source folder…")
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

        info = QLabel(
            "✔  All VCS-tracked files are always included.\n"
            "Check folders below to also copy them completely.\n"
            "Expand a checked folder to exclude specific file types."
        )
        info.setStyleSheet("font-size: 12px; font-weight: normal; padding: 2px 0 6px 0;")
        tree_v.addWidget(info)

        self.tree = FolderTreeWidget()
        self.tree.setMinimumHeight(220)
        tree_v.addWidget(self.tree)

        tree_btn_row = QHBoxLayout()
        btn_check_all   = QPushButton("Check all")
        btn_check_all.setObjectName("btnSecondary")
        btn_check_all.clicked.connect(self.tree.check_all)
        btn_uncheck_all = QPushButton("Uncheck all")
        btn_uncheck_all.setObjectName("btnSecondary")
        btn_uncheck_all.clicked.connect(self.tree.uncheck_all)
        tree_btn_row.addWidget(btn_check_all)
        tree_btn_row.addWidget(btn_uncheck_all)
        tree_btn_row.addStretch()
        tree_v.addLayout(tree_btn_row)
        layout.addWidget(tree_group)

        # ── Extra file types ──────────────────────────────────────────
        ext_group = QGroupBox("Additional file types to include (from non-full folders)")
        ext_layout = QHBoxLayout(ext_group)
        ext_layout.setSpacing(14)
        self._ext_checks: dict[str, QCheckBox] = {}
        for ext, label in EXTRA_TYPES:
            cb = QCheckBox(label)
            cb.setChecked(ext in (".trc", ".log"))
            self._ext_checks[ext] = cb
            ext_layout.addWidget(cb)
        ext_layout.addStretch()
        layout.addWidget(ext_group)

        # ── Destination ───────────────────────────────────────────────
        dest_group = QGroupBox("Destination")
        dest_v = QVBoxLayout(dest_group)

        dest_row = QHBoxLayout()
        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("Select destination folder…")
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
        layout.addWidget(dest_group)

        # ── Progress ──────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # ── Action buttons ────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self.btn_abort = QPushButton("✕  Abort")
        self.btn_abort.setObjectName("btnSecondary")
        self.btn_abort.setEnabled(False)
        self.btn_abort.clicked.connect(self._abort)
        self.btn_start = QPushButton("▶  Start Backup")
        self.btn_start.clicked.connect(self._start)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_abort)
        btn_row.addWidget(self.btn_start)
        layout.addLayout(btn_row)

        if default_src and os.path.isdir(default_src):
            self._load_tree(default_src, silent=True)

    # ── Browsing ───────────────────────────────────────────────────────────

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

    # ── Backup ────────────────────────────────────────────────────────────

    def _start(self):
        src  = self.src_input.text().strip()
        dest = self.dest_input.text().strip()

        if not src or not os.path.isdir(src):
            self.logger.warning("Backup: invalid source folder")
            return
        if not dest or not os.path.isdir(dest):
            self.logger.warning("Backup: invalid destination folder")
            return

        full_dirs_map  = self.tree.get_full_dirs()   # {path: excluded_exts}
        extra_exts     = {ext for ext, _ in EXTRA_TYPES if self._ext_checks[ext].isChecked()}

        cfg = BackupConfig(
            src_root   = src,
            dest       = dest,
            to_zip     = self.rb_zip.isChecked(),
            vcs        = self._vcs,
            full_dirs  = full_dirs_map,
            vcs_dirs   = {src},
            extra_exts = extra_exts,
        )

        self._worker = BackupWorker(cfg)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self.logger.info)
        self._worker.finished.connect(self._on_finished)
        self._thread.started.connect(self._worker.run)

        self.btn_start.setEnabled(False)
        self.btn_abort.setEnabled(True)
        self.progress_bar.setVisible(True)
        self._thread.start()
        self.logger.info("Backup started…")

    def _abort(self):
        if self._worker:
            self._worker.abort()
        self.logger.warning("Backup abort requested…")

    def _on_finished(self, success: bool, summary: str):
        self._thread.quit()
        self._thread.wait()
        self.btn_start.setEnabled(True)
        self.btn_abort.setEnabled(False)
        self.progress_bar.setVisible(False)
        if success:
            self.logger.info(f"✅ Backup complete – {summary}")
        else:
            self.logger.error(f"❌ Backup failed – {summary}")
