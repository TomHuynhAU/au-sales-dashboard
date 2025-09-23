import pandas as pd
from src.data.transforms import filter_data, compute_kpis, top_latest

def _df():
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01","2024-02-01","2024-02-01"]),
        "state": ["NSW","NSW","QLD"],
        "category": ["Food","Food","Clothing"],
        "sales": [100,200,50],
    })

def test_filter_data_state():
    df = _df()
    out = filter_data(df, ["NSW"], None, None, None)
    assert out["state"].nunique() == 1
    assert out["state"].unique()[0] == "NSW"

def test_compute_kpis_basic():
    df = _df()
    k = compute_kpis(df)
    assert k["total"] == 350
    assert k["avg_per_month"] > 0  # có giá trị trung bình theo tháng

def test_top_latest():
    df = _df()
    top = top_latest(df, n=2)
    assert len(top) <= 2
    assert {"state","category","sales","date"} <= set(top.columns)
