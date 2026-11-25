@echo off
cd /d "%~dp0"
echo === 1/2 Construction de l'application ===
python -m pip install --quiet opencv-python pillow reportlab customtkinter pyinstaller
python -m PyInstaller --noconfirm --onedir --windowed --name RotoPDF --icon icon.ico --add-data "icon.ico;." --collect-all customtkinter rotopdf.py
if errorlevel 1 goto fail

echo === 2/2 Construction de l'installateur ===
for %%V in (7 6) do (
  if exist "%ProgramFiles%\Inno Setup %%V\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup %%V\ISCC.exe"
  if exist "%ProgramFiles(x86)%\Inno Setup %%V\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup %%V\ISCC.exe"
  if exist "%LOCALAPPDATA%\Programs\Inno Setup %%V\ISCC.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup %%V\ISCC.exe"
  if defined ISCC goto build
)
where ISCC >nul 2>&1
if not errorlevel 1 (
  set "ISCC=ISCC"
  goto build
)
echo.
echo Inno Setup est introuvable. Installe-le (gratuit) : https://jrsoftware.org/isdl.php
echo Ou en une commande : winget install --id JRSoftware.InnoSetup.7 -e -s winget
echo puis relance ce script.
pause
exit /b 1

:build
"%ISCC%" installer.iss
if errorlevel 1 goto fail
echo.
echo Termine : l'installateur est dans Output\RotoPDF_Setup.exe
pause
exit /b 0

:fail
echo.
echo Une erreur est survenue.
pause
exit /b 1
