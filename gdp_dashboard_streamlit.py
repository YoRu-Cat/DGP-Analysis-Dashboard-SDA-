from __future__ import annotations

import streamlit as st
import numpy as np
import pandas as pd
from functools import reduce
import warnings
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pycountry

from data_loader import ConfigLoader, GDPDataLoader
from data_processor import GDPDataProcessor
from core.engine import TransformationEngine
from plugins.inputs import _df_to_records

warnings.filterwarnings('ignore')


st.set_page_config(
    page_title="GDP Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


_CUSTOM_CSS = """
<style>
    .stApp {
        background-color: #0a0a0a;
    }

    section[data-testid="stSidebar"] {
        background-color: #0e0e0e;
        border-right: 1px solid #1a1a1a;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e7e9ea;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    div[data-testid="stExpander"] {
        background-color: #111111;
        border: 1px solid #1a1a1a;
        border-radius: 8px;
        transition: border-color 0.2s ease;
    }
    div[data-testid="stExpander"]:hover {
        border-color: #252525;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #111111 0%, #0e0e0e 100%);
        border: 1px solid #1a1a1a;
        border-left: 3px solid #1d9bf0;
        border-radius: 8px;
        padding: 18px 22px;
        transition: border-left-color 0.25s ease, box-shadow 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-left-color: #00ba7c;
        box-shadow: 0 2px 12px rgba(29, 155, 240, 0.06);
    }
    div[data-testid="stMetric"] label {
        color: #6b7280 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #e7e9ea !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        font-size: 0.78rem !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: transparent;
        border-bottom: 1px solid #1a1a1a;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 0;
        border: none;
        border-bottom: 2px solid transparent;
        color: #6b7280;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 0.88rem;
        transition: color 0.2s ease, border-bottom-color 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #b0b0b0;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #1d9bf0 !important;
        border-bottom: 2px solid #1d9bf0 !important;
        font-weight: 600;
    }

    .stDataFrame {
        border: 1px solid #1a1a1a;
        border-radius: 8px;
        overflow: hidden;
    }

    div[data-baseweb="select"] {
        background-color: #111111;
        border-radius: 6px;
    }

    .stRadio > div {
        gap: 2px;
    }
    .stRadio label {
        color: #e7e9ea !important;
        font-size: 0.88rem;
    }

    hr {
        border-color: #1a1a1a;
        margin: 12px 0;
    }

    .dashboard-title {
        text-align: center;
        padding: 16px 0 12px 0;
        margin-bottom: 24px;
        border-bottom: 1px solid #1a1a1a;
        position: relative;
    }
    .dashboard-title::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #1d9bf0, transparent);
    }
    .dashboard-title h1 {
        color: #e7e9ea;
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.02em;
    }

    .stats-block {
        background-color: #0e0e0e;
        border: 1px solid #1a1a1a;
        border-radius: 8px;
        padding: 20px;
        font-family: 'Cascadia Code', 'Fira Code', 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #d4d4d4;
        white-space: pre-wrap;
        line-height: 1.65;
        max-height: 600px;
        overflow-y: auto;
    }

    .stPlotlyChart {
        border: 1px solid #1a1a1a;
        border-radius: 8px;
        overflow: hidden;
    }

    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background-color: #0a0a0a !important;
        border-bottom: 1px solid #141414;
    }

    .sidebar-section {
        font-size: 0.68rem;
        font-weight: 600;
        color: #1d9bf0;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 22px 0 8px 0;
        padding: 0 0 6px 0;
        border-bottom: 1px solid #1a1a1a;
    }

    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    ::-webkit-scrollbar-thumb {
        background: #252525;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #353535;
    }

    .stSelectbox label, .stMultiSelect label, .stNumberInput label {
        color: #8b8b8b !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }

    div[data-testid="stMarkdownContainer"] p {
        line-height: 1.55;
    }

    .stCaption {
        color: #555555 !important;
    }
</style>
"""

st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)


_PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        font=dict(family="Segoe UI, sans-serif", color="#e7e9ea"),
        paper_bgcolor="#0a0a0a",
        plot_bgcolor="#0a0a0a",
        title=dict(font=dict(size=18, color="#e7e9ea")),
        xaxis=dict(
            gridcolor="#1e1e1e", gridwidth=0.5,
            zerolinecolor="#1e1e1e",
            linecolor="#2f3336", linewidth=1,
            tickfont=dict(color="#71767b"),
            title_font=dict(color="#71767b"),
        ),
        yaxis=dict(
            gridcolor="#1e1e1e", gridwidth=0.5,
            zerolinecolor="#1e1e1e",
            linecolor="#2f3336", linewidth=1,
            tickfont=dict(color="#71767b"),
            title_font=dict(color="#71767b"),
        ),
        legend=dict(
            bgcolor="rgba(15,15,15,0.85)",
            bordercolor="#1e1e1e",
            font=dict(color="#e7e9ea"),
        ),
        colorway=[
            "#1d9bf0", "#00ba7c", "#f4212e", "#ffad1f",
            "#794bc4", "#ff7a00", "#17bf63", "#e0245e",
            "#7856ff", "#ff6b35",
        ],
        margin=dict(l=60, r=30, t=60, b=50),
    )
)

_PLOTLY_LAYOUT = _PLOTLY_TEMPLATE["layout"]


_format_gdp = lambda v: (
    f"${v / 1e12:.2f}T" if abs(v) >= 1e12 else
    f"${v / 1e9:.2f}B" if abs(v) >= 1e9 else
    f"${v / 1e6:.2f}M" if abs(v) >= 1e6 else
    f"${v:,.0f}"
)


@st.cache_data(show_spinner=False)
def load_all_data():
    config = ConfigLoader()
    loader = GDPDataLoader(config)
    loader.load_data()

    df = loader.get_dataframe()
    year_columns = loader.get_year_columns()
    countries = loader.get_countries()
    continents = loader.get_continents()
    processor = GDPDataProcessor(df, year_columns)
    summary = loader.get_summary()
    raw_config = config.config if hasattr(config, 'config') else {}

    return df, year_columns, countries, continents, processor, summary, raw_config, config


df, year_columns, countries, continents, processor, data_summary, raw_config, config_obj = load_all_data()


