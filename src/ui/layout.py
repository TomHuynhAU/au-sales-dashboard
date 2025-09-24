from dash import dcc, html
import pandas as pd

def serve_layout(states, categories, min_date: pd.Timestamp, max_date: pd.Timestamp):
    return html.Div(
        [
            html.H2("AU Sales Dashboard"),
            html.Div(
                [
                    html.Div(
                        [html.Label("States"),
                         dcc.Dropdown([{"label": s, "value": s} for s in states],
                                      multi=True, id="state-dd")],
                        style={"width": "30%", "display": "inline-block", "marginRight": "1rem"},
                    ),
                    html.Div(
                        [html.Label("Categories"),
                         dcc.Dropdown([{"label": c, "value": c} for c in categories],
                                      multi=True, id="cat-dd")],
                        style={"width": "30%", "display": "inline-block", "marginRight": "1rem"},
                    ),
                    html.Div(
                        [html.Label("Date Range"),
                         dcc.DatePickerRange(id="date-range", start_date=min_date, end_date=max_date)],
                        style={"display": "inline-block"},
                    ),
                ],
                style={"marginBottom": "1rem"},
            ),
            # KPI
            html.Div(id="kpi-cards", style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),
            # Charts + table
            dcc.Graph(id="sales-line"),
            dcc.Graph(id="sales-bar"),
            html.H4("Latest Top Categories by Sales"),
            html.Div(id="top-table"),
        ],
        style={"padding": "1rem 1.5rem", "fontFamily": "system-ui, Segoe UI, Roboto"},
    )
