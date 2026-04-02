import os
import re
import shutil
import datetime
from pathlib import Path
from src.core.file_search import getFiles

OUTPUT_FOLDER = "results/searched"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def search_logs(folder, start_date, end_date, all_files, file_type, terms, mode, regex, copy, logger):
    logger.info("Search started")
    logger.debug(f"Folder: {folder}")
    logger.debug(f"Date range: {start_date} - {end_date}")
    logger.debug(f"All Files: {all_files}")
    logger.debug(f"Terms: {terms}")
    logger.debug(f"Mode: {mode}")
    logger.debug(f"Filetype: {file_type}")
    logger.debug(f"Regex: {regex}")

    files = getFiles(folder, start_date, end_date, all_files, file_type)

    if isinstance(terms, str):
        terms = [t.strip() for t in terms.split(';')]

    if len(files) == 0:
        logger.warning(f"No {file_type} files found in {folder}")
        return

    results = {}
    copied = 0

    if copy:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_terms = "-".join(re.sub(r'[<>:"/\\|?*]', '', t)[:30] for t in terms)
        copy_folder = os.path.join(OUTPUT_FOLDER, f"files_{safe_terms}_{timestamp}")
        os.makedirs(copy_folder, exist_ok=True)
    else:
        copy_folder = None

    for file in files:
        mtime = datetime.datetime.fromtimestamp(Path(file).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"[{mtime}]\t{os.path.basename(file)}")

        matched_lines = _search_logs(file, terms, mode, regex, logger)

        if matched_lines:
            results[file] = matched_lines

            if copy:
                dest = os.path.join(copy_folder, os.path.basename(file))
                shutil.copy2(file, dest)
                logger.info(f"Copied file to: {copy_folder}")
                copied += 1

    logger.debug(f"copy_folder contents: {os.listdir(copy_foler)}")
    if copy and copied == 0:
        os.rmdir(copy_folder)
        logger.debug(f"Removed empty copy folder: {copy_folder}")

    _write_results(results, terms, mode, copy, logger)
    logger.info("Search finished")


def _search_logs(file, terms, mode, regex, logger):
    """
    Searches a single file for lines matching the given terms.
    Returns a list of (line_number, line) tuples for matches.
    """
    matched_lines = []

    try:
        with open(file, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f, start=1):
                if _line_matches(line, terms, mode, regex):
                    matched_lines.append((i, line.rstrip()))
    except Exception as e:
        logger.error(f"Error reading file {file}: {e}")

    logger.debug(f"  -> {len(matched_lines)} matching lines found in {os.path.basename(file)}")
    return matched_lines


def _line_matches(line, terms, mode, regex):
    """
    Checks whether a line matches the search terms.
    mode: 'and' -> all terms must match, 'or' -> at least one term must match
    regex: if True, terms are treated as regular expressions
    """
    def matches_term(line, term):
        if regex:
            return bool(re.search(term, line))
        else:
            return term in line

    if mode.lower() == 'and':
        return all(matches_term(line, term) for term in terms)
    else:  # 'or'
        return any(matches_term(line, term) for term in terms)


def _write_results(results, terms, mode, copy, logger):
    """
    Writes all matched lines to a result file in OUTPUT_FOLDER.
    """
    if not results:
        logger.warning("No matching lines found in any file.")
        return

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_terms = "-".join(re.sub(r'[<>:"/\\|?*]', '', t)[:30] for t in terms)
    filename = os.path.join(OUTPUT_FOLDER, f"search_{safe_terms}_{timestamp}.txt")

    total = 0
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(f"Search terms : {terms}\n")
        out.write(f"Mode         : {mode}\n")
        out.write(f"Timestamp    : {timestamp}\n")
        out.write("=" * 60 + "\n\n")

        for file, lines in results.items():
            out.write(f"{os.path.basename(file)}\n")
            for line_no, line in lines:
                out.write(f"\tLine {line_no}>\t{line}\n")
            out.write("\n")
            total += len(lines)



    logger.info(f"Results written to {filename} ({total} matching lines across {len(results)} files)")

