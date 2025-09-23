from __future__ import annotations
from dash import Dash
from .config import DEFAULT_CSV, ABS_TABLE3_XLSX
from .data.loaders import load_sales, load_abs_table3
from .ui.layout import serve_layout
from .ui.callbacks import register_callbacks
from .logging_conf import logger

def create_app(csv_path: str | None = None) -> Dash:
    # df = load_sales(csv_path or str(DEFAULT_CSV))
    df = load_abs_table3(str(ABS_TABLE3_XLSX)) 
    print("Loaded rows:", len(df))
    print("Columns:", df.columns.tolist()[:10])
    print("Date range:", df["date"].min(), "->", df["date"].max())
    print("States:", sorted(df["state"].unique())[:8])
    states = sorted(df["state"].unique())
    categories = sorted(df["category"].unique())
    min_date, max_date = df["date"].min(), df["date"].max()

    app = Dash(__name__)
    app.layout = serve_layout(states, categories, min_date, max_date)
    register_callbacks(app, df)
    return app


app = create_app()
server = app.server

if __name__ == "__main__":
    logger.info("Running on http://127.0.0.1:8050")
    app.run_server(debug=True, host="0.0.0.0", port=8050)
