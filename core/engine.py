from __future__ import annotations

from typing import List, Dict, Any, Optional
from functools import reduce

import numpy as np
import pandas as pd

from core.contracts import DataSink


_safe_div = lambda num, den: (num / den) if den != 0 else 0.0

_year_keys = lambda row: sorted(filter(lambda k: isinstance(k, int), row.keys()))


def _raw_to_df(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(raw_data)


def _resolve_years(df: pd.DataFrame, date_range: List[int]) -> List[int]:
    all_years = sorted(filter(lambda c: isinstance(c, int), df.columns))
    start, end = date_range[0], date_range[1]
    return list(filter(lambda y: start <= y <= end, all_years))


def _continent_df(df: pd.DataFrame, continent: str) -> pd.DataFrame:
    return df[df['Continent'] == continent]


def _all_continents(df: pd.DataFrame) -> List[str]:
    return sorted(filter(pd.notna, df['Continent'].unique()))


class TransformationEngine:

    _ANALYSES: tuple = (
        'top_countries',
        'bottom_countries',
        'growth_rate',
        'avg_gdp_by_continent',
        'global_gdp_trend',
        'fastest_growing_continent',
        'consistent_decline',
        'continent_contribution',
    )

    def __init__(self, sink: DataSink, config: Dict[str, Any] | None = None):
        self.sink: DataSink = sink
        self.config: Dict[str, Any] = config or {}
        self.df: Optional[pd.DataFrame] = None
        self.year_columns: List[int] = []

        self._dispatch: Dict[str, Any] = {
            'top_countries':             self._top_countries,
            'bottom_countries':          self._bottom_countries,
            'growth_rate':               self._growth_rate,
            'avg_gdp_by_continent':      self._avg_gdp_by_continent,
            'global_gdp_trend':          self._global_gdp_trend,
            'fastest_growing_continent': self._fastest_growing_continent,
            'consistent_decline':        self._consistent_decline,
            'continent_contribution':    self._continent_contribution,
        }

    def execute(self, raw_data: List[Dict[str, Any]]) -> None:
        self.df = _raw_to_df(raw_data)
        self.year_columns = sorted(
            filter(lambda c: isinstance(c, int), self.df.columns)
        )

        pipeline_cfg = self.config.get('pipeline', {})
        analyses = pipeline_cfg.get('analyses', list(self._ANALYSES))
        params = pipeline_cfg.get('default_params', {})

        list(map(
            lambda name: self._run_and_emit(name, params),
            analyses,
        ))

    def get_available_analyses(self) -> List[str]:
        return list(self._ANALYSES)

    def run_analysis(
        self,
        analysis_name: str,
        params: Dict[str, Any],
    ) -> Optional[List[Dict[str, Any]]]:
        handler = self._dispatch.get(analysis_name)
        if handler is None:
            return None
        return handler(params)

    def _run_and_emit(self, name: str, params: Dict[str, Any]) -> None:
        results = self.run_analysis(name, params)
        if results is not None:
            title = name.replace('_', ' ').title()
            self.sink.write(results, title=title)

    def _top_countries(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        continent = params.get('continent', 'Asia')
        year = params.get('year', self.year_columns[-1] if self.year_columns else 2020)
        n = params.get('top_n', 10)

        cdf = _continent_df(self.df, continent)
        if cdf.empty or year not in cdf.columns:
            return []

        top = cdf.nlargest(n, year)
        return list(map(
            lambda row: {
                'rank': row[0],
                'country': row[1]['Country Name'],
                'continent': continent,
                'year': year,
                'gdp': row[1][year],
            },
            enumerate(top.iterrows(), 1),
        ))

    def _bottom_countries(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        continent = params.get('continent', 'Asia')
        year = params.get('year', self.year_columns[-1] if self.year_columns else 2020)
        n = params.get('top_n', 10)

        cdf = _continent_df(self.df, continent)
        if cdf.empty or year not in cdf.columns:
            return []

        valid = cdf.dropna(subset=[year])
        bottom = valid.nsmallest(n, year)
        return list(map(
            lambda row: {
                'rank': row[0],
                'country': row[1]['Country Name'],
                'continent': continent,
                'year': year,
                'gdp': row[1][year],
            },
            enumerate(bottom.iterrows(), 1),
        ))

    def _growth_rate(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        continent = params.get('continent', 'Asia')
        date_range = params.get('date_range', [2000, 2020])

        cdf = _continent_df(self.df, continent)
        if cdf.empty:
            return []

        years = _resolve_years(self.df, date_range)
        if len(years) < 2:
            return []

        first_year, last_year = years[0], years[-1]

        def _country_growth(row_tuple):
            _, row = row_tuple
            first_val = row.get(first_year, np.nan)
            last_val = row.get(last_year, np.nan)
            if pd.isna(first_val) or pd.isna(last_val) or first_val == 0:
                return None
            growth = _safe_div(last_val - first_val, first_val) * 100
            return {
                'country': row['Country Name'],
                'continent': continent,
                'start_year': first_year,
                'end_year': last_year,
                'start_gdp': first_val,
                'end_gdp': last_val,
                'growth_pct': round(growth, 2),
            }

        results = list(filter(
            lambda r: r is not None,
            map(_country_growth, cdf.iterrows()),
        ))
        return sorted(results, key=lambda r: r['growth_pct'], reverse=True)

    def _avg_gdp_by_continent(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        date_range = params.get('date_range', [2000, 2020])
        years = _resolve_years(self.df, date_range)
        if not years:
            return []

        continents = _all_continents(self.df)

        def _avg_for_continent(continent):
            cdf = _continent_df(self.df, continent)
            if cdf.empty:
                return None
            total = reduce(
                lambda acc, y: acc + cdf[y].dropna().mean(),
                years,
                0.0,
            )
            avg = _safe_div(total, len(years))
            return {
                'continent': continent,
                'avg_gdp': round(avg, 2),
                'start_year': years[0],
                'end_year': years[-1],
                'country_count': len(cdf),
            }

        return list(filter(
            lambda r: r is not None,
            map(_avg_for_continent, continents),
        ))

    def _global_gdp_trend(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        date_range = params.get('date_range', [2000, 2020])
        years = _resolve_years(self.df, date_range)
        if not years:
            return []

        return list(map(
            lambda y: {
                'year': y,
                'total_gdp': round(self.df[y].dropna().sum(), 2),
                'country_count': int(self.df[y].dropna().count()),
            },
            years,
        ))

    def _fastest_growing_continent(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        date_range = params.get('date_range', [2000, 2020])
        years = _resolve_years(self.df, date_range)
        if len(years) < 2:
            return []

        first_year, last_year = years[0], years[-1]
        continents = _all_continents(self.df)

        def _continent_growth(continent):
            cdf = _continent_df(self.df, continent)
            if cdf.empty:
                return None
            first_total = cdf[first_year].dropna().sum()
            last_total = cdf[last_year].dropna().sum()
            if first_total == 0:
                return None
            growth = _safe_div(last_total - first_total, first_total) * 100
            return {
                'continent': continent,
                'start_year': first_year,
                'end_year': last_year,
                'start_gdp': round(first_total, 2),
                'end_gdp': round(last_total, 2),
                'growth_pct': round(growth, 2),
            }

        results = list(filter(
            lambda r: r is not None,
            map(_continent_growth, continents),
        ))
        return sorted(results, key=lambda r: r['growth_pct'], reverse=True)

    def _consistent_decline(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        decline_years = params.get('decline_years', 5)
        all_years = sorted(filter(lambda c: isinstance(c, int), self.df.columns))

        if len(all_years) < decline_years:
            return []

        check_years = all_years[-decline_years:]

        def _is_declining(row_tuple):
            _, row = row_tuple
            vals = list(map(lambda y: row.get(y, np.nan), check_years))
            if any(map(pd.isna, vals)):
                return None
            pairs = list(zip(vals[:-1], vals[1:]))
            all_declining = all(map(lambda p: p[1] < p[0], pairs))
            if not all_declining:
                return None
            total_decline = _safe_div(vals[-1] - vals[0], vals[0]) * 100 if vals[0] != 0 else 0
            return {
                'country': row['Country Name'],
                'continent': row.get('Continent', 'N/A'),
                'decline_years': decline_years,
                'start_year': check_years[0],
                'end_year': check_years[-1],
                'start_gdp': vals[0],
                'end_gdp': vals[-1],
                'decline_pct': round(total_decline, 2),
            }

        results = list(filter(
            lambda r: r is not None,
            map(_is_declining, self.df.iterrows()),
        ))
        return sorted(results, key=lambda r: r['decline_pct'])

    def _continent_contribution(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        date_range = params.get('date_range', [2000, 2020])
        years = _resolve_years(self.df, date_range)
        if not years:
            return []

        continents = _all_continents(self.df)

        global_total = reduce(
            lambda acc, y: acc + self.df[y].dropna().sum(),
            years,
            0.0,
        )

        if global_total == 0:
            return []

        def _contrib(continent):
            cdf = _continent_df(self.df, continent)
            if cdf.empty:
                return None
            cont_total = reduce(
                lambda acc, y: acc + cdf[y].dropna().sum(),
                years,
                0.0,
            )
            pct = _safe_div(cont_total, global_total) * 100
            return {
                'continent': continent,
                'total_gdp': round(cont_total, 2),
                'global_total_gdp': round(global_total, 2),
                'contribution_pct': round(pct, 2),
                'start_year': years[0],
                'end_year': years[-1],
            }

        results = list(filter(
            lambda r: r is not None,
            map(_contrib, continents),
        ))
        return sorted(results, key=lambda r: r['contribution_pct'], reverse=True)
