@echo off
cd /d "%~dp0"
python -m pip install --quiet opencv-python pillow reportlab customtkinter
start "" pythonw rotopdf.py
