# GDP Analysis Dashboard
# Mulkon aur continents ka GDP data analyze karne ke liye

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

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
TITLE_BAR_HEIGHT = 80
LEFT_PANEL_WIDTH = 350
MAX_COMPARE_COUNTRIES = 10
MAX_CORRELATION_COUNTRIES = 15
DEFAULT_TOP_N = 10
UPDATE_DELAY_MS = 300
DATA_FILE = 'gdp_with_continent_filled.xlsx'

COLOR_PRIMARY = '#3498db'
COLOR_SUCCESS = '#2ecc71'
COLOR_DANGER = '#e74c3c'
COLOR_DARK = '#2c3e50'
COLOR_LIGHT_BG = '#f0f0f0'
COLOR_WHITE = 'white'
COLOR_SECTION_BG = '#ecf0f1'

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class GDPDashboard:
    
    def __init__(self, root):
        self.root = root
        self.root.title("GDP Analysis Dashboard")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=COLOR_LIGHT_BG)
        
        self.load_data()
        self.create_widgets()
        
        # Shuru mein ek default graph dikhao
        self.root.after(100, self.show_default_analysis)
        
    def load_data(self):
        # Excel file se data load karo
        try:
            self.df = pd.read_excel(DATA_FILE)
            
            # Year columns nikalo
            self.year_columns = [col for col in self.df.columns if isinstance(col, int)]
            self.year_columns.sort()
            
            # Countries aur continents ki list banao
            self.countries = sorted(self.df['Country Name'].unique())
            self.continents = sorted(self.df['Continent'].dropna().unique())
            
            print(f"Data loaded: {len(self.df)} countries, {len(self.year_columns)} years")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.root.destroy()
    
    def create_widgets(self):
        # Title bar banao
        self._create_title_bar()
        
        main_container = tk.Frame(self.root, bg=COLOR_LIGHT_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Baayi taraf control panel
        left_panel = tk.Frame(main_container, bg=COLOR_WHITE, width=LEFT_PANEL_WIDTH, 
                             relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=5)
        left_panel.pack_propagate(False)
        
        # Daahini taraf visualization panel
        right_panel = tk.Frame(main_container, bg=COLOR_WHITE, relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)
        
        self.create_control_panel(left_panel)
        self.create_visualization_panel(right_panel)
    
    def _create_title_bar(self):
        title_frame = tk.Frame(self.root, bg=COLOR_DARK, height=TITLE_BAR_HEIGHT)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🌍 GDP Analysis Dashboard 📊", 
            font=('Arial', 24, 'bold'),
            bg=COLOR_DARK,
            fg=COLOR_WHITE
        )
        title_label.pack(expand=True)
    
    def create_control_panel(self, parent):
        # Scrollable frame banao controls ke liye
        canvas = tk.Canvas(parent, bg=COLOR_WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_WHITE)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Analysis type ka section
        self.create_section_header(scrollable_frame, "📈 Analysis Type")
        self._create_analysis_type_options(scrollable_frame)
        
        # Country selection section
        self.create_section_header(scrollable_frame, "🌐 Country Selection")
        self._create_country_selection(scrollable_frame)
        
        # Continent selection dropdown
        self.create_section_header(scrollable_frame, "🗺️ Continent Selection")
        self._create_continent_selection(scrollable_frame)
        
        # Year range ki selection
        self.create_section_header(scrollable_frame, "📅 Year Range")
        self._create_year_range_selection(scrollable_frame)
        
        # Top N countries ki selection
        self.create_section_header(scrollable_frame, "🏆 Top N Countries")
        self._create_top_n_selection(scrollable_frame)
        
        # Action buttons
        self._create_action_buttons(scrollable_frame)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_analysis_type_options(self, parent):
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
                parent,
                text=text,
                variable=self.analysis_type,
                value=value,
                bg=COLOR_WHITE,
                font=('Arial', 10),
                command=self.on_analysis_change
            )
            rb.pack(anchor=tk.W, padx=20, pady=2)
    
    def _create_country_selection(self, parent):
        # Pehla country dropdown
        tk.Label(parent, text="Primary Country:", bg=COLOR_WHITE, 
                font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20, pady=(5, 2))
        self.country_var = tk.StringVar(value=self.countries[0])
        country_combo = ttk.Combobox(parent, textvariable=self.country_var, 
                                     values=self.countries, width=30, state='readonly')
        country_combo.pack(padx=20, pady=(0, 10))
        country_combo.bind('<<ComboboxSelected>>', lambda e: self.on_primary_country_change())
        
        # Compare karne ke liye countries ki list
        tk.Label(parent, text="Compare With:", bg=COLOR_WHITE, 
                font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20, pady=(5, 2))
        
        compare_frame = tk.Frame(parent, bg=COLOR_WHITE)
        compare_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        self.compare_listbox = tk.Listbox(compare_frame, height=4, selectmode=tk.MULTIPLE, 
                                         exportselection=False)
        compare_scrollbar = ttk.Scrollbar(compare_frame, orient=tk.VERTICAL, 
                                         command=self.compare_listbox.yview)
        self.compare_listbox.configure(yscrollcommand=compare_scrollbar.set)
        
        for country in self.countries:
            self.compare_listbox.insert(tk.END, country)
        
        self.compare_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        compare_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.compare_listbox.bind('<<ListboxSelect>>', lambda e: self.on_compare_selection_change())
    
    def _create_continent_selection(self, parent):
        self.continent_var = tk.StringVar(value=self.continents[0] if self.continents else "")
        continent_combo = ttk.Combobox(parent, textvariable=self.continent_var, 
                                      values=self.continents, width=30, state='readonly')
        continent_combo.pack(padx=20, pady=(0, 10))
        continent_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
    
    def _create_year_range_selection(self, parent):
        year_frame = tk.Frame(parent, bg=COLOR_WHITE)
        year_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        tk.Label(year_frame, text="From:", bg=COLOR_WHITE, font=('Arial', 9)).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_year_var = tk.StringVar(value=str(self.year_columns[0]))
        start_year_combo = ttk.Combobox(year_frame, textvariable=self.start_year_var, 
                                       values=[str(y) for y in self.year_columns], 
                                       width=10, state='readonly')
        start_year_combo.grid(row=0, column=1, padx=(0, 10))
        start_year_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
        
        tk.Label(year_frame, text="To:", bg=COLOR_WHITE, font=('Arial', 9)).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.end_year_var = tk.StringVar(value=str(self.year_columns[-1]))
        end_year_combo = ttk.Combobox(year_frame, textvariable=self.end_year_var, 
                                     values=[str(y) for y in self.year_columns], 
                                     width=10, state='readonly')
        end_year_combo.grid(row=0, column=3)
        end_year_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
    
    def _create_top_n_selection(self, parent):
        top_frame = tk.Frame(parent, bg=COLOR_WHITE)
        top_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        tk.Label(top_frame, text="Top N:", bg=COLOR_WHITE, font=('Arial', 9)).pack(
            side=tk.LEFT, padx=(0, 10))
        self.top_n_var = tk.IntVar(value=DEFAULT_TOP_N)
        top_n_spinner = tk.Spinbox(top_frame, from_=5, to=50, textvariable=self.top_n_var, 
                                  width=10, command=self.on_selection_change)
        top_n_spinner.pack(side=tk.LEFT)
    
    def _create_action_buttons(self, parent):
        button_frame = tk.Frame(parent, bg=COLOR_WHITE)
        button_frame.pack(pady=20, padx=20, fill=tk.X)
        
        analyze_btn = tk.Button(
            button_frame,
            text="🔍 Analyze",
            command=self.perform_analysis,
            bg=COLOR_PRIMARY,
            fg=COLOR_WHITE,
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
            bg=COLOR_SUCCESS,
            fg=COLOR_WHITE,
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
            bg=COLOR_DANGER,
            fg=COLOR_WHITE,
            font=('Arial', 11, 'bold'),
            relief=tk.RAISED,
            borderwidth=2,
            cursor='hand2'
        )
        clear_btn.pack(fill=tk.X, pady=5)
    
    def create_section_header(self, parent, text):
        # Section header banao
        frame = tk.Frame(parent, bg=COLOR_SECTION_BG, height=35)
        frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        frame.pack_propagate(False)
        
        label = tk.Label(frame, text=text, bg=COLOR_SECTION_BG, 
                        font=('Arial', 11, 'bold'), fg=COLOR_DARK)
        label.pack(anchor=tk.W, padx=10, pady=5)
    
    def create_visualization_panel(self, parent):
        # Visualization panel mein tabs banao
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pehla tab - graphs ke liye
        self.viz_frame = tk.Frame(self.notebook, bg=COLOR_WHITE)
        self.notebook.add(self.viz_frame, text="📊 Visualization")
        
        # Dusra tab - statistics ke liye
        self.stats_frame = tk.Frame(self.notebook, bg=COLOR_WHITE)
        self.notebook.add(self.stats_frame, text="📋 Statistics")
        
        # Stats text area
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
        # Jab user analysis type change kare
        self.perform_analysis_delayed()
    
    def on_primary_country_change(self):
        # Jab primary country change ho
        if self.analysis_type.get() in ["country_trend", "compare_countries", "growth_rate"]:
            self.analysis_type.set("country_trend")
        self.compare_listbox.selection_clear(0, tk.END)
        self.perform_analysis_delayed()
    
    def on_compare_selection_change(self):
        # Jab compare list mein selection change ho
        selected_indices = self.compare_listbox.curselection()
        if len(selected_indices) >= 1:
            self.analysis_type.set("compare_countries")
        self.perform_analysis_delayed()
    
    def on_selection_change(self):
        # Koi bhi selection change ho to update karo
        self.perform_analysis_delayed()
    
    def perform_analysis_delayed(self):
        # Thoda delay kar ke analysis chalaao taake bahut zyada updates na hon
        if hasattr(self, '_update_timer'):
            self.root.after_cancel(self._update_timer)
        self._update_timer = self.root.after(UPDATE_DELAY_MS, self.perform_analysis)
    
    def get_year_range(self):
        # Selected year range nikalo
        start_year = int(self.start_year_var.get())
        end_year = int(self.end_year_var.get())
        
        if start_year > end_year:
            start_year, end_year = end_year, start_year
            
        return [y for y in self.year_columns if start_year <= y <= end_year]
    
    def _get_country_data(self, country, years):
        country_data = self.df[self.df['Country Name'] == country]
        if country_data.empty:
            return None
        return country_data[years].values.flatten()
    
    def _calculate_growth_rates(self, gdp_values, years):
        growth_rates = []
        growth_years = []
        
        for i in range(1, len(gdp_values)):
            if not np.isnan(gdp_values[i]) and not np.isnan(gdp_values[i-1]) and gdp_values[i-1] != 0:
                growth_rate = ((gdp_values[i] - gdp_values[i-1]) / gdp_values[i-1]) * 100
                growth_rates.append(growth_rate)
                growth_years.append(years[i])
        
        return growth_rates, growth_years
    
    def perform_analysis(self):
        # Jo analysis select hai wo chalaao
        analysis = self.analysis_type.get()
        
        analysis_map = {
            "country_trend": self.plot_country_trend,
            "compare_countries": self.plot_compare_countries,
            "continent_analysis": self.plot_continent_analysis,
            "top_countries": self.plot_top_countries,
            "growth_rate": self.plot_growth_rate,
            "statistics": self.show_statistics,
            "year_comparison": self.plot_year_comparison,
            "correlation": self.plot_correlation
        }
        
        try:
            analysis_function = analysis_map.get(analysis)
            if analysis_function:
                analysis_function()
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            print(f"Error details: {e}")
    
    def plot_country_trend(self):
        # Ek country ka GDP trend dikhao
        country = self.country_var.get()
        years = self.get_year_range()
        
        gdp_values = self._get_country_data(country, years)
        if gdp_values is None:
            messagebox.showwarning("Warning", f"No data found for {country}")
            return
        
        # Graph banao
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        ax.plot(years, gdp_values, marker='o', linewidth=2, markersize=4, color=COLOR_PRIMARY)
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('GDP (USD)', fontsize=12, fontweight='bold')
        ax.set_title(f'GDP Trend: {country}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.ticklabel_format(style='plain', axis='y')
        
        # Agar bahut zyada years hain to labels ghumao
        if len(years) > 20:
            ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_country_statistics(country, years, gdp_values)
    
    def plot_compare_countries(self):
        # Multiple countries ka comparison dikhao
        primary_country = self.country_var.get()
        selected_indices = self.compare_listbox.curselection()
        
        # Primary country ko list mein shuru mein daalo
        countries = [primary_country]
        
        # Selected countries ko add karo (agar primary country already selected hai to skip karo)
        for i in selected_indices:
            country = self.compare_listbox.get(i)
            if country != primary_country:
                countries.append(country)
        
        if len(countries) > MAX_COMPARE_COUNTRIES:
            messagebox.showwarning("Warning", 
                f"Please select maximum {MAX_COMPARE_COUNTRIES - 1} countries to compare with primary country")
            return
            
        years = self.get_year_range()
        
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(countries)))
        
        for idx, country in enumerate(countries):
            gdp_values = self._get_country_data(country, years)
            if gdp_values is not None:
                # Primary country ko thicker line aur larger marker se dikhao
                if country == primary_country:
                    ax.plot(years, gdp_values, marker='o', label=f"{country} (Primary)", 
                           linewidth=3, markersize=5, color=colors[idx])
                else:
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
        
        self.show_comparison_statistics(countries, years)
    
    def plot_continent_analysis(self):
        # Continent wise GDP analysis dikhao
        continent = self.continent_var.get()
        years = self.get_year_range()
        
        continent_data = self.df[self.df['Continent'] == continent]
        if continent_data.empty:
            messagebox.showwarning("Warning", f"No data found for {continent}")
            return
        
        # Multiple subplots banao
        fig = Figure(figsize=(14, 10))
        
        # Plot 1: Total GDP trend
        ax1 = fig.add_subplot(221)
        total_gdp = continent_data[years].sum()
        ax1.plot(years, total_gdp.values, marker='o', linewidth=2, color=COLOR_SUCCESS)
        ax1.set_title(f'Total GDP Trend: {continent}', fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Total GDP (USD)')
        ax1.grid(True, alpha=0.3)
        ax1.ticklabel_format(style='plain', axis='y')
        
        # Plot 2: Top countries in latest year
        ax2 = fig.add_subplot(222)
        latest_year = years[-1]
        top_countries = continent_data.nlargest(DEFAULT_TOP_N, latest_year)
        countries_list = top_countries['Country Name'].values
        gdp_list = top_countries[latest_year].values
        
        bars = ax2.barh(countries_list, gdp_list, color=COLOR_PRIMARY)
        ax2.set_title(f'Top {DEFAULT_TOP_N} Countries in {latest_year}', fontweight='bold')
        ax2.set_xlabel('GDP (USD)')
        ax2.ticklabel_format(style='plain', axis='x')
        
        # Plot 3: Average GDP by country
        ax3 = fig.add_subplot(223)
        avg_gdp = continent_data[years].mean(axis=1)
        continent_data_with_avg = continent_data.copy()
        continent_data_with_avg['avg_gdp'] = avg_gdp
        top_avg = continent_data_with_avg.nlargest(DEFAULT_TOP_N, 'avg_gdp')
        
        ax3.barh(top_avg['Country Name'].values, top_avg['avg_gdp'].values, color=COLOR_DANGER)
        ax3.set_title(f'Top {DEFAULT_TOP_N} by Average GDP ({years[0]}-{years[-1]})', fontweight='bold')
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
        
        self.show_continent_statistics(continent, years)
    
    def plot_top_countries(self):
        # Top N countries ka GDP dikhao
        top_n = self.top_n_var.get()
        years = self.get_year_range()
        latest_year = years[-1]
        
        top_countries = self.df.nlargest(top_n, latest_year)
        
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
        
        # Value labels lagao bars par
        for bar, value in zip(bars, gdp_list):
            ax.text(value, bar.get_y() + bar.get_height()/2, 
                   f' {value:,.0f}', 
                   va='center', fontsize=8)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_top_countries_statistics(top_countries, latest_year)
    
    def plot_growth_rate(self):
        # GDP growth rate dikhao
        country = self.country_var.get()
        years = self.get_year_range()
        
        if len(years) < 2:
            messagebox.showwarning("Warning", "Need at least 2 years for growth rate calculation")
            return
        
        gdp_values = self._get_country_data(country, years)
        if gdp_values is None:
            messagebox.showwarning("Warning", f"No data found for {country}")
            return
        
        # Growth rates calculate karo
        growth_rates, growth_years = self._calculate_growth_rates(gdp_values, years)
        
        # Graph banao
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        colors = [COLOR_SUCCESS if gr >= 0 else COLOR_DANGER for gr in growth_rates]
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
        
        self.show_growth_statistics(country, growth_years, growth_rates)
    
    def plot_year_comparison(self):
        # Alag alag years mein continents ka comparison
        years = self.get_year_range()
        
        # Select evenly spaced years for comparison
        max_comparison_years = 6
        if len(years) > max_comparison_years:
            step = len(years) // max_comparison_years
            comparison_years = years[::step][:max_comparison_years]
        else:
            comparison_years = years
        
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
        
        self.show_year_comparison_statistics(comparison_years)
    
    def plot_correlation(self):
        selected_indices = self.compare_listbox.curselection()
        if len(selected_indices) < 2:
            messagebox.showwarning("Warning", "Please select at least 2 countries for correlation analysis")
            return
        
        if len(selected_indices) > MAX_CORRELATION_COUNTRIES:
            messagebox.showwarning("Warning", 
                f"Please select maximum {MAX_CORRELATION_COUNTRIES} countries for better visualization")
            return
            
        countries = [self.compare_listbox.get(i) for i in selected_indices]
        years = self.get_year_range()
        
        # Build correlation matrix
        data_dict = {}
        for country in countries:
            gdp_values = self._get_country_data(country, years)
            if gdp_values is not None:
                data_dict[country] = gdp_values
        
        corr_df = pd.DataFrame(data_dict)
        correlation_matrix = corr_df.corr()
        
        fig = Figure(figsize=(12, 10))
        ax = fig.add_subplot(111)
        
        im = ax.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        
        ax.set_xticks(np.arange(len(countries)))
        ax.set_yticks(np.arange(len(countries)))
        ax.set_xticklabels(countries, rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(countries, fontsize=8)
        
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20)
        
        for i in range(len(countries)):
            for j in range(len(countries)):
                text = ax.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=7)
        
        ax.set_title('GDP Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_correlation_statistics(correlation_matrix, countries)
    
    def show_statistics(self):
        years = self.get_year_range()
        
        stats_text = "=" * 80 + "\n"
        stats_text += " " * 25 + "GDP STATISTICAL SUMMARY\n"
        stats_text += "=" * 80 + "\n\n"
        
        stats_text += "OVERALL STATISTICS\n"
        stats_text += "-" * 80 + "\n"
        stats_text += f"Total Countries: {len(self.df)}\n"
        stats_text += f"Year Range: {years[0]} - {years[-1]}\n"
        stats_text += f"Total Years: {len(years)}\n\n"
        
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
        
        top_10 = self.df.nlargest(DEFAULT_TOP_N, latest_year)
        stats_text += f"TOP {DEFAULT_TOP_N} COUNTRIES IN {latest_year}\n"
        stats_text += "-" * 80 + "\n"
        for idx, row in enumerate(top_10.iterrows(), 1):
            country = row[1]['Country Name']
            gdp = row[1][latest_year]
            continent = row[1]['Continent']
            stats_text += f"{idx:2d}. {country:30s} ${gdp:20,.0f}  [{continent}]\n"
        
        stats_text += "\n"
        
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
        stats_text = "=" * 80 + "\n"
        stats_text += "CORRELATION ANALYSIS\n"
        stats_text += "=" * 80 + "\n\n"
        
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
        # Graph ko display karo
        # Pehle se jo graph hai wo clear karo
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Visualization tab par switch karo
        self.notebook.select(self.viz_frame)
    
    def clear_visualization(self):
        # Saari visualizations clear kar do
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        self.stats_text.delete(1.0, tk.END)
        
        messagebox.showinfo("Info", "Visualization cleared")
    
    def export_analysis(self):
        # Current analysis ko file mein save karo
        try:
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
        # Dashboard khulte hi pehli country ka graph dikha do
        try:
            self.perform_analysis()
        except Exception as e:
            print(f"Could not load default visualization: {e}")


def main():
    root = tk.Tk()
    app = GDPDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
