@echo off
setlocal enabledelayedexpansion

:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: uv is not installed. Please install it first.
    exit /b 1
)

:: Check if Python virtual environment exists, if not create it
if not exist ".venv" (
    echo Creating Python virtual environment...
    uv venv
)

:: Activate the virtual environment
call .venv\Scripts\activate.bat

:: Install dependencies if needed
if not exist "uv.lock" (
    echo Installing dependencies...
    uv pip install -e .
)

:: Start the MCP server
echo Starting MCP server...
uv run python src/mcp-server/server.py

endlocal
