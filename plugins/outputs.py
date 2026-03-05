from __future__ import annotations

from typing import List, Dict, Any, Optional
from functools import reduce
import os

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import numpy as np


_FORMAT_GDP = lambda v: (
    f"${v / 1e12:.2f}T" if abs(v) >= 1e12 else
    f"${v / 1e9:.2f}B" if abs(v) >= 1e9 else
    f"${v / 1e6:.2f}M" if abs(v) >= 1e6 else
    f"${v:,.0f}"
)

_SEPARATOR = "=" * 70
_SUB_SEP = "-" * 70


class ConsoleWriter:

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}

    def write(self, records: List[Dict[str, Any]], title: str = "") -> None:
        if title:
            print(f"\n{_SEPARATOR}")
            print(f"  {title.upper()}")
            print(_SEPARATOR)

        if not records:
            print("  No data available.\n")
            return

        keys = list(records[0].keys())
        header = "  ".join(map(lambda k: f"{k:<20s}", keys))
        print(f"\n  {header}")
        print(f"  {_SUB_SEP}")

        list(map(
            lambda rec: print("  " + "  ".join(map(
                lambda k: f"{_format_value(rec.get(k, '')):<20s}",
                keys,
            ))),
            records,
        ))
        print()

    def write_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        print(f"\n  [CHART: {chart_type}] {title}")
        labels = data.get('labels', [])
        values = data.get('values', [])
        if labels and values:
            list(map(
                lambda pair: print(f"    {pair[0]:<30s} {_format_value(pair[1])}"),
                zip(labels, values),
            ))
        print()

    def write_summary(self, summary: Dict[str, Any], title: str = "") -> None:
        if title:
            print(f"\n  --- {title} ---")
        list(map(
            lambda kv: print(f"    {kv[0]:<25s}: {_format_value(kv[1])}"),
            summary.items(),
        ))
        print()