if "engine" not in st.session_state:
    from plugins.outputs import ConsoleWriter
    _sink = ConsoleWriter(config=raw_config)
    _engine = TransformationEngine(_sink, raw_config)
    _engine.load_data(_df_to_records(df))
    st.session_state.engine = _engine


engine: TransformationEngine = st.session_state.engine


_PALETTE = raw_config.get("colors", {}).get("chart_palette", [
    "#1d9bf0", "#00ba7c", "#f4212e", "#ffad1f",
    "#794bc4", "#ff7a00", "#17bf63", "#e0245e",
])


with st.sidebar:
    st.markdown("## GDP Dashboard")
    st.caption(f"{data_summary['total_countries']} countries · {data_summary['total_years']} years · {data_summary['year_range']}")
    st.markdown("---")

    st.markdown('<div class="sidebar-section">Analysis</div>', unsafe_allow_html=True)

    analysis_options_p1 = [
        "Geographic Map",
        "Country GDP Trend",
        "Compare Countries",
        "Continent Analysis",
        "Top Countries",
        "GDP Growth Rate",
        "Statistical Summary",
        "Year Comparison",
        "Correlation Analysis",
        "Regional Analysis (Pie + Bar)",
        "Year Analysis (Line + Scatter)",
        "Complete Analysis (All Charts)",
    ]
    analysis_options_p2 = [
        "Top Countries (Engine)",
        "Bottom Countries (Engine)",
        "Growth Rate (Engine)",
        "Avg GDP by Continent",
        "Global GDP Trend",
        "Fastest Growing Continent",
        "Consistent Decline",
        "Continent Contribution",
        "Run All Engine Analyses",
    ]

    analysis_choice = st.radio(
        "Select analysis",
        options=analysis_options_p1 + ["───── Phase 2 Engine ─────"] + analysis_options_p2,
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.markdown('<div class="sidebar-section">Country</div>', unsafe_allow_html=True)

    phase1_filters = raw_config.get("phase1_filters", {})
    default_country = phase1_filters.get("country", countries[0]) if phase1_filters.get("country") in countries else countries[0]

    def _on_primary_change():
        new_primary = st.session_state["primary_country"]
        if "compare_countries" in st.session_state:
            st.session_state["compare_countries"] = [
                c for c in st.session_state["compare_countries"]
                if c != new_primary
            ]

    country_var = st.selectbox(
        "Primary Country", countries,
        index=countries.index(default_country),
        key="primary_country",
        on_change=_on_primary_change,
    )

    compare_countries = st.multiselect(
        "Compare With",
        options=[c for c in countries if c != country_var],
        default=list(filter(
            lambda c: c in countries and c != country_var,
            raw_config.get("phase1_operations", {}).get("compute_countries", []),
        )),
        key="compare_countries",
    )

    st.markdown("---")

    st.markdown('<div class="sidebar-section">Continent</div>', unsafe_allow_html=True)

    default_continent = phase1_filters.get("region", continents[0]) if phase1_filters.get("region") in continents else continents[0]
    continent_var = st.selectbox("Continent", continents, index=continents.index(default_continent))

    st.markdown("---")

    st.markdown('<div class="sidebar-section">Year Range</div>', unsafe_allow_html=True)

    col_y1, col_y2 = st.columns(2)
    with col_y1:
        start_year = st.selectbox("From", year_columns, index=0)
    with col_y2:
        default_end = phase1_filters.get("year", str(year_columns[-1]))
        end_idx = year_columns.index(int(default_end)) if int(default_end) in year_columns else len(year_columns) - 1
        end_year = st.selectbox("To", year_columns, index=end_idx)

    if start_year > end_year:
        start_year, end_year = end_year, start_year

    selected_years = list(filter(lambda y: start_year <= y <= end_year, year_columns))

    st.markdown("---")

    st.markdown('<div class="sidebar-section">Top N</div>', unsafe_allow_html=True)
    top_n = st.number_input("Top N", min_value=3, max_value=50, value=raw_config.get("ui", {}).get("default_top_n", 10), step=1)


st.markdown('<div class="dashboard-title"><h1>GDP Analysis Dashboard</h1></div>', unsafe_allow_html=True)

kpi_cols = st.columns(4)
latest_year = selected_years[-1] if selected_years else year_columns[-1]
world_stats = processor.get_world_statistics(latest_year)

with kpi_cols[0]:
    st.metric("World GDP", _format_gdp(world_stats['total_gdp']), f"in {latest_year}")
with kpi_cols[1]:
    st.metric("Avg GDP", _format_gdp(world_stats['avg_gdp']))
with kpi_cols[2]:
    st.metric("Countries", f"{data_summary['total_countries']}")
with kpi_cols[3]:
    st.metric("Years", f"{data_summary['total_years']}")


def _engine_params():
    return {
        "continent": continent_var,
        "year": end_year,
        "date_range": [start_year, end_year],
        "top_n": top_n,
        "decline_years": 5,
    }


def render_engine_results(results, title, label_key=None, value_key=None):
    if not results:
        st.warning(f"No results for: {title}")
        return

    rdf = pd.DataFrame(results)
    st.subheader(title)

    if label_key is None:
        label_key = next(filter(lambda k: k in ("country", "continent", "year"), rdf.columns), rdf.columns[0])
    if value_key is None:
        value_key = next(
            filter(lambda k: k in ("gdp", "avg_gdp", "total_gdp", "growth_pct", "contribution_pct", "decline_pct"), rdf.columns),
            None,
        )

    tab_chart, tab_table = st.tabs(["Chart", "Data"])

    with tab_chart:
        if value_key:
            fig = go.Figure(layout=_PLOTLY_LAYOUT)
            labels = rdf[label_key].astype(str).tolist()
            values = rdf[value_key].astype(float).tolist()
            colours = list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(labels))))
            fig.add_trace(go.Bar(
                x=values, y=labels, orientation="h",
                marker=dict(color=colours, line=dict(width=0)),
                text=list(map(lambda v: _format_gdp(v) if abs(v) > 1e5 else f"{v:.2f}", values)),
                textposition="auto",
                textfont=dict(color="#e7e9ea", size=11),
            ))
            fig.update_layout(
                title=title,
                yaxis=dict(autorange="reversed"),
                height=max(400, 36 * len(labels)),
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No numeric value column detected for charting.")

    with tab_table:
        st.dataframe(rdf, width="stretch", hide_index=True)


if analysis_choice.startswith("─"):
    st.info("Select a Phase 2 analysis from above or below the separator.")


elif analysis_choice == "Geographic Map":
    _COUNTRY_NAME_OVERRIDES = {
        "United States": "USA", "Russia": "RUS", "South Korea": "KOR",
        "North Korea": "PRK", "Iran": "IRN", "Venezuela": "VEN",
        "Bolivia": "BOL", "Tanzania": "TZA", "Vietnam": "VNM",
        "Syria": "SYR", "Laos": "LAO", "Moldova": "MDA",
        "Brunei": "BRN", "Ivory Coast": "CIV", "Cote d'Ivoire": "CIV",
        "Democratic Republic of the Congo": "COD", "Congo, Dem. Rep.": "COD",
        "Republic of the Congo": "COG", "Congo, Rep.": "COG",
        "Czech Republic": "CZE", "Czechia": "CZE",
        "Egypt": "EGY", "Egypt, Arab Rep.": "EGY",
        "Gambia": "GMB", "Gambia, The": "GMB",
        "Hong Kong": "HKG", "Hong Kong SAR, China": "HKG",
        "Macao": "MAC", "Macao SAR, China": "MAC",
        "Kyrgyzstan": "KGZ", "Kyrgyz Republic": "KGZ",
        "Micronesia": "FSM", "Micronesia, Fed. Sts.": "FSM",
        "Slovakia": "SVK", "Slovak Republic": "SVK",
        "St. Kitts and Nevis": "KNA", "St. Lucia": "LCA",
        "St. Vincent and the Grenadines": "VCT",
        "Eswatini": "SWZ", "Swaziland": "SWZ",
        "Macedonia": "MKD", "North Macedonia": "MKD",
        "Yemen": "YEM", "Yemen, Rep.": "YEM",
        "Korea, Rep.": "KOR", "Korea, Dem. People's Rep.": "PRK",
        "Iran, Islamic Rep.": "IRN", "Venezuela, RB": "VEN",
        "Lao PDR": "LAO", "Russian Federation": "RUS",
        "Turkiye": "TUR", "Turkey": "TUR",
        "West Bank and Gaza": "PSE", "Palestinian Territories": "PSE",
        "Bahamas, The": "BHS", "Bahamas": "BHS",
    }

    def _get_iso(name):
        if name in _COUNTRY_NAME_OVERRIDES:
            return _COUNTRY_NAME_OVERRIDES[name]
        try:
            return pycountry.countries.lookup(name).alpha_3
        except LookupError:
            try:
                results = pycountry.countries.search_fuzzy(name)
                if results:
                    return results[0].alpha_3
            except LookupError:
                pass
        return None

    all_map_countries = [country_var] + compare_countries

    map_rows = []
    for c in countries:
        iso = _get_iso(c)
        if iso is None:
            continue
        gdp_val = processor.get_country_data(c, [latest_year])
        if gdp_val is not None and len(gdp_val) > 0 and not np.isnan(gdp_val[0]):
            if c == country_var:
                role = "Primary"
            elif c in compare_countries:
                role = "Secondary"
            else:
                role = "Other"
            map_rows.append({
                "Country": c,
                "ISO": iso,
                "GDP": gdp_val[0],
                "GDP_Formatted": _format_gdp(gdp_val[0]),
                "Role": role,
                "Continent": df[df["Country Name"] == c]["Continent"].values[0] if not df[df["Country Name"] == c].empty else "Unknown",
            })
    map_df = pd.DataFrame(map_rows)

    tab_world, tab_selected, tab_data = st.tabs(["World Heatmap", "Selected Countries", "Data"])

    with tab_world:
        fig_world = px.choropleth(
            map_df,
            locations="ISO",
            color="GDP",
            hover_name="Country",
            hover_data={"GDP_Formatted": True, "Continent": True, "ISO": False, "GDP": False, "Role": False},
            color_continuous_scale=[
                [0, "#111111"], [0.15, "#1a1a1a"], [0.35, "#333333"],
                [0.55, "#555555"], [0.75, "#888888"], [0.9, "#b0b0b0"], [1, "#e0e0e0"],
            ],
            labels={"GDP_Formatted": "GDP", "Continent": "Continent"},
        )
        fig_world.update_layout(
            paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
            font=dict(family="Inter, sans-serif", color="#b0b0b0"),
            title=dict(text=f"World GDP Heatmap -- {latest_year}", font=dict(size=18, color="#e8e8e8")),
            geo=dict(
                bgcolor="#0a0a0a", lakecolor="#0a0a0a", landcolor="#161616",
                showframe=False, showcoastlines=True, coastlinecolor="#252525",
                showocean=True, oceancolor="#0a0a0a",
                showcountries=True, countrycolor="#1f1f1f",
                projection_type="natural earth",
            ),
            coloraxis_colorbar=dict(
                title="GDP (USD)", tickfont=dict(color="#666666"),
                title_font=dict(color="#808080"), bgcolor="rgba(14,14,14,0.8)",
                bordercolor="#1f1f1f", outlinecolor="#1a1a1a",
            ),
            margin=dict(l=0, r=0, t=50, b=0), height=550,
        )

        primary_df = map_df[map_df["Role"] == "Primary"]
        if not primary_df.empty:
            fig_world.add_trace(go.Choropleth(
                locations=primary_df["ISO"],
                z=[1] * len(primary_df),
                text=primary_df["Country"] + " (Primary)<br>" + primary_df["GDP_Formatted"],
                hoverinfo="text",
                colorscale=[[0, "rgba(255,255,255,0.35)"], [1, "rgba(255,255,255,0.35)"]],
                showscale=False, marker_line_color="#ffffff", marker_line_width=3,
                name="Primary",
            ))

        secondary_df = map_df[map_df["Role"] == "Secondary"]
        if not secondary_df.empty:
            fig_world.add_trace(go.Choropleth(
                locations=secondary_df["ISO"],
                z=[1] * len(secondary_df),
                text=secondary_df["Country"] + " (Compare)<br>" + secondary_df["GDP_Formatted"],
                hoverinfo="text",
                colorscale=[[0, "rgba(160,160,160,0.25)"], [1, "rgba(160,160,160,0.25)"]],
                showscale=False, marker_line_color="#a0a0a0", marker_line_width=2,
                name="Compare",
            ))

        st.plotly_chart(fig_world, use_container_width=True, key=f"world_map_{country_var}_{'_'.join(sorted(compare_countries))}")

    with tab_selected:
        if len(all_map_countries) == 0:
            st.info("Select countries from the sidebar to view them on the map.")
        else:
            sel_rows = map_df[map_df["Country"].isin(all_map_countries)]
            if sel_rows.empty:
                st.warning("No geographic data found for the selected countries.")
            else:
                fig_sel = go.Figure()

                sec_rows = sel_rows[sel_rows["Role"] == "Secondary"]
                if not sec_rows.empty:
                    fig_sel.add_trace(go.Choropleth(
                        locations=sec_rows["ISO"], z=sec_rows["GDP"],
                        text=sec_rows.apply(lambda r: f"{r['Country']} (Compare)<br>{r['GDP_Formatted']}", axis=1),
                        hoverinfo="text",
                        colorscale=[[0, "#2a2a2a"], [1, "#808080"]],
                        showscale=False, marker_line_color="#a0a0a0", marker_line_width=1.5,
                        name="Compare",
                    ))

                pri_rows = sel_rows[sel_rows["Role"] == "Primary"]
                if not pri_rows.empty:
                    fig_sel.add_trace(go.Choropleth(
                        locations=pri_rows["ISO"], z=pri_rows["GDP"],
                        text=pri_rows.apply(lambda r: f"{r['Country']} (Primary)<br>{r['GDP_Formatted']}", axis=1),
                        hoverinfo="text",
                        colorscale=[[0, "#c0c0c0"], [1, "#ffffff"]],
                        showscale=False, marker_line_color="#ffffff", marker_line_width=2.5,
                        name="Primary",
                    ))

                fig_sel.update_layout(
                    paper_bgcolor="#0a0a0a",
                    font=dict(family="Inter, sans-serif", color="#b0b0b0"),
                    title=dict(text=f"Primary & Compare Countries -- GDP in {latest_year}", font=dict(size=18, color="#e8e8e8")),
                    geo=dict(
                        bgcolor="#0a0a0a", lakecolor="#0a0a0a", landcolor="#161616",
                        showframe=False, showcoastlines=True, coastlinecolor="#252525",
                        showocean=True, oceancolor="#0a0a0a",
                        showcountries=True, countrycolor="#1f1f1f",
                        projection_type="natural earth", fitbounds="locations",
                    ),
                    margin=dict(l=0, r=0, t=50, b=0), height=500,
                    showlegend=True,
                    legend=dict(font=dict(color="#b0b0b0"), bgcolor="rgba(14,14,14,0.8)", bordercolor="#1f1f1f"),
                )
                st.plotly_chart(fig_sel, use_container_width=True, key=f"sel_map_{country_var}_{'_'.join(sorted(compare_countries))}")

                st.markdown("---")
                pri_stat = sel_rows[sel_rows["Country"] == country_var]
                if not pri_stat.empty:
                    st.markdown("**Primary Country**")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric(country_var, pri_stat.iloc[0]["GDP_Formatted"])
                    with c2:
                        st.metric("Continent", pri_stat.iloc[0]["Continent"])
                    with c3:
                        st.metric("Role", "Primary")

                if compare_countries:
                    st.markdown("**Compare Countries**")
                    sec_cols = st.columns(min(len(compare_countries), 4))
                    for idx, cname in enumerate(compare_countries[:4]):
                        row = sel_rows[sel_rows["Country"] == cname]
                        with sec_cols[idx]:
                            if not row.empty:
                                st.metric(cname, row.iloc[0]["GDP_Formatted"], row.iloc[0]["Continent"])

    with tab_data:
        display_map_df = map_df[["Country", "Continent", "GDP_Formatted", "Role"]].rename(
            columns={"GDP_Formatted": f"GDP ({latest_year})", "Role": "Status"}
        ).sort_values("Status", ascending=True)
        st.dataframe(display_map_df, use_container_width=True, hide_index=True, height=500)


elif analysis_choice == "Country GDP Trend":
    gdp_values = processor.get_country_data(country_var, selected_years)
    if gdp_values is None:
        st.warning(f"No data found for {country_var}")
    else:
        tab_chart, tab_stats = st.tabs(["Visualization", "Statistics"])
        with tab_chart:
            fig = go.Figure(layout=_PLOTLY_LAYOUT)
            fig.add_trace(go.Scatter(
                x=selected_years, y=gdp_values,
                mode="lines+markers",
                line=dict(color="#1d9bf0", width=2.5),
                marker=dict(size=6, color="#1d9bf0", line=dict(color="#f4212e", width=1.5)),
                fill="tozeroy", fillcolor="rgba(29,155,240,0.08)",
                name=country_var,
            ))
            fig.update_layout(title=f"GDP Trend: {country_var}", xaxis_title="Year", yaxis_title="GDP (USD)")
            st.plotly_chart(fig, width="stretch")

        with tab_stats:
            stats = processor.calculate_statistics(gdp_values)
            if stats:
                c1, c2, c3 = st.columns(3)
                c1.metric("Maximum GDP", _format_gdp(stats['max']))
                c2.metric("Average GDP", _format_gdp(stats['mean']))
                c3.metric("Minimum GDP", _format_gdp(stats['min']))
                growth = processor.calculate_growth_summary(gdp_values, list(map(int, selected_years)))
                if growth:
                    g1, g2 = st.columns(2)
                    g1.metric("Total Growth", f"{growth['total_growth']:.2f}%")
                    if 'avg_annual_growth' in growth:
                        g2.metric("Avg Annual Growth", f"{growth['avg_annual_growth']:.2f}%")


elif analysis_choice == "Compare Countries":
    all_compare = [country_var] + compare_countries
    if len(all_compare) < 2:
        st.warning("Select at least one country from **Compare With** to compare.")
    else:
        tab_chart, tab_stats = st.tabs(["Visualization", "Statistics"])
        with tab_chart:
            fig = go.Figure(layout=_PLOTLY_LAYOUT)
            list(map(
                lambda ic: fig.add_trace(go.Scatter(
                    x=selected_years,
                    y=processor.get_country_data(ic[1], selected_years),
                    mode="lines+markers",
                    name=f"{ic[1]} (Primary)" if ic[1] == country_var else ic[1],
                    line=dict(color=_PALETTE[ic[0] % len(_PALETTE)], width=3 if ic[1] == country_var else 2),
                    marker=dict(size=7 if ic[1] == country_var else 4),
                )) if processor.get_country_data(ic[1], selected_years) is not None else None,
                enumerate(all_compare),
            ))
            fig.update_layout(title="GDP Comparison Between Countries", xaxis_title="Year", yaxis_title="GDP (USD)")
            st.plotly_chart(fig, width="stretch")

        with tab_stats:
            rows = list(filter(
                lambda r: r is not None,
                map(
                    lambda c: {
                        "Country": c,
                        f"GDP ({latest_year})": processor.get_country_data(c, [latest_year])[0] if processor.get_country_data(c, [latest_year]) is not None else None,
                        "Avg GDP": float(np.nanmean(processor.get_country_data(c, selected_years))) if processor.get_country_data(c, selected_years) is not None else None,
                    },
                    all_compare,
                ),
            ))
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


elif analysis_choice == "Continent Analysis":
    continent_data = processor.get_continent_data(continent_var)
    if continent_data.empty:
        st.warning(f"No data found for {continent_var}")
    else:
        tab_chart, tab_stats = st.tabs(["Visualization", "Statistics"])
        with tab_chart:
            fig = make_subplots(rows=2, cols=2, subplot_titles=[
                f"Total GDP Trend: {continent_var}",
                f"Top {top_n} Countries in {latest_year}",
                f"Top {top_n} by Average GDP ({selected_years[0]}-{selected_years[-1]})",
                f"GDP Distribution in {latest_year}",
            ], vertical_spacing=0.12, horizontal_spacing=0.10)

            total_gdp = processor.calculate_total_gdp(continent_data, selected_years)
            fig.add_trace(go.Scatter(
                x=selected_years, y=total_gdp.values, mode="lines+markers",
                line=dict(color="#00ba7c", width=2.5),
                marker=dict(size=5), fill="tozeroy", fillcolor="rgba(0,186,124,0.08)",
                showlegend=False,
            ), row=1, col=1)

            top_c = continent_data.nlargest(top_n, latest_year)
            fig.add_trace(go.Bar(
                y=top_c["Country Name"], x=top_c[latest_year], orientation="h",
                marker=dict(color=list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(top_c))))),
                showlegend=False,
                text=list(map(_format_gdp, top_c[latest_year])), textposition="auto",
                textfont=dict(color="#e7e9ea", size=10),
            ), row=1, col=2)

            avg_gdp = processor.calculate_average_gdp(continent_data, selected_years)
            cdata_avg = continent_data.copy()
            cdata_avg["avg_gdp"] = avg_gdp
            top_avg = cdata_avg.nlargest(top_n, "avg_gdp")
            fig.add_trace(go.Bar(
                y=top_avg["Country Name"], x=top_avg["avg_gdp"], orientation="h",
                marker=dict(color="#f4212e"), showlegend=False,
                text=list(map(_format_gdp, top_avg["avg_gdp"])), textposition="auto",
                textfont=dict(color="#e7e9ea", size=10),
            ), row=2, col=1)

            latest_gdp = continent_data[latest_year].dropna()
            fig.add_trace(go.Histogram(
                x=latest_gdp, nbinsx=20,
                marker=dict(color="#794bc4", line=dict(color="#1e1e1e", width=0.5)),
                showlegend=False,
            ), row=2, col=2)

            fig.update_layout(
                height=750,
                paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
                font=dict(color="#e7e9ea"),
                title_font=dict(color="#e7e9ea"),
            )
            list(map(
                lambda ax: fig.update_layout(**{
                    f"xaxis{ax}": dict(gridcolor="#1e1e1e", linecolor="#2f3336", tickfont=dict(color="#71767b")),
                    f"yaxis{ax}": dict(gridcolor="#1e1e1e", linecolor="#2f3336", tickfont=dict(color="#71767b")),
                }),
                ["", "2", "3", "4"],
            ))
            st.plotly_chart(fig, width="stretch")

        with tab_stats:
            summary = processor.get_continent_summary(continent_var, latest_year)
            if summary:
                m1, m2, m3 = st.columns(3)
                m1.metric("Total GDP", _format_gdp(summary['total_gdp']))
                m2.metric("Avg GDP", _format_gdp(summary['avg_gdp']))
                m3.metric("Countries", summary['country_count'])
                st.markdown(f"**Top 5 in {latest_year}**")
                st.dataframe(
                    summary['top_countries'][['Country Name', latest_year, 'Continent']].reset_index(drop=True),
                    width="stretch", hide_index=True,
                )


elif analysis_choice == "Top Countries":
    top_countries = processor.get_top_countries(latest_year, top_n)
    tab_chart, tab_stats = st.tabs(["Visualization", "Statistics"])
    with tab_chart:
        fig = go.Figure(layout=_PLOTLY_LAYOUT)
        cnames = top_countries["Country Name"].values
        gdp_vals = top_countries[latest_year].values
        colours = list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(cnames))))
        fig.add_trace(go.Bar(
            y=cnames, x=gdp_vals, orientation="h",
            marker=dict(color=colours, line=dict(width=0)),
            text=list(map(_format_gdp, gdp_vals)), textposition="auto",
            textfont=dict(color="#e7e9ea", size=11),
        ))
        fig.update_layout(
            title=f"Top {top_n} Countries by GDP in {latest_year}",
            yaxis=dict(autorange="reversed"),
            height=max(400, 40 * len(cnames)),
        )
        st.plotly_chart(fig, width="stretch")

    with tab_stats:
        total_top = top_countries[latest_year].sum()
        total_world = df[latest_year].sum()
        pct = (total_top / total_world) * 100
        s1, s2, s3 = st.columns(3)
        s1.metric("Combined GDP", _format_gdp(total_top))
        s2.metric("World GDP", _format_gdp(total_world))
        s3.metric("Share of World", f"{pct:.1f}%")
        st.dataframe(
            top_countries[["Country Name", latest_year, "Continent"]].reset_index(drop=True).rename(
                columns={latest_year: f"GDP ({latest_year})"}
            ),
            width="stretch", hide_index=True,
        )


