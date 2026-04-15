# LogFolder-Lab


PyInstaller --onefile --windowed --name LogFolderLab --icon=LFL.ico --add-data "styles.qss;." --add-data "LFL.ico;." --add-data "ico;ico" --add-data "img;img" --add-binary "C:\Users\Windows10\miniconda3\envs\LogFolderLab\Lib\site-packages\pylibdmtx\libdmtx-64.dll;pylibdmtx" .\main.py