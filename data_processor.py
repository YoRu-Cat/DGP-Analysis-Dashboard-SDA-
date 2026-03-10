import numpy as np
import pandas as pd
from functools import reduce
from itertools import combinations


class GDPDataProcessor:
    
    def __init__(self, df, year_columns):
        self.df = df
        self.year_columns = year_columns
    
    def get_country_data(self, country, years):
        country_data = self.df[self.df['Country Name'] == country]
        if country_data.empty:
            return None
        return country_data[years].values.flatten()
    
    def get_continent_data(self, continent):
        return self.df[self.df['Continent'] == continent]
    
    def calculate_growth_rates(self, gdp_values, years):
        value_pairs = list(zip(gdp_values[:-1], gdp_values[1:]))
        year_pairs = list(zip(years[:-1], years[1:]))
        
        growth_data = list(map(
            lambda pair_idx: (
                ((value_pairs[pair_idx][1] - value_pairs[pair_idx][0]) / value_pairs[pair_idx][0]) * 100,
                year_pairs[pair_idx][1]
            ) if not np.isnan(value_pairs[pair_idx][0]) and not np.isnan(value_pairs[pair_idx][1]) and value_pairs[pair_idx][0] != 0
            else (None, year_pairs[pair_idx][1]),
            range(len(value_pairs))
        ))
        
        valid_growth = list(filter(lambda x: x[0] is not None, growth_data))
        
        growth_rates = list(map(lambda x: x[0], valid_growth))
        growth_years = list(map(lambda x: x[1], valid_growth))
        
        return growth_rates, growth_years
    
    def get_top_countries(self, year, n=10):
        return self.df.nlargest(n, year)
    
    def calculate_total_gdp(self, data, years):
        return data[years].sum()
    
    def calculate_average_gdp(self, data, years):
        return data[years].mean(axis=1)
    
    def get_correlation_matrix(self, countries, years):
        country_data_pairs = list(filter(
            lambda pair: pair[1] is not None,
            map(lambda c: (c, self.get_country_data(c, years)), countries)
        ))
        
        if not country_data_pairs:
            return None
        
        data_dict = dict(country_data_pairs)
        corr_df = pd.DataFrame(data_dict)
        return corr_df.corr()
    
    def calculate_statistics(self, gdp_values):
        valid_gdp = list(filter(lambda g: not np.isnan(g), gdp_values))
        
        if not valid_gdp:
            return None
        
        return {
            'max': reduce(lambda a, b: a if a > b else b, valid_gdp),
            'min': reduce(lambda a, b: a if a < b else b, valid_gdp),
            'mean': reduce(lambda a, b: a + b, valid_gdp) / len(valid_gdp),
            'median': np.median(valid_gdp),
            'std': np.std(valid_gdp),
            'count': len(valid_gdp)
        }
    
    def calculate_growth_summary(self, gdp_values, years):
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
        return dict(map(
            lambda year: (year, dict(map(
                lambda continent: (continent, self.get_continent_data(continent)[year].sum()),
                continents
            ))),
            comparison_years
        ))
    
    def get_top_correlations(self, correlation_matrix, n=10):
        countries = correlation_matrix.columns
        
        correlations = list(map(
            lambda pair: (pair[0], pair[1], correlation_matrix.loc[pair[0], pair[1]]),
            combinations(countries, 2)
        ))
        
        sorted_correlations = sorted(correlations, key=lambda x: abs(x[2]), reverse=True)
        return sorted_correlations[:n]


def filter_by_region(df, region):
    region_col = 'Continent' if 'Continent' in df.columns else 'Region'
    return df[df[region_col] == region]


def filter_by_country(df, country):
    return df[df['Country Name'] == country]


def calculate_regional_average(df, region, year_columns):
    region_data = filter_by_region(df, region)
    
    year_totals = list(map(lambda year: region_data[year].sum(), year_columns))
    valid_totals = list(filter(lambda x: x > 0, year_totals))
    
    if valid_totals:
        return reduce(lambda a, b: a + b, valid_totals) / len(valid_totals)
    return 0


def calculate_regional_sum(df, region, year_columns):
    region_data = filter_by_region(df, region)
    
    return reduce(
        lambda total, year: total + region_data[year].sum(),
        year_columns,
        0
    )


def calculate_country_average(df, country, year_columns):
    country_data = filter_by_country(df, country)
    
    if country_data.empty:
        return 0
    
    gdp_values = list(map(lambda year: country_data[year].iloc[0], year_columns))
    valid_values = list(filter(lambda x: x > 0, gdp_values))
    
    if valid_values:
        return reduce(lambda a, b: a + b, valid_values) / len(valid_values)
    return 0


def calculate_country_sum(df, country, year_columns):
    country_data = filter_by_country(df, country)
    
    if country_data.empty:
        return 0
    
    return reduce(
        lambda total, year: total + country_data[year].iloc[0],
        year_columns,
        0
    )