elif analysis_choice == "GDP Growth Rate":
    gdp_values = processor.get_country_data(country_var, selected_years)
    if gdp_values is None or len(selected_years) < 2:
        st.warning("Need at least 2 years and valid data for growth rate.")
    else:
        growth_rates, growth_years = processor.calculate_growth_rates(gdp_values, selected_years)
        tab_chart, tab_stats = st.tabs(["Visualization", "Statistics"])
        with tab_chart:
            fig = go.Figure(layout=_PLOTLY_LAYOUT)
            colours = list(map(lambda g: "#00ba7c" if g >= 0 else "#f4212e", growth_rates))
            fig.add_trace(go.Bar(
                x=growth_years, y=growth_rates,
                marker=dict(color=colours, line=dict(width=0.3, color="#ffffff")),
                text=list(map(lambda g: f"{g:.1f}%", growth_rates)),
                textposition="outside", textfont=dict(color="#e7e9ea", size=10),
            ))
            fig.add_hline(y=0, line=dict(color="#794bc4", width=1, dash="dash"))
            fig.update_layout(title=f"GDP Growth Rate: {country_var}", xaxis_title="Year", yaxis_title="Growth Rate (%)")
            st.plotly_chart(fig, width="stretch")

        with tab_stats:
            valid_rates = list(filter(lambda r: not np.isnan(r), growth_rates))
            if valid_rates:
                c1, c2, c3 = st.columns(3)
                c1.metric("Avg Growth", f"{np.mean(valid_rates):.2f}%")
                c2.metric("Max Growth", f"{max(valid_rates):.2f}%")
                c3.metric("Min Growth", f"{min(valid_rates):.2f}%")
                pos = len(list(filter(lambda r: r > 0, valid_rates)))
                neg = len(list(filter(lambda r: r < 0, valid_rates)))
                st.caption(f"Positive years: {pos}  ·  Negative years: {neg}")