class GraphicsChartWriter:

    def __init__(self, config: Dict[str, Any] | None = None, output_dir: str = "output_charts"):
        self.config = config or {}
        self.output_dir = output_dir
        self._chart_count = 0
        os.makedirs(self.output_dir, exist_ok=True)

        viz = self.config.get('visualization', {})
        self._fig_size = tuple(viz.get('figure_size', [12, 6]))
        self._style = viz.get('style', 'dark_background')
        self._bg_color = viz.get('chart_bg_color', '#000000')
        self._face_color = viz.get('chart_face_color', '#000000')
        self._grid_color = viz.get('grid_color', '#2f3336')
        self._grid_alpha = viz.get('grid_alpha', 0.3)
        self._title_size = viz.get('title_font_size', 16)
        self._label_size = viz.get('label_font_size', 12)
        self._tick_size = viz.get('tick_font_size', 9)

        colors_cfg = self.config.get('colors', {})
        self._palette = colors_cfg.get('chart_palette', [
            '#1d9bf0', '#00ba7c', '#f4212e', '#ffad1f',
            '#794bc4', '#ff7a00', '#17bf63', '#e0245e',
        ])
        self._text_color = colors_cfg.get('text_primary', '#e7e9ea')
        self._secondary_color = colors_cfg.get('text_secondary', '#71767b')

        plt.style.use(self._style)

    def write(self, records: List[Dict[str, Any]], title: str = "") -> None:
        if not records:
            return

        keys = list(records[0].keys())
        label_key = next(
            filter(lambda k: k in ('country', 'continent', 'year'), keys),
            keys[0],
        )
        value_key = next(
            filter(lambda k: k in ('gdp', 'avg_gdp', 'total_gdp', 'growth_pct', 'contribution_pct', 'decline_pct'), keys),
            None,
        )

        if value_key is None:
            return

        labels = list(map(lambda r: str(r.get(label_key, '')), records))
        values = list(map(lambda r: float(r.get(value_key, 0)), records))

        self.write_chart(
            chart_type='bar',
            data={'labels': labels, 'values': values},
            title=title or 'Analysis Results',
            options={'value_key': value_key},
        )

    def write_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        opts = options or {}
        dispatch = {
            'bar': self._draw_bar,
            'line': self._draw_line,
            'pie': self._draw_pie,
            'grouped_bar': self._draw_grouped_bar,
            'heatmap': self._draw_heatmap,
        }
        drawer = dispatch.get(chart_type, self._draw_bar)
        fig, ax = plt.subplots(figsize=self._fig_size)
        self._style_figure(fig)
        drawer(ax, data, title, opts)
        self._style_ax(ax, title)
        self._save_figure(fig, title)
        plt.close(fig)

    def write_summary(self, summary: Dict[str, Any], title: str = "") -> None:
        fig, ax = plt.subplots(figsize=(10, 4))
        self._style_figure(fig)
        ax.axis('off')

        lines = list(map(
            lambda kv: f"{kv[0]}: {_format_value(kv[1])}",
            summary.items(),
        ))
        text_block = "\n".join([title, _SUB_SEP] + lines if title else lines)
        ax.text(
            0.05, 0.95, text_block,
            transform=ax.transAxes,
            fontsize=self._label_size,
            color=self._text_color,
            verticalalignment='top',
            fontfamily='monospace',
        )
        self._save_figure(fig, title or "summary")
        plt.close(fig)

    def _style_figure(self, fig) -> None:
        fig.patch.set_facecolor(self._face_color)

    def _style_ax(self, ax, title: str = "") -> None:
        ax.set_facecolor(self._bg_color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self._grid_color)
        ax.spines['bottom'].set_color(self._grid_color)
        ax.tick_params(colors=self._secondary_color, labelsize=self._tick_size)
        ax.xaxis.label.set_color(self._secondary_color)
        ax.yaxis.label.set_color(self._secondary_color)
        if title:
            ax.set_title(title, color=self._text_color, fontsize=self._title_size, pad=15)
        ax.grid(True, alpha=self._grid_alpha, color=self._grid_color)

    def _draw_bar(self, ax, data, title, opts) -> None:
        labels = data.get('labels', [])
        values = data.get('values', [])
        if not labels:
            return
        colors = list(map(
            lambda i: self._palette[i % len(self._palette)],
            range(len(labels)),
        ))
        bars = ax.bar(range(len(labels)), values, color=colors, edgecolor='none', width=0.7)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=self._tick_size)
        value_key = opts.get('value_key', 'gdp')
        ax.set_ylabel(value_key.replace('_', ' ').title(), fontsize=self._label_size)

    def _draw_line(self, ax, data, title, opts) -> None:
        labels = data.get('labels', [])
        values = data.get('values', [])
        if not labels:
            return
        color = self._palette[0]
        ax.plot(labels, values, color=color, linewidth=2, marker='o', markersize=4)
        ax.fill_between(labels, values, alpha=0.1, color=color)

    def _draw_pie(self, ax, data, title, opts) -> None:
        labels = data.get('labels', [])
        values = data.get('values', [])
        if not labels:
            return
        colors = list(map(
            lambda i: self._palette[i % len(self._palette)],
            range(len(labels)),
        ))
        ax.pie(
            values, labels=labels, colors=colors, autopct='%1.1f%%',
            textprops={'color': self._text_color, 'fontsize': self._tick_size},
        )

    def _draw_grouped_bar(self, ax, data, title, opts) -> None:
        groups = data.get('groups', {})
        labels = data.get('labels', [])
        if not groups or not labels:
            return
        group_names = list(groups.keys())
        x = np.arange(len(labels))
        width = 0.8 / len(group_names)
        list(map(
            lambda gi: ax.bar(
                x + gi[0] * width, gi[1], width,
                label=group_names[gi[0]],
                color=self._palette[gi[0] % len(self._palette)],
            ),
            enumerate(map(lambda g: groups[g], group_names)),
        ))
        ax.set_xticks(x + width * (len(group_names) - 1) / 2)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.legend(facecolor=self._bg_color, edgecolor=self._grid_color, labelcolor=self._text_color)

    def _draw_heatmap(self, ax, data, title, opts) -> None:
        matrix = data.get('matrix', [])
        xlabels = data.get('xlabels', [])
        ylabels = data.get('ylabels', [])
        if not matrix:
            return
        im = ax.imshow(matrix, cmap='Blues', aspect='auto')
        ax.set_xticks(range(len(xlabels)))
        ax.set_xticklabels(xlabels, rotation=45, ha='right')
        ax.set_yticks(range(len(ylabels)))
        ax.set_yticklabels(ylabels)
        plt.colorbar(im, ax=ax)

    def _save_figure(self, fig, title: str) -> None:
        self._chart_count += 1
        safe_name = title.lower().replace(' ', '_').replace('/', '_')[:50] if title else 'chart'
        filename = f"{self._chart_count:03d}_{safe_name}.png"
        path = os.path.join(self.output_dir, filename)
        fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
        print(f"  [SAVED] {path}")


