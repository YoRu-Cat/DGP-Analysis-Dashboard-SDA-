# GDP Dashboard Test Script
# Dashboard theek se chal rahi hai ya nahi ye check karta hai

import pandas as pd
import numpy as np
import json
import os
import sys
from functools import reduce


def test_data_loading():
    # Pehle dekhte hain data load ho raha hai ya nahi
    print("Test 1: Data Loading...", end=" ")
    try:
        # Load config for file path
        config_path = 'config.json'
        config = json.load(open(config_path, 'r', encoding='utf-8')) if os.path.exists(config_path) else None
        file_path = config['data']['file_path'] if config else 'gdp_with_continent_filled.xlsx'
        
        file_extension = os.path.splitext(file_path)[1].lower()
        loader_map = {
            '.csv': lambda fp: pd.read_csv(fp),
            '.xlsx': lambda fp: pd.read_excel(fp),
            '.xls': lambda fp: pd.read_excel(fp)
        }
        df = loader_map.get(file_extension, lambda fp: pd.read_excel(fp))(file_path)
        
        assert len(df) > 0, "DataFrame is empty"
        assert 'Country Name' in df.columns, "Missing Country Name column"
        assert 'Continent' in df.columns, "Missing Continent column"
        print("\u2713 PASSED")
        return True, df
    except Exception as e:
        print(f"\u2717 FAILED: {e}")
        return False, None


def test_data_structure(df):
    # Data ki structure check karo
    print("Test 2: Data Structure...", end=" ")
    try:
        year_columns = list(filter(lambda col: isinstance(col, int), df.columns))
        assert len(year_columns) > 0, "No year columns found"
        assert min(year_columns) >= 1960, "Years start before 1960"
        assert max(year_columns) <= 2030, "Years extend beyond 2030"
        print("\u2713 PASSED")
        return True
    except Exception as e:
        print(f"\u2717 FAILED: {e}")
        return False


def test_data_integrity(df):
    # Data sahi hai ya nahi check karo
    print("Test 3: Data Integrity...", end=" ")
    try:
        # Zaroori columns check karo - functional check using all + map
        required_cols = ['Country Name', 'Country Code', 'Continent']
        missing_cols = list(filter(lambda col: col not in df.columns, required_cols))
        assert not missing_cols, f"Missing columns: {', '.join(missing_cols)}"
        
        # Country names check karo
        assert df['Country Name'].notna().all(), "Some countries have null names"
        
        # Continents check karo
        continents = df['Continent'].dropna().unique()
        assert len(continents) > 0, "No continents found"
        
        print("\u2713 PASSED")
        return True
    except Exception as e:
        print(f"\u2717 FAILED: {e}")
        return False


def test_numerical_data(df):
    # GDP numbers sahi hain ya nahi
    print("Test 4: Numerical Data...", end=" ")
    try:
        year_columns = list(filter(lambda col: isinstance(col, int), df.columns))
        
        # Koi GDP data hai ya nahi
        total_data_points = df[year_columns].notna().sum().sum()
        assert total_data_points > 0, "No GDP data found"
        
        # Negative values check karo
        has_negative = (df[year_columns] < 0).any().any()
        if has_negative:
            print("\u26A0 WARNING: Negative GDP values detected", end=" ")
        
        print("\u2713 PASSED")
        return True
    except Exception as e:
        print(f"\u2717 FAILED: {e}")
        return False


def test_imports():
    # Saari libraries install hain ya nahi
    print("Test 5: Required Libraries...", end=" ")
    try:
        import pandas
        import numpy
        import matplotlib
        import seaborn
        import tkinter
        print("\u2713 PASSED")
        return True
    except ImportError as e:
        print(f"\u2717 FAILED: {e}")
        return False