elif analysis_choice == "Statistical Summary":
    tab_stats, tab_world = st.tabs(["Country Stats", "World Stats"])
    with tab_stats:
        st.subheader(f"Statistics for {country_var}")
        gdp_values = processor.get_country_data(country_var, selected_years)
        if gdp_values is not None:
            stats = processor.calculate_statistics(gdp_values)
            if stats:
                r1 = st.columns(3)
                r1[0].metric(f"GDP in {latest_year}", _format_gdp(gdp_values[-1]))
                r1[1].metric("Max GDP", _format_gdp(stats['max']))
                r1[2].metric("Min GDP", _format_gdp(stats['min']))
                r2 = st.columns(3)
                r2[0].metric("Average GDP", _format_gdp(stats['mean']))
                r2[1].metric("Median GDP", _format_gdp(stats['median']))
                r2[2].metric("Std Deviation", _format_gdp(stats['std']))
                growth = processor.calculate_growth_summary(gdp_values, list(map(int, selected_years)))
                if growth:
                    g1, g2 = st.columns(2)
                    g1.metric("Total Growth", f"{growth['total_growth']:.2f}%")
                    if 'avg_annual_growth' in growth:
                        g2.metric("Avg Annual Growth", f"{growth['avg_annual_growth']:.2f}%")

    with tab_world:
        st.subheader(f"World Statistics ({latest_year})")
        w1 = st.columns(3)
        w1[0].metric("Total World GDP", _format_gdp(world_stats['total_gdp']))
        w1[1].metric("Average GDP", _format_gdp(world_stats['avg_gdp']))
        w1[2].metric("Median GDP", _format_gdp(world_stats['median_gdp']))
        w2 = st.columns(3)
        w2[0].metric("Max GDP", _format_gdp(world_stats['max_gdp']))
        w2[1].metric("Min GDP", _format_gdp(world_stats['min_gdp']))
        w2[2].metric("Std Deviation", _format_gdp(world_stats['std_gdp']))

        st.markdown("---")
        st.markdown(f"**Top {top_n} Countries in {latest_year}**")
        top_c = processor.get_top_countries(latest_year, top_n)
        display_df = top_c[["Country Name", latest_year, "Continent"]].reset_index(drop=True)
        display_df.index = display_df.index + 1
        display_df.index.name = "Rank"
        st.dataframe(display_df.rename(columns={latest_year: f"GDP ({latest_year})"}), width="stretch")

        st.markdown("---")
        st.markdown(f"**By Continent ({latest_year})**")
        cont_rows = list(filter(
            lambda r: r is not None,
            map(
                lambda c: (
                    {"Continent": c, "Total GDP": s['total_gdp'], "Avg GDP": s['avg_gdp'], "Countries": s['country_count']}
                    if (s := processor.get_continent_summary(c, latest_year)) else None
                ),
                continents,
            ),
        ))
        st.dataframe(pd.DataFrame(cont_rows), width="stretch", hide_index=True)