def _format_value(v) -> str:
    if isinstance(v, float):
        return _FORMAT_GDP(v) if abs(v) > 1e5 else f"{v:.2f}"
    return str(v)


class TkinterSink:

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self._viz_frame = None
        self._stats_text = None
        self._notebook = None

        viz = self.config.get('visualization', {})
        self._fig_size = tuple(viz.get('figure_size', [12, 6]))
        self._style = viz.get('style', 'dark_background')
        self._bg_color = viz.get('chart_bg_color', '#000000')
        self._face_color = viz.get('chart_face_color', '#000000')
        self._grid_color = viz.get('grid_color', '#2f3336')
        self._grid_alpha = viz.get('grid_alpha', 0.3)
        self._title_size = viz.get('title_font_size', 16)
        self._label_size = viz.get('label_font_size', 12)
        self._tick_size = viz.get('tick_font_size', 9)

        colors_cfg = self.config.get('colors', {})
        self._palette = colors_cfg.get('chart_palette', [
            '#1d9bf0', '#00ba7c', '#f4212e', '#ffad1f',
            '#794bc4', '#ff7a00', '#17bf63', '#e0245e',
        ])
        self._text_color = colors_cfg.get('text_primary', '#e7e9ea')
        self._secondary_color = colors_cfg.get('text_secondary', '#71767b')

    def bind(self, viz_frame, stats_text, notebook) -> None:
        self._viz_frame = viz_frame
        self._stats_text = stats_text
        self._notebook = notebook

    def write(self, records: List[Dict[str, Any]], title: str = "") -> None:
        if not records:
            self._write_stats(f"  {title}\n  No data available.\n")
            return

        keys = list(records[0].keys())
        label_key = next(
            filter(lambda k: k in ('country', 'continent', 'year'), keys),
            keys[0],
        )
        value_key = next(
            filter(lambda k: k in (
                'gdp', 'avg_gdp', 'total_gdp', 'growth_pct',
                'contribution_pct', 'decline_pct', 'start_gdp', 'end_gdp',
            ), keys),
            None,
        )

        self._append_stats_table(records, keys, title)

        if value_key is not None:
            labels = list(map(lambda r: str(r.get(label_key, '')), records))
            values = list(map(lambda r: float(r.get(value_key, 0)), records))
            self._render_chart(
                chart_type='bar',
                labels=labels,
                values=values,
                title=title,
                value_key=value_key,
            )

    def write_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        opts = options or {}
        labels = data.get('labels', [])
        values = data.get('values', [])
        if labels and values:
            self._render_chart(
                chart_type=chart_type,
                labels=labels,
                values=values,
                title=title,
                value_key=opts.get('value_key', 'gdp'),
            )

    def write_summary(self, summary: Dict[str, Any], title: str = "") -> None:
        lines = list(map(
            lambda kv: f"    {kv[0]:<25s}: {_format_value(kv[1])}",
            summary.items(),
        ))
        block = (
            ([f"\n  --- {title} ---"] + lines + [""])
            if title else (lines + [""])
        )
        self._write_stats("\n".join(block))

    def _append_stats_table(self, records, keys, title) -> None:
        import tkinter as tk
        if self._stats_text is None:
            return

        header_line = "  ".join(map(lambda k: f"{k:<20s}", keys))
        row_lines = list(map(
            lambda rec: "  ".join(map(
                lambda k: f"{_format_value(rec.get(k, '')):<20s}", keys,
            )),
            records,
        ))
        block = (
            [f"\n{'=' * 70}", f"  {title.upper()}", '=' * 70, "",
             f"  {header_line}", f"  {'-' * 70}"]
            + list(map(lambda r: f"  {r}", row_lines))
            + [""]
        )
        text = "\n".join(block)
        self._stats_text.config(state=tk.NORMAL)
        self._stats_text.insert(tk.END, text)
        self._stats_text.config(state=tk.DISABLED)

    def _write_stats(self, text: str) -> None:
        import tkinter as tk
        if self._stats_text is None:
            return
        self._stats_text.config(state=tk.NORMAL)
        self._stats_text.insert(tk.END, text)
        self._stats_text.config(state=tk.DISABLED)

    def _render_chart(self, chart_type, labels, values, title, value_key='gdp') -> None:
        import tkinter as tk
        if self._viz_frame is None:
            return

        list(map(lambda w: w.destroy(), self._viz_frame.winfo_children()))

        plt.style.use(self._style)
        fig = Figure(figsize=self._fig_size)
        fig.patch.set_facecolor(self._face_color)
        ax = fig.add_subplot(111)

        dispatch = {
            'bar': self._draw_bar,
            'line': self._draw_line,
            'pie': self._draw_pie,
        }
        drawer = dispatch.get(chart_type, self._draw_bar)
        drawer(ax, labels, values, value_key)

        ax.set_facecolor(self._bg_color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self._grid_color)
        ax.spines['bottom'].set_color(self._grid_color)
        ax.tick_params(colors=self._secondary_color, labelsize=self._tick_size)
        ax.xaxis.label.set_color(self._secondary_color)
        ax.yaxis.label.set_color(self._secondary_color)
        if title:
            ax.set_title(title, color=self._text_color, fontsize=self._title_size, pad=15)
        ax.grid(True, alpha=self._grid_alpha, color=self._grid_color)

        fig.tight_layout()

        colors_cfg = self.config.get('colors', {})
        canvas = FigureCanvasTkAgg(fig, master=self._viz_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.configure(bg=colors_cfg.get('dark', '#000000'))
        widget.pack(fill=tk.BOTH, expand=True)

        if self._notebook is not None:
            self._notebook.select(self._viz_frame)

    def _draw_bar(self, ax, labels, values, value_key) -> None:
        colors = list(map(
            lambda i: self._palette[i % len(self._palette)],
            range(len(labels)),
        ))
        ax.barh(range(len(labels)), values, color=colors, edgecolor='none', height=0.65)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=self._tick_size)
        ax.set_xlabel(value_key.replace('_', ' ').title(), fontsize=self._label_size)
        ax.xaxis.set_major_formatter(FuncFormatter(
            lambda x, _: (f'${x/1e12:.1f}T' if x >= 1e12 else
                          f'${x/1e9:.0f}B' if x >= 1e9 else
                          f'${x/1e6:.0f}M' if x >= 1e6 else f'{x:,.1f}')
        ))

    def _draw_line(self, ax, labels, values, value_key) -> None:
        color = self._palette[0]
        ax.plot(labels, values, color=color, linewidth=2, marker='o', markersize=4)
        ax.fill_between(labels, values, alpha=0.1, color=color)
        ax.set_ylabel(value_key.replace('_', ' ').title(), fontsize=self._label_size)

    def _draw_pie(self, ax, labels, values, value_key) -> None:
        colors = list(map(
            lambda i: self._palette[i % len(self._palette)],
            range(len(labels)),
        ))
        ax.pie(
            values, labels=labels, colors=colors, autopct='%1.1f%%',
            textprops={'color': self._text_color, 'fontsize': self._tick_size},
        )


