
#Data Loader Module
#Handles loading GDP data from Excel files with validation.

import pandas as pd
import json
import os
from functools import reduce


class ConfigLoader:
    """Loads and validates configuration from config.json"""
    
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self._validate_config(config)
            return config
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to load configuration: {str(e)}")
    
    def _validate_config(self, config):
        """Validate configuration structure"""
        required_sections = ['data', 'ui', 'colors', 'analysis_types', 'visualization']
        
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            raise ValueError(f"Missing required configuration section: {', '.join(missing_sections)}")
        
        data_required = ['file_path', 'required_columns']
        missing_data_fields = list(filter(lambda key: key not in config['data'], data_required))
        
        if missing_data_fields:
            raise ValueError(f"Missing in data configuration: {', '.join(missing_data_fields)}")
    
    def get(self, section, key=None):
        """Get configuration value"""
        if key is None:
            return self.config.get(section, {})
        return self.config.get(section, {}).get(key)


class GDPDataLoader:
    """Loads and validates GDP data from Excel files"""
    
    def __init__(self, config):
        self.config = config
        self.df = None
        self.year_columns = []
        self.countries = []
        self.continents = []
    
    def load_data(self):
        """Load GDP data from CSV or Excel file (smart format detection)"""
        file_path = self.config.get('data', 'file_path')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Data file not found: {file_path}\n"
                f"Please ensure the data file (CSV or Excel) exists in the project directory."
            )
        
        # Smart format detection based on file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.csv':
                # Load CSV file
                self.df = pd.read_csv(file_path)
                print(f"Loaded CSV file: {file_path}")
            elif file_extension in ['.xlsx', '.xls']:
                # Load Excel file
                self.df = pd.read_excel(file_path)
                print(f"Loaded Excel file: {file_path}")
            else:
                raise ValueError(
                    f"Unsupported file format: {file_extension}\n"
                    f"Supported formats: .csv, .xlsx, .xls"
                )
        except Exception as e:
            raise Exception(f"Failed to read data file ({file_extension}): {str(e)}")
        
        self._validate_data()
        self._extract_metadata()
        
        return self
    
    def _validate_data(self):
        """Validate loaded data structure"""
        if self.df is None or self.df.empty:
            raise ValueError("Loaded data is empty")
        
        required_columns = self.config.get('data', 'required_columns')
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        
        if missing_columns:
            raise ValueError(
                f"Missing required columns in data: {', '.join(missing_columns)}\n"
                f"Available columns: {', '.join(self.df.columns)}"
            )
        
        # Check for year columns (numeric columns)
        year_cols = [col for col in self.df.columns if isinstance(col, int)]
        if not year_cols:
            raise ValueError("No year columns found in data (expected numeric column names)")
    
    def _extract_metadata(self):
        """Extract years, countries, and continents from data"""
        self.year_columns = sorted(
            list(filter(lambda col: isinstance(col, int), self.df.columns))
        )
        
        self.countries = sorted([
            country for country in self.df['Country Name'].unique() if pd.notna(country)
        ])
        
        continents_raw = self.df['Continent'].dropna().unique()
        self.continents = sorted(list(map(str, filter(lambda x: pd.notna(x), continents_raw))))
        
        if not self.countries:
            raise ValueError("No countries found in data")
        
        if not self.continents:
            raise ValueError("No continents found in data")
    
    def get_dataframe(self):
        """Get the loaded dataframe"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        return self.df
    
    def get_year_columns(self):
        """Get list of year columns"""
        return self.year_columns
    
    def get_countries(self):
        """Get list of countries"""
        return self.countries
    
    def get_continents(self):
        """Get list of continents"""
        return self.continents
    
    def get_summary(self):
        """Get data summary"""
        if self.df is None:
            return "No data loaded"
        
        return {
            'total_countries': len(self.df),
            'total_years': len(self.year_columns),
            'year_range': f"{self.year_columns[0]} - {self.year_columns[-1]}",
            'continents': len(self.continents)
        }