elif analysis_choice == "Year Comparison":
    viz_config = raw_config.get("visualization", {})
    max_comp = viz_config.get("max_comparison_years", 6)
    if len(selected_years) > max_comp:
        step = len(selected_years) // max_comp
        comparison_years = selected_years[::step][:max_comp]
    else:
        comparison_years = selected_years

    comparison_data = processor.get_year_comparison_data(comparison_years, continents)

    tab_chart, tab_stats = st.tabs(["Visualization", "Statistics"])
    with tab_chart:
        fig = go.Figure(layout=_PLOTLY_LAYOUT)
        list(map(
            lambda iy: fig.add_trace(go.Bar(
                x=continents,
                y=list(map(lambda c: comparison_data[iy[1]][c], continents)),
                name=str(iy[1]),
                marker=dict(color=_PALETTE[iy[0] % len(_PALETTE)]),
            )),
            enumerate(comparison_years),
        ))
        fig.update_layout(
            barmode="group",
            title="GDP Comparison Across Continents",
            xaxis_title="Continent", yaxis_title="Total GDP (USD)",
        )
        st.plotly_chart(fig, width="stretch")

    with tab_stats:
        header = ["Continent"] + list(map(str, comparison_years))
        rows = list(map(
            lambda c: dict(
                [("Continent", c)] + list(map(
                    lambda y: (str(y), comparison_data[y][c]),
                    comparison_years,
                ))
            ),
            continents,
        ))
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


elif analysis_choice == "Correlation Analysis":
    all_corr = [country_var] + compare_countries
    if len(all_corr) < 2:
        st.warning("Select at least one country in **Compare With** for correlation analysis.")
    else:
        corr_matrix = processor.get_correlation_matrix(all_corr, selected_years)
        if corr_matrix is None:
            st.warning("Could not build correlation matrix.")
        else:
            tab_chart, tab_stats = st.tabs(["Heatmap", "Top Correlations"])
            with tab_chart:
                fig = go.Figure(layout=_PLOTLY_LAYOUT)
                fig.add_trace(go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns.tolist(),
                    y=corr_matrix.index.tolist(),
                    colorscale=[[0, "#f4212e"], [0.5, "#0a0a0a"], [1, "#1d9bf0"]],
                    zmin=-1, zmax=1,
                    text=corr_matrix.round(2).values,
                    texttemplate="%{text}",
                    textfont=dict(color="#e7e9ea", size=10),
                ))
                fig.update_layout(title="GDP Correlation Matrix", height=500 + 30 * len(all_corr))
                st.plotly_chart(fig, width="stretch")

            with tab_stats:
                top_corr = processor.get_top_correlations(corr_matrix, 10)
                corr_rows = list(map(
                    lambda i_t: {"#": i_t[0], "Country A": i_t[1][0], "Country B": i_t[1][1], "Correlation": round(i_t[1][2], 4)},
                    enumerate(top_corr, 1),
                ))
                st.dataframe(pd.DataFrame(corr_rows), width="stretch", hide_index=True)


elif analysis_choice == "Regional Analysis (Pie + Bar)":
    phase1_ops = raw_config.get("phase1_operations", {})
    regions = phase1_ops.get("compute_regions", continents)

    regional_pairs = list(filter(
        lambda p: p[1] > 0,
        map(lambda r: (r, df[df["Continent"] == r][latest_year].sum()), regions),
    ))
    region_names = list(map(lambda p: p[0], regional_pairs))
    gdp_vals = list(map(lambda p: p[1], regional_pairs))

    col_pie, col_bar = st.columns(2)
    with col_pie:
        fig_pie = go.Figure(layout=_PLOTLY_LAYOUT)
        fig_pie.add_trace(go.Pie(
            labels=region_names, values=gdp_vals,
            marker=dict(colors=list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(region_names))))),
            textinfo="label+percent", textfont=dict(color="#e7e9ea"),
            hole=0.35,
        ))
        fig_pie.update_layout(title=f"Regional GDP Distribution ({latest_year})", showlegend=False)
        st.plotly_chart(fig_pie, width="stretch")

    with col_bar:
        fig_bar = go.Figure(layout=_PLOTLY_LAYOUT)
        fig_bar.add_trace(go.Bar(
            x=region_names, y=gdp_vals,
            marker=dict(color=list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(region_names))))),
            text=list(map(_format_gdp, gdp_vals)), textposition="auto",
            textfont=dict(color="#e7e9ea", size=11),
        ))
        fig_bar.update_layout(title=f"Regional GDP Comparison ({latest_year})", xaxis_title="Region", yaxis_title="GDP (USD)")
        st.plotly_chart(fig_bar, width="stretch")

    total = reduce(lambda a, b: a + b, gdp_vals, 0)
    pcts = list(map(lambda g: g / total * 100, gdp_vals))
    stat_rows = list(map(
        lambda rg_p: {"Region": rg_p[0], "GDP": rg_p[1], "Share (%)": round(rg_p[2], 1)},
        zip(region_names, gdp_vals, pcts),
    ))
    st.dataframe(pd.DataFrame(stat_rows), width="stretch", hide_index=True)


elif analysis_choice == "Year Analysis (Line + Scatter)":
    gdp_values = processor.get_country_data(country_var, selected_years)
    if gdp_values is None:
        st.warning(f"No data found for {country_var}")
    else:
        col_line, col_scatter = st.columns(2)
        with col_line:
            fig = go.Figure(layout=_PLOTLY_LAYOUT)
            fig.add_trace(go.Scatter(
                x=selected_years, y=gdp_values, mode="lines+markers",
                line=dict(color="#00ba7c", width=2.5),
                marker=dict(size=5, line=dict(color="#f4212e", width=1)),
                fill="tozeroy", fillcolor="rgba(0,186,124,0.06)",
                name=country_var,
            ))
            fig.update_layout(title=f"{country_var} — GDP Trend", xaxis_title="Year", yaxis_title="GDP (USD)")
            st.plotly_chart(fig, width="stretch")

        with col_scatter:
            fig2 = go.Figure(layout=_PLOTLY_LAYOUT)
            colours = list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(selected_years))))
            fig2.add_trace(go.Scatter(
                x=selected_years, y=gdp_values, mode="markers",
                marker=dict(size=12, color=colours, line=dict(color="#e7e9ea", width=0.5)),
                name=country_var,
            ))
            fig2.update_layout(title=f"{country_var} — Scatter Analysis", xaxis_title="Year", yaxis_title="GDP (USD)")
            st.plotly_chart(fig2, width="stretch")

        stats = processor.calculate_statistics(gdp_values)
        if stats:
            c1, c2, c3 = st.columns(3)
            c1.metric("Max GDP", _format_gdp(stats['max']))
            c2.metric("Avg GDP", _format_gdp(stats['mean']))
            c3.metric("Min GDP", _format_gdp(stats['min']))