# ══════════════════════════════════════════════════════════════
# StreamlitSink — DataSink implementation for Streamlit GUI
# ══════════════════════════════════════════════════════════════

class StreamlitSink:
    """DataSink that accumulates results for rendering in a Streamlit app.

    Stores tables, chart descriptors, and summary text in session-state-like
    lists so the Streamlit page can drain them after an engine run.
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self._tables: List[Dict[str, Any]] = []
        self._charts: List[Dict[str, Any]] = []
        self._summaries: List[str] = []

    # -- protocol methods --

    def write(self, records: List[Dict[str, Any]], title: str = "") -> None:
        self._tables.append({"title": title, "records": records})

    def write_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._charts.append({
            "chart_type": chart_type,
            "data": data,
            "title": title,
            "options": options or {},
        })

    def write_summary(self, summary: Dict[str, Any]) -> None:
        lines = list(map(
            lambda kv: f"{kv[0].replace('_', ' ').title()}: {_format_value(kv[1])}",
            summary.items(),
        ))
        self._summaries.append("\n".join(lines))

    # -- accessors --

    def drain_tables(self) -> List[Dict[str, Any]]:
        tables, self._tables = self._tables, []
        return tables

    def drain_charts(self) -> List[Dict[str, Any]]:
        charts, self._charts = self._charts, []
        return charts

    def drain_summaries(self) -> List[str]:
        summaries, self._summaries = self._summaries, []
        return summaries
