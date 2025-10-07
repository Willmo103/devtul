@echo off
REM :: This script syncs the uv app, installs the [dev] deps and runs the pyinstaller to build the exe.
REM Enhanced: safer execution, logging, argument parsing, error handling.

setlocal enabledelayedexpansion

:: Defaults
set "APP_NAME=devtul"
set "ENTRY=src/devtul/main.py"
set "MODE=onefile"    :: options: onefile or onedir
set "CONSOLE=yes"     :: yes => --console (default), no => --windowed
set "DO_SYNC=yes"
set "DO_INSTALL=yes"
set "LOG_DIR=build_logs"
set "CLEAN=no"

:: Timestamp and logfile
for /f "tokens=1-4 delims=/ :.,-" %%a in ("%date% %time%") do (
  set "TS=%date%_%time%"
)
:: sanitize TS for filename
set "TS=%date%_%time%"
set "TS=%TS: =_%"
set "TS=%TS::=_%"
set "TS=%TS:/=_%"
set "TS=%TS:.=_%"
set "LOGFILE=%LOG_DIR%\build_%TS%.log"

:: Help/usage
:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--help" goto usage
if /I "%~1"=="-h" goto usage
if /I "%~1"=="--clean" ( set "CLEAN=yes" & shift & goto parse_args )
if /I "%~1"=="--no-sync" ( set "DO_SYNC=no" & shift & goto parse_args )
if /I "%~1"=="--no-install" ( set "DO_INSTALL=no" & shift & goto parse_args )
if /I "%~1"=="--onefile" ( set "MODE=onefile" & shift & goto parse_args )
if /I "%~1"=="--onedir" ( set "MODE=onedir" & shift & goto parse_args )
if /I "%~1"=="--windowed" ( set "CONSOLE=no" & shift & goto parse_args )
if /I "%~1"=="--console" ( set "CONSOLE=yes" & shift & goto parse_args )
if /I "%~1:~0,7%"=="--name=" (
  set "APP_NAME=%~1"
  set "APP_NAME=%APP_NAME:--name=%"
  shift
  goto parse_args
)
:: unknown arg: ignore but show a warning
echo Warning: unknown argument "%~1"
shift
goto parse_args

:args_done

:: Show help
:usage
echo Usage: %~n0 [--clean] [--no-sync] [--no-install] [--onefile|--onedir] [--windowed] [--name=appname]
echo.
echo Examples:
echo   %~n0 --clean --name=myapp --onefile
exit /b 0

:: Ensure log directory exists
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Write header to logfile
(
  echo ------------------------------------------------------------
  echo Build started at %date% %time%
  echo Script: %~f0
  echo App: %APP_NAME%
  echo Entry: %ENTRY%
  echo Mode: %MODE%
  echo Console: %CONSOLE%
  echo DO_SYNC: %DO_SYNC%
  echo DO_INSTALL: %DO_INSTALL%
  echo CLEAN: %CLEAN%
  echo ------------------------------------------------------------
) > "%LOGFILE%"

:: Move to script directory to ensure relative paths are correct
pushd "%~dp0"
if errorlevel 1 (
  echo Failed to change directory to script location. >> "%LOGFILE%"
  echo Failed to change directory to script location.
  goto fail
)

:: Helper: check command exists
:check_cmd
rem %1 = command to check
where %1 >nul 2>&1
if errorlevel 1 (
  echo Required command "%1" not found. >> "%LOGFILE%"
  echo Required command "%1" not found.
  exit /b 2
)
exit /b 0

:: Optional clean
if /I "%CLEAN%"=="yes" (
  echo Cleaning previous build artifacts... | tee "%LOGFILE%"
  if exist "dist" (
    rmdir /s /q "dist" >> "%LOGFILE%" 2>&1
    if errorlevel 1 (
      echo Failed to remove dist directory. >> "%LOGFILE%"
      echo Failed to remove dist directory.
      goto fail
    )
  )
  if exist "build" (
    rmdir /s /q "build" >> "%LOGFILE%" 2>&1
    if errorlevel 1 (
      echo Failed to remove build directory. >> "%LOGFILE%"
      echo Failed to remove build directory.
      goto fail
    )
  )
  if exist "%APP_NAME%.spec" del /f /q "%APP_NAME%.spec" >> "%LOGFILE%" 2>&1
)

