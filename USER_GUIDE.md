# GDP Analysis Dashboard - User Guide

## Quick Start Guide

### Installation

1. **Install Python** (if not already installed)
   - Download Python 3.7+ from https://www.python.org/
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   python test_dashboard.py
   ```

### Launching the Dashboard

**Windows Users:**

- Double-click `launch_dashboard.bat`
- Or run: `python gdp_dashboard.py`

**Mac/Linux Users:**

- Run: `./launch_dashboard.sh` (make it executable first: `chmod +x launch_dashboard.sh`)
- Or run: `python3 gdp_dashboard.py`

---

## Using the Dashboard

### Main Interface

The dashboard has two main panels:

1. **Left Control Panel** - Analysis configuration
2. **Right Visualization Panel** - Charts and statistics

### Step-by-Step Guide

#### 1. Country GDP Trend Analysis

**Objective:** View GDP trend for a single country

**Steps:**

1. Select "Country GDP Trend" analysis type
2. Choose a country from "Primary Country" dropdown
3. Set year range (From/To)
4. Click "Analyze"

**Result:** Line chart showing GDP over time + detailed statistics

**Example Use Case:**

- Analyze USA's economic growth from 1990 to 2020

---

#### 2. Compare Multiple Countries

**Objective:** Compare GDP trends between countries

**Steps:**

1. Select "Compare Countries" analysis type
2. Select 2-10 countries from "Compare With" list (hold Ctrl/Cmd to select multiple)
3. Set year range
4. Click "Analyze"

**Result:** Multi-line chart with all selected countries + comparison table

**Example Use Cases:**

- Compare BRICS nations (Brazil, Russia, India, China, South Africa)
- Compare European economies (Germany, France, UK, Italy)
- Compare neighboring countries

---

#### 3. Continent Analysis

**Objective:** Comprehensive analysis of a continent

**Steps:**

1. Select "Continent Analysis" analysis type
2. Choose a continent from dropdown
3. Set year range
4. Click "Analyze"

**Result:** Four visualizations:

- Total continent GDP trend
- Top 10 countries in latest year
- Top 10 by average GDP
- GDP distribution histogram

**Example Use Cases:**

- Analyze Africa's economic development
- Compare Asian economies
- Study European integration

---

#### 4. Top Countries Ranking

**Objective:** See the wealthiest countries

**Steps:**

1. Select "Top Countries" analysis type
2. Set "Top N" value (5-50)
3. Click "Analyze"

**Result:** Horizontal bar chart with rankings

**Example Use Cases:**

- Identify top 10 economies globally
- Find top 20 GDP producers
- Compare economic powerhouses

---

#### 5. Growth Rate Analysis

**Objective:** Track economic growth or decline

**Steps:**

1. Select "GDP Growth Rate" analysis type
2. Choose a country
3. Set year range (minimum 2 years)
4. Click "Analyze"

**Result:** Bar chart showing year-over-year % changes (green = growth, red = decline)

**Example Use Cases:**

- Identify recession periods
- Track recovery after economic crises
- Analyze boom periods

---

#### 6. Statistical Summary

**Objective:** Get comprehensive numerical analysis

**Steps:**

1. Select "Statistical Summary" analysis type
2. Set year range
3. Click "Analyze"

**Result:** Detailed text report with:

- Overall statistics
- Latest year data
- Top 10 countries
- Statistics by continent

**Example Use Cases:**

- Generate reports for presentations
- Get quick facts and figures
- Understand global economic distribution

---

#### 7. Year Comparison

**Objective:** Compare continents across different time periods

**Steps:**

1. Select "Year Comparison" analysis type
2. Set year range (automatically selects 6 evenly spaced years)
3. Click "Analyze"

**Result:** Grouped bar chart showing continental GDP evolution

**Example Use Cases:**

- Track how continents have developed
- Compare economic shifts over decades
- Identify growth patterns

---

#### 8. Correlation Analysis

**Objective:** Find relationships between countries' economies

**Steps:**

1. Select "Correlation Analysis" analysis type
2. Select 2-15 countries from "Compare With" list
3. Set year range
4. Click "Analyze"

**Result:** Correlation heatmap with coefficients (-1 to +1)

- Values near +1: Strong positive correlation
- Values near 0: No correlation
- Values near -1: Strong negative correlation

**Example Use Cases:**

- Identify economically linked countries
- Find trading partners' correlations
- Study economic dependencies

---

## Tips and Tricks

### Best Practices

1. **Start with Statistical Summary**
   - Get an overview before diving into specific analyses

2. **Use Appropriate Year Ranges**
   - Recent trends: Last 10-20 years
   - Historical analysis: Full range (1960-2024)
   - Crisis analysis: Narrow ranges around events

3. **Limit Comparisons**
   - Max 10 countries for comparisons (better visibility)
   - Max 15 for correlation analysis

4. **Export Your Work**
   - Click "Export Data" to save statistics as text file
   - Screenshots for charts (use system screenshot tool)

### Keyboard Shortcuts

- **Ctrl+A**: Select all (in listboxes)
- **Ctrl+Click**: Multi-select in lists
- **Shift+Click**: Select range in lists

### Data Interpretation

**Understanding GDP Values:**

- Numbers displayed in USD (US Dollars)
- Use scientific notation for very large numbers
- NaN = Data not available for that year

**Growth Rates:**

- Positive % = Economy growing
- Negative % = Economy contracting
- Large swings may indicate:
  - Economic crises
  - Wars/conflicts
  - Policy changes
  - Data anomalies

**Correlation Coefficients:**

- 0.8 to 1.0 = Very strong correlation
- 0.6 to 0.8 = Strong correlation
- 0.4 to 0.6 = Moderate correlation
- 0.2 to 0.4 = Weak correlation
- 0.0 to 0.2 = Very weak/no correlation

---

## Common Tasks

### Task 1: Generate a Country Report

1. Select country in "Primary Country"
2. Run "Country GDP Trend" analysis
3. Run "GDP Growth Rate" analysis
4. Run "Statistical Summary"
5. Export statistics

### Task 2: Compare Regional Economies

1. Identify countries in the region
2. Use "Compare Countries" analysis
3. Select all countries in the list
4. Set relevant year range
5. Analyze trends

### Task 3: Track Economic Crisis Impact

1. Set year range around crisis (e.g., 2007-2012 for 2008 crisis)
2. Use "Growth Rate" analysis
3. Compare multiple affected countries
4. Analyze recovery patterns

### Task 4: Research Continental Development

1. Select continent
2. Run "Continent Analysis"
3. Review all four visualizations
4. Run "Statistical Summary" for detailed numbers
5. Compare with other continents using "Year Comparison"

---

## Troubleshooting

### Problem: Dashboard won't start

**Solutions:**

1. Check Python installation: `python --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Verify data file exists: `gdp_with_continent_filled.xlsx`
4. Run test script: `python test_dashboard.py`

