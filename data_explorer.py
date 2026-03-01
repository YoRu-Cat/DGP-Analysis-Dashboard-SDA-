# GDP Data Explorer
# Command line se jaldi se data dekh sakte hain

import pandas as pd
import json
import os
import sys
from functools import reduce


def load_config(config_path='config.json'):
    """Load configuration from config.json"""
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_data(config):
    """Data load karo using config file path"""
    try:
        file_path = config['data']['file_path']
        file_extension = os.path.splitext(file_path)[1].lower()
        
        loader_map = {
            '.csv': lambda fp: pd.read_csv(fp),
            '.xlsx': lambda fp: pd.read_excel(fp),
            '.xls': lambda fp: pd.read_excel(fp)
        }
        
        loader = loader_map.get(file_extension)
        if loader is None:
            print(f"Unsupported file format: {file_extension}")
            return None
        
        return loader(file_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def show_menu():
    """Menu options dikhao"""
    print("\n" + "="*60)
    print("  GDP DATA EXPLORER")
    print("="*60)
    print("1. Show all countries")
    print("2. Show all continents")
    print("3. Search country by name")
    print("4. Show country GDP for specific year")
    print("5. Show top N countries by GDP (latest year)")
    print("6. Show countries in a continent")
    print("7. Show data summary")
    print("8. Show available years")
    print("9. Compare two countries")
    print("0. Exit")
    print("="*60)


def show_all_countries(df):
    """Saare countries ki list"""
    countries = sorted(df['Country Name'].unique())
    print(f"\nTotal Countries: {len(countries)}\n")
    list(map(
        lambda pair: print(f"{pair[0]:3d}. {pair[1]}"),
        enumerate(countries, 1)
    ))


def show_all_continents(df):
    """Saare continents aur unke countries"""
    continents = sorted(df['Continent'].dropna().unique())
    print(f"\nTotal Continents: {len(continents)}\n")
    list(map(
        lambda continent: print(f"  {continent:<20s} ({len(df[df['Continent'] == continent])} countries)"),
        continents
    ))


def search_country(df, search_term):
    """Naam se country search karo"""
    matches = df[df['Country Name'].str.contains(search_term, case=False, na=False)]
    if matches.empty:
        print(f"\nNo countries found matching '{search_term}'")
    else:
        print(f"\nFound {len(matches)} match(es):\n")
        list(map(
            lambda row: print(f"  {row[1]['Country Name']} ({row[1]['Country Code']}) - {row[1]['Continent']}"),
            matches.iterrows()
        ))


def show_country_gdp_for_year(df, country, year):
    """Specific country aur year ka GDP dikhao"""
    country_data = df[df['Country Name'].str.lower() == country.lower()]
    if country_data.empty:
        print(f"\nCountry '{country}' not found")
        return
    
    try:
        year = int(year)
        if year not in df.columns:
            print(f"\nYear {year} not available in dataset")
            return
        
        gdp = country_data[year].values[0]
        if pd.isna(gdp):
            print(f"\nNo GDP data available for {country} in {year}")
        else:
            print(f"\n{country} GDP in {year}: ${gdp:,.0f}")
    except ValueError:
        print(f"\nInvalid year: {year}")


def show_top_countries(df, config, n=10):
    """Top N countries by GDP using config default_top_n"""
    year_columns = sorted(list(filter(lambda col: isinstance(col, int), df.columns)))
    latest_year = year_columns[-1]
    
    top_countries = df.nlargest(n, latest_year)
    print(f"\nTop {n} Countries by GDP in {latest_year}:\n")
    print(f"{'Rank':<6} {'Country':<35} {'GDP':<25} {'Continent':<15}")
    print("-"*85)
    
    list(map(
        lambda pair: print(f"{pair[0]:<6} {pair[1][1]['Country Name']:<35} ${pair[1][1][latest_year]:<24,.0f} {pair[1][1]['Continent']:<15}"),
        enumerate(top_countries.iterrows(), 1)
    ))


def show_continent_countries(df, continent):
    """Ek continent ke saare countries"""
    continent_data = df[df['Continent'].str.lower() == continent.lower()]
    if continent_data.empty:
        print(f"\nContinent '{continent}' not found")
        return
    
    countries = sorted(continent_data['Country Name'].unique())
    print(f"\nCountries in {continent} ({len(countries)} total):\n")
    list(map(
        lambda pair: print(f"{pair[0]:3d}. {pair[1]}"),
        enumerate(countries, 1)
    ))


def show_summary(df, config):
    """Dataset ka summary dikhao using config"""
    year_columns = sorted(list(filter(lambda col: isinstance(col, int), df.columns)))
    latest_year = year_columns[-1]
    
    phase1 = config.get('phase1_filters', {})
    stat_op = config.get('phase1_operations', {}).get('statistical_operation', 'average')
    
    print("\n" + "="*60)
    print("  DATASET SUMMARY")
    print("="*60)
    print(f"Total Countries/Regions: {len(df)}")
    print(f"Year Range: {year_columns[0]} - {year_columns[-1]}")
    print(f"Total Years: {len(year_columns)}")
    print(f"\nContinents: {', '.join(sorted(df['Continent'].dropna().unique()))}")
    
    latest_data = df[latest_year].dropna()
    print(f"\nStatistics for {latest_year}:")
    print(f"  Total World GDP: ${latest_data.sum():,.0f}")
    print(f"  Average GDP: ${latest_data.mean():,.0f}")
    print(f"  Median GDP: ${latest_data.median():,.0f}")
    print(f"  Max GDP: ${latest_data.max():,.0f}")
    print(f"  Min GDP: ${latest_data.min():,.0f}")
    
    # Use phase1_filters config to show default focus
    if phase1:
        print(f"\nDefault Focus (from config):")
        print(f"  Region: {phase1.get('region', 'N/A')}")
        print(f"  Year: {phase1.get('year', 'N/A')}")
        print(f"  Country: {phase1.get('country', 'N/A')}")
        print(f"  Statistical Operation: {stat_op}")
    
    print("="*60)


def show_available_years(df):
    """Dataset mein konse years hain"""
    year_columns = sorted(list(filter(lambda col: isinstance(col, int), df.columns)))
    
    print(f"\nAvailable Years ({len(year_columns)} total):")
    print(f"From {year_columns[0]} to {year_columns[-1]}")
    print("\nYears:", ', '.join(map(str, year_columns)))


def compare_countries(df, country1, country2):
    """Do countries ka comparison"""
    data1 = df[df['Country Name'].str.lower() == country1.lower()]
    data2 = df[df['Country Name'].str.lower() == country2.lower()]
    
    if data1.empty:
        print(f"\nCountry '{country1}' not found")
        return
    if data2.empty:
        print(f"\nCountry '{country2}' not found")
        return
    
    year_columns = sorted(list(filter(lambda col: isinstance(col, int), df.columns)))
    latest_year = year_columns[-1]
    first_year = year_columns[0]
    
    gdp1_latest = data1[latest_year].values[0]
    gdp2_latest = data2[latest_year].values[0]
    gdp1_first = data1[first_year].values[0]
    gdp2_first = data2[first_year].values[0]
    
    print(f"\n{'='*70}")
    print(f"COMPARISON: {country1.upper()} vs {country2.upper()}")
    print(f"{'='*70}")
    
    print(f"\n{'':<25} {country1:<25} {country2:<25}")
    print(f"{'-'*70}")
    print(f"{'Continent':<25} {data1['Continent'].values[0]:<25} {data2['Continent'].values[0]:<25}")
    print(f"{'GDP in ' + str(latest_year):<25} ${gdp1_latest:<24,.0f} ${gdp2_latest:<24,.0f}")
    print(f"{'GDP in ' + str(first_year):<25} ${gdp1_first:<24,.0f} ${gdp2_first:<24,.0f}")
    
    growth1_str = (
        f"{((gdp1_latest - gdp1_first) / gdp1_first) * 100:<24.2f}%"
        if not pd.isna(gdp1_first) and gdp1_first != 0
        else f"{'N/A':<24}"
    )
    growth2_str = (
        f" {((gdp2_latest - gdp2_first) / gdp2_first) * 100:<24.2f}%"
        if not pd.isna(gdp2_first) and gdp2_first != 0
        else f" {'N/A':<24}"
    )
    print(f"{'Total Growth':<25} {growth1_str}{growth2_str}")
    print(f"{'='*70}\n")


def handle_choice(choice, df, config):
    """Handle a single menu choice - returns whether to continue"""
    handlers = {
        '1': lambda: show_all_countries(df),
        '2': lambda: show_all_continents(df),
        '3': lambda: search_country(df, input("Enter country name (partial match): ").strip()),
        '4': lambda: show_country_gdp_for_year(df, input("Enter country name: ").strip(), input("Enter year: ").strip()),
        '5': lambda: show_top_countries(df, config, int(n) if (n := input("Enter number of top countries (default 10): ").strip()).isdigit() else config.get('ui', {}).get('default_top_n', 10)),
        '6': lambda: show_continent_countries(df, input("Enter continent name: ").strip()),
        '7': lambda: show_summary(df, config),
        '8': lambda: show_available_years(df),
        '9': lambda: compare_countries(df, input("Enter first country name: ").strip(), input("Enter second country name: ").strip()),
    }
    
    if choice == '0':
        print("\nThank you for using GDP Data Explorer!")
        return False
    
    handler = handlers.get(choice)
    if handler:
        handler()
        input("\nPress Enter to continue...")
    else:
        print("\nInvalid choice. Please try again.")
        input("\nPress Enter to continue...")
    
    return True


def run_explorer(df, config):
    """Recursive main loop - functional alternative to while True"""
    show_menu()
    choice = input("\nEnter your choice: ").strip()
    
    should_continue = handle_choice(choice, df, config)
    
    if should_continue:
        return run_explorer(df, config)
    return None


def main():
    """Program start karo"""
    print("\nLoading GDP data...")
    
    config = load_config()
    if config is None:
        print("Failed to load config. Exiting...")
        return
    
    df = load_data(config)
    
    if df is None:
        print("Failed to load data. Exiting...")
        return
    
    print(f"Data loaded successfully! ({len(df)} countries)")
    
    sys.setrecursionlimit(10000)
    run_explorer(df, config)


if __name__ == "__main__":
    main()
