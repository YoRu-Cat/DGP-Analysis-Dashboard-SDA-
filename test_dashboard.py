# GDP Dashboard Test Script
# Dashboard theek se chal rahi hai ya nahi ye check karta hai

import pandas as pd
import numpy as np
import sys


def test_data_loading():
    # Pehle dekhte hain data load ho raha hai ya nahi
    print("Test 1: Data Loading...", end=" ")
    try:
        df = pd.read_excel('gdp_with_continent_filled.xlsx')
        assert len(df) > 0, "DataFrame is empty"
        assert 'Country Name' in df.columns, "Missing Country Name column"
        assert 'Continent' in df.columns, "Missing Continent column"
        print("✓ PASSED")
        return True, df
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False, None


def test_data_structure(df):
    # Data ki structure check karo
    print("Test 2: Data Structure...", end=" ")
    try:
        year_columns = [col for col in df.columns if isinstance(col, int)]
        assert len(year_columns) > 0, "No year columns found"
        assert min(year_columns) >= 1960, "Years start before 1960"
        assert max(year_columns) <= 2030, "Years extend beyond 2030"
        print("✓ PASSED")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_data_integrity(df):
    # Data sahi hai ya nahi check karo
    print("Test 3: Data Integrity...", end=" ")
    try:
        # Zaroori columns check karo
        required_cols = ['Country Name', 'Country Code', 'Continent']
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"
        
        # Country names check karo
        assert df['Country Name'].notna().all(), "Some countries have null names"
        
        # Continents check karo
        continents = df['Continent'].dropna().unique()
        assert len(continents) > 0, "No continents found"
        
        print("✓ PASSED")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_numerical_data(df):
    # GDP numbers sahi hain ya nahi
    print("Test 4: Numerical Data...", end=" ")
    try:
        year_columns = [col for col in df.columns if isinstance(col, int)]
        
        # Koi GDP data hai ya nahi
        total_data_points = df[year_columns].notna().sum().sum()
        assert total_data_points > 0, "No GDP data found"
        
        # Negative values check karo
        has_negative = (df[year_columns] < 0).any().any()
        if has_negative:
            print("⚠ WARNING: Negative GDP values detected", end=" ")
        
        print("✓ PASSED")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
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
        print("✓ PASSED")
        return True
    except ImportError as e:
        print(f"✗ FAILED: {e}")
        return False


def test_basic_analysis(df):
    # Basic analysis functions test karo
    print("Test 6: Basic Analysis...", end=" ")
    try:
        year_columns = [col for col in df.columns if isinstance(col, int)]
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
        
        print("✓ PASSED")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_statistics(df):
    # Statistical calculations test karo
    print("Test 7: Statistical Calculations...", end=" ")
    try:
        year_columns = [col for col in df.columns if isinstance(col, int)]
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
        
        print("✓ PASSED")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_data_coverage(df):
    # Kitna data available hai check karo
    print("Test 8: Data Coverage...", end=" ")
    try:
        year_columns = [col for col in df.columns if isinstance(col, int)]
        
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
    
    tests_passed = 0
    total_tests = 8
    
    # Test 1: Data load ho raha hai?
    success, df = test_data_loading()
    if success:
        tests_passed += 1
    else:
        print("\nCritical error: Cannot load data. Stopping tests.")
        return
    
    # Baaki tests chalaao
    if test_data_structure(df):
        tests_passed += 1
    
    # Test 3: Data Integrity
    if test_data_integrity(df):
        tests_passed += 1
    
    # Test 4: Numerical Data
    if test_numerical_data(df):
        tests_passed += 1
    
    # Test 5: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 6: Basic Analysis
    if test_basic_analysis(df):
        tests_passed += 1
    
    # Test 7: Statistics
    if test_statistics(df):
        tests_passed += 1
    
    # Test 8: Data Coverage
    if test_data_coverage(df):
        tests_passed += 1
    
    # Results summary
    print("\n" + "="*60)
    print(f"  TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    print("="*60)
    
    if tests_passed == total_tests:
        print("\n✓ All tests passed! The dashboard is ready to use.")
        print("  Run 'python gdp_dashboard.py' to launch the application.")
    else:
        print(f"\n⚠ {total_tests - tests_passed} test(s) failed.")
        print("  Please check the errors above and fix them before running the dashboard.")
    
    print("\n" + "="*60 + "\n")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
