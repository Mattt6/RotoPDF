@echo off
cd /d "%~dp0"
python -m pip install --quiet opencv-python pillow reportlab customtkinter pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name RotoPDF --icon icon.ico --add-data "icon.ico;." --collect-all customtkinter rotopdf.py
echo.
echo Termine : l'application est dans dist\RotoPDF.exe
pause
