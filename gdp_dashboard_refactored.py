# GDP Analysis Dashboard
# Mulkon aur continents ka GDP data analyze karne ke liye

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import tkinter as tk
from tkinter import messagebox, scrolledtext
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import warnings
import numpy as np
from functools import reduce
import mplcyberpunk

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
        colors = self.config.get('colors')
        self.root.title(ui_config['title'])
        self.root.geometry(f"{ui_config['window_width']}x{ui_config['window_height']}")
        self.root.configure(bg=colors['dark'])
        
        # Apply professional dark visualization settings
        viz_config = self.config.get('visualization')
        plt.style.use('dark_background')
        plt.rcParams.update({
            'figure.facecolor': viz_config.get('chart_face_color', '#0d0d0d'),
            'axes.facecolor': viz_config.get('chart_bg_color', '#000000'),
            'axes.edgecolor': '#2f3336',
            'axes.labelcolor': '#e7e9ea',
            'text.color': '#e7e9ea',
            'xtick.color': '#71767b',
            'ytick.color': '#71767b',
            'grid.color': viz_config.get('grid_color', '#2f3336'),
            'grid.alpha': viz_config.get('grid_alpha', 0.4),
            'font.family': 'Segoe UI',
            'axes.titlesize': viz_config.get('title_font_size', 16),
            'axes.labelsize': viz_config.get('label_font_size', 12),
            'xtick.labelsize': viz_config.get('tick_font_size', 9),
            'ytick.labelsize': viz_config.get('tick_font_size', 9),
        })
        
        # Store chart palette for quick access
        self.neon_palette = colors.get('chart_palette', 
            ['#1d9bf0', '#00ba7c', '#f4212e', '#ffad1f', '#794bc4', '#ff7a00'])
        
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
        
        # Force all text to X-white after widgets exist
        self._force_white_text(self.root)
        
        # Shuru mein ek default graph dikhao
        self.root.after(100, self.show_default_analysis)
    
    def create_widgets(self):
        # Title bar banao
        self._create_title_bar()
        
        colors = self.config.get('colors')
        ui_config = self.config.get('ui')
        
        main_container = tk.Frame(self.root, bg=colors['dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Neon left panel
        left_panel = tk.Frame(main_container, bg=colors['dark_card'],
                             width=ui_config['left_panel_width'],
                             relief=tk.FLAT, borderwidth=0,
                             highlightbackground=colors['dark_border'],
                             highlightthickness=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=5)
        left_panel.pack_propagate(False)
        
        # Right panel
        right_panel = tk.Frame(main_container, bg=colors['dark_card'],
                              relief=tk.FLAT, borderwidth=0,
                              highlightbackground=colors['dark_border'],
                              highlightthickness=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)
        
        self.create_control_panel(left_panel)
        self.create_visualization_panel(right_panel)
    
    def _create_title_bar(self):
        colors = self.config.get('colors')
        ui_config = self.config.get('ui')
        
        title_frame = tk.Frame(self.root, bg=colors['dark_surface'],
                              height=ui_config['title_bar_height'],
                              highlightbackground=colors['dark_border'],
                              highlightthickness=1)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text=ui_config['title_emoji'],
            font=('Segoe UI', 22, 'bold'),
            bg=colors['dark_surface'],
            fg='#e7e9ea'
        )
        title_label.pack(expand=True)
        
        # Subtle X-blue accent line at bottom of title
        accent_line = tk.Frame(self.root, bg=colors['ui_accent'], height=2)
        accent_line.pack(fill=tk.X)
    
    def create_control_panel(self, parent):
        colors = self.config.get('colors')
        
        # Dark themed scrollable frame with purple scrollbar
        canvas = tk.Canvas(parent, bg=colors['dark_card'], highlightthickness=0)
        scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=canvas.yview, bootstyle="primary round")
        scrollable_frame = tk.Frame(canvas, bg=colors['dark_card'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling enable karo
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
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
        
        def create_radio(analysis):
            rb = tk.Radiobutton(
                parent,
                text=analysis['name'],
                variable=self.analysis_type,
                value=analysis['value'],
                bg=colors['dark_card'],
                fg='#ffffff',
                selectcolor=colors['dark_highlight'],
                activebackground=colors['dark_card'],
                activeforeground='#ffffff',
                font=('Segoe UI', 9),
                command=self.on_analysis_change,
                relief=tk.FLAT,
                highlightthickness=0,
                indicatoron=True
            )
            rb.pack(anchor=tk.W, padx=20, pady=2)
            return rb
        
        list(map(create_radio, analyses))
    
    def _create_country_selection(self, parent):
        colors = self.config.get('colors')
        
        # Use phase1_filters.country as default if available
        phase1_filters = self.config.get('phase1_filters')
        default_country = (
            phase1_filters.get('country', self.countries[0])
            if phase1_filters and phase1_filters.get('country') in self.countries
            else self.countries[0]
        )
        
        # Primary country dropdown
        tk.Label(parent, text="Primary Country:", bg=colors['dark_card'], fg='#ffffff',
                font=('Segoe UI', 8)).pack(anchor=tk.W, padx=20, pady=(5, 2))
        self.country_var = tk.StringVar(value=default_country)
        country_combo = ttkb.Combobox(parent, textvariable=self.country_var, 
                                     values=self.countries, width=30, state='readonly',
                                     bootstyle="primary")
        country_combo.pack(padx=20, pady=(0, 10))
        country_combo.bind('<<ComboboxSelected>>', lambda e: self.on_primary_country_change())
        
        # Compare list
        tk.Label(parent, text="Compare With:", bg=colors['dark_card'], fg='#ffffff',
                font=('Segoe UI', 8)).pack(anchor=tk.W, padx=20, pady=(5, 2))
        
        compare_frame = tk.Frame(parent, bg=colors['dark_card'])
        compare_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        self.compare_listbox = tk.Listbox(compare_frame, height=4, selectmode=tk.MULTIPLE,
                                         exportselection=False,
                                         bg=colors['dark_surface'],
                                         fg='#ffffff',
                                         selectbackground=colors['ui_accent'],
                                         selectforeground='#ffffff',
                                         font=('Segoe UI', 8),
                                         relief=tk.FLAT,
                                         highlightbackground=colors['dark_border'],
                                         highlightthickness=2)
        compare_scrollbar = ttkb.Scrollbar(compare_frame, orient=tk.VERTICAL, 
                                         command=self.compare_listbox.yview,
                                         bootstyle="primary round")
        self.compare_listbox.configure(yscrollcommand=compare_scrollbar.set)
        
        # Populate listbox using map
        list(map(lambda country: self.compare_listbox.insert(tk.END, country), self.countries))
        
        # Pre-select compute_countries from config
        phase1_ops = self.config.get('phase1_operations')
        if phase1_ops:
            compute_countries = phase1_ops.get('compute_countries', [])
            all_countries_list = list(self.countries)
            list(map(
                lambda c: self.compare_listbox.selection_set(all_countries_list.index(c)) if c in all_countries_list else None,
                compute_countries
            ))
        
        self.compare_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        compare_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.compare_listbox.bind('<<ListboxSelect>>', lambda e: self.on_compare_selection_change())
    
    def _create_continent_selection(self, parent):
        colors = self.config.get('colors')
        
        # Use phase1_filters.region as default if available
        phase1_filters = self.config.get('phase1_filters')
        default_continent = (
            phase1_filters.get('region', self.continents[0])
            if phase1_filters and phase1_filters.get('region') in self.continents
            else (self.continents[0] if self.continents else "")
        )
        
        self.continent_var = tk.StringVar(value=default_continent)
        continent_combo = ttkb.Combobox(parent, textvariable=self.continent_var, 
                                      values=self.continents, width=30, state='readonly',
                                      bootstyle="primary")
        continent_combo.pack(padx=20, pady=(0, 10))
        continent_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
    
    def _create_year_range_selection(self, parent):
        colors = self.config.get('colors')
        
        # Use phase1_filters.year as default end year if available
        phase1_filters = self.config.get('phase1_filters')
        default_end_year = str(self.year_columns[-1])
        if phase1_filters:
            configured_year = phase1_filters.get('year', '')
            if configured_year and int(configured_year) in self.year_columns:
                default_end_year = configured_year
        
        year_frame = tk.Frame(parent, bg=colors['dark_card'])
        year_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        tk.Label(year_frame, text="From:", bg=colors['dark_card'], fg='#ffffff',
                font=('Segoe UI', 8)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_year_var = tk.StringVar(value=str(self.year_columns[0]))
        start_year_combo = ttkb.Combobox(year_frame, textvariable=self.start_year_var, 
                                       values=list(map(str, self.year_columns)), 
                                       width=10, state='readonly', bootstyle="primary")
        start_year_combo.grid(row=0, column=1, padx=(0, 10))
        start_year_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
        
        tk.Label(year_frame, text="To:", bg=colors['dark_card'], fg='#ffffff',
                font=('Segoe UI', 8)).grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.end_year_var = tk.StringVar(value=default_end_year)
        end_year_combo = ttkb.Combobox(year_frame, textvariable=self.end_year_var, 
                                     values=list(map(str, self.year_columns)), 
                                     width=10, state='readonly', bootstyle="primary")
        end_year_combo.grid(row=0, column=3)
        end_year_combo.bind('<<ComboboxSelected>>', lambda e: self.on_selection_change())
    
    def _create_top_n_selection(self, parent):
        colors = self.config.get('colors')
        ui_config = self.config.get('ui')
        
        top_frame = tk.Frame(parent, bg=colors['dark_card'])
        top_frame.pack(padx=20, pady=(0, 10), fill=tk.X)
        
        tk.Label(top_frame, text="Top N:", bg=colors['dark_card'], fg='#ffffff',
                font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 10))
        self.top_n_var = tk.IntVar(value=ui_config['default_top_n'])
        top_n_spinner = tk.Spinbox(top_frame, from_=5, to=50, textvariable=self.top_n_var,
                                  width=10, command=self.on_selection_change,
                                  bg=colors['dark_surface'], fg='#ffffff',
                                  buttonbackground=colors['dark_border'],
                                  relief=tk.FLAT,
                                  highlightbackground=colors['dark_border'],
                                  highlightthickness=2,
                                  font=('Segoe UI', 9))
        top_n_spinner.pack(side=tk.LEFT)
    
    def _create_action_buttons(self, parent):
        colors = self.config.get('colors')
        
        # Add header for action buttons
        action_header = tk.Frame(parent, bg=colors['section_bg'], height=30)
        action_header.pack(fill=tk.X, padx=15, pady=(12, 4))
        action_header.pack_propagate(False)
        
        header_label = tk.Label(action_header, text="⚡ Actions", bg=colors['section_bg'],
                        font=('Segoe UI', 9, 'bold'), fg='#ffffff')
        header_label.pack(anchor=tk.W, padx=10, pady=5)
        
        button_frame = tk.Frame(parent, bg=colors['dark_card'])
        button_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # White analyze button with black text
        analyze_btn = tk.Button(
            button_frame,
            text="🔍 Analyze",
            command=self.perform_analysis,
            bg='#ffffff',
            fg='#000000',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            borderwidth=0,
            cursor='hand2',
            height=2,
            activebackground='#e0e0e0',
            activeforeground='#000000',
            highlightbackground='#ffffff',
            highlightthickness=0
        )
        analyze_btn.pack(fill=tk.X, pady=5)
        
        # White export button with black text
        export_btn = tk.Button(
            button_frame,
            text="💾 Export Results to TXT",
            command=self.export_analysis,
            bg='#ffffff',
            fg='#000000',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            borderwidth=0,
            cursor='hand2',
            height=2,
            activebackground='#e0e0e0',
            activeforeground='#000000',
            highlightbackground='#ffffff',
            highlightthickness=0
        )
        export_btn.pack(fill=tk.X, pady=5)
        
        # White clear button with black text
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear Visualization",
            command=self.clear_visualization,
            bg='#ffffff',
            fg='#000000',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            borderwidth=0,
            cursor='hand2',
            height=2,
            activebackground='#e0e0e0',
            activeforeground='#000000',
            highlightbackground='#ffffff',
            highlightthickness=0
        )
        clear_btn.pack(fill=tk.X, pady=5)
    
    def _force_white_text(self, widget):
        """Recursively force fg on all tk.Label, tk.Radiobutton, tk.Checkbutton widgets and white bg on Buttons."""
        try:
            widget_class = widget.winfo_class()
            if widget_class in ('Label', 'Radiobutton', 'Checkbutton'):
                widget.configure(fg='#e7e9ea')
            elif widget_class == 'Button':
                widget.configure(bg='#ffffff', fg='#000000',
                                 activebackground='#e0e0e0', activeforeground='#000000',
                                 highlightbackground='#ffffff')
        except Exception:
            pass
        list(map(self._force_white_text, widget.winfo_children()))

    def create_section_header(self, parent, text):
        colors = self.config.get('colors')
        
        # Dark themed section header with accent color
        frame = tk.Frame(parent, bg=colors['section_bg'], height=30)
        frame.pack(fill=tk.X, padx=15, pady=(12, 4))
        frame.pack_propagate(False)
        
        label = tk.Label(frame, text=text, bg=colors['section_bg'],
                        font=('Segoe UI', 9, 'bold'), fg='#ffffff')
        label.pack(anchor=tk.W, padx=10, pady=5)
    
    def create_visualization_panel(self, parent):
        colors = self.config.get('colors')
        
        # Clean dark notebook with ttkbootstrap darkly theme
        style = ttkb.Style()
        style.configure('primary.TNotebook', background=colors['dark_card'])
        style.configure('primary.TNotebook.Tab',
                       background=colors['dark_surface'],
                       foreground=colors['text_secondary'],
                       padding=[16, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('primary.TNotebook.Tab',
                 background=[('selected', colors['dark_card'])],
                 foreground=[('selected', '#e7e9ea')])
        
        self.notebook = ttkb.Notebook(parent, bootstyle="primary")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Graph tab - pure black bg
        self.viz_frame = tk.Frame(self.notebook, bg=colors['dark'])
        self.notebook.add(self.viz_frame, text="  📊 Visualization  ")
        
        # Statistics tab - pure black bg
        self.stats_frame = tk.Frame(self.notebook, bg=colors['dark'])
        self.notebook.add(self.stats_frame, text="  📋 Statistics  ")
        
        # Stats text area - white text with neon border
        self.stats_text = scrolledtext.ScrolledText(
            self.stats_frame,
            wrap=tk.WORD,
            font=('Cascadia Code', 10),
            bg=colors['dark_card'],
            fg='#e7e9ea',
            insertbackground='#e7e9ea',
            relief=tk.FLAT,
            borderwidth=0,
            highlightbackground=colors['dark_border'],
            highlightthickness=2,
            selectbackground=colors['ui_accent'],
            selectforeground='#ffffff'
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
    
    def _style_figure(self, fig, nrows=1, ncols=1):
        """Apply clean dark background to figure"""
        colors = self.config.get('colors')
        viz_config = self.config.get('visualization')
        fig.patch.set_facecolor(viz_config.get('chart_face_color', '#0d0d0d'))
        fig.patch.set_alpha(1.0)
        return fig
    
    def _style_ax(self, ax, title='', xlabel='', ylabel='', grid=True):
        """Apply clean X/Twitter dark theme styling to axes"""
        colors = self.config.get('colors')
        viz_config = self.config.get('visualization')
        ax.set_facecolor(viz_config.get('chart_bg_color', '#000000'))
        # Subtle border, top/right off
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#2f3336')
        ax.spines['left'].set_linewidth(1)
        ax.spines['bottom'].set_color('#2f3336')
        ax.spines['bottom'].set_linewidth(1)
        if title:
            ax.set_title(title, fontsize=viz_config.get('title_font_size', 16),
                        fontweight='bold', color='#e7e9ea', pad=16,
                        fontfamily='Segoe UI')
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=viz_config.get('label_font_size', 12),
                         fontweight='bold', color='#71767b',
                         labelpad=8)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=viz_config.get('label_font_size', 12),
                         fontweight='bold', color='#71767b',
                         labelpad=8)
        if grid:
            ax.grid(True, alpha=0.4,
                   color='#2f3336',
                   linestyle='-', linewidth=0.5)
        ax.tick_params(colors='#71767b', length=4, width=0.6)
        return ax

    def _format_gdp(self, value):
        """Format GDP value as abbreviated string: T / B / M"""
        if value >= 1e12:
            return f'${value / 1e12:.2f}T'
        elif value >= 1e9:
            return f'${value / 1e9:.1f}B'
        elif value >= 1e6:
            return f'${value / 1e6:.1f}M'
        return f'${value:,.0f}'
    
    def get_year_range(self):
        # Selected year range nikalo
        start_year = int(self.start_year_var.get())
        end_year = int(self.end_year_var.get())
        
        if start_year > end_year:
            start_year, end_year = end_year, start_year
            
        return list(filter(lambda y: start_year <= y <= end_year, self.year_columns))
    
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
        
        # Neon styled graph
        fig = Figure(figsize=tuple(viz_config['figure_size']))
        self._style_figure(fig)
        ax = fig.add_subplot(111)
        self._style_ax(ax, title=f'GDP Trend: {country}', xlabel='Year', ylabel='GDP (USD)')
        
        ax.plot(years, gdp_values, marker='o', linewidth=2.5, markersize=5, 
               color=colors['neon_cyan'], markeredgecolor=colors['neon_pink'],
               markeredgewidth=1.5, zorder=5)
        
        # Add subtle fill under curve
        ax.fill_between(years, gdp_values, alpha=0.1, color=colors['neon_cyan'])
        
        ax.yaxis.set_major_formatter(FuncFormatter(
            lambda y, _: (f'${y/1e12:.1f}T' if y >= 1e12 else
                          f'${y/1e9:.0f}B' if y >= 1e9 else
                          f'${y/1e6:.0f}M' if y >= 1e6 else f'${y:,.0f}')
        ))
        
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
        # Add selected countries (skip if primary already selected) using filter
        selected_countries = list(filter(
            lambda c: c != primary_country,
            map(lambda i: self.compare_listbox.get(i), selected_indices)
        ))
        countries = [primary_country] + selected_countries
        
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
        self._style_figure(fig)
        ax = fig.add_subplot(111)
        self._style_ax(ax, title='GDP Comparison Between Countries', xlabel='Year', ylabel='GDP (USD)')
        
        # Use neon palette for multi-country comparison
        neon_colors = colors_config.get('chart_palette', self.neon_palette)
        
        def plot_country(idx_country):
            idx, country = idx_country
            gdp_values = self.processor.get_country_data(country, years)
            if gdp_values is not None:
                color = neon_colors[idx % len(neon_colors)]
                lw, ms, label = (
                    (3, 6, f"{country} (Primary)") if country == primary_country
                    else (2, 4, country)
                )
                ax.plot(years, gdp_values, marker='o', label=label,
                       linewidth=lw, markersize=ms, color=color, alpha=0.9)
        
        list(map(plot_country, enumerate(countries)))
        
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9,
                 facecolor=colors_config['dark_surface'], edgecolor=colors_config['dark_border'],
                 labelcolor=colors_config['text_primary'], framealpha=0.85)
        ax.yaxis.set_major_formatter(FuncFormatter(
            lambda y, _: (f'${y/1e12:.1f}T' if y >= 1e12 else
                          f'${y/1e9:.0f}B' if y >= 1e9 else
                          f'${y/1e6:.0f}M' if y >= 1e6 else f'${y:,.0f}')
        ))
        
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
        
        # Dark multi-subplot figure
        fig = Figure(figsize=tuple(viz_config['figure_size_large']))
        self._style_figure(fig)
        
        # Fix: assign latest_year BEFORE it's used in subplot titles
        latest_year = years[-1]
        
        # Plot 1: Total GDP trend with neon glow
        ax1 = fig.add_subplot(221)
        self._style_ax(ax1, title=f'Total GDP Trend: {continent}', xlabel='Year', ylabel='Total GDP (USD)')
        total_gdp = self.processor.calculate_total_gdp(continent_data, years)
        ax1.plot(years, total_gdp.values, marker='o', linewidth=2.5, color=colors['neon_green'],
                markeredgecolor=colors['neon_pink'], markeredgewidth=1)
        ax1.fill_between(years, total_gdp.values, alpha=0.08, color=colors['neon_green'])
        ax1.yaxis.set_major_formatter(FuncFormatter(
            lambda y, _: (f'${y/1e12:.1f}T' if y >= 1e12 else f'${y/1e9:.0f}B' if y >= 1e9 else f'${y/1e6:.0f}M')
        ))

        
        # Plot 2: Top countries - horizontal neon bars
        ax2 = fig.add_subplot(222)
        self._style_ax(ax2, title=f"Top {ui_config['default_top_n']} Countries in {latest_year}", xlabel='GDP (USD)', grid=False)
        top_countries = continent_data.nlargest(ui_config['default_top_n'], latest_year)
        countries_list = top_countries['Country Name'].values
        gdp_list = top_countries[latest_year].values
        
        bar_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(countries_list))))
        bars2 = ax2.barh(countries_list, gdp_list, color=bar_colors, alpha=0.88,
                         edgecolor='white', linewidth=0.25, height=0.65)
        ax2.barh(countries_list, gdp_list, color='white', alpha=0.05, edgecolor='none', height=0.65)
        ax2.grid(axis='x', alpha=0.15, color=colors.get('dark_border', '#2d2d5e'), linestyle='--', linewidth=0.5)
        ax2.set_xlim(0, max(gdp_list) * 1.22)
        ax2.xaxis.set_major_formatter(FuncFormatter(
            lambda x, _: (f'${x/1e12:.0f}T' if x >= 1e12 else f'${x/1e9:.0f}B' if x >= 1e9 else f'${x/1e6:.0f}M')
        ))
        list(map(
            lambda bv: ax2.text(max(gdp_list) * 0.015, bv[0].get_y() + bv[0].get_height() / 2,
                                self._format_gdp(bv[1]), va='center', ha='left', fontsize=7,
                                color='white', fontweight='bold', alpha=0.9),
            zip(bars2, gdp_list)
        ))
        
        # Plot 3: Average GDP - neon bars
        ax3 = fig.add_subplot(223)
        self._style_ax(ax3, title=f"Top {ui_config['default_top_n']} by Average GDP ({years[0]}-{years[-1]})", xlabel='Average GDP (USD)', grid=False)
        avg_gdp = self.processor.calculate_average_gdp(continent_data, years)
        continent_data_with_avg = continent_data.copy()
        continent_data_with_avg['avg_gdp'] = avg_gdp
        top_avg = continent_data_with_avg.nlargest(ui_config['default_top_n'], 'avg_gdp')
        
        avg_vals = top_avg['avg_gdp'].values
        avg_names = top_avg['Country Name'].values
        bars3 = ax3.barh(avg_names, avg_vals, color=colors['neon_pink'], alpha=0.88,
                         edgecolor='white', linewidth=0.25, height=0.65)
        ax3.barh(avg_names, avg_vals, color='white', alpha=0.05, edgecolor='none', height=0.65)
        ax3.grid(axis='x', alpha=0.15, color=colors.get('dark_border', '#2d2d5e'), linestyle='--', linewidth=0.5)
        ax3.set_xlim(0, max(avg_vals) * 1.22)
        ax3.xaxis.set_major_formatter(FuncFormatter(
            lambda x, _: (f'${x/1e12:.0f}T' if x >= 1e12 else f'${x/1e9:.0f}B' if x >= 1e9 else f'${x/1e6:.0f}M')
        ))
        list(map(
            lambda bv: ax3.text(max(avg_vals) * 0.015, bv[0].get_y() + bv[0].get_height() / 2,
                                self._format_gdp(bv[1]), va='center', ha='left', fontsize=7,
                                color='white', fontweight='bold', alpha=0.9),
            zip(bars3, avg_vals)
        ))
        
        # Plot 4: GDP distribution (controlled by enable_histogram config)
        phase1_viz = self.config.get('phase1_visualizations')
        enable_histogram = phase1_viz.get('enable_histogram', True) if phase1_viz else True
        
        if enable_histogram:
            ax4 = fig.add_subplot(224)
            self._style_ax(ax4, title=f'GDP Distribution in {latest_year}', xlabel='GDP (USD)', ylabel='Number of Countries', grid=False)
            latest_gdp = continent_data[latest_year].dropna()
            ax4.hist(latest_gdp, bins=viz_config['histogram_bins'], color=colors['neon_purple'],
                    edgecolor=colors['dark_border'], alpha=0.75)
            ax4.xaxis.set_major_formatter(FuncFormatter(
                lambda x, _: (f'${x/1e12:.0f}T' if x >= 1e12 else f'${x/1e9:.0f}B' if x >= 1e9 else f'${x/1e6:.0f}M')
            ))
        
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
        colors = self.config.get('colors')
        fig = Figure(figsize=tuple(viz_config['figure_size_tall']))
        self._style_figure(fig)
        ax = fig.add_subplot(111)
        self._style_ax(ax, title=f'Top {top_n} Countries by GDP in {latest_year}', xlabel='GDP (USD)', grid=False)
        
        countries_list = top_countries['Country Name'].values
        gdp_list = top_countries[latest_year].values
        bar_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(countries_list))))
        
        bars = ax.barh(countries_list, gdp_list, color=bar_colors, alpha=0.88,
                       edgecolor='white', linewidth=0.25, height=0.65)
        # Subtle white sheen overlay for depth
        ax.barh(countries_list, gdp_list, color='white', alpha=0.05,
                edgecolor='none', height=0.65)
        ax.grid(axis='x', alpha=0.18, color=colors.get('dark_border', '#2d2d5e'),
                linestyle='--', linewidth=0.5)
        ax.set_xlim(0, max(gdp_list) * 1.22)
        # Abbreviated x-axis tick labels
        ax.xaxis.set_major_formatter(FuncFormatter(
            lambda x, _: (f'${x/1e12:.0f}T' if x >= 1e12 else
                          f'${x/1e9:.0f}B' if x >= 1e9 else
                          f'${x/1e6:.0f}M' if x >= 1e6 else f'${x:,.0f}')
        ))
        # Abbreviated value labels inside bars
        list(map(
            lambda bv: ax.text(
                max(gdp_list) * 0.015,
                bv[0].get_y() + bv[0].get_height() / 2,
                self._format_gdp(bv[1]),
                va='center', ha='left', fontsize=9,
                color='white', fontweight='bold', alpha=0.95
            ),
            zip(bars, gdp_list)
        ))
        # Rank badges on the left
        list(map(
            lambda ib: ax.text(
                -max(gdp_list) * 0.008,
                ib[1].get_y() + ib[1].get_height() / 2,
                f'#{ib[0] + 1}',
                va='center', ha='right', fontsize=8,
                color=colors.get('text_secondary', '#9878cc'), fontweight='bold'
            ),
            enumerate(bars)
        ))
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
        
        # Neon growth rate chart
        fig = Figure(figsize=tuple(viz_config['figure_size']))
        self._style_figure(fig)
        ax = fig.add_subplot(111)
        self._style_ax(ax, title=f'GDP Growth Rate: {country}', xlabel='Year', ylabel='Growth Rate (%)')
        
        bar_colors = list(map(
            lambda gr: colors_config['neon_green'] if gr >= 0 else colors_config['neon_pink'],
            growth_rates
        ))
        ax.bar(growth_years, growth_rates, color=bar_colors, alpha=0.88,
               edgecolor='white', linewidth=0.25, width=0.7)
        ax.bar(growth_years, growth_rates, color='white', alpha=0.04, edgecolor='none', width=0.7)
        ax.axhline(y=0, color=colors_config.get('ui_accent_dim', '#7c3aed'),
                   linestyle='--', linewidth=1.0, alpha=0.7)
        # Growth rate % labels above/below each bar
        list(map(
            lambda yg: ax.text(
                yg[1], yg[0] + (abs(yg[0]) * 0.05 + 0.15) * (1 if yg[0] >= 0 else -1),
                f'{yg[0]:.1f}%',
                ha='center', va='bottom' if yg[0] >= 0 else 'top',
                fontsize=7, color='white', fontweight='bold', alpha=0.85
            ),
            zip(growth_rates, growth_years)
        ))
        
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
        self._style_figure(fig)
        ax = fig.add_subplot(111)
        self._style_ax(ax, title='GDP Comparison Across Continents', xlabel='Continent', ylabel='Total GDP (USD)')
        
        x = np.arange(len(self.continents))
        width = 0.8 / len(comparison_years)
        
        # Use neon palette for year bars
        neon_colors = self.neon_palette
        
        comparison_data = self.processor.get_year_comparison_data(comparison_years, self.continents)
        
        def plot_year_bar(idx_year):
            idx, year = idx_year
            continent_gdp = list(map(lambda c: comparison_data[year][c], self.continents))
            offset = (idx - len(comparison_years)/2) * width + width/2
            ax.bar(x + offset, continent_gdp, width, label=str(year),
                  color=neon_colors[idx % len(neon_colors)], alpha=0.88,
                  edgecolor='white', linewidth=0.2)
        
        list(map(plot_year_bar, enumerate(comparison_years)))
        
        ax.set_xticks(x)
        ax.set_xticklabels(self.continents, rotation=45, ha='right')
        ax.legend(facecolor=self.config.get('colors')['dark_surface'],
                 edgecolor=self.config.get('colors')['dark_border'],
                 labelcolor=self.config.get('colors')['text_primary'],
                 framealpha=0.85, fontsize=9)
        ax.yaxis.set_major_formatter(FuncFormatter(
            lambda y, _: (f'${y/1e12:.0f}T' if y >= 1e12 else
                          f'${y/1e9:.0f}B' if y >= 1e9 else
                          f'${y/1e6:.0f}M' if y >= 1e6 else f'${y:,.0f}')
        ))
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_year_comparison_statistics(comparison_years)
    
    def plot_correlation(self):
        primary_country = self.country_var.get()
        selected_indices = self.compare_listbox.curselection()
        
        # Primary country ko list mein shuru mein daalo
        # Selected countries ko add karo using filter (skip primary if already selected)
        selected_countries = list(filter(
            lambda c: c != primary_country,
            map(lambda i: self.compare_listbox.get(i), selected_indices)
        ))
        countries = [primary_country] + selected_countries
        
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
        colors = self.config.get('colors')
        fig = Figure(figsize=tuple(viz_config['correlation_figure_size']))
        self._style_figure(fig)
        ax = fig.add_subplot(111)
        self._style_ax(ax, title='GDP Correlation Matrix', grid=False)
        
        # Custom colormap for dark theme: magenta -> dark -> cyan
        from matplotlib.colors import LinearSegmentedColormap
        neon_cmap = LinearSegmentedColormap.from_list('neon_corr', 
            [colors['neon_pink'], colors['dark'], colors['neon_cyan']], N=256)
        
        im = ax.imshow(correlation_matrix, cmap=neon_cmap, aspect='auto', vmin=-1, vmax=1)
        
        ax.set_xticks(np.arange(len(countries)))
        ax.set_yticks(np.arange(len(countries)))
        ax.set_xticklabels(countries, rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(countries, fontsize=8)
        
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20, 
                      color=colors['text_primary'])
        cbar.ax.yaxis.set_tick_params(color=colors['text_secondary'])
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=colors['text_secondary'])
        
        # Add text annotations using map
        from itertools import product as iter_product
        list(map(
            lambda ij: ax.text(ij[1], ij[0], f'{correlation_matrix.iloc[ij[0], ij[1]]:.2f}',
                              ha="center", va="center", color=colors['text_primary'], 
                              fontsize=7, fontweight='bold'),
            iter_product(range(len(countries)), range(len(countries)))
        ))
        
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
        
        region_names = list(map(lambda r: r[0], valid_regions))
        gdp_values = list(map(lambda r: r[1], valid_regions))
        
        # Use phase1_visualizations.region_charts config to control which charts to show
        phase1_viz = self.config.get('phase1_visualizations')
        region_charts = phase1_viz.get('region_charts', ['pie', 'bar']) if phase1_viz else ['pie', 'bar']
        num_charts = len(region_charts)
        
        fig = Figure(figsize=tuple(viz_config['figure_size_large']))
        self._style_figure(fig)
        
        def render_chart(idx_chart):
            idx, chart_type = idx_chart
            ax = fig.add_subplot(1, num_charts, idx + 1)
            self._style_ax(ax, grid=False)
            if chart_type == 'pie':
                # Neon colored pie chart
                pie_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(region_names))))
                wedges, texts, autotexts = ax.pie(gdp_values, labels=region_names, autopct='%1.1f%%', 
                                                   startangle=90, colors=pie_colors,
                                                   textprops={'color': colors_config['text_primary'], 'fontsize': 10})
                plt.setp(autotexts, fontweight='bold', fontsize=9)
                ax.set_title(f'Regional GDP Distribution ({latest_year})', fontweight='bold', 
                           fontsize=14, color=colors_config['text_primary'], pad=12)
            elif chart_type == 'bar':
                bar_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(region_names))))
                ax.bar(region_names, gdp_values, color=bar_colors, alpha=0.88,
                       edgecolor='white', linewidth=0.25, width=0.65)
                ax.bar(region_names, gdp_values, color='white', alpha=0.04, edgecolor='none', width=0.65)
                self._style_ax(ax, title=f'Regional GDP Comparison ({latest_year})', xlabel='Region', ylabel='GDP (USD)', grid=False)
                ax.tick_params(axis='x', rotation=45)
                ax.grid(axis='y', alpha=0.15, color=colors_config.get('dark_border', '#2d2d5e'), linestyle='--', linewidth=0.5)
                ax.yaxis.set_major_formatter(FuncFormatter(
                    lambda y, _: (f'${y/1e12:.0f}T' if y >= 1e12 else f'${y/1e9:.0f}B' if y >= 1e9 else f'${y/1e6:.0f}M')
                ))
        
        list(map(render_chart, enumerate(region_charts)))
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_phase1_regional_statistics(region_names, gdp_values, latest_year)
    
    def plot_phase1_year_analysis(self):
        """Year-specific GDP analysis - chart types driven by phase1_visualizations.year_charts"""
        country = self.country_var.get()
        years = self.get_year_range()
        years_int = list(map(int, years))
        
        country_data = self.processor.get_country_data(country, years)
        
        if country_data is None:
            messagebox.showwarning("Warning", f"No data found for {country}")
            return
        
        viz_config = self.config.get('visualization')
        colors_config = self.config.get('colors')
        
        # Use phase1_visualizations.year_charts config
        phase1_viz = self.config.get('phase1_visualizations')
        year_charts = phase1_viz.get('year_charts', ['line', 'scatter']) if phase1_viz else ['line', 'scatter']
        num_charts = len(year_charts)
        
        fig = Figure(figsize=tuple(viz_config['figure_size_large']))
        self._style_figure(fig)
        
        def render_year_chart(idx_chart):
            idx, chart_type = idx_chart
            ax = fig.add_subplot(1, num_charts, idx + 1)
            if chart_type == 'line':
                self._style_ax(ax, title=f'{country} - GDP Trend Over Years', xlabel='Year', ylabel='GDP (USD)')
                ax.plot(years_int, country_data, marker='o', linewidth=2.5, 
                       color=colors_config['neon_cyan'], markeredgecolor=colors_config['neon_pink'],
                       markeredgewidth=1.5, label=country)
                ax.fill_between(years_int, country_data, alpha=0.08, color=colors_config['neon_cyan'])
                ax.legend(facecolor=colors_config['dark_surface'], edgecolor=colors_config['dark_border'],
                         labelcolor=colors_config['text_primary'], framealpha=0.85)
                ax.yaxis.set_major_formatter(FuncFormatter(
                    lambda y, _: (f'${y/1e12:.1f}T' if y >= 1e12 else f'${y/1e9:.0f}B' if y >= 1e9 else f'${y/1e6:.0f}M')
                ))

            elif chart_type == 'scatter':
                self._style_ax(ax, title=f'{country} - GDP Scatter Analysis', xlabel='Year', ylabel='GDP (USD)')
                scatter_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(years_int))))
                ax.scatter(years_int, country_data, c=scatter_colors, s=120, alpha=0.85, 
                          edgecolors=colors_config['text_primary'], linewidth=0.5, zorder=5)
                ax.yaxis.set_major_formatter(FuncFormatter(
                    lambda y, _: (f'${y/1e12:.1f}T' if y >= 1e12 else f'${y/1e9:.0f}B' if y >= 1e9 else f'${y/1e6:.0f}M')
                ))
        
        list(map(render_year_chart, enumerate(year_charts)))
        
        fig.tight_layout()
        self.display_plot(fig)
        
        self.show_country_statistics(country, years_int, country_data)
    
    def plot_phase1_complete_analysis(self):
        """Complete analysis driven by phase1 config - charts, regions, and countries"""
        phase1_config = self.config.get('phase1_operations')
        regions = phase1_config.get('compute_regions', self.continents[:5]) if phase1_config else self.continents[:5]
        
        # Use phase1_visualizations config for chart types
        phase1_viz = self.config.get('phase1_visualizations')
        region_charts = phase1_viz.get('region_charts', ['pie', 'bar']) if phase1_viz else ['pie', 'bar']
        year_charts = phase1_viz.get('year_charts', ['line', 'scatter']) if phase1_viz else ['line', 'scatter']
        
        country = self.country_var.get()
        years = self.get_year_range()
        years_int = list(map(int, years))
        latest_year = years[-1]
        
        viz_config = self.config.get('visualization')
        colors_config = self.config.get('colors')
        
        fig = Figure(figsize=tuple(viz_config.get('figure_size_large', [14, 10])))
        self._style_figure(fig)
        
        # Build regional GDP data using map/filter
        regional_gdp_pairs = list(filter(
            lambda pair: pair[1] > 0,
            map(lambda region: (region, self.df[self.df['Continent'] == region][latest_year].sum()), regions)
        ))
        valid_region_names = list(map(lambda p: p[0], regional_gdp_pairs))
        valid_region_values = list(map(lambda p: p[1], regional_gdp_pairs))
        
        # Subplot 1: First region chart type (pie or bar)
        ax1 = fig.add_subplot(221)
        self._style_ax(ax1, grid=False)
        if 'pie' in region_charts:
            pie_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(valid_region_names))))
            wedges, texts, autotexts = ax1.pie(valid_region_values, labels=valid_region_names, autopct='%1.1f%%', 
                                                startangle=90, colors=pie_colors,
                                                textprops={'color': colors_config['text_primary']})
            plt.setp(autotexts, fontweight='bold', fontsize=9)
            ax1.set_title(f'Regional GDP Distribution ({latest_year})', fontweight='bold', 
                         color=colors_config['text_primary'], fontsize=14)
        elif 'bar' in region_charts:
            bar_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(valid_region_names))))
            ax1.bar(valid_region_names, valid_region_values, color=bar_colors, alpha=0.88,
                   edgecolor='white', linewidth=0.25, width=0.65)
            ax1.bar(valid_region_names, valid_region_values, color='white', alpha=0.04, edgecolor='none', width=0.65)
            self._style_ax(ax1, title=f'Regional GDP Bar Chart ({latest_year})', grid=False)
            ax1.tick_params(axis='x', rotation=45)
            ax1.yaxis.set_major_formatter(FuncFormatter(
                lambda y, _: (f'${y/1e12:.0f}T' if y >= 1e12 else f'${y/1e9:.0f}B' if y >= 1e9 else f'${y/1e6:.0f}M')
            ))
        
        # Subplot 2: Second region chart type
        ax2 = fig.add_subplot(222)
        self._style_ax(ax2, grid=False)
        if 'bar' in region_charts:
            bar_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(valid_region_names))))
            ax2.bar(valid_region_names, valid_region_values, color=bar_colors, alpha=0.88,
                   edgecolor='white', linewidth=0.25, width=0.65)
            ax2.bar(valid_region_names, valid_region_values, color='white', alpha=0.04, edgecolor='none', width=0.65)
            self._style_ax(ax2, title=f'Regional GDP Bar Chart ({latest_year})', xlabel='Region', ylabel='GDP (USD)', grid=False)
            ax2.tick_params(axis='x', rotation=45)
            ax2.yaxis.set_major_formatter(FuncFormatter(
                lambda y, _: (f'${y/1e12:.0f}T' if y >= 1e12 else f'${y/1e9:.0f}B' if y >= 1e9 else f'${y/1e6:.0f}M')
            ))
        elif 'pie' in region_charts:
            pie_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(valid_region_names))))
            ax2.pie(valid_region_values, labels=valid_region_names, autopct='%1.1f%%', startangle=90, colors=pie_colors,
                   textprops={'color': colors_config['text_primary']})
            ax2.set_title(f'Regional GDP Distribution ({latest_year})', fontweight='bold',
                         color=colors_config['text_primary'], fontsize=14)
        
        country_data = self.processor.get_country_data(country, years)
        
        # Subplot 3: Line chart with neon glow
        ax3 = fig.add_subplot(223)
        if country_data is not None and 'line' in year_charts:
            self._style_ax(ax3, title=f'{country} - Line Graph', xlabel='Year', ylabel='GDP (USD)')
            ax3.plot(years_int, country_data, marker='o', linewidth=2.5, color=colors_config['neon_green'],
                    markeredgecolor=colors_config['neon_pink'], markeredgewidth=1)
            ax3.fill_between(years_int, country_data, alpha=0.08, color=colors_config['neon_green'])
            ax3.yaxis.set_major_formatter(FuncFormatter(
                lambda y, _: (f'${y/1e12:.1f}T' if y >= 1e12 else f'${y/1e9:.0f}B' if y >= 1e9 else f'${y/1e6:.0f}M')
            ))

        
        # Subplot 4: Scatter with neon colors
        ax4 = fig.add_subplot(224)
        if country_data is not None and 'scatter' in year_charts:
            self._style_ax(ax4, title=f'{country} - Scatter Plot', xlabel='Year', ylabel='GDP (USD)')
            scatter_colors = list(map(lambda i: self.neon_palette[i % len(self.neon_palette)], range(len(years_int))))
            ax4.scatter(years_int, country_data, c=scatter_colors, s=120, alpha=0.85,
                       edgecolors=colors_config['text_primary'], linewidth=0.5, zorder=5)
            ax4.yaxis.set_major_formatter(FuncFormatter(
                lambda y, _: (f'${y/1e12:.1f}T' if y >= 1e12 else f'${y/1e9:.0f}B' if y >= 1e9 else f'${y/1e6:.0f}M')
            ))
        
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
        
        # Build region lines using reduce over zipped data
        stats += reduce(
            lambda acc, item: acc + f"{item[0]:20s}: ${item[1]:,.0f} ({item[2]:.1f}%)\n",
            zip(region_names, gdp_values, percentages),
            ""
        )
        
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
        
        # Get statistical_operation from config
        phase1_ops = self.config.get('phase1_operations')
        stat_operation = phase1_ops.get('statistical_operation', 'average') if phase1_ops else 'average'
        
        # Get selected primary country
        selected_country = self.country_var.get()
        
        stats_text = "=" * 80 + "\n"
        stats_text += " " * 25 + "GDP STATISTICAL SUMMARY\n"
        stats_text += "=" * 80 + "\n\n"
        stats_text += f"Default Statistical Operation: {stat_operation.upper()}\n\n"
        
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
                growth_summary = self.processor.calculate_growth_summary(country_data, list(map(int, years)))
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
        
        # Build top countries text using reduce
        stats_text += reduce(
            lambda acc, pair: acc + f"{pair[0]:2d}. {pair[1][1]['Country Name']:30s} ${pair[1][1][latest_year]:20,.0f}  [{pair[1][1]['Continent']}]\n",
            enumerate(top_countries.iterrows(), 1),
            ""
        )
        
        stats_text += "\n"
        
        stats_text += f"STATISTICS BY CONTINENT ({latest_year})\n"
        stats_text += "-" * 80 + "\n"
        stats_text += f"{'Continent':<20} {'Total GDP':<25} {'Avg GDP':<25} {'Countries':<10}\n"
        stats_text += "-" * 80 + "\n"
        
        # Build continent stats using reduce
        stats_text += reduce(
            lambda acc, continent: (
                acc + f"{continent:<20} ${summary['total_gdp']:<24,.0f} ${summary['avg_gdp']:<24,.0f} {summary['country_count']:<10}\n"
                if (summary := self.processor.get_continent_summary(continent, latest_year))
                else acc
            ),
            self.continents,
            ""
        )
        
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
        
        # Build comparison rows using reduce
        stats_text += reduce(
            lambda acc, country: (
                acc + f"{country:<30} ${country_data[latest_year].values[0]:<24,.0f} ${country_data[years].mean(axis=1).values[0]:<24,.0f}\n"
                if not (country_data := self.df[self.df['Country Name'] == country]).empty
                else acc
            ),
            countries,
            ""
        )
        
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
        
        # Build top 5 rows using reduce
        stats_text += reduce(
            lambda acc, pair: acc + f"{pair[0]}. {pair[1][1]['Country Name']:<40} ${pair[1][1][latest_year]:,.0f}\n",
            enumerate(summary['top_countries'].iterrows(), 1),
            ""
        )
        
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
        
        # Build ranking rows using reduce
        stats_text += reduce(
            lambda acc, pair: acc + f"{pair[0]:<6} {pair[1][1]['Country Name']:<30} ${pair[1][1][year]:<24,.0f} {pair[1][1]['Continent']:<15}\n",
            enumerate(top_countries.iterrows(), 1),
            ""
        )
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def show_growth_statistics(self, country, years, growth_rates):
        valid_rates = list(filter(lambda r: not np.isnan(r), growth_rates))
        
        stats_text = "=" * 80 + "\n"
        stats_text += f"GROWTH RATE STATISTICS FOR {country.upper()}\n"
        stats_text += "=" * 80 + "\n\n"
        
        if valid_rates:
            stats_text += f"Average Growth Rate: {np.mean(valid_rates):.2f}%\n"
            stats_text += f"Median Growth Rate: {np.median(valid_rates):.2f}%\n"
            stats_text += f"Max Growth Rate: {max(valid_rates):.2f}% (Year: {years[growth_rates.index(max(valid_rates))]})\n"
            stats_text += f"Min Growth Rate: {min(valid_rates):.2f}% (Year: {years[growth_rates.index(min(valid_rates))]})\n"
            stats_text += f"Std Deviation: {np.std(valid_rates):.2f}%\n\n"
            
            positive_years = len(list(filter(lambda r: r > 0, valid_rates)))
            negative_years = len(list(filter(lambda r: r < 0, valid_rates)))
            
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
        stats_text += reduce(lambda acc, year: acc + f"{str(year):<15}", comparison_years, "")
        stats_text += "\n" + "-" * 80 + "\n"
        
        comparison_data = self.processor.get_year_comparison_data(comparison_years, self.continents)
        
        # Build continent rows using reduce
        stats_text += reduce(
            lambda acc, continent: acc + f"{continent:<20}" + reduce(
                lambda row, year: row + f"${comparison_data[year][continent]/1e12:.2f}T"[:14] + " ",
                comparison_years,
                ""
            ) + "\n",
            self.continents,
            ""
        )
        
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
        
        # Build correlation rows using reduce
        stats_text += reduce(
            lambda acc, pair: acc + f"{pair[0]:2d}. {pair[1][0]:25s} <-> {pair[1][1]:25s} : {pair[1][2]:6.3f}\n",
            enumerate(correlations, 1),
            ""
        )
        
        stats_text += "\n" + "=" * 80 + "\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def display_plot(self, fig):
        # Graph ko display karo
        # Pehle se jo graph hai wo clear karo - using map
        list(map(lambda w: w.destroy(), self.viz_frame.winfo_children()))
        
        colors = self.config.get('colors')
        canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.configure(bg=colors['dark'])
        widget.pack(fill=tk.BOTH, expand=True)
        
        # Visualization tab par switch karo
        self.notebook.select(self.viz_frame)
    
    def clear_visualization(self):
        # Saari visualizations clear kar do - using map
        list(map(lambda w: w.destroy(), self.viz_frame.winfo_children()))
        
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
    style = ttkb.Style('darkly')
    
    # Force pure black on ALL ttkbootstrap theme colors
    style.colors.bg = '#000000'
    style.colors.dark = '#000000'
    style.colors.border = '#010101'
    style.colors.inputbg = '#000000'
    style.colors.inputfg = '#e7e9ea'
    style.configure('.', background='#000000', fieldbackground='#000000',
                    foreground='#e7e9ea', bordercolor='#2f3336',
                    darkcolor='#000000', lightcolor='#111111')
    style.configure('TFrame', background='#000000')
    style.configure('TLabel', background='#000000', foreground='#e7e9ea')
    style.configure('TNotebook', background='#000000')
    style.configure('TNotebook.Tab', background='#000000', foreground='#71767b')
    style.map('TNotebook.Tab',
              background=[('selected', '#000000')],
              foreground=[('selected', '#e7e9ea')])
    style.configure('TCombobox', fieldbackground='#000000', background='#000000',
                    foreground='#e7e9ea', selectbackground='#1d9bf0')
    style.configure('primary.TNotebook', background='#000000')
    style.configure('primary.TNotebook.Tab', background='#000000',
                    foreground='#71767b')
    style.map('primary.TNotebook.Tab',
              background=[('selected', '#111111')],
              foreground=[('selected', '#e7e9ea')])
    
    # Force tk.Button colors via option database (overrides ttkbootstrap defaults)
    root.option_add('*Button.background', '#ffffff')
    root.option_add('*Button.foreground', '#000000')
    root.option_add('*Button.activeBackground', '#e0e0e0')
    root.option_add('*Button.activeForeground', '#000000')
    root.option_add('*Button.highlightBackground', '#ffffff')
    
    app = GDPDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
