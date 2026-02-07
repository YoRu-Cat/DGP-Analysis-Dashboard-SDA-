"""
Data Processor Module
Handles all GDP data processing, calculations, and statistical operations.
"""

import numpy as np
import pandas as pd


class GDPDataProcessor:
    """Processes GDP data and performs calculations"""
    
    def __init__(self, df, year_columns):
        self.df = df
        self.year_columns = year_columns
    
    def get_country_data(self, country, years):
        """Get GDP data for a specific country across given years"""
        country_data = self.df[self.df['Country Name'] == country]
        if country_data.empty:
            return None
        return country_data[years].values.flatten()
    
    def get_continent_data(self, continent):
        """Get all data for a specific continent"""
        return self.df[self.df['Continent'] == continent]
    
    def calculate_growth_rates(self, gdp_values, years):
        """Calculate year-over-year GDP growth rates"""
        growth_rates = []
        growth_years = []
        
        for i in range(1, len(gdp_values)):
            if not np.isnan(gdp_values[i]) and not np.isnan(gdp_values[i-1]) and gdp_values[i-1] != 0:
                growth_rate = ((gdp_values[i] - gdp_values[i-1]) / gdp_values[i-1]) * 100
                growth_rates.append(growth_rate)
                growth_years.append(years[i])
        
        return growth_rates, growth_years
    
    def get_top_countries(self, year, n=10):
        """Get top N countries by GDP in a specific year"""
        return self.df.nlargest(n, year)
    
    def calculate_total_gdp(self, data, years):
        """Calculate total GDP across years"""
        return data[years].sum()
    
    def calculate_average_gdp(self, data, years):
        """Calculate average GDP across years"""
        return data[years].mean(axis=1)
    
    def get_correlation_matrix(self, countries, years):
        """Build correlation matrix for selected countries"""
        data_dict = {}
        for country in countries:
            gdp_values = self.get_country_data(country, years)
            if gdp_values is not None:
                data_dict[country] = gdp_values
        
        if not data_dict:
            return None
        
        corr_df = pd.DataFrame(data_dict)
        return corr_df.corr()
    
    def calculate_statistics(self, gdp_values):
        """Calculate statistical measures for GDP values"""
        valid_gdp = [g for g in gdp_values if not np.isnan(g)]
        
        if not valid_gdp:
            return None
        
        return {
            'max': max(valid_gdp),
            'min': min(valid_gdp),
            'mean': np.mean(valid_gdp),
            'median': np.median(valid_gdp),
            'std': np.std(valid_gdp),
            'count': len(valid_gdp)
        }
    
    def calculate_growth_summary(self, gdp_values, years):
        """Calculate growth summary from first to last value"""
        first_valid = next((g for g in gdp_values if not np.isnan(g)), None)
        last_valid = next((g for g in reversed(gdp_values) if not np.isnan(g)), None)
        
        if not first_valid or not last_valid or first_valid == 0:
            return None
        
        total_growth = ((last_valid - first_valid) / first_valid) * 100
        years_spanned = years[-1] - years[0]
        
        result = {
            'total_growth': total_growth,
            'first_value': first_valid,
            'last_value': last_valid
        }
        
        if years_spanned > 0:
            result['avg_annual_growth'] = total_growth / years_spanned
        
        return result
    
    def get_continent_summary(self, continent, year):
        """Get summary statistics for a continent in a specific year"""
        continent_data = self.get_continent_data(continent)
        
        if continent_data.empty:
            return None
        
        return {
            'total_gdp': continent_data[year].sum(),
            'avg_gdp': continent_data[year].mean(),
            'country_count': len(continent_data),
            'top_countries': continent_data.nlargest(5, year)
        }
    
    def get_world_statistics(self, year):
        """Get world-level statistics for a specific year"""
        year_data = self.df[year].dropna()
        
        return {
            'total_gdp': year_data.sum(),
            'avg_gdp': year_data.mean(),
            'median_gdp': year_data.median(),
            'std_gdp': year_data.std(),
            'max_gdp': year_data.max(),
            'min_gdp': year_data.min(),
            'country_count': len(year_data)
        }
    
    def get_year_comparison_data(self, comparison_years, continents):
        """Get GDP data for year comparison across continents"""
        data = {}
        
        for year in comparison_years:
            data[year] = {}
            for continent in continents:
                continent_data = self.get_continent_data(continent)
                data[year][continent] = continent_data[year].sum()
        
        return data
    
    def get_top_correlations(self, correlation_matrix, n=10):
        """Get top N correlations from correlation matrix"""
        countries = correlation_matrix.columns
        correlations = []
        
        for i in range(len(countries)):
            for j in range(i+1, len(countries)):
                corr_value = correlation_matrix.iloc[i, j]
                correlations.append((countries[i], countries[j], corr_value))
        
        correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        return correlations[:n]
