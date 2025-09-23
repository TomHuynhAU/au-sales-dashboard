from src.data.loaders import load_sales

def test_load_sales_smoke(tmp_path):
    # tạo 1 CSV tạm thời để kiểm tra schema & đọc được
    p = tmp_path / "sales.csv"
    p.write_text("date,state,category,sales\n2024-01-01,NSW,Food,10\n")
    df = load_sales(str(p))
    assert set(df.columns) == {"date", "state", "category", "sales"}
    assert len(df) == 1
    # kiểu date phải là datetime64
    assert str(df["date"].dtype).startswith("datetime64")
