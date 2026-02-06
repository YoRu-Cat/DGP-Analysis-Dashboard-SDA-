@echo off
REM GDP Dashboard Launcher for Windows
REM This script launches the GDP Analysis Dashboard

echo ========================================
echo   GDP Analysis Dashboard Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if required file exists
if not exist "gdp_with_continent_filled.xlsx" (
    echo ERROR: Data file not found!
    echo Please ensure 'gdp_with_continent_filled.xlsx' is in this directory
    pause
    exit /b 1
)

echo Data file found!
echo.

REM Check if required packages are installed
echo Checking dependencies...
python -c "import pandas, matplotlib, seaborn, numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo All dependencies satisfied!
echo.
echo Launching GDP Analysis Dashboard...
echo.

REM Launch the dashboard
python gdp_dashboard.py

if errorlevel 1 (
    echo.
    echo ERROR: Dashboard failed to start
    pause
    exit /b 1
)

echo.
echo Dashboard closed successfully!
pause