:: Step 1: uv sync (optional)
if /I "%DO_SYNC%"=="yes" (
  echo Running: uv sync
  where uv >nul 2>&1
  if errorlevel 1 (
    echo uv not found in PATH. Skipping uv sync. >> "%LOGFILE%"
    echo uv not found in PATH. Skipping uv sync.
  ) else (
    echo --- uv sync output --- >> "%LOGFILE%"
    call uv sync >> "%LOGFILE%" 2>&1
    if errorlevel 1 (
      echo uv sync failed. Check log: %LOGFILE% >> "%LOGFILE%"
      echo uv sync failed. Check log: %LOGFILE%
      goto fail
    )
  )
)

:: Step 2: install dev dependencies (optional)
if /I "%DO_INSTALL%"=="yes" (
  echo Installing development dependencies...
  echo Attempting: uv pip install .[dev] >> "%LOGFILE%"
  where uv >nul 2>&1
  if errorlevel 0 (
    call uv pip install .[dev] >> "%LOGFILE%" 2>&1
    if errorlevel 1 (
      echo uv pip install failed, falling back to python -m pip install -e .[dev] >> "%LOGFILE%"
      call python -m pip install -e .[dev] >> "%LOGFILE%" 2>&1
      if errorlevel 1 (
        echo pip install failed. See log: %LOGFILE% >> "%LOGFILE%"
        echo pip install failed. See log: %LOGFILE%
        goto fail
      )
    )
  ) else (
    echo uv not available; using python -m pip install -e .[dev] >> "%LOGFILE%"
    call python -m pip install -e .[dev] >> "%LOGFILE%" 2>&1
    if errorlevel 1 (
      echo pip install failed. See log: %LOGFILE% >> "%LOGFILE%"
      echo pip install failed. See log: %LOGFILE%
      goto fail
    )
  )
)

:: Step 3: run pyinstaller
echo Preparing to run PyInstaller...
where pyinstaller >nul 2>&1
if errorlevel 1 (
  echo pyinstaller not found on PATH; will use python -m PyInstaller >> "%LOGFILE%"
  set "PYINST_CMD=python -m PyInstaller"
) else (
  set "PYINST_CMD=pyinstaller"
)

set "PYI_FLAGS="
if /I "%MODE%"=="onefile" set "PYI_FLAGS=%PYI_FLAGS% --onefile"
if /I "%MODE%"=="onedir" set "PYI_FLAGS=%PYI_FLAGS%"
if /I "%CONSOLE%"=="no" set "PYI_FLAGS=%PYI_FLAGS% --windowed" else set "PYI_FLAGS=%PYI_FLAGS% --console"

echo Building %APP_NAME% (%MODE%)...
echo Command: %PYINST_CMD% --name %APP_NAME% %PYI_FLAGS% %ENTRY% >> "%LOGFILE%"
%PYINST_CMD% --name %APP_NAME% %PYI_FLAGS% %ENTRY% >> "%LOGFILE%" 2>&1
if errorlevel 1 (
  echo PyInstaller failed. Check log: %LOGFILE% >> "%LOGFILE%"
  echo PyInstaller failed. Check log: %LOGFILE%
  goto fail
)

:: Success
echo ------------------------------------------------------------
echo Build completed successfully at %date% %time% >> "%LOGFILE%"
echo Build completed successfully.
echo Artifact(s) located in: dist\%APP_NAME%
echo Log: %LOGFILE%
popd
exit /b 0

:fail
echo ------------------------------------------------------------
echo Build failed at %date% %time% >> "%LOGFILE%"
echo Build failed. See log: %LOGFILE%
popd
exit /b 1
