@echo off
REM Build script for Steam Shelf GUI
REM This script builds the PyInstaller executable with the correct paths

echo Building Steam Shelf GUI executable...
cd /d "%~dp0"
pyinstaller --onefile --noconsole --icon=icon.ico --name=steam-shelf --paths=src .\scripts\steam-shelf-gui.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!
    echo Executable created at: dist\steam-shelf.exe
) else (
    echo.
    echo Build failed with error code %ERRORLEVEL%
)

pause