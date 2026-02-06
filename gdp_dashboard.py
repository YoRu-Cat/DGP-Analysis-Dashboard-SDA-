"""
GDP Analysis Dashboard
A comprehensive tool for analyzing and visualizing GDP data across countries and continents
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class GDPDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("GDP Analysis Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Load data
        self.load_data()
        
        # Create UI
        self.create_widgets()
        
        # Show default visualization on startup
        self.root.after(100, self.show_default_analysis)
        
    def load_data(self):
        """Load and prepare GDP data"""
        try:
            self.df = pd.read_excel('gdp_with_continent_filled.xlsx')
            
            # Extract year columns
            self.year_columns = [col for col in self.df.columns if isinstance(col, int)]
            self.year_columns.sort()
            
            # Get unique countries and continents
            self.countries = sorted(self.df['Country Name'].unique())
            self.continents = sorted(self.df['Continent'].dropna().unique())
            
            print(f"Data loaded: {len(self.df)} countries, {len(self.year_columns)} years")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.root.destroy()
    
    def create_widgets(self):
        """Create the main UI layout"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🌍 GDP Analysis Dashboard 📊", 
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(expand=True)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, bg='white', width=350, relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=5)
        left_panel.pack_propagate(False)
        
        # Right panel - Visualizations
        right_panel = tk.Frame(main_container, bg='white', relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)
        
        self.create_control_panel(left_panel)
        self.create_visualization_panel(right_panel)
        
    def create_control_panel(self, parent):
        """Create control panel with analysis options"""
        # Scrollable frame
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Analysis Type Selection
        self.create_section_header(scrollable_frame, "📈 Analysis Type")
        
        self.analysis_type = tk.StringVar(value="country_trend")
        analyses = [
            ("Country GDP Trend", "country_trend"),
            ("Compare Countries", "compare_countries"),
            ("Continent Analysis", "continent_analysis"),
            ("Top Countries", "top_countries"),
            ("GDP Growth Rate", "growth_rate"),
            ("Statistical Summary", "statistics"),
            ("Year Comparison", "year_comparison"),
            ("Correlation Analysis", "correlation")
        ]
        
        for text, value in analyses:
            rb = tk.Radiobutton(
                scrollable_frame,
                text=text,
                variable=self.analysis_type,
                value=value,
                bg='white',
                font=('Arial', 10),
                command=self.on_analysis_change
            )
            rb.pack(anchor=tk.W, padx=20, pady=2)
        
        # Country Selection
        self.create_section_header(scrollable_frame, "🌐 Country Selection")
        
        # Primary country
        tk.Label(scrollable_frame, text="Primary Country:", bg='white', font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20, pady=(5, 2))
        self.country_var = tk.StringVar(value=self.countries[0])
        country_combo = ttk.Combobox(scrollable_frame, textvariable=self.country_var, values=self.countries, width=30, state='readonly')
        country_combo.pack(padx=20, pady=(0, 10))
        country_combo.bind('<<ComboboxSelected>>', lambda e: self.on_primary_country_change())
        
        # Secondary countries (for comparison)
        tk.Label(scrollable_frame, text="Compare With:", bg='white', font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20, pady=(5, 2))
        
        compare_frame = tk.Frame(scrollable_frame, bg='white')
        compare_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        self.compare_listbox = tk.Listbox(compare_frame, height=4, selectmode=tk.MULTIPLE, exportselection=False)
        compare_scrollbar = ttk.Scrollbar(compare_frame, orient=tk.VERTICAL, command=self.compare_listbox.yview)
        self.compare_listbox.configure(yscrollcommand=compare_scrollbar.set)
        
        for country in self.countries:  # Show all countries
            self.compare_listbox.insert(tk.END, country)
        
        self.compare_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        compare_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.compare_listbox.bind('<<ListboxSelect>>', lambda e: self.on_compare_selection_change())
        
        # Continent Selection
        self.create_section_header(scrollable_frame, "🗺️ Continent Selection")
        
        self.continent_var = tk.StringVar(value=self.continents[0] if self.continents else "")
        continent_combo = ttk.Combobox(scrollable_frame, textvariable=self.continent_var, values=self.continents, width=30, state='readonly')
        continent_combo.pack(padx=20, pady=(0, 10))
        continent_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
        
        # Year Range Selection
        self.create_section_header(scrollable_frame, "📅 Year Range")
        
        year_frame = tk.Frame(scrollable_frame, bg='white')
        year_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        tk.Label(year_frame, text="From:", bg='white', font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_year_var = tk.StringVar(value=str(self.year_columns[0]))
        start_year_combo = ttk.Combobox(year_frame, textvariable=self.start_year_var, values=[str(y) for y in self.year_columns], width=10, state='readonly')
        start_year_combo.grid(row=0, column=1, padx=(0, 10))
        start_year_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
        
        tk.Label(year_frame, text="To:", bg='white', font=('Arial', 9)).grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.end_year_var = tk.StringVar(value=str(self.year_columns[-1]))
        end_year_combo = ttk.Combobox(year_frame, textvariable=self.end_year_var, values=[str(y) for y in self.year_columns], width=10, state='readonly')
        end_year_combo.grid(row=0, column=3)
        end_year_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
        
        # Top N Selection
        self.create_section_header(scrollable_frame, "🏆 Top N Countries")
        
        top_frame = tk.Frame(scrollable_frame, bg='white')
        top_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        tk.Label(top_frame, text="Top N:", bg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 10))
        self.top_n_var = tk.IntVar(value=10)
        top_n_spinner = tk.Spinbox(top_frame, from_=5, to=50, textvariable=self.top_n_var, width=10, command=self.on_selection_change)
        top_n_spinner.pack(side=tk.LEFT)
        
        # Action Buttons
        button_frame = tk.Frame(scrollable_frame, bg='white')
        button_frame.pack(pady=20, padx=20, fill=tk.X)
        
        analyze_btn = tk.Button(
            button_frame,
            text="🔍 Analyze",
            command=self.perform_analysis,
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief=tk.RAISED,
            borderwidth=3,
            cursor='hand2'
        )
        analyze_btn.pack(fill=tk.X, pady=5)
        
        export_btn = tk.Button(
            button_frame,
            text="💾 Export Data",
            command=self.export_analysis,
            bg='#2ecc71',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief=tk.RAISED,
            borderwidth=2,
            cursor='hand2'
        )
        export_btn.pack(fill=tk.X, pady=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_visualization,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief=tk.RAISED,
            borderwidth=2,
            cursor='hand2'
        )
        clear_btn.pack(fill=tk.X, pady=5)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_section_header(self, parent, text):
        """Create a styled section header"""
        frame = tk.Frame(parent, bg='#ecf0f1', height=35)
        frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        frame.pack_propagate(False)
        
        label = tk.Label(frame, text=text, bg='#ecf0f1', font=('Arial', 11, 'bold'), fg='#2c3e50')
        label.pack(anchor=tk.W, padx=10, pady=5)
        
    def create_visualization_panel(self, parent):
        """Create visualization panel"""
        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Visualization tab
        self.viz_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.viz_frame, text="📊 Visualization")
        
        # Statistics tab
        self.stats_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.stats_frame, text="📋 Statistics")
        
        # Statistics text area
        self.stats_text = scrolledtext.ScrolledText(
            self.stats_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            bg='#f9f9f9',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def on_analysis_change(self):
        """Handle analysis type change"""
        # Don't auto-switch when user manually changes analysis type
        self.perform_analysis_delayed()
    
    def on_primary_country_change(self):
        """Handle primary country dropdown change"""
        # Switch to Country GDP Trend mode when primary country is changed
        if self.analysis_type.get() in ["country_trend", "compare_countries", "growth_rate"]:
            self.analysis_type.set("country_trend")
        # Clear compare listbox selections
        self.compare_listbox.selection_clear(0, tk.END)
        self.perform_analysis_delayed()
    
    def on_compare_selection_change(self):
        """Handle compare countries listbox selection change"""
        # Auto-switch to Compare Countries if multiple countries are selected
        selected_indices = self.compare_listbox.curselection()
        if len(selected_indices) > 1:
            self.analysis_type.set("compare_countries")
        elif len(selected_indices) == 1:
            # If only one country selected, stay in compare mode if already there
            pass
        self.perform_analysis_delayed()
    
    def on_selection_change(self):
        """Handle any other selection change and update visualization"""
        self.perform_analysis_delayed()
    
    def perform_analysis_delayed(self):
        """Delayed analysis execution to avoid rapid updates"""
        # Cancel any pending update
        if hasattr(self, '_update_timer'):
            self.root.after_cancel(self._update_timer)
        # Schedule update after 300ms to avoid rapid updates
        self._update_timer = self.root.after(300, self.perform_analysis)
        
    def get_year_range(self):
        """Get selected year range"""
        start_year = int(self.start_year_var.get())
        end_year = int(self.end_year_var.get())
        
        if start_year > end_year:
            start_year, end_year = end_year, start_year
            
        return [y for y in self.year_columns if start_year <= y <= end_year]
        
    def perform_analysis(self):
        """Perform the selected analysis"""
        analysis = self.analysis_type.get()
        
        try:
            if analysis == "country_trend":
                self.plot_country_trend()
            elif analysis == "compare_countries":
                self.plot_compare_countries()
            elif analysis == "continent_analysis":
                self.plot_continent_analysis()
            elif analysis == "top_countries":
                self.plot_top_countries()
            elif analysis == "growth_rate":
                self.plot_growth_rate()
            elif analysis == "statistics":
                self.show_statistics()
            elif analysis == "year_comparison":
                self.plot_year_comparison()
            elif analysis == "correlation":
                self.plot_correlation()
                
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            print(f"Error details: {e}")
    
    def plot_country_trend(self):
        """Plot GDP trend for a single country"""
        country = self.country_var.get()
        years = self.get_year_range()
        
        country_data = self.df[self.df['Country Name'] == country]
        if country_data.empty:
            messagebox.showwarning("Warning", f"No data found for {country}")
            return
            
        gdp_values = country_data[years].values.flatten()
        
        # Create plot
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        ax.plot(years, gdp_values, marker='o', linewidth=2, markersize=4, color='#3498db')
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('GDP (USD)', fontsize=12, fontweight='bold')
        ax.set_title(f'GDP Trend: {country}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.ticklabel_format(style='plain', axis='y')
        
        # Rotate x-axis labels if too many years
        if len(years) > 20:
            ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        # Show statistics
        self.show_country_statistics(country, years, gdp_values)
    
    def plot_compare_countries(self):
        """Compare GDP trends for multiple countries"""
        selected_indices = self.compare_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select countries to compare")
            return
            
        countries = [self.compare_listbox.get(i) for i in selected_indices]
        if len(countries) > 10:
            messagebox.showwarning("Warning", "Please select maximum 10 countries for better visualization")
            return
            
        years = self.get_year_range()
        
        # Create plot
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(countries)))
        
        for idx, country in enumerate(countries):
            country_data = self.df[self.df['Country Name'] == country]
            if not country_data.empty:
                gdp_values = country_data[years].values.flatten()
                ax.plot(years, gdp_values, marker='o', label=country, 
                       linewidth=2, markersize=3, color=colors[idx])
        
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('GDP (USD)', fontsize=12, fontweight='bold')
        ax.set_title('GDP Comparison Between Countries', fontsize=14, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.ticklabel_format(style='plain', axis='y')
        
        if len(years) > 20:
            ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        # Show comparison statistics
        self.show_comparison_statistics(countries, years)
    
    def plot_continent_analysis(self):
        """Analyze GDP by continent"""
        continent = self.continent_var.get()
        years = self.get_year_range()
        
        continent_data = self.df[self.df['Continent'] == continent]
        if continent_data.empty:
            messagebox.showwarning("Warning", f"No data found for {continent}")
            return
        
        # Create subplots
        fig = Figure(figsize=(14, 10))
        
        # Plot 1: Total GDP trend
        ax1 = fig.add_subplot(221)
        total_gdp = continent_data[years].sum()
        ax1.plot(years, total_gdp.values, marker='o', linewidth=2, color='#2ecc71')
        ax1.set_title(f'Total GDP Trend: {continent}', fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Total GDP (USD)')
        ax1.grid(True, alpha=0.3)
        ax1.ticklabel_format(style='plain', axis='y')
        
        # Plot 2: Top countries in latest year
        ax2 = fig.add_subplot(222)
        latest_year = years[-1]
        top_countries = continent_data.nlargest(10, latest_year)
        countries_list = top_countries['Country Name'].values
        gdp_list = top_countries[latest_year].values
        
        bars = ax2.barh(countries_list, gdp_list, color='#3498db')
        ax2.set_title(f'Top 10 Countries in {latest_year}', fontweight='bold')
        ax2.set_xlabel('GDP (USD)')
        ax2.ticklabel_format(style='plain', axis='x')
        
        # Plot 3: Average GDP by country
        ax3 = fig.add_subplot(223)
        avg_gdp = continent_data[years].mean(axis=1)
        continent_data_with_avg = continent_data.copy()
        continent_data_with_avg['avg_gdp'] = avg_gdp
        top_avg = continent_data_with_avg.nlargest(10, 'avg_gdp')
        
        ax3.barh(top_avg['Country Name'].values, top_avg['avg_gdp'].values, color='#e74c3c')
        ax3.set_title(f'Top 10 by Average GDP ({years[0]}-{years[-1]})', fontweight='bold')
        ax3.set_xlabel('Average GDP (USD)')
        ax3.ticklabel_format(style='plain', axis='x')
        
        # Plot 4: GDP distribution
        ax4 = fig.add_subplot(224)
        latest_gdp = continent_data[latest_year].dropna()
        ax4.hist(latest_gdp, bins=20, color='#9b59b6', edgecolor='black', alpha=0.7)
        ax4.set_title(f'GDP Distribution in {latest_year}', fontweight='bold')
        ax4.set_xlabel('GDP (USD)')
        ax4.set_ylabel('Number of Countries')
        ax4.ticklabel_format(style='plain', axis='x')
        
        fig.tight_layout()
        self.display_plot(fig)
        
        # Show continent statistics
        self.show_continent_statistics(continent, years)
    
    def plot_top_countries(self):
        """Plot top N countries by GDP"""
        top_n = self.top_n_var.get()
        years = self.get_year_range()
        latest_year = years[-1]
        
        top_countries = self.df.nlargest(top_n, latest_year)
        
        # Create plot
        fig = Figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        
        countries_list = top_countries['Country Name'].values
        gdp_list = top_countries[latest_year].values
        colors = plt.cm.viridis(np.linspace(0, 1, len(countries_list)))
        
        bars = ax.barh(countries_list, gdp_list, color=colors)
        ax.set_xlabel('GDP (USD)', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Countries by GDP in {latest_year}', fontsize=14, fontweight='bold')
        ax.ticklabel_format(style='plain', axis='x')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, gdp_list)):
            ax.text(value, bar.get_y() + bar.get_height()/2, 
                   f' {value:,.0f}', 
                   va='center', fontsize=8)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        # Show top countries statistics
        self.show_top_countries_statistics(top_countries, latest_year)
    
    def plot_growth_rate(self):
        """Plot GDP growth rate"""
        country = self.country_var.get()
        years = self.get_year_range()
        
        if len(years) < 2:
            messagebox.showwarning("Warning", "Need at least 2 years for growth rate calculation")
            return
        
        country_data = self.df[self.df['Country Name'] == country]
        if country_data.empty:
            messagebox.showwarning("Warning", f"No data found for {country}")
            return
        
        gdp_values = country_data[years].values.flatten()
        
        # Calculate growth rates
        growth_rates = []
        growth_years = []
        
        for i in range(1, len(gdp_values)):
            if not np.isnan(gdp_values[i]) and not np.isnan(gdp_values[i-1]) and gdp_values[i-1] != 0:
                growth_rate = ((gdp_values[i] - gdp_values[i-1]) / gdp_values[i-1]) * 100
                growth_rates.append(growth_rate)
                growth_years.append(years[i])
        
        # Create plot
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        colors = ['#2ecc71' if gr >= 0 else '#e74c3c' for gr in growth_rates]
        ax.bar(growth_years, growth_rates, color=colors, alpha=0.7, edgecolor='black')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Growth Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'GDP Growth Rate: {country}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        if len(growth_years) > 20:
            ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        # Show growth statistics
        self.show_growth_statistics(country, growth_years, growth_rates)
    
    def plot_year_comparison(self):
        """Compare GDP across continents for specific years"""
        years = self.get_year_range()
        
        # Select evenly spaced years for comparison
        if len(years) > 6:
            step = len(years) // 6
            comparison_years = years[::step][:6]
        else:
            comparison_years = years
        
        # Create plot
        fig = Figure(figsize=(14, 8))
        ax = fig.add_subplot(111)
        
        x = np.arange(len(self.continents))
        width = 0.8 / len(comparison_years)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(comparison_years)))
        
        for idx, year in enumerate(comparison_years):
            continent_gdp = []
            for continent in self.continents:
                continent_data = self.df[self.df['Continent'] == continent]
                total_gdp = continent_data[year].sum()
                continent_gdp.append(total_gdp)
            
            offset = (idx - len(comparison_years)/2) * width + width/2
            ax.bar(x + offset, continent_gdp, width, label=str(year), color=colors[idx])
        
        ax.set_xlabel('Continent', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total GDP (USD)', fontsize=12, fontweight='bold')
        ax.set_title('GDP Comparison Across Continents', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(self.continents, rotation=45, ha='right')
        ax.legend()
        ax.ticklabel_format(style='plain', axis='y')
        ax.grid(True, alpha=0.3, axis='y')
        
        fig.tight_layout()
        self.display_plot(fig)
        
        # Show year comparison statistics
        self.show_year_comparison_statistics(comparison_years)
    
    def plot_correlation(self):
        """Show correlation between selected countries"""
        selected_indices = self.compare_listbox.curselection()
        if len(selected_indices) < 2:
            messagebox.showwarning("Warning", "Please select at least 2 countries for correlation analysis")
            return
        
        if len(selected_indices) > 15:
            messagebox.showwarning("Warning", "Please select maximum 15 countries for better visualization")
            return
            
        countries = [self.compare_listbox.get(i) for i in selected_indices]
        years = self.get_year_range()
        
        # Build correlation matrix
        data_dict = {}
        for country in countries:
            country_data = self.df[self.df['Country Name'] == country]
            if not country_data.empty:
                data_dict[country] = country_data[years].values.flatten()
        
        corr_df = pd.DataFrame(data_dict)
        correlation_matrix = corr_df.corr()
        
        # Create plot
        fig = Figure(figsize=(12, 10))
        ax = fig.add_subplot(111)
        
        im = ax.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        
        # Set ticks
        ax.set_xticks(np.arange(len(countries)))
        ax.set_yticks(np.arange(len(countries)))
        ax.set_xticklabels(countries, rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(countries, fontsize=8)
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20)
        
        # Add correlation values
        for i in range(len(countries)):
            for j in range(len(countries)):
                text = ax.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=7)
        
        ax.set_title('GDP Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        # Show correlation statistics
        self.show_correlation_statistics(correlation_matrix, countries)
    
    def show_statistics(self):
        """Display statistical summary"""
        years = self.get_year_range()
        
        stats_text = "=" * 80 + "\n"
        stats_text += " " * 25 + "GDP STATISTICAL SUMMARY\n"
        stats_text += "=" * 80 + "\n\n"
        
        # Overall statistics
        stats_text += "OVERALL STATISTICS\n"
        stats_text += "-" * 80 + "\n"
        stats_text += f"Total Countries: {len(self.df)}\n"
        stats_text += f"Year Range: {years[0]} - {years[-1]}\n"
        stats_text += f"Total Years: {len(years)}\n\n"
        
        # Latest year statistics
        latest_year = years[-1]
        latest_data = self.df[latest_year].dropna()
        
        stats_text += f"STATISTICS FOR {latest_year}\n"
        stats_text += "-" * 80 + "\n"
        stats_text += f"Total World GDP: ${latest_data.sum():,.0f}\n"
        stats_text += f"Average GDP: ${latest_data.mean():,.0f}\n"
        stats_text += f"Median GDP: ${latest_data.median():,.0f}\n"
        stats_text += f"Std Deviation: ${latest_data.std():,.0f}\n"
        stats_text += f"Max GDP: ${latest_data.max():,.0f}\n"
        stats_text += f"Min GDP: ${latest_data.min():,.0f}\n\n"
        
        # Top 10 countries
        top_10 = self.df.nlargest(10, latest_year)
        stats_text += f"TOP 10 COUNTRIES IN {latest_year}\n"
        stats_text += "-" * 80 + "\n"
        for idx, row in enumerate(top_10.iterrows(), 1):
            country = row[1]['Country Name']
            gdp = row[1][latest_year]
            continent = row[1]['Continent']
            stats_text += f"{idx:2d}. {country:30s} ${gdp:20,.0f}  [{continent}]\n"
        
        stats_text += "\n"
        
        # By continent
        stats_text += f"STATISTICS BY CONTINENT ({latest_year})\n"
        stats_text += "-" * 80 + "\n"
        stats_text += f"{'Continent':<20} {'Total GDP':<25} {'Avg GDP':<25} {'Countries':<10}\n"
        stats_text += "-" * 80 + "\n"
        
        for continent in self.continents:
            continent_data = self.df[self.df['Continent'] == continent]
            total = continent_data[latest_year].sum()
            avg = continent_data[latest_year].mean()
            count = len(continent_data)
            stats_text += f"{continent:<20} ${total:<24,.0f} ${avg:<24,.0f} {count:<10}\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
        self.notebook.select(self.stats_frame)
    
    def show_country_statistics(self, country, years, gdp_values):
        """Show statistics for a single country"""
        valid_gdp = [g for g in gdp_values if not np.isnan(g)]
        
        stats_text = "=" * 80 + "\n"
        stats_text += f"STATISTICS FOR {country.upper()}\n"
        stats_text += "=" * 80 + "\n\n"
        
        stats_text += f"Period: {years[0]} - {years[-1]}\n"
        stats_text += f"Data Points: {len(valid_gdp)} / {len(years)}\n\n"
        
        if valid_gdp:
            stats_text += f"Maximum GDP: ${max(valid_gdp):,.0f} (Year: {years[gdp_values.tolist().index(max(valid_gdp))]})\n"
            stats_text += f"Minimum GDP: ${min(valid_gdp):,.0f} (Year: {years[gdp_values.tolist().index(min(valid_gdp))]})\n"
            stats_text += f"Average GDP: ${np.mean(valid_gdp):,.0f}\n"
            stats_text += f"Median GDP: ${np.median(valid_gdp):,.0f}\n"
            stats_text += f"Std Deviation: ${np.std(valid_gdp):,.0f}\n\n"
            
            # Growth from first to last
            first_valid = next((g for g in gdp_values if not np.isnan(g)), None)
            last_valid = next((g for g in reversed(gdp_values) if not np.isnan(g)), None)
            
            if first_valid and last_valid and first_valid != 0:
                total_growth = ((last_valid - first_valid) / first_valid) * 100
                stats_text += f"Total Growth: {total_growth:,.2f}%\n"
                years_spanned = years[-1] - years[0]
                if years_spanned > 0:
                    avg_annual_growth = total_growth / years_spanned
                    stats_text += f"Average Annual Growth: {avg_annual_growth:,.2f}%\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def show_comparison_statistics(self, countries, years):
        """Show comparison statistics"""
        stats_text = "=" * 80 + "\n"
        stats_text += "COUNTRY COMPARISON STATISTICS\n"
        stats_text += "=" * 80 + "\n\n"
        
        latest_year = years[-1]
        
        stats_text += f"Period: {years[0]} - {years[-1]}\n"
        stats_text += f"Countries: {len(countries)}\n\n"
        
        stats_text += f"{'Country':<30} {'GDP in ' + str(latest_year):<25} {'Avg GDP':<25}\n"
        stats_text += "-" * 80 + "\n"
        
        for country in countries:
            country_data = self.df[self.df['Country Name'] == country]
            if not country_data.empty:
                latest_gdp = country_data[latest_year].values[0]
                avg_gdp = country_data[years].mean(axis=1).values[0]
                stats_text += f"{country:<30} ${latest_gdp:<24,.0f} ${avg_gdp:<24,.0f}\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def show_continent_statistics(self, continent, years):
        """Show continent statistics"""
        continent_data = self.df[self.df['Continent'] == continent]
        latest_year = years[-1]
        
        stats_text = "=" * 80 + "\n"
        stats_text += f"STATISTICS FOR {continent.upper()}\n"
        stats_text += "=" * 80 + "\n\n"
        
        stats_text += f"Period: {years[0]} - {years[-1]}\n"
        stats_text += f"Total Countries: {len(continent_data)}\n\n"
        
        total_gdp = continent_data[latest_year].sum()
        avg_gdp = continent_data[latest_year].mean()
        
        stats_text += f"Total GDP ({latest_year}): ${total_gdp:,.0f}\n"
        stats_text += f"Average GDP ({latest_year}): ${avg_gdp:,.0f}\n\n"
        
        # Wealthiest countries
        top_5 = continent_data.nlargest(5, latest_year)
        stats_text += f"TOP 5 COUNTRIES IN {latest_year}\n"
        stats_text += "-" * 80 + "\n"
        for idx, row in enumerate(top_5.iterrows(), 1):
            country = row[1]['Country Name']
            gdp = row[1][latest_year]
            stats_text += f"{idx}. {country:<40} ${gdp:,.0f}\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def show_top_countries_statistics(self, top_countries, year):
        """Show top countries statistics"""
        stats_text = "=" * 80 + "\n"
        stats_text += f"TOP COUNTRIES STATISTICS ({year})\n"
        stats_text += "=" * 80 + "\n\n"
        
        total_top = top_countries[year].sum()
        total_world = self.df[year].sum()
        percentage = (total_top / total_world) * 100
        
        stats_text += f"Combined GDP: ${total_top:,.0f}\n"
        stats_text += f"World GDP: ${total_world:,.0f}\n"
        stats_text += f"Percentage of World: {percentage:.2f}%\n\n"
        
        stats_text += f"{'Rank':<6} {'Country':<30} {'GDP':<25} {'Continent':<15}\n"
        stats_text += "-" * 80 + "\n"
        
        for idx, row in enumerate(top_countries.iterrows(), 1):
            country = row[1]['Country Name']
            gdp = row[1][year]
            continent = row[1]['Continent']
            stats_text += f"{idx:<6} {country:<30} ${gdp:<24,.0f} {continent:<15}\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def show_growth_statistics(self, country, years, growth_rates):
        """Show growth rate statistics"""
        valid_rates = [r for r in growth_rates if not np.isnan(r)]
        
        stats_text = "=" * 80 + "\n"
        stats_text += f"GROWTH RATE STATISTICS FOR {country.upper()}\n"
        stats_text += "=" * 80 + "\n\n"
        
        if valid_rates:
            stats_text += f"Average Growth Rate: {np.mean(valid_rates):.2f}%\n"
            stats_text += f"Median Growth Rate: {np.median(valid_rates):.2f}%\n"
            stats_text += f"Max Growth Rate: {max(valid_rates):.2f}% (Year: {years[growth_rates.index(max(valid_rates))]})\n"
            stats_text += f"Min Growth Rate: {min(valid_rates):.2f}% (Year: {years[growth_rates.index(min(valid_rates))]})\n"
            stats_text += f"Std Deviation: {np.std(valid_rates):.2f}%\n\n"
            
            positive_years = sum(1 for r in valid_rates if r > 0)
            negative_years = sum(1 for r in valid_rates if r < 0)
            
            stats_text += f"Years with Positive Growth: {positive_years}\n"
            stats_text += f"Years with Negative Growth: {negative_years}\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def show_year_comparison_statistics(self, comparison_years):
        """Show year comparison statistics"""
        stats_text = "=" * 80 + "\n"
        stats_text += "YEAR COMPARISON STATISTICS\n"
        stats_text += "=" * 80 + "\n\n"
        
        stats_text += f"{'Continent':<20}"
        for year in comparison_years:
            stats_text += f"{str(year):<15}"
        stats_text += "\n" + "-" * 80 + "\n"
        
        for continent in self.continents:
            stats_text += f"{continent:<20}"
            continent_data = self.df[self.df['Continent'] == continent]
            for year in comparison_years:
                total = continent_data[year].sum()
                stats_text += f"${total/1e12:.2f}T"[:14] + " "
            stats_text += "\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def show_correlation_statistics(self, correlation_matrix, countries):
        """Show correlation statistics"""
        stats_text = "=" * 80 + "\n"
        stats_text += "CORRELATION ANALYSIS\n"
        stats_text += "=" * 80 + "\n\n"
        
        # Find highest correlations (excluding diagonal)
        correlations = []
        for i in range(len(countries)):
            for j in range(i+1, len(countries)):
                corr_value = correlation_matrix.iloc[i, j]
                correlations.append((countries[i], countries[j], corr_value))
        
        correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        stats_text += "HIGHEST CORRELATIONS:\n"
        stats_text += "-" * 80 + "\n"
        
        for i, (country1, country2, corr) in enumerate(correlations[:10], 1):
            stats_text += f"{i:2d}. {country1:25s} <-> {country2:25s} : {corr:6.3f}\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def display_plot(self, fig):
        """Display matplotlib figure in tkinter"""
        # Clear previous plot
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Switch to visualization tab
        self.notebook.select(self.viz_frame)
    
    def clear_visualization(self):
        """Clear all visualizations"""
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        self.stats_text.delete(1.0, tk.END)
        
        messagebox.showinfo("Info", "Visualization cleared")
    
    def export_analysis(self):
        """Export current analysis to file"""
        try:
            # Export statistics to text file
            stats_content = self.stats_text.get(1.0, tk.END)
            
            if stats_content.strip():
                with open('gdp_analysis_report.txt', 'w', encoding='utf-8') as f:
                    f.write(stats_content)
                
                messagebox.showinfo("Success", "Analysis exported to: gdp_analysis_report.txt")
            else:
                messagebox.showwarning("Warning", "No statistics to export. Run an analysis first.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def show_default_analysis(self):
        """Show a default visualization on startup"""
        try:
            # Automatically run the default analysis (country trend for first country)
            self.perform_analysis()
        except Exception as e:
            print(f"Could not load default visualization: {e}")


def main():
    root = tk.Tk()
    app = GDPDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
