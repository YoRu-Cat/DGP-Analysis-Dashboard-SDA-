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
python -c "import pandas, matplotlib, seaborn, numpy, streamlit, plotly" >nul 2>&1
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
echo Launching GDP Analysis Dashboard (Streamlit)...
echo.

REM Launch the Streamlit dashboard
python -m streamlit run gdp_dashboard_streamlit.py --server.headless=true --theme.base=dark --theme.primaryColor=#1d9bf0 --theme.backgroundColor=#0a0a0a --theme.secondaryBackgroundColor=#111111 --theme.textColor=#e7e9ea

if errorlevel 1 (
    echo.
    echo ERROR: Dashboard failed to start
    pause
    exit /b 1
)

echo.
echo Dashboard closed successfully!
pause
