# GDP Data Explorer
# Command line se jaldi se data dekh sakte hain

import pandas as pd
import sys


def load_data():
    # Data load karo
    try:
        df = pd.read_excel('gdp_with_continent_filled.xlsx')
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def show_menu():
    # Menu options dikhao
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
    # Saare countries ki list
    countries = sorted(df['Country Name'].unique())
    print(f"\nTotal Countries: {len(countries)}\n")
    for i, country in enumerate(countries, 1):
        print(f"{i:3d}. {country}")


def show_all_continents(df):
    # Saare continents aur unke countries
    continents = sorted(df['Continent'].dropna().unique())
    print(f"\nTotal Continents: {len(continents)}\n")
    for continent in continents:
        count = len(df[df['Continent'] == continent])
        print(f"  {continent:<20s} ({count} countries)")


def search_country(df, search_term):
    # Naam se country search karo
    matches = df[df['Country Name'].str.contains(search_term, case=False, na=False)]
    if matches.empty:
        print(f"\nNo countries found matching '{search_term}'")
    else:
        print(f"\nFound {len(matches)} match(es):\n")
        for _, row in matches.iterrows():
            print(f"  {row['Country Name']} ({row['Country Code']}) - {row['Continent']}")


def show_country_gdp_for_year(df, country, year):
    # Specific country aur year ka GDP dikhao
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


def show_top_countries(df, n=10):
    # Top N countries by GDP
    year_columns = [col for col in df.columns if isinstance(col, int)]
    latest_year = max(year_columns)
    
    top_countries = df.nlargest(n, latest_year)
    print(f"\nTop {n} Countries by GDP in {latest_year}:\n")
    print(f"{'Rank':<6} {'Country':<35} {'GDP':<25} {'Continent':<15}")
    print("-"*85)
    
    for i, row in enumerate(top_countries.iterrows(), 1):
        country = row[1]['Country Name']
        gdp = row[1][latest_year]
        continent = row[1]['Continent']
        print(f"{i:<6} {country:<35} ${gdp:<24,.0f} {continent:<15}")


def show_continent_countries(df, continent):
    # Ek continent ke saare countries
    continent_data = df[df['Continent'].str.lower() == continent.lower()]
    if continent_data.empty:
        print(f"\nContinent '{continent}' not found")
        return
    
    countries = sorted(continent_data['Country Name'].unique())
    print(f"\nCountries in {continent} ({len(countries)} total):\n")
    for i, country in enumerate(countries, 1):
        print(f"{i:3d}. {country}")


def show_summary(df):
    # Dataset ka summary dikhao
    year_columns = [col for col in df.columns if isinstance(col, int)]
    year_columns.sort()
    latest_year = year_columns[-1]
    
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
    print("="*60)


def show_available_years(df):
    # Dataset mein konse years hain
    year_columns = [col for col in df.columns if isinstance(col, int)]
    year_columns.sort()
    
    print(f"\nAvailable Years ({len(year_columns)} total):")
    print(f"From {year_columns[0]} to {year_columns[-1]}")
    print("\nYears:", ', '.join(map(str, year_columns)))


def compare_countries(df, country1, country2):
    # Do countries ka comparison
    data1 = df[df['Country Name'].str.lower() == country1.lower()]
    data2 = df[df['Country Name'].str.lower() == country2.lower()]
    
    if data1.empty:
        print(f"\nCountry '{country1}' not found")
        return
    if data2.empty:
        print(f"\nCountry '{country2}' not found")
        return
    
    year_columns = [col for col in df.columns if isinstance(col, int)]
    latest_year = max(year_columns)
    first_year = min(year_columns)
    
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
    
    if not pd.isna(gdp1_first) and gdp1_first != 0:
        growth1 = ((gdp1_latest - gdp1_first) / gdp1_first) * 100
        print(f"{'Total Growth':<25} {growth1:<24.2f}%", end="")
    else:
        print(f"{'Total Growth':<25} {'N/A':<24}", end="")
    
    if not pd.isna(gdp2_first) and gdp2_first != 0:
        growth2 = ((gdp2_latest - gdp2_first) / gdp2_first) * 100
        print(f" {growth2:<24.2f}%")
    else:
        print(f" {'N/A':<24}")
    
    print(f"{'='*70}\n")


def main():
    # Program start karo
    print("\nLoading GDP data...")
    df = load_data()
    
    if df is None:
        print("Failed to load data. Exiting...")
        return
    
    print(f"Data loaded successfully! ({len(df)} countries)")
    
    while True:
        show_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            show_all_countries(df)
        elif choice == '2':
            show_all_continents(df)
        elif choice == '3':
            search_term = input("Enter country name (partial match): ").strip()
            search_country(df, search_term)
        elif choice == '4':
            country = input("Enter country name: ").strip()
            year = input("Enter year: ").strip()
            show_country_gdp_for_year(df, country, year)
        elif choice == '5':
            n = input("Enter number of top countries (default 10): ").strip()
            n = int(n) if n.isdigit() else 10
            show_top_countries(df, n)
        elif choice == '6':
            continent = input("Enter continent name: ").strip()
            show_continent_countries(df, continent)
        elif choice == '7':
            show_summary(df)
        elif choice == '8':
            show_available_years(df)
        elif choice == '9':
            country1 = input("Enter first country name: ").strip()
            country2 = input("Enter second country name: ").strip()
            compare_countries(df, country1, country2)
        elif choice == '0':
            print("\nThank you for using GDP Data Explorer!")
            break
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
