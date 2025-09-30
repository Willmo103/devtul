:: This script syncs the uv app, installs the [dev] deps and runs the pyinstaller to build the exe.
@echo off

where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found, installing...
) else (
    echo PyInstaller found, skipping install.
    goto build
)
python -m pip install -U pyinstaller
if errorlevel 1 (
    echo Failed to install pyinstaller
    exit /b 1
)

:build
echo Building executable with PyInstaller...
pyinstaller --name devtul --onefile --console main.py
echo Build complete. Executable is in the dist\ folder.
copy dist\devtul.exe C:\Users\AppData\local\Programs\devtul\devtul.exe /Y
exit /b 0

