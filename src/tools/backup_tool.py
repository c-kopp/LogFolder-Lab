import os
import shutil
import zipfile
import sqlite3
import subprocess

from pathlib import Path
from datetime import date

from PyQt6.QtCore import QObject, pyqtSignal

# ──────────────────────────────────────────────────────────────────────────────
# VCS detection
# ──────────────────────────────────────────────────────────────────────────────

def detect_vcs(folder: str) -> str:
    if os.path.isdir(os.path.join(folder, ".svn")):
        return "svn"

    if os.path.isdir(os.path.join(folder, ".git")):
        return "git"

    return "none"


def _get_svn_tracked(folder: str) -> set[str]:
    tracked: set[str] = set()

    wc_db = os.path.join(folder, ".svn", "wc.db")
    if not os.path.isfile(wc_db):
        for parent in Path(folder).parents:
            candidate = parent / ".svn" / "wc.db"
            if candidate.is_file():
                wc_db = str(candidate)
                break

    if not os.path.isfile(wc_db):
        return tracked

    try:
        conn = sqlite3.connect(wc_db)
        cur  = conn.cursor()
        cur.execute("""
            SELECT local_relpath FROM nodes
            WHERE kind = 'file' AND presence = 'normal'
            AND local_relpath != ''
        """)
        wc_root = str(Path(wc_db).parent.parent)

        for (rel_path,) in cur.fetchall():
            abs_path = os.path.normpath(
                os.path.join(wc_root, rel_path.replace("/", os.sep))
            )
            if os.path.isfile(abs_path) and abs_path.startswith(os.path.abspath(folder)):
                tracked.add(abs_path)
        conn.close()

    except Exception:
        pass

    return tracked


def get_tracked_files(folder: str, vcs: str) -> tuple[set[str], str]:
    tracked: set[str] = set()
    warning = ""
    try:
        if vcs == "svn":
            tracked = _get_svn_tracked(folder)
            if not tracked:
                warning = "No SVN tracked files found - check that .svn/wc.db exists in the source folder."

        elif vcs == "git":
            result = subprocess.run(
                ["git", "-C", folder, "ls-files"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                return tracked, f"Git error: {result.stderr.strip()}"
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    tracked.add(os.path.normpath(os.path.join(folder, line)))

    except Exception as e:
        warning = str(e)

    return tracked, warning


# ──────────────────────────────────────────────────────────────────────────────
# BackupConfig
# ──────────────────────────────────────────────────────────────────────────────

class BackupConfig:
    def __init__(
        self,
        src_root:    str,
        dest:        str,
        to_zip:      bool,
        vcs:         str,
        full_dirs:   dict[str, set[str]],
        backup_name: str = "",
    ):
        self.src_root    = src_root
        self.dest        = dest
        self.to_zip      = to_zip
        self.vcs         = vcs
        self.full_dirs   = full_dirs
        self.backup_name = backup_name


# ──────────────────────────────────────────────────────────────────────────────
# File collector
# ──────────────────────────────────────────────────────────────────────────────

def collect_files(cfg: BackupConfig, tracked: set[str]) -> list[tuple[str, str]]:
    copy_list: list[tuple[str, str]] = []

    for dirpath, dirnames, filenames in os.walk(cfg.src_root):
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".")
            and d not in ("__pycache__", "node_modules")
        ]

        abs_dir = os.path.abspath(dirpath)
        rel_dir = os.path.relpath(dirpath, cfg.src_root)

        matched_full_dir = next(
            (p for p in cfg.full_dirs
             if abs_dir == p or abs_dir.startswith(p + os.sep)),
            None
        )

        for fname in filenames:
            if fname.startswith(".") or fname.startswith("._") or fname.startswith("~"):
                continue

            abs_file = os.path.normpath(os.path.join(dirpath, fname))
            rel_file = os.path.join(rel_dir, fname)
            ext      = os.path.splitext(fname)[1].lower()

            if matched_full_dir is not None:
                if ext and ext not in cfg.full_dirs[matched_full_dir]:
                    copy_list.append((abs_file, rel_file))

            elif abs_file in tracked:
                copy_list.append((abs_file, rel_file))

    return copy_list


# ──────────────────────────────────────────────────────────────────────────────
# BackupWorker
# ──────────────────────────────────────────────────────────────────────────────

class BackupWorker(QObject):
    progress = pyqtSignal(str)        # only for "PROGRESS:cur:total:filename"
    finished = pyqtSignal(bool, str)

    def __init__(self, cfg: BackupConfig, logger):
        super().__init__()
        self.cfg    = cfg
        self.logger = logger
        self._abort = False

    def abort(self):
        self._abort = True

    def run(self):
        backup_name = self.cfg.backup_name or date.today().strftime("%Y-%m-%d")

        try:
            self.logger.info("Reading VCS tracked files...")
            if self.cfg.vcs != "none":
                tracked, warning = get_tracked_files(self.cfg.src_root, self.cfg.vcs)

                if warning:
                    self.logger.warning(warning)

            else:
                tracked = set()

            self.logger.debug(f"{len(tracked)} tracked files found")

            copy_list = collect_files(self.cfg, tracked)
            self.logger.info(f"{len(copy_list)} files to copy")
            self.logger.debug(copy_list)

            if not copy_list:
                self.logger.warning("No files to copy - backup aborted.")
                self.finished.emit(False, "No files to copy - backup aborted.")
                return

            if self._abort:
                self.logger.warning("Aborted by user.")
                self.finished.emit(False, "Aborted by user.")
                return

            if self.cfg.to_zip:
                summary = self._write_zip(copy_list, backup_name)
            else:
                summary = self._copy_folder(copy_list, backup_name)

            self.logger.info(summary)
            self.finished.emit(True, summary)

        except Exception as e:
            self.logger.error(str(e))
            self.finished.emit(False, str(e))

    def _write_zip(self, copy_list: list, backup_name: str) -> str:
        zip_path = os.path.join(self.cfg.dest, backup_name + ".zip")
        total = len(copy_list)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, (abs_src, rel) in enumerate(copy_list):
                if self._abort:
                    raise RuntimeError("Aborted by user.")
                try:
                    zf.write(abs_src, os.path.join(backup_name, rel))
                except Exception as e:
                    self.logger.warning(f"Skip {rel}: {e}")
                self.progress.emit(f"PROGRESS:{i+1}:{total}:{rel}")

        return f"ZIP created: {zip_path}"

    def _copy_folder(self, copy_list: list, backup_name: str) -> str:
        os.environ["COPYFILE_DISABLE"] = "1"
        dest_root = os.path.join(self.cfg.dest, backup_name)
        self.logger.info(f"Copying to: {dest_root}")
        total = len(copy_list)

        for i, (abs_src, rel) in enumerate(copy_list):
            if self._abort:
                raise RuntimeError("Aborted by user.")
            dest_file = os.path.join(dest_root, rel)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            try:
                shutil.copy(abs_src, dest_file)
            except Exception as e:
                self.logger.warning(f"Skip {rel}: {e}")
            self.progress.emit(f"PROGRESS:{i+1}:{total}:{rel}")

        return f"Backup folder: {dest_root}"