### Problem: Chart is empty or shows errors

**Solutions:**

1. Verify country name is correct (use list to select)
2. Check year range is valid
3. Ensure data exists for selected parameters
4. Try "Clear" button and re-analyze

### Problem: Slow performance

**Solutions:**

1. Reduce year range
2. Select fewer countries for comparison
3. Close other applications
4. Restart dashboard

### Problem: Can't see full chart

**Solutions:**

1. Maximize window
2. Scroll if scrollbar appears
3. Reduce number of data points
4. Export and view externally

---

## Advanced Usage

### Command-Line Data Explorer

For quick queries without the GUI:

```bash
python data_explorer.py
```

Features:

- Search countries
- Quick GDP lookups
- Compare two countries
- List countries by continent
- Data summaries

### Batch Analysis

To analyze multiple countries programmatically, modify the dashboard script or create custom scripts using pandas.

### Custom Export Formats

Current: Text file export
Future: Can be extended to support Excel, CSV, PDF

---

## Data Information

### Dataset Details

- **Source:** GDP data with continent classifications
- **Format:** Excel (.xlsx)
- **Coverage:** 1960-2024 (65 years)
- **Countries:** 266 countries and regions
- **Indicator:** GDP in current US dollars

### Data Limitations

- Some countries have incomplete data
- Historical data may be less accurate
- Regional aggregates included
- Political changes affect country consistency

---

## Glossary

**GDP**: Gross Domestic Product - total value of goods and services produced

**Growth Rate**: Percentage change from one period to another

**Correlation**: Statistical measure of relationship between two variables

**Continent**: Geographic grouping of countries

**Time Series**: Data points ordered by time

**Aggregate**: Combined total of multiple items

---

## Support and Resources

### Getting Help

1. Read this guide
2. Check README.md for technical details
3. Run test script to verify setup
4. Review error messages carefully

### Learning Resources

- **Economics Basics**: Understand GDP concepts
- **Data Analysis**: Learn pandas for custom analysis
- **Visualization**: Study matplotlib for custom charts

### Project Files

- `gdp_dashboard.py` - Main application
- `data_explorer.py` - Command-line tool
- `test_dashboard.py` - Testing script
- `requirements.txt` - Dependencies
- `gdp_with_continent_filled.xlsx` - Data file

---

## Quick Reference Card

| Analysis Type      | Best For                 | Min. Requirements   |
| ------------------ | ------------------------ | ------------------- |
| Country Trend      | Single country history   | 1 country, 1+ years |
| Compare Countries  | Multi-country comparison | 2+ countries        |
| Continent Analysis | Regional overview        | 1 continent         |
| Top Countries      | Rankings                 | Top N value         |
| Growth Rate        | Economic changes         | 1 country, 2+ years |
| Statistics         | Comprehensive data       | Any range           |
| Year Comparison    | Cross-period analysis    | 1+ years            |
| Correlation        | Economic relationships   | 2+ countries        |

---

**Version:** 1.0  
**Last Updated:** February 2026
