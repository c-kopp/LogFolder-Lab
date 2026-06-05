diff --git a/src/tools/search_tool.py b/src/tools/search_tool.py
--- a/src/tools/search_tool.py
+++ b/src/tools/search_tool.py
@@ -10,7 +10,7 @@
 from pathlib import Path

 OUTPUT_FOLDER = config.get_output_folder("Search")
-os.makedirs(OUTPUT_FOLDER, exist_ok=True)


 def search_logs(folder, start_date, end_date, all_files, file_type, terms, mode, regex, copy, exclude_sim, logger):
@@ -24,7 +24,7 @@
     logger.debug(f"Date range: {start_date} - {end_date}")
     logger.debug(f"All Files: {all_files}")
     logger.debug(f"Terms: {terms}")
-    logger.debug(f"Mode: {mode}")
+    logger.debug("Mode: " + mode)
     logger.debug(f"Filetype: {file_type}")
     logger.debug(f"Regex: {regex}")
     logger.debug(f"Exclude Simulated files: {exclude_sim}")

@@ -102,7 +102,7 @@
         if exclude_sim:
             if "Serial number of Instrument:" in line:
                 serial = line.split("Serial number of Instrument:")[-1].strip()
-                if serial in ("1234", "0000"):
+                if serial == "1234" or serial == "0000":
                     logger.warning(f"Serial Number of Instrument: {serial} -> simulated file")
                     break

@@ -158,7 +158,7 @@
     with open(filename, 'w', encoding='utf-8') as out:
         out.write(f"Search terms : {terms}\n")
         out.write(f"Mode         : {mode}\n")
-        out.write(f"Timestamp    : {timestamp}\n")
+        out.write("Timestamp    : " + timestamp + "\n")
         out.write(f"Results      : {total} matching lines across {len(results)} files\n")
         out.write("=" * 60 + "\n\n")

