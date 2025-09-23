from __future__ import annotations
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dash_table, html
from ..data.transforms import filter_data, compute_kpis, top_latest

def _kpi_view(kpis: dict):
    box = {
        "flex": "1 1 0",
        "background": "#f6f8fc",
        "border": "1px solid #e2e8f0",
        "borderRadius": "12px",
        "padding": "12px 16px",
    }
    fmt_money = lambda x: f"${x:,.0f}"
    mom_txt = "–" if kpis["mom"] is None else ("▲ " if kpis["mom"] >= 0 else "▼ ") + f"{kpis['mom']:.1f}%"
    return [
        html.Div([html.H3(fmt_money(kpis["total"])), html.P("Total Sales")], style=box),
        html.Div([html.H3(fmt_money(kpis["avg_per_month"])), html.P("Avg / Month")], style=box),
        html.Div([html.H3(mom_txt), html.P("MoM Growth")], style=box),
    ]

def register_callbacks(app: Dash, base_df: pd.DataFrame) -> None:
    @app.callback(
        Output("sales-line", "figure"),
        Output("sales-bar", "figure"),
        Output("top-table", "children"),
        Output("kpi-cards", "children"),
        Input("state-dd", "value"),
        Input("cat-dd", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    )
    def update(states, cats, start, end):
        start_ts = pd.to_datetime(start) if start else None
        end_ts = pd.to_datetime(end) if end else None
        df = filter_data(base_df, states, cats, start_ts, end_ts)

        if df.empty:
            empty_line = px.line(pd.DataFrame({"date": [], "sales": []}), x="date", y="sales")
            empty_bar = px.bar(pd.DataFrame({"category": [], "sales": []}), x="category", y="sales")
            return empty_line, empty_bar, dash_table.DataTable(data=[]), _kpi_view(
                {"total": 0.0, "avg_per_month": 0.0, "mom": None}
            )

        line_fig = px.line(df, x="date", y="sales", color="state", markers=True)
        bar_fig = px.bar(df.groupby("category", as_index=False)["sales"].sum(), x="category", y="sales")
        table_df = top_latest(df, n=5)
        table = dash_table.DataTable(
            data=table_df.to_dict("records"),
            columns=[{"name": c.capitalize(), "id": c} for c in table_df.columns],
            page_size=5,
        )
        kpis = compute_kpis(df)
        return line_fig, bar_fig, table, _kpi_view(kpis)
