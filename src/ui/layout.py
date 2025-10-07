from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dash_table, html
from ..data.transforms import filter_data, compute_kpis, top_latest

def _kpi_view(kpis: dict):
    """Create modern minimalist KPI cards"""
    
    def create_kpi_card(value, label, trend=None, is_currency=True):
        # Format value
        if is_currency:
            display_value = f"${value:,.0f}"
        else:
            display_value = str(value)
        
        # Trend indicator
        trend_element = None
        if trend is not None:
            trend_color = "#10b981" if trend >= 0 else "#ef4444"
            trend_icon = "↑" if trend >= 0 else "↓"
            trend_element = html.Div(
                f"{trend_icon} {abs(trend):.1f}%",
                style={
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": trend_color,
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "2px"
                }
            )
        
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(label, style={
                            "fontSize": "13px",
                            "color": "#64748b",
                            "fontWeight": "500",
                            "marginBottom": "8px",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px"
                        }),
                        html.Div(display_value, style={
                            "fontSize": "28px",
                            "fontWeight": "700",
                            "color": "#0f172a",
                            "lineHeight": "1.2",
                            "marginBottom": "4px"
                        }),
                    ],
                    style={"flex": "1"}
                ),
                trend_element if trend_element else html.Div()
            ],
            style={
                "background": "white",
                "border": "1px solid #e2e8f0",
                "borderRadius": "12px",
                "padding": "20px",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "space-between",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                "transition": "all 0.2s ease",
                "minHeight": "120px"
            }
        )
    
    mom = kpis.get("mom")
    
    return [
        create_kpi_card(kpis["total"], "Total Sales", None),
        create_kpi_card(kpis["avg_per_month"], "Avg / Month", None),
        create_kpi_card(
            f"{mom:.1f}%" if mom is not None else "—",
            "MoM Growth",
            mom,
            is_currency=False
        ) if mom is not None else create_kpi_card("—", "MoM Growth", None, is_currency=False)
    ]

def _style_chart(fig, chart_type="line"):
    """Apply minimalist styling to charts"""
    
    # Color palette
    colors = ["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#06b6d4"]
    
    if chart_type == "line":
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=6),
        )
    elif chart_type == "bar":
        fig.update_traces(
            marker=dict(
                color=colors[0],
                line=dict(width=0)
            )
        )
    
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto",
            size=12,
            color="#475569"
        ),
        margin=dict(l=20, r=20, t=20, b=40),
        hovermode="x unified",
        showlegend=chart_type == "line",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#e2e8f0",
            borderwidth=1
        ),
        colorway=colors
    )
    
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linewidth=1,
        linecolor="#e2e8f0",
        tickfont=dict(size=11)
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#f1f5f9",
        showline=False,
        tickfont=dict(size=11)
    )
    
    return fig

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
            empty_line = _style_chart(empty_line, "line")
            empty_bar = _style_chart(empty_bar, "bar")
            return empty_line, empty_bar, dash_table.DataTable(data=[]), _kpi_view(
                {"total": 0.0, "avg_per_month": 0.0, "mom": None}
            )

        # Line chart
        line_fig = px.line(df, x="date", y="sales", color="state", markers=True)
        line_fig = _style_chart(line_fig, "line")
        
        # Bar chart
        bar_data = df.groupby("category", as_index=False)["sales"].sum().sort_values("sales", ascending=False)
        bar_fig = px.bar(bar_data, x="category", y="sales")
        bar_fig = _style_chart(bar_fig, "bar")
        
        # Table
        table_df = top_latest(df, n=5)
        table = dash_table.DataTable(
            data=table_df.to_dict("records"),
            columns=[{"name": c.capitalize(), "id": c} for c in table_df.columns],
            page_size=5,
            style_table={
                "overflowX": "auto"
            },
            style_header={
                "backgroundColor": "#f8fafc",
                "fontWeight": "600",
                "fontSize": "13px",
                "color": "#475569",
                "textTransform": "uppercase",
                "letterSpacing": "0.5px",
                "border": "none",
                "borderBottom": "2px solid #e2e8f0",
                "padding": "12px 16px"
            },
            style_cell={
                "textAlign": "left",
                "padding": "12px 16px",
                "fontSize": "14px",
                "color": "#1e293b",
                "border": "none",
                "borderBottom": "1px solid #f1f5f9"
            },
            style_data={
                "backgroundColor": "white"
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#f8fafc"
                }
            ]
        )
        
        kpis = compute_kpis(df)
        return line_fig, bar_fig, table, _kpi_view(kpis)