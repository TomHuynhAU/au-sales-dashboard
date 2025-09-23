from __future__ import annotations
import pandas as pd

REQUIRED_COLS = {"date", "state", "category", "sales"}

def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [c.strip().lower() for c in out.columns]
    return out

def validate_schema(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

def filter_data(df: pd.DataFrame, states, categories, start, end) -> pd.DataFrame:
    out = df.copy()
    if states: out = out[out["state"].isin(states)]
    if categories: out = out[out["category"].isin(categories)]
    if start is not None: out = out[out["date"] >= start]
    if end is not None: out = out[out["date"] <= end]
    return out

def compute_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total": 0.0, "avg_per_month": 0.0, "mom": None}
    total = float(df["sales"].sum())

    m = df.copy()
    m["month"] = m["date"].dt.to_period("M").dt.to_timestamp()
    by_month = m.groupby("month", as_index=False)["sales"].sum().sort_values("month")
    avg = float(by_month["sales"].mean()) if not by_month.empty else 0.0

    if len(by_month) >= 2:
        last, prev = by_month.iloc[-1]["sales"], by_month.iloc[-2]["sales"]
        mom = None if prev == 0 else (last - prev) / prev * 100.0
    else:
        mom = None
    return {"total": total, "avg_per_month": avg, "mom": mom}

def top_latest(df: pd.DataFrame, n=5) -> pd.DataFrame:
    latest = df.sort_values("date").groupby(["state", "category"]).tail(1)
    return latest.sort_values("sales", ascending=False).head(n)[["state", "category", "sales", "date"]]
