# GDP Analysis Dashboard
# Mulkon aur continents ka GDP data analyze karne ke liye

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import warnings
import numpy as np

from data_loader import ConfigLoader, GDPDataLoader
from data_processor import GDPDataProcessor

warnings.filterwarnings('ignore')


class GDPDashboard:
    
    def __init__(self, root):
        self.root = root
        
        # Load configuration
        try:
            self.config = ConfigLoader()
        except Exception as e:
            messagebox.showerror("Configuration Error", str(e))
            root.destroy()
            return
        
        # Setup UI from config
        ui_config = self.config.get('ui')
        self.root.title(ui_config['title'])
        self.root.geometry(f"{ui_config['window_width']}x{ui_config['window_height']}")
        self.root.configure(bg=self.config.get('colors', 'light_bg'))
        
        # Apply visualization settings
        viz_config = self.config.get('visualization')
        sns.set_style(viz_config['style'])
        plt.rcParams['figure.figsize'] = viz_config['figure_size']
        
        # Load data
        try:
            data_loader = GDPDataLoader(self.config)
            data_loader.load_data()
            
            # Get data components
            self.df = data_loader.get_dataframe()
            self.year_columns = data_loader.get_year_columns()
            self.countries = data_loader.get_countries()
            self.continents = data_loader.get_continents()
            
            # Initialize data processor
            self.processor = GDPDataProcessor(self.df, self.year_columns)
            
            # Print data summary
            summary = data_loader.get_summary()
            print(f"Data loaded: {summary['total_countries']} countries, {summary['total_years']} years")
            
        except Exception as e:
            messagebox.showerror("Data Loading Error", str(e))
            root.destroy()
            return
        
        self.create_widgets()
        
        # Shuru mein ek default graph dikhao
        self.root.after(100, self.show_default_analysis)
    
    def create_widgets(self):
        # Title bar banao
        self._create_title_bar()
        
        colors = self.config.get('colors')
        ui_config = self.config.get('ui')
        
        main_container = tk.Frame(self.root, bg=colors['light_bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Baayi taraf control panel
        left_panel = tk.Frame(main_container, bg=colors['white'], 
                             width=ui_config['left_panel_width'], 
                             relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=5)
        left_panel.pack_propagate(False)
        
        # Daahini taraf visualization panel
        right_panel = tk.Frame(main_container, bg=colors['white'], 
                              relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)
        
        self.create_control_panel(left_panel)
        self.create_visualization_panel(right_panel)
    
    def _create_title_bar(self):
        colors = self.config.get('colors')
        ui_config = self.config.get('ui')
        
        title_frame = tk.Frame(self.root, bg=colors['dark'], 
                              height=ui_config['title_bar_height'])
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text=ui_config['title_emoji'], 
            font=('Arial', 24, 'bold'),
            bg=colors['dark'],
            fg=colors['white']
        )
        title_label.pack(expand=True)
    
    def create_control_panel(self, parent):
        colors = self.config.get('colors')
        
        # Scrollable frame banao controls ke liye
        canvas = tk.Canvas(parent, bg=colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=colors['white'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling enable karo
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel to canvas and all child widgets
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
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
        colors = self.config.get('colors')
        analyses = self.config.get('analysis_types')
        
        self.analysis_type = tk.StringVar(value=analyses[0]['value'])
        
        for analysis in analyses:
            rb = tk.Radiobutton(
                parent,
                text=analysis['name'],
                variable=self.analysis_type,
                value=analysis['value'],
                bg=colors['white'],
                font=('Arial', 10),
                command=self.on_analysis_change
            )
            rb.pack(anchor=tk.W, padx=20, pady=2)
    
    def _create_country_selection(self, parent):
        colors = self.config.get('colors')
        
        # Pehla country dropdown
        tk.Label(parent, text="Primary Country:", bg=colors['white'], 
                font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20, pady=(5, 2))
        self.country_var = tk.StringVar(value=self.countries[0])
        country_combo = ttk.Combobox(parent, textvariable=self.country_var, 
                                     values=self.countries, width=30, state='readonly')
        country_combo.pack(padx=20, pady=(0, 10))
        country_combo.bind('<<ComboboxSelected>>', lambda e: self.on_primary_country_change())
        
        # Compare karne ke liye countries ki list
        tk.Label(parent, text="Compare With:", bg=colors['white'], 
                font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20, pady=(5, 2))
        
        compare_frame = tk.Frame(parent, bg=colors['white'])
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
        colors = self.config.get('colors')
        
        self.continent_var = tk.StringVar(value=self.continents[0] if self.continents else "")
        continent_combo = ttk.Combobox(parent, textvariable=self.continent_var, 
                                      values=self.continents, width=30, state='readonly')
        continent_combo.pack(padx=20, pady=(0, 10))
        continent_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
    
    def _create_year_range_selection(self, parent):
        colors = self.config.get('colors')
        
        year_frame = tk.Frame(parent, bg=colors['white'])
        year_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        tk.Label(year_frame, text="From:", bg=colors['white'], font=('Arial', 9)).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_year_var = tk.StringVar(value=str(self.year_columns[0]))
        start_year_combo = ttk.Combobox(year_frame, textvariable=self.start_year_var, 
                                       values=[str(y) for y in self.year_columns], 
                                       width=10, state='readonly')
        start_year_combo.grid(row=0, column=1, padx=(0, 10))
        start_year_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
        
        tk.Label(year_frame, text="To:", bg=colors['white'], font=('Arial', 9)).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.end_year_var = tk.StringVar(value=str(self.year_columns[-1]))
        end_year_combo = ttk.Combobox(year_frame, textvariable=self.end_year_var, 
                                     values=[str(y) for y in self.year_columns], 
                                     width=10, state='readonly')
        end_year_combo.grid(row=0, column=3)
        end_year_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
    
    def _create_top_n_selection(self, parent):
        colors = self.config.get('colors')
        ui_config = self.config.get('ui')
        
        top_frame = tk.Frame(parent, bg=colors['white'])
        top_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        tk.Label(top_frame, text="Top N:", bg=colors['white'], font=('Arial', 9)).pack(
            side=tk.LEFT, padx=(0, 10))
        self.top_n_var = tk.IntVar(value=ui_config['default_top_n'])
        top_n_spinner = tk.Spinbox(top_frame, from_=5, to=50, textvariable=self.top_n_var, 
                                  width=10, command=self.on_selection_change)
        top_n_spinner.pack(side=tk.LEFT)
    
    def _create_action_buttons(self, parent):
        colors = self.config.get('colors')
        
        # Add header for action buttons
        action_header = tk.Frame(parent, bg=colors['section_bg'], height=35)
        action_header.pack(fill=tk.X, padx=15, pady=(15, 5))
        action_header.pack_propagate(False)
        
        header_label = tk.Label(action_header, text="⚡ Actions", bg=colors['section_bg'], 
                        font=('Arial', 11, 'bold'), fg=colors['dark'])
        header_label.pack(anchor=tk.W, padx=10, pady=5)
        
        button_frame = tk.Frame(parent, bg=colors['white'])
        button_frame.pack(pady=10, padx=20, fill=tk.X)
        
        analyze_btn = tk.Button(
            button_frame,
            text="🔍 Analyze",
            command=self.perform_analysis,
            bg=colors['primary'],
            fg=colors['white'],
            font=('Arial', 12, 'bold'),
            relief=tk.RAISED,
            borderwidth=3,
            cursor='hand2',
            height=2
        )
        analyze_btn.pack(fill=tk.X, pady=5)
        
        export_btn = tk.Button(
            button_frame,
            text="💾 Export Results to TXT",
            command=self.export_analysis,
            bg=colors['success'],
            fg=colors['white'],
            font=('Arial', 11, 'bold'),
            relief=tk.RAISED,
            borderwidth=2,
            cursor='hand2',
            height=2
        )
        export_btn.pack(fill=tk.X, pady=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear Visualization",
            command=self.clear_visualization,
            bg=colors['danger'],
            fg=colors['white'],
            font=('Arial', 11, 'bold'),
            relief=tk.RAISED,
            borderwidth=2,
            cursor='hand2',
            height=2
        )
        clear_btn.pack(fill=tk.X, pady=5)
    
    def create_section_header(self, parent, text):
        colors = self.config.get('colors')
        
        # Section header banao
        frame = tk.Frame(parent, bg=colors['section_bg'], height=35)
        frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        frame.pack_propagate(False)
        
        label = tk.Label(frame, text=text, bg=colors['section_bg'], 
                        font=('Arial', 11, 'bold'), fg=colors['dark'])
        label.pack(anchor=tk.W, padx=10, pady=5)
    
    def create_visualization_panel(self, parent):
        colors = self.config.get('colors')
        
        # Visualization panel mein tabs banao
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pehla tab - graphs ke liye
        self.viz_frame = tk.Frame(self.notebook, bg=colors['white'])
        self.notebook.add(self.viz_frame, text="📊 Visualization")
        
        # Dusra tab - statistics ke liye
        self.stats_frame = tk.Frame(self.notebook, bg=colors['white'])
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
        analysis_types_with_country = ["country_trend", "compare_countries", "growth_rate", "statistics", "phase1_year", "phase1_complete"]
        current_analysis = self.analysis_type.get()
        
        # If not already on a country-focused analysis, switch to country trend
        if current_analysis not in analysis_types_with_country:
            self.analysis_type.set("country_trend")
        
        # Don't clear compare listbox - allow user to select primary and compare countries
        # self.compare_listbox.selection_clear(0, tk.END)
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
        ui_config = self.config.get('ui')
        if hasattr(self, '_update_timer'):
            self.root.after_cancel(self._update_timer)
        self._update_timer = self.root.after(ui_config['update_delay_ms'], self.perform_analysis)
    
    def get_year_range(self):
        # Selected year range nikalo
        start_year = int(self.start_year_var.get())
        end_year = int(self.end_year_var.get())
        
        if start_year > end_year:
            start_year, end_year = end_year, start_year
            
        return [y for y in self.year_columns if start_year <= y <= end_year]
    
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
            "correlation": self.plot_correlation,
            "phase1_regional": self.plot_phase1_regional_analysis,
            "phase1_year": self.plot_phase1_year_analysis,
            "phase1_complete": self.plot_phase1_complete_analysis
        }
        
        try:
            analysis_function = analysis_map.get(analysis)
            if analysis_function:
                analysis_function()
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Analysis failed: {str(e)}")
            print(f"Error details: {e}")
    
    def plot_country_trend(self):
        # Ek country ka GDP trend dikhao
        country = self.country_var.get()
        years = self.get_year_range()
        
        gdp_values = self.processor.get_country_data(country, years)
        if gdp_values is None:
            messagebox.showwarning("Warning", f"No data found for {country}")
            return
        
        colors = self.config.get('colors')
        viz_config = self.config.get('visualization')
        
        # Graph banao
        fig = Figure(figsize=tuple(viz_config['figure_size']))
        ax = fig.add_subplot(111)
        
        ax.plot(years, gdp_values, marker='o', linewidth=2, markersize=4, color=colors['primary'])
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('GDP (USD)', fontsize=12, fontweight='bold')
        ax.set_title(f'GDP Trend: {country}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.ticklabel_format(style='plain', axis='y')
        
        # Agar bahut zyada years hain to labels ghumao
        if len(years) > viz_config['max_years_rotation']:
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
        
        # Check if at least 2 countries are selected
        if len(countries) < 2:
            messagebox.showwarning("Selection Required", 
                "Please select at least one country from the 'Compare Countries' list to compare with the primary country.\n\n"
                "Tip: Hold Ctrl and click to select multiple countries.")
            return
        
        ui_config = self.config.get('ui')
        if len(countries) > ui_config['max_compare_countries']:
            messagebox.showwarning("Warning", 
                f"Please select maximum {ui_config['max_compare_countries'] - 1} countries to compare with primary country")
            return
            
        years = self.get_year_range()
        colors_config = self.config.get('colors')
        viz_config = self.config.get('visualization')
        
        fig = Figure(figsize=tuple(viz_config['figure_size']))
        ax = fig.add_subplot(111)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(countries)))
        
        for idx, country in enumerate(countries):
            gdp_values = self.processor.get_country_data(country, years)
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
        
        if len(years) > viz_config['max_years_rotation']:
            ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_comparison_statistics(countries, years)
    
    def plot_continent_analysis(self):
        # Continent wise GDP analysis dikhao
        continent = self.continent_var.get()
        years = self.get_year_range()
        
        continent_data = self.processor.get_continent_data(continent)
        if continent_data.empty:
            messagebox.showwarning("Warning", f"No data found for {continent}")
            return
        
        ui_config = self.config.get('ui')
        colors = self.config.get('colors')
        viz_config = self.config.get('visualization')
        
        # Multiple subplots banao
        fig = Figure(figsize=tuple(viz_config['figure_size_large']))
        
        # Plot 1: Total GDP trend
        ax1 = fig.add_subplot(221)
        total_gdp = self.processor.calculate_total_gdp(continent_data, years)
        ax1.plot(years, total_gdp.values, marker='o', linewidth=2, color=colors['success'])
        ax1.set_title(f'Total GDP Trend: {continent}', fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Total GDP (USD)')
        ax1.grid(True, alpha=0.3)
        ax1.ticklabel_format(style='plain', axis='y')
        
        # Plot 2: Top countries in latest year
        ax2 = fig.add_subplot(222)
        latest_year = years[-1]
        top_countries = continent_data.nlargest(ui_config['default_top_n'], latest_year)
        countries_list = top_countries['Country Name'].values
        gdp_list = top_countries[latest_year].values
        
        ax2.barh(countries_list, gdp_list, color=colors['primary'])
        ax2.set_title(f"Top {ui_config['default_top_n']} Countries in {latest_year}", fontweight='bold')
        ax2.set_xlabel('GDP (USD)')
        ax2.ticklabel_format(style='plain', axis='x')
        
        # Plot 3: Average GDP by country
        ax3 = fig.add_subplot(223)
        avg_gdp = self.processor.calculate_average_gdp(continent_data, years)
        continent_data_with_avg = continent_data.copy()
        continent_data_with_avg['avg_gdp'] = avg_gdp
        top_avg = continent_data_with_avg.nlargest(ui_config['default_top_n'], 'avg_gdp')
        
        ax3.barh(top_avg['Country Name'].values, top_avg['avg_gdp'].values, color=colors['danger'])
        ax3.set_title(f"Top {ui_config['default_top_n']} by Average GDP ({years[0]}-{years[-1]})", fontweight='bold')
        ax3.set_xlabel('Average GDP (USD)')
        ax3.ticklabel_format(style='plain', axis='x')
        
        # Plot 4: GDP distribution
        ax4 = fig.add_subplot(224)
        latest_gdp = continent_data[latest_year].dropna()
        ax4.hist(latest_gdp, bins=viz_config['histogram_bins'], color='#9b59b6', edgecolor='black', alpha=0.7)
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
        
        top_countries = self.processor.get_top_countries(latest_year, top_n)
        
        viz_config = self.config.get('visualization')
        fig = Figure(figsize=tuple(viz_config['figure_size_tall']))
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
        
        gdp_values = self.processor.get_country_data(country, years)
        if gdp_values is None:
            messagebox.showwarning("Warning", f"No data found for {country}")
            return
        
        # Growth rates calculate karo
        growth_rates, growth_years = self.processor.calculate_growth_rates(gdp_values, years)
        
        colors_config = self.config.get('colors')
        viz_config = self.config.get('visualization')
        
        # Graph banao
        fig = Figure(figsize=tuple(viz_config['figure_size']))
        ax = fig.add_subplot(111)
        
        colors = [colors_config['success'] if gr >= 0 else colors_config['danger'] for gr in growth_rates]
        ax.bar(growth_years, growth_rates, color=colors, alpha=0.7, edgecolor='black')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Growth Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'GDP Growth Rate: {country}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        if len(growth_years) > viz_config['max_years_rotation']:
            ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_growth_statistics(country, growth_years, growth_rates)
    
    def plot_year_comparison(self):
        # Alag alag years mein continents ka comparison
        years = self.get_year_range()
        
        viz_config = self.config.get('visualization')
        
        # Select evenly spaced years for comparison
        max_years = viz_config['max_comparison_years']
        if len(years) > max_years:
            step = len(years) // max_years
            comparison_years = years[::step][:max_years]
        else:
            comparison_years = years
        
        fig = Figure(figsize=tuple(viz_config['figure_size_large']))
        ax = fig.add_subplot(111)
        
        x = np.arange(len(self.continents))
        width = 0.8 / len(comparison_years)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(comparison_years)))
        
        comparison_data = self.processor.get_year_comparison_data(comparison_years, self.continents)
        
        for idx, year in enumerate(comparison_years):
            continent_gdp = [comparison_data[year][continent] for continent in self.continents]
            
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
        primary_country = self.country_var.get()
        selected_indices = self.compare_listbox.curselection()
        
        # Primary country ko list mein shuru mein daalo
        countries = [primary_country]
        
        # Selected countries ko add karo (agar primary country already selected hai to skip karo)
        for i in selected_indices:
            country = self.compare_listbox.get(i)
            if country != primary_country:
                countries.append(country)
        
        ui_config = self.config.get('ui')
        if len(countries) < 2:
            messagebox.showwarning("Selection Required", 
                "Please select at least one country from the 'Compare Countries' list for correlation analysis with the primary country.\n\n"
                "Tip: Hold Ctrl and click to select multiple countries.")
            return
        
        if len(countries) > ui_config['max_correlation_countries']:
            messagebox.showwarning("Warning", 
                f"Please select maximum {ui_config['max_correlation_countries'] - 1} countries for better visualization")
            return
            
        years = self.get_year_range()
        
        # Build correlation matrix
        correlation_matrix = self.processor.get_correlation_matrix(countries, years)
        
        if correlation_matrix is None:
            messagebox.showwarning("Warning", "Could not build correlation matrix")
            return
        
        viz_config = self.config.get('visualization')
        fig = Figure(figsize=tuple(viz_config['correlation_figure_size']))
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
                ax.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                       ha="center", va="center", color="black", fontsize=7)
        
        ax.set_title('GDP Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_correlation_statistics(correlation_matrix, countries)
    
    def plot_phase1_regional_analysis(self):
        """Regional GDP analysis with Pie and Bar charts"""
        phase1_config = self.config.get('phase1_operations')
        if phase1_config:
            regions = phase1_config.get('compute_regions', self.continents)
        else:
            regions = self.continents
        
        years = self.get_year_range()
        latest_year = years[-1]
        colors_config = self.config.get('colors')
        viz_config = self.config.get('visualization')
        
        regional_gdps = list(map(
            lambda region: (region, self.df[self.df['Continent'] == region][latest_year].sum()),
            regions
        ))
        
        valid_regions = list(filter(lambda x: x[1] > 0, regional_gdps))
        
        region_names = [r[0] for r in valid_regions]
        gdp_values = [r[1] for r in valid_regions]
        
        fig = Figure(figsize=tuple(viz_config['figure_size_large']))
        
        ax1 = fig.add_subplot(121)
        colors_pie = plt.cm.Set3(range(len(region_names)))
        ax1.pie(gdp_values, labels=region_names, autopct='%1.1f%%', startangle=90, colors=colors_pie)
        ax1.set_title(f'Regional GDP Distribution ({latest_year})', fontweight='bold', fontsize=12)
        
        ax2 = fig.add_subplot(122)
        bars = ax2.bar(region_names, gdp_values, color=plt.cm.viridis(np.linspace(0, 1, len(region_names))))
        ax2.set_xlabel('Region', fontweight='bold')
        ax2.set_ylabel('GDP (USD)', fontweight='bold')
        ax2.set_title(f'Regional GDP Comparison ({latest_year})', fontweight='bold', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        ax2.ticklabel_format(style='plain', axis='y')
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_phase1_regional_statistics(region_names, gdp_values, latest_year)
    
    def plot_phase1_year_analysis(self):
        """Year-specific GDP analysis with Line and Scatter plots"""
        country = self.country_var.get()
        years = self.get_year_range()
        years_int = [int(y) for y in years]
        
        country_data = self.processor.get_country_data(country, years)
        
        if country_data is None:
            messagebox.showwarning("Warning", f"No data found for {country}")
            return
        
        viz_config = self.config.get('visualization')
        colors_config = self.config.get('colors')
        
        fig = Figure(figsize=tuple(viz_config['figure_size_large']))
        
        ax1 = fig.add_subplot(121)
        ax1.plot(years_int, country_data, marker='o', linewidth=2, color=colors_config['primary'], label=country)
        ax1.set_xlabel('Year', fontweight='bold')
        ax1.set_ylabel('GDP (USD)', fontweight='bold')
        ax1.set_title(f'{country} - GDP Trend Over Years', fontweight='bold', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.ticklabel_format(style='plain', axis='y')
        
        ax2 = fig.add_subplot(122)
        colors_scatter = plt.cm.coolwarm(np.linspace(0, 1, len(years_int)))
        ax2.scatter(years_int, country_data, c=colors_scatter, s=100, alpha=0.6, edgecolors='black')
        ax2.set_xlabel('Year', fontweight='bold')
        ax2.set_ylabel('GDP (USD)', fontweight='bold')
        ax2.set_title(f'{country} - GDP Scatter Analysis', fontweight='bold', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.ticklabel_format(style='plain', axis='y')
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_country_statistics(country, years_int, country_data)
    
    def plot_phase1_complete_analysis(self):
        phase1_config = self.config.get('phase1_operations')
        if phase1_config:
            regions = phase1_config.get('compute_regions', self.continents[:5])
        else:
            regions = self.continents[:5]
        
        country = self.country_var.get()
        years = self.get_year_range()
        years_int = [int(y) for y in years]
        latest_year = years[-1]
        
        viz_config = self.config.get('visualization')
        colors_config = self.config.get('colors')
        
        fig = Figure(figsize=(14, 10))
        
        ax1 = fig.add_subplot(221)
        regional_gdps = {region: self.df[self.df['Continent'] == region][latest_year].sum() for region in regions}
        valid_regions = {k: v for k, v in regional_gdps.items() if v > 0}
        
        ax1.pie(valid_regions.values(), labels=valid_regions.keys(), autopct='%1.1f%%', startangle=90)
        ax1.set_title(f'Regional GDP Distribution ({latest_year})', fontweight='bold')
        
        ax2 = fig.add_subplot(222)
        ax2.bar(valid_regions.keys(), valid_regions.values(), color=plt.cm.viridis(np.linspace(0, 1, len(valid_regions))))
        ax2.set_xlabel('Region', fontweight='bold')
        ax2.set_ylabel('GDP (USD)', fontweight='bold')
        ax2.set_title(f'Regional GDP Bar Chart ({latest_year})', fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.ticklabel_format(style='plain', axis='y')
        
        ax3 = fig.add_subplot(223)
        country_data = self.processor.get_country_data(country, years)
        if country_data is not None:
            ax3.plot(years_int, country_data, marker='o', linewidth=2, color=colors_config['success'])
            ax3.set_xlabel('Year', fontweight='bold')
            ax3.set_ylabel('GDP (USD)', fontweight='bold')
            ax3.set_title(f'{country} - Line Graph', fontweight='bold')
            ax3.grid(True, alpha=0.3)
            ax3.ticklabel_format(style='plain', axis='y')
        
        ax4 = fig.add_subplot(224)
        if country_data is not None:
            ax4.scatter(years_int, country_data, c=plt.cm.coolwarm(np.linspace(0, 1, len(years_int))), 
                       s=100, alpha=0.6, edgecolors='black')
            ax4.set_xlabel('Year', fontweight='bold')
            ax4.set_ylabel('GDP (USD)', fontweight='bold')
            ax4.set_title(f'{country} - Scatter Plot', fontweight='bold')
            ax4.grid(True, alpha=0.3)
            ax4.ticklabel_format(style='plain', axis='y')
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_phase1_complete_statistics(regions, country, years_int, latest_year)
    
    def show_phase1_regional_statistics(self, region_names, gdp_values, year):
        """Display regional statistics"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        from functools import reduce
        total_gdp = reduce(lambda a, b: a + b, gdp_values, 0)
        
        percentages = list(map(lambda gdp: (gdp / total_gdp) * 100, gdp_values))
        
        stats = f"Regional GDP Analysis ({year})\n"
        stats += "=" * 60 + "\n\n"
        
        for region, gdp, pct in zip(region_names, gdp_values, percentages):
            stats += f"{region:20s}: ${gdp:,.0f} ({pct:.1f}%)\n"
        
        stats += "\n" + "-" * 60 + "\n"
        stats += f"Total GDP: ${total_gdp:,.0f}\n"
        stats += f"Average GDP: ${total_gdp / len(gdp_values):,.0f}\n"
        
        self.stats_text.insert(tk.END, stats)
        self.stats_text.config(state=tk.DISABLED)
    
    def show_phase1_complete_statistics(self, regions, country, years, year):
        """Display complete statistics"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        stats = "Complete GDP Analysis\n"
        stats += "=" * 60 + "\n\n"
        stats += f"Configuration:\n"
        stats += f"  Selected Regions: {', '.join(regions)}\n"
        stats += f"  Selected Country: {country}\n"
        stats += f"  Year Range: {years[0]} - {years[-1]}\n"
        stats += f"  Latest Year: {year}\n\n"
        
        stats += "Visualizations Generated:\n"
        stats += "  ✓ Pie Chart - Regional GDP Distribution\n"
        stats += "  ✓ Bar Chart - Regional GDP Comparison\n"
        stats += "  ✓ Line Graph - Country GDP Trend\n"
        stats += "  ✓ Scatter Plot - Country GDP Analysis\n\n"
        
        self.stats_text.insert(tk.END, stats)
        self.stats_text.config(state=tk.DISABLED)
    
    def show_statistics(self):
        years = self.get_year_range()
        latest_year = years[-1]
        
        ui_config = self.config.get('ui')
        world_stats = self.processor.get_world_statistics(latest_year)
        
        # Get selected primary country
        selected_country = self.country_var.get()
        
        stats_text = "=" * 80 + "\n"
        stats_text += " " * 25 + "GDP STATISTICAL SUMMARY\n"
        stats_text += "=" * 80 + "\n\n"
        
        # Show primary country statistics first
        stats_text += f"SELECTED COUNTRY: {selected_country}\n"
        stats_text += "-" * 80 + "\n"
        
        country_data = self.processor.get_country_data(selected_country, years)
        if country_data is not None:
            country_stats = self.processor.calculate_statistics(country_data)
            if country_stats:
                stats_text += f"GDP in {latest_year}: ${country_data[-1]:,.0f}\n"
                stats_text += f"Maximum GDP ({years[0]}-{years[-1]}): ${country_stats['max']:,.0f}\n"
                stats_text += f"Minimum GDP ({years[0]}-{years[-1]}): ${country_stats['min']:,.0f}\n"
                stats_text += f"Average GDP: ${country_stats['mean']:,.0f}\n"
                stats_text += f"Median GDP: ${country_stats['median']:,.0f}\n"
                stats_text += f"Std Deviation: ${country_stats['std']:,.0f}\n"
                
                # Calculate growth
                growth_summary = self.processor.calculate_growth_summary(country_data, [int(y) for y in years])
                if growth_summary:
                    stats_text += f"Total Growth: {growth_summary['total_growth']:.2f}%\n"
                    if 'avg_annual_growth' in growth_summary:
                        stats_text += f"Avg Annual Growth: {growth_summary['avg_annual_growth']:.2f}%\n"
        stats_text += "\n"
        
        stats_text += "OVERALL STATISTICS\n"
        stats_text += "-" * 80 + "\n"
        stats_text += f"Total Countries: {len(self.df)}\n"
        stats_text += f"Year Range: {years[0]} - {years[-1]}\n"
        stats_text += f"Total Years: {len(years)}\n\n"
        
        stats_text += f"STATISTICS FOR {latest_year}\n"
        stats_text += "-" * 80 + "\n"
        stats_text += f"Total World GDP: ${world_stats['total_gdp']:,.0f}\n"
        stats_text += f"Average GDP: ${world_stats['avg_gdp']:,.0f}\n"
        stats_text += f"Median GDP: ${world_stats['median_gdp']:,.0f}\n"
        stats_text += f"Std Deviation: ${world_stats['std_gdp']:,.0f}\n"
        stats_text += f"Max GDP: ${world_stats['max_gdp']:,.0f}\n"
        stats_text += f"Min GDP: ${world_stats['min_gdp']:,.0f}\n\n"
        
        top_n = ui_config['default_top_n']
        top_countries = self.processor.get_top_countries(latest_year, top_n)
        stats_text += f"TOP {top_n} COUNTRIES IN {latest_year}\n"
        stats_text += "-" * 80 + "\n"
        for idx, row in enumerate(top_countries.iterrows(), 1):
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
            summary = self.processor.get_continent_summary(continent, latest_year)
            if summary:
                stats_text += f"{continent:<20} ${summary['total_gdp']:<24,.0f} ${summary['avg_gdp']:<24,.0f} {summary['country_count']:<10}\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
        self.notebook.select(self.stats_frame)
    
    def show_country_statistics(self, country, years, gdp_values):
        stats = self.processor.calculate_statistics(gdp_values)
        
        if stats is None:
            return
        
        stats_text = "=" * 80 + "\n"
        stats_text += f"STATISTICS FOR {country.upper()}\n"
        stats_text += "=" * 80 + "\n\n"
        
        stats_text += f"Period: {years[0]} - {years[-1]}\n"
        stats_text += f"Data Points: {stats['count']} / {len(years)}\n\n"
        
        stats_text += f"Maximum GDP: ${stats['max']:,.0f} (Year: {years[gdp_values.tolist().index(stats['max'])]})\n"
        stats_text += f"Minimum GDP: ${stats['min']:,.0f} (Year: {years[gdp_values.tolist().index(stats['min'])]})\n"
        stats_text += f"Average GDP: ${stats['mean']:,.0f}\n"
        stats_text += f"Median GDP: ${stats['median']:,.0f}\n"
        stats_text += f"Std Deviation: ${stats['std']:,.0f}\n\n"
        
        growth_summary = self.processor.calculate_growth_summary(gdp_values, years)
        if growth_summary:
            stats_text += f"Total Growth: {growth_summary['total_growth']:,.2f}%\n"
            if 'avg_annual_growth' in growth_summary:
                stats_text += f"Average Annual Growth: {growth_summary['avg_annual_growth']:,.2f}%\n"
        
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
        latest_year = years[-1]
        summary = self.processor.get_continent_summary(continent, latest_year)
        
        if summary is None:
            return
        
        stats_text = "=" * 80 + "\n"
        stats_text += f"STATISTICS FOR {continent.upper()}\n"
        stats_text += "=" * 80 + "\n\n"
        
        stats_text += f"Period: {years[0]} - {years[-1]}\n"
        stats_text += f"Total Countries: {summary['country_count']}\n\n"
        
        stats_text += f"Total GDP ({latest_year}): ${summary['total_gdp']:,.0f}\n"
        stats_text += f"Average GDP ({latest_year}): ${summary['avg_gdp']:,.0f}\n\n"
        
        stats_text += f"TOP 5 COUNTRIES IN {latest_year}\n"
        stats_text += "-" * 80 + "\n"
        for idx, row in enumerate(summary['top_countries'].iterrows(), 1):
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
        
        comparison_data = self.processor.get_year_comparison_data(comparison_years, self.continents)
        
        for continent in self.continents:
            stats_text += f"{continent:<20}"
            for year in comparison_years:
                total = comparison_data[year][continent]
                stats_text += f"${total/1e12:.2f}T"[:14] + " "
            stats_text += "\n"
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def show_correlation_statistics(self, correlation_matrix, countries):
        stats_text = "=" * 80 + "\n"
        stats_text += "CORRELATION ANALYSIS\n"
        stats_text += "=" * 80 + "\n\n"
        
        correlations = self.processor.get_top_correlations(correlation_matrix, 10)
        
        stats_text += "HIGHEST CORRELATIONS:\n"
        stats_text += "-" * 80 + "\n"
        
        for i, (country1, country2, corr) in enumerate(correlations, 1):
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
                export_file = self.config.get('data', 'export_file')
                with open(export_file, 'w', encoding='utf-8') as f:
                    f.write(stats_content)
                
                messagebox.showinfo("Success", f"Analysis exported to: {export_file}")
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
