# GDP Analysis Dashboard

A comprehensive interactive dashboard for analyzing and visualizing GDP data across countries and continents from 1960 to 2024.

## Features

### 📊 Analysis Types

1. **Country GDP Trend** - View GDP trends for individual countries over time
2. **Compare Countries** - Compare GDP trends among multiple countries
3. **Continent Analysis** - Comprehensive analysis of continents with multiple visualizations
4. **Top Countries** - View top N countries by GDP
5. **GDP Growth Rate** - Analyze year-over-year GDP growth rates
6. **Statistical Summary** - Detailed statistical summaries
7. **Year Comparison** - Compare GDP across continents for different years
8. **Correlation Analysis** - Analyze GDP correlations between countries

### 🎯 Key Features

- **Interactive GUI** - User-friendly interface built with tkinter
- **Multiple Visualizations** - Line charts, bar charts, histograms, correlation matrices
- **Flexible Filtering** - Select countries, continents, and year ranges
- **Statistical Analysis** - Comprehensive statistics for all analyses
- **Data Export** - Export analysis reports to text files
- **Real-time Updates** - Dynamic visualizations based on user selections

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Required Libraries

Install the required libraries using:

```bash
pip install pandas openpyxl matplotlib seaborn numpy
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Dashboard

1. Make sure the `gdp_with_continent_filled.xlsx` file is in the same directory as the script
2. Run the application:

```bash
python gdp_dashboard.py
```

### Using the Dashboard

1. **Select Analysis Type** - Choose from 8 different analysis types using radio buttons
2. **Choose Parameters**:
   - Select primary country
   - Select multiple countries for comparison
   - Choose continent
   - Set year range
   - Adjust top N value
3. **Click "Analyze"** - Generate visualizations and statistics
4. **View Results**:
   - Visualization tab shows charts and graphs
   - Statistics tab shows detailed numerical analysis
5. **Export Data** - Click "Export Data" to save analysis reports

### Analysis Examples

#### Country GDP Trend

- Select a country from the dropdown
- Choose year range
- Click "Analyze" to see the trend line

#### Compare Countries

- Select "Compare Countries" analysis type
- Choose multiple countries from the list (hold Ctrl/Cmd)
- Click "Analyze" to see comparative trends

#### Continent Analysis

- Select "Continent Analysis"
- Choose a continent
- View 4 different visualizations:
  - Total GDP trend
  - Top 10 countries
  - Average GDP rankings
  - GDP distribution

## Data Structure

The application expects an Excel file with the following structure:

- **Country Name** - Name of the country/region
- **Country Code** - ISO country code
- **Indicator Name** - GDP indicator description
- **Indicator Code** - GDP indicator code
- **Year Columns** (1960-2024) - GDP values for each year
- **Continent** - Continent classification

## Technical Details

### Libraries Used

- **pandas** - Data manipulation and analysis
- **matplotlib** - Core plotting library
- **seaborn** - Statistical visualizations
- **tkinter** - GUI framework (built-in with Python)
- **numpy** - Numerical computations
- **openpyxl** - Excel file reading

### Architecture

- **Main Class**: `GDPDashboard` - Handles all UI and analysis logic
- **Data Loading**: Automatic loading and validation of Excel data
- **Visualization Engine**: Matplotlib figures embedded in tkinter
- **Analysis Modules**: Separate methods for each analysis type

## Features in Detail

### 1. Country GDP Trend

Shows a line chart of GDP over selected years for a single country with detailed statistics including max, min, average, and growth rates.

### 2. Compare Countries

Overlays multiple country GDP trends on a single chart for easy comparison. Supports up to 10 countries simultaneously.

### 3. Continent Analysis

Four-panel visualization showing:

- Total continent GDP over time
- Top 10 countries by latest year
- Top 10 countries by average GDP
- GDP distribution histogram

### 4. Top Countries

Horizontal bar chart showing the top N countries by GDP for the latest year with color-coded bars and value labels.

### 5. GDP Growth Rate

Bar chart showing year-over-year percentage change in GDP with positive growth in green and negative in red.

### 6. Statistical Summary

Comprehensive text report including:

- Overall statistics
- Latest year statistics
- Top 10 countries
- Statistics by continent

### 7. Year Comparison

Grouped bar chart comparing continents across multiple years, showing how continental GDP has evolved.

### 8. Correlation Analysis

Heatmap showing correlation coefficients between selected countries' GDP trends with numerical values displayed.

## Export Functionality

The dashboard can export analysis reports to `gdp_analysis_report.txt` containing:

- Statistical summaries
- Rankings
- Comparison data
- Growth metrics

## Troubleshooting

### Common Issues

1. **"Failed to load data" error**
   - Ensure `gdp_with_continent_filled.xlsx` is in the same directory
   - Check file permissions

2. **Visualization not displaying**
   - Try clicking "Clear" and running the analysis again
   - Check if year range is valid

3. **Missing libraries**
   - Run `pip install -r requirements.txt`
   - Ensure Python version is 3.7 or higher

## System Requirements

- **OS**: Windows, macOS, or Linux
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 100MB free space
- **Display**: 1280x720 minimum resolution (1400x900 recommended)

## Performance Notes

- Large year ranges may take longer to process
- Comparing many countries (>10) may reduce chart readability
- Correlation analysis with 15+ countries may be slower

## Future Enhancements

Potential improvements:

- Interactive tooltips on charts
- More export formats (PDF, Excel, HTML)
- Predictive analysis using machine learning
- Real-time data updates from online sources
- Custom color themes
- Animation of GDP changes over time

## License

This project is provided as-is for educational and analytical purposes.

## Support

For issues or questions, please refer to the documentation or check the code comments for detailed implementation notes.

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Author**: GDP Analysis Dashboard Team
