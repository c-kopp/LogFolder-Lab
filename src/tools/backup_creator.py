import os
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, QThread


# ──────────────────────────────────────────────────────────────────────────────
# Extra file-type definitions
# ──────────────────────────────────────────────────────────────────────────────

EXTRA_TYPES = [
    (".trc",  "Trace files (.trc)"),
    (".log",  "Log files (.log)"),
    (".mp4",  "Video files (.mp4)"),
    (".csv",  "CSV files (.csv)"),
    (".txt",  "Text files (.txt)"),
    (".xlsx", "Excel files (.xlsx)"),
    (".xls",  "Excel files (.xls)"),
    (".mdb",  "Access DB (.mdb)"),
]


# ──────────────────────────────────────────────────────────────────────────────
# VCS helpers
# ──────────────────────────────────────────────────────────────────────────────

def detect_vcs(folder: str) -> str:
    """Returns 'svn', 'git', or 'none'."""
    if os.path.isdir(os.path.join(folder, ".svn")):
        return "svn"
    p = Path(folder)
    for parent in [p, *p.parents]:
        if (parent / ".git").is_dir():
            return "git"
    return "none"


def get_tracked_files(folder: str, vcs: str) -> set:
    """Returns a set of absolute normalised paths tracked by the VCS."""
    tracked = set()
    try:
        if vcs == "svn":
            result = subprocess.run(
                ["svn", "list", "--recursive", folder],
                capture_output=True, text=True, timeout=30
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and not line.endswith("/"):
                    tracked.add(os.path.normpath(os.path.join(folder, line)))

        elif vcs == "git":
            result = subprocess.run(
                ["git", "-C", folder, "ls-files"],
                capture_output=True, text=True, timeout=30
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    tracked.add(os.path.normpath(os.path.join(folder, line)))

    except Exception:
        pass
    return tracked


# ──────────────────────────────────────────────────────────────────────────────
# BackupConfig  (plain dataclass-style object for type clarity)
# ──────────────────────────────────────────────────────────────────────────────

class BackupConfig:
    def __init__(
        self,
        src_root:   str,
        dest:       str,
        to_zip:     bool,
        vcs:        str,
        full_dirs:  dict,   # {abs_path: set[excluded_extensions]}
        vcs_dirs:   set,
        extra_exts: set,
    ):
        self.src_root   = src_root
        self.dest       = dest
        self.to_zip     = to_zip
        self.vcs        = vcs
        self.full_dirs  = full_dirs   # dict[str, set[str]]
        self.vcs_dirs   = vcs_dirs
        self.extra_exts = extra_exts


# ──────────────────────────────────────────────────────────────────────────────
# File collector
# ──────────────────────────────────────────────────────────────────────────────

def collect_files(
    cfg: BackupConfig,
    tracked: set[str],
    progress_cb,
) -> list[tuple[str, str]]:
    """
    Walks the source tree and returns a list of (abs_src, rel_path) tuples.
    Calls progress_cb(message) for status updates.
    """
    copy_list: list[tuple[str, str]] = []

    for dirpath, dirnames, filenames in os.walk(cfg.src_root):
        # skip hidden / vcs metadata
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".") and d not in ("__pycache__", "node_modules")
        ]

        rel_dir = os.path.relpath(dirpath, cfg.src_root)
        abs_dir = os.path.abspath(dirpath)

        # full_dirs override: copy everything except excluded extensions
        matched_full_dir = None
        for full_path in cfg.full_dirs:
            if abs_dir == full_path or abs_dir.startswith(full_path + os.sep):
                matched_full_dir = full_path
                break

        for fname in filenames:
            abs_file = os.path.normpath(os.path.join(dirpath, fname))
            rel_file = os.path.join(rel_dir, fname)
            ext = os.path.splitext(fname)[1].lower() or "(no extension)"

            if matched_full_dir is not None:
                excluded = cfg.full_dirs[matched_full_dir]
                if ext not in excluded:
                    copy_list.append((abs_file, rel_file))
            else:
                # VCS-tracked files + chosen extra extensions
                if abs_file in tracked or ext in cfg.extra_exts:
                    copy_list.append((abs_file, rel_file))

    return copy_list


# ──────────────────────────────────────────────────────────────────────────────
# Background worker
# ──────────────────────────────────────────────────────────────────────────────

class BackupWorker(QObject):
    progress = pyqtSignal(str)        # log message
    finished = pyqtSignal(bool, str)  # success, summary

    def __init__(self, cfg: BackupConfig):
        super().__init__()
        self.cfg    = cfg
        self._abort = False

    def abort(self):
        self._abort = True

    def run(self):
        cfg = self.cfg

        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        src_name    = os.path.basename(cfg.src_root.rstrip("/\\"))
        backup_name = f"{src_name}_backup_{timestamp}"

        try:
            # 1. Tracked files
            self.progress.emit("🔍 Reading VCS tracked files…")
            tracked = get_tracked_files(cfg.src_root, cfg.vcs) if cfg.vcs != "none" else set()
            self.progress.emit(f"   {len(tracked)} tracked files found")

            # 2. Collect
            self.progress.emit("📋 Collecting files…")
            copy_list = collect_files(cfg, tracked, self.progress.emit)
            self.progress.emit(f"   {len(copy_list)} files to copy")

            if self._abort:
                self.finished.emit(False, "Aborted by user.")
                return

            # 3. Copy / ZIP
            if cfg.to_zip:
                summary = self._write_zip(copy_list, backup_name)
            else:
                summary = self._copy_folder(copy_list, backup_name)

            self.finished.emit(True, summary)

        except Exception as e:
            self.finished.emit(False, str(e))

    # ── private ───────────────────────────────────────────────────────────────

    def _write_zip(self, copy_list: list, backup_name: str) -> str:
        zip_path = os.path.join(self.cfg.dest, backup_name + ".zip")
        self.progress.emit(f"📦 Creating ZIP: {zip_path}")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, (abs_src, rel) in enumerate(copy_list):
                if self._abort:
                    raise RuntimeError("Aborted by user.")
                try:
                    zf.write(abs_src, os.path.join(backup_name, rel))
                except Exception as e:
                    self.progress.emit(f"   ⚠ Skip {rel}: {e}")
                if i % 50 == 0:
                    self.progress.emit(f"   … {i}/{len(copy_list)}")
        return f"ZIP created: {zip_path}"

    def _copy_folder(self, copy_list: list, backup_name: str) -> str:
        dest_root = os.path.join(self.cfg.dest, backup_name)
        self.progress.emit(f"📁 Copying to: {dest_root}")
        for i, (abs_src, rel) in enumerate(copy_list):
            if self._abort:
                raise RuntimeError("Aborted by user.")
            dest_file = os.path.join(dest_root, rel)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            try:
                shutil.copy2(abs_src, dest_file)
            except Exception as e:
                self.progress.emit(f"   ⚠ Skip {rel}: {e}")
            if i % 50 == 0:
                self.progress.emit(f"   … {i}/{len(copy_list)}")
        return f"Backup folder: {dest_root}"
