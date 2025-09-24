from dash import dcc, html
import pandas as pd

def serve_layout(states, categories, min_date: pd.Timestamp, max_date: pd.Timestamp):
    return html.Div(
        [
            # Header
            html.Header(
                [
                    html.Div(
                        [
                            html.H1("AU Sales Dashboard", className="title"),
                            html.P("Realtime insights across states · categories · time", className="subtitle"),
                        ],
                        className="title-wrap",
                    ),
                    html.Div(
                        [
                            html.A("Reset filters", id="reset-filters", className="btn btn-ghost", href="#"),
                        ],
                        className="header-actions",
                    ),
                ],
                className="app-header glass",
            ),

            # Controls
            html.Section(
                [
                    html.Div(
                        [
                            html.Label("States", className="label"),
                            dcc.Dropdown(
                                [{"label": s, "value": s} for s in states],
                                multi=True, id="state-dd", className="dd"
                            ),
                        ],
                        className="control",
                    ),
                    html.Div(
                        [
                            html.Label("Categories", className="label"),
                            dcc.Dropdown(
                                [{"label": c, "value": c} for c in categories],
                                multi=True, id="cat-dd", className="dd"
                            ),
                        ],
                        className="control",
                    ),
                    html.Div(
                        [
                            html.Label("Date Range", className="label"),
                            dcc.DatePickerRange(
                                id="date-range", start_date=min_date, end_date=max_date, className="daterange"
                            ),
                        ],
                        className="control",
                    ),
                ],
                className="controls sticky",
            ),

            # KPI cards
            html.Section(id="kpi-cards", className="kpi-grid"),

            # Charts
            html.Section(
                [
                    html.Div([dcc.Graph(id="sales-line")], className="card"),
                    html.Div([dcc.Graph(id="sales-bar")], className="card"),
                ],
                className="charts-grid",
            ),

            # Table
            html.Section(
                [
                    html.Div(
                        [
                            html.Div(
                                [html.H3("Latest Top Categories by Sales", className="section-title")],
                                className="section-head"
                            ),
                            html.Div(id="top-table", className="table-wrap"),
                        ],
                        className="card",
                    )
                ],
                className="section",
            ),

            # Footer
            html.Footer(
                [
                    html.Span("© 2025 AU Sales • Minimal UI"),
                ],
                className="app-footer",
            ),
        ],
        className="shell",
    )
