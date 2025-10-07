from dash import dcc, html
import pandas as pd

def serve_layout(states: list[str], categories: list[str], min_date: pd.Timestamp, max_date: pd.Timestamp):
    return html.Div(
        [
            # Header
            html.Div(
                [
                    html.H1("AU Sales Dashboard", style={"margin": 0, "fontWeight": 700}),
                    html.P("Clean UI 2025 • Interactive sales insights",
                           style={"margin": "4px 0 0", "color": "#64748b"}),
                ],
                style={"marginBottom": "16px"},
            ),

            # Filters (grid 3 cột)
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("State", style={"fontWeight": 600, "marginBottom": 6}),
                            dcc.Dropdown(
                                id="state-dd",
                                options=[{"label": s, "value": s} for s in states],
                                value=states,      # mặc định chọn tất cả
                                multi=True,
                                placeholder="Select state(s)",
                            ),
                        ],
                        style={"flex": "1 1 0", "minWidth": 220},
                    ),
                    html.Div(
                        [
                            html.Label("Category", style={"fontWeight": 600, "marginBottom": 6}),
                            dcc.Dropdown(
                                id="cat-dd",
                                options=[{"label": c, "value": c} for c in categories],
                                value=categories,  # mặc định chọn tất cả
                                multi=True,
                                placeholder="Select category(ies)",
                            ),
                        ],
                        style={"flex": "1 1 0", "minWidth": 220},
                    ),
                    html.Div(
                        [
                            html.Label("Date range", style={"fontWeight": 600, "marginBottom": 6}),
                            dcc.DatePickerRange(
                                id="date-range",
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=min_date,
                                end_date=max_date,
                                display_format="YYYY-MM-DD",
                                updatemode="bothdates",
                            ),
                        ],
                        style={"flex": "1 1 0", "minWidth": 260},
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(3, minmax(220px, 1fr))",
                    "gap": "16px",
                    "marginBottom": "16px",
                },
            ),

            # KPI cards (để callback fill)
            html.Div(
                id="kpi-cards",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(3, 1fr)",
                    "gap": "16px",
                    "marginBottom": "16px",
                },
            ),

            # Charts 2 cột
            html.Div(
                [
                    dcc.Graph(id="sales-line", config={"displayModeBar": False}, style={"height": "380px"}),
                    dcc.Graph(id="sales-bar",  config={"displayModeBar": False}, style={"height": "380px"}),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "16px",
                    "marginBottom": "16px",
                },
            ),

            # Latest table
            html.Div(
                [
                    html.H3("Latest Records", style={"margin": "0 0 8px"}),
                    html.Div(id="top-table"),
                ],
                style={
                    "background": "white",
                    "border": "1px solid #e2e8f0",
                    "borderRadius": "12px",
                    "padding": "16px",
                },
            ),
        ],
        style={"padding": "16px", "fontFamily": "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto"},
    )