def test_basic_analysis(df):
    # Basic analysis functions test karo
    print("Test 6: Basic Analysis...", end=" ")
    try:
        year_columns = list(filter(lambda col: isinstance(col, int), df.columns))
        latest_year = max(year_columns)
        
        # Top countries nikalne ki koshish karo
        top_10 = df.nlargest(10, latest_year)
        assert len(top_10) == 10, "Failed to get top 10 countries"
        
        # Continent se filter karo
        continent = df['Continent'].dropna().iloc[0]
        continent_data = df[df['Continent'] == continent]
        assert len(continent_data) > 0, "Failed to filter by continent"
        
        # Year range test karo
        year_subset = year_columns[:10]
        subset_data = df[year_subset]
        assert subset_data.shape[1] == 10, "Failed to subset years"
        
        print("\u2713 PASSED")
        return True
    except Exception as e:
        print(f"\u2717 FAILED: {e}")
        return False


def test_statistics(df):
    # Statistical calculations test karo
    print("Test 7: Statistical Calculations...", end=" ")
    try:
        year_columns = list(filter(lambda col: isinstance(col, int), df.columns))
        latest_year = max(year_columns)
        
        # Basic statistics nikalo
        latest_data = df[latest_year].dropna()
        mean_gdp = latest_data.mean()
        median_gdp = latest_data.median()
        std_gdp = latest_data.std()
        
        assert not np.isnan(mean_gdp), "Mean calculation failed"
        assert not np.isnan(median_gdp), "Median calculation failed"
        assert not np.isnan(std_gdp), "Std deviation calculation failed"
        
        # Growth rate calculate karo
        first_year = min(year_columns)
        sample_country = df.iloc[0]
        gdp_first = sample_country[first_year]
        gdp_last = sample_country[latest_year]
        
        if not np.isnan(gdp_first) and not np.isnan(gdp_last) and gdp_first != 0:
            growth = ((gdp_last - gdp_first) / gdp_first) * 100
            assert not np.isnan(growth), "Growth calculation failed"
        
        print("\u2713 PASSED")
        return True
    except Exception as e:
        print(f"\u2717 FAILED: {e}")
        return False


def test_data_coverage(df):
    # Kitna data available hai check karo
    print("Test 8: Data Coverage...", end=" ")
    try:
        year_columns = list(filter(lambda col: isinstance(col, int), df.columns))
        
        # Data coverage calculate karo
        total_cells = len(df) * len(year_columns)
        filled_cells = df[year_columns].notna().sum().sum()
        coverage = (filled_cells / total_cells) * 100
        
        print(f"✓ PASSED (Coverage: {coverage:.1f}%)")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def main():
    # Saare tests run karo
    print("\n" + "="*60)
    print("  GDP DASHBOARD TEST SUITE")
    print("="*60 + "\n")
    
    # Test 1: Data load ho raha hai?
    success, df = test_data_loading()
    if not success:
        print("\nCritical error: Cannot load data. Stopping tests.")
        return False
    
    # Run all remaining tests using reduce to count passes
    test_functions = [
        lambda: test_data_structure(df),
        lambda: test_data_integrity(df),
        lambda: test_numerical_data(df),
        lambda: test_imports(),
        lambda: test_basic_analysis(df),
        lambda: test_statistics(df),
        lambda: test_data_coverage(df)
    ]
    
    remaining_passed = reduce(
        lambda count, test_fn: count + (1 if test_fn() else 0),
        test_functions,
        0
    )
    
    tests_passed = 1 + remaining_passed  # +1 for data loading test
    total_tests = 8
    
    # Results summary
    print("\n" + "="*60)
    print(f"  TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    print("="*60)
    
    if tests_passed == total_tests:
        print("\n\u2713 All tests passed! The dashboard is ready to use.")
        print("  Run 'python gdp_dashboard_refactored.py' to launch the application.")
    else:
        print(f"\n\u26A0 {total_tests - tests_passed} test(s) failed.")
        print("  Please check the errors above and fix them before running the dashboard.")
    
    print("\n" + "="*60 + "\n")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