elif analysis_choice == "Complete Analysis (All Charts)":
    phase1_ops = raw_config.get("phase1_operations", {})
    regions = phase1_ops.get("compute_regions", continents[:5])

    regional_pairs = list(filter(
        lambda p: p[1] > 0,
        map(lambda r: (r, df[df["Continent"] == r][latest_year].sum()), regions),
    ))
    region_names = list(map(lambda p: p[0], regional_pairs))
    gdp_vals = list(map(lambda p: p[1], regional_pairs))

    gdp_values = processor.get_country_data(country_var, selected_years)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f"Regional GDP Distribution ({latest_year})",
            f"Regional GDP Comparison ({latest_year})",
            f"{country_var} — Line Graph",
            f"{country_var} — Scatter Plot",
        ],
        specs=[[{"type": "pie"}, {"type": "bar"}], [{"type": "scatter"}, {"type": "scatter"}]],
        vertical_spacing=0.12, horizontal_spacing=0.08,
    )

    fig.add_trace(go.Pie(
        labels=region_names, values=gdp_vals,
        marker=dict(colors=list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(region_names))))),
        textinfo="label+percent", textfont=dict(color="#e7e9ea"), hole=0.3,
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=region_names, y=gdp_vals,
        marker=dict(color=list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(region_names))))),
        showlegend=False,
    ), row=1, col=2)

    if gdp_values is not None:
        fig.add_trace(go.Scatter(
            x=selected_years, y=gdp_values, mode="lines+markers",
            line=dict(color="#00ba7c", width=2.5),
            marker=dict(size=5, line=dict(color="#f4212e", width=1)),
            fill="tozeroy", fillcolor="rgba(0,186,124,0.06)",
            showlegend=False,
        ), row=2, col=1)

    if gdp_values is not None:
        scatter_colors = list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(selected_years))))
        fig.add_trace(go.Scatter(
            x=selected_years, y=gdp_values, mode="markers",
            marker=dict(size=10, color=scatter_colors, line=dict(color="#e7e9ea", width=0.5)),
            showlegend=False,
        ), row=2, col=2)

    fig.update_layout(
        height=800,
        paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
        font=dict(color="#e7e9ea"),
        showlegend=False,
    )
    list(map(
        lambda ax: fig.update_layout(**{
            f"xaxis{ax}": dict(gridcolor="#1e1e1e", linecolor="#2f3336", tickfont=dict(color="#71767b")),
            f"yaxis{ax}": dict(gridcolor="#1e1e1e", linecolor="#2f3336", tickfont=dict(color="#71767b")),
        }),
        ["", "2", "3", "4"],
    ))
    st.plotly_chart(fig, width="stretch")

    st.markdown("---")
    st.caption(f"Configuration: Regions = {', '.join(regions)} · Country = {country_var} · Range = {selected_years[0]}–{selected_years[-1]}")


elif analysis_choice == "Top Countries (Engine)":
    results = engine.run_analysis("top_countries", _engine_params())
    render_engine_results(results, "Top Countries (Engine)")

elif analysis_choice == "Bottom Countries (Engine)":
    results = engine.run_analysis("bottom_countries", _engine_params())
    render_engine_results(results, "Bottom Countries (Engine)")

elif analysis_choice == "Growth Rate (Engine)":
    results = engine.run_analysis("growth_rate", _engine_params())
    render_engine_results(results, "Growth Rate (Engine)")

elif analysis_choice == "Avg GDP by Continent":
    results = engine.run_analysis("avg_gdp_by_continent", _engine_params())
    render_engine_results(results, "Average GDP by Continent")

elif analysis_choice == "Global GDP Trend":
    results = engine.run_analysis("global_gdp_trend", _engine_params())
    if results:
        rdf = pd.DataFrame(results)
        st.subheader("Global GDP Trend")
        tab_chart, tab_table = st.tabs(["Chart", "Data"])
        with tab_chart:
            fig = go.Figure(layout=_PLOTLY_LAYOUT)
            fig.add_trace(go.Scatter(
                x=rdf["year"], y=rdf["total_gdp"], mode="lines+markers",
                line=dict(color="#1d9bf0", width=2.5),
                marker=dict(size=5),
                fill="tozeroy", fillcolor="rgba(29,155,240,0.08)",
            ))
            fig.update_layout(title="Global GDP Trend", xaxis_title="Year", yaxis_title="Total GDP (USD)")
            st.plotly_chart(fig, width="stretch")
        with tab_table:
            st.dataframe(rdf, width="stretch", hide_index=True)
    else:
        st.warning("No results.")

elif analysis_choice == "Fastest Growing Continent":
    results = engine.run_analysis("fastest_growing_continent", _engine_params())
    render_engine_results(results, "Fastest Growing Continent")

elif analysis_choice == "Consistent Decline":
    results = engine.run_analysis("consistent_decline", _engine_params())
    if results:
        render_engine_results(results, "Consistent Decline")
    else:
        st.info("No countries found with consistent GDP decline over the last 5 years.")

elif analysis_choice == "Continent Contribution":
    results = engine.run_analysis("continent_contribution", _engine_params())
    if results:
        rdf = pd.DataFrame(results)
        st.subheader("Continent Contribution to Global GDP")
        tab_chart, tab_table = st.tabs(["Chart", "Data"])
        with tab_chart:
            fig = go.Figure(layout=_PLOTLY_LAYOUT)
            fig.add_trace(go.Pie(
                labels=rdf["continent"], values=rdf["contribution_pct"],
                marker=dict(colors=list(map(lambda i: _PALETTE[i % len(_PALETTE)], range(len(rdf))))),
                textinfo="label+percent", textfont=dict(color="#e7e9ea"),
                hole=0.4,
            ))
            fig.update_layout(title="Continent Contribution (%)", showlegend=True)
            st.plotly_chart(fig, width="stretch")
        with tab_table:
            st.dataframe(rdf, width="stretch", hide_index=True)
    else:
        st.warning("No results.")

elif analysis_choice == "Run All Engine Analyses":
    st.subheader("All Phase 2 Engine Analyses")
    params = _engine_params()
    analyses = engine.get_available_analyses()
    list(map(
        lambda name: (
            st.markdown(f"### {name.replace('_', ' ').title()}"),
            (
                render_engine_results(r, name.replace('_', ' ').title())
                if (r := engine.run_analysis(name, params))
                else st.caption("No results.")
            ),
            st.markdown("---"),
        ),
        analyses,
    ))


st.markdown("---")
st.caption("GDP Analysis Dashboard · Phase 1 + Phase 2 · Streamlit Edition")

