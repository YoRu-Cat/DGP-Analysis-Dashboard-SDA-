#!/bin/bash
# GDP Dashboard Launcher for Linux/Mac
# This script launches the GDP Analysis Dashboard

echo "========================================"
echo "  GDP Analysis Dashboard Launcher"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "Python found: $(python3 --version)"
echo

# Check if required file exists
if [ ! -f "gdp_with_continent_filled.xlsx" ]; then
    echo "ERROR: Data file not found!"
    echo "Please ensure 'gdp_with_continent_filled.xlsx' is in this directory"
    exit 1
fi

echo "Data file found!"
echo

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import pandas, matplotlib, seaborn, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo "All dependencies satisfied!"
echo
echo "Launching GDP Analysis Dashboard..."
echo

# Launch the dashboard
python3 gdp_dashboard.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Dashboard failed to start"
    exit 1
fi

echo
echo "Dashboard closed successfully!"
