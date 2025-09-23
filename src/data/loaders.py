# src/data/loaders.py
from __future__ import annotations

import re
from typing import Optional

import pandas as pd

from ..config import DEFAULT_CSV
from .transforms import standardise_columns, validate_schema

# Map tên bang đầy đủ -> viết tắt
FULL_TO_ABBR = {
    "NEW SOUTH WALES": "NSW",
    "VICTORIA": "VIC",
    "QUEENSLAND": "QLD",
    "SOUTH AUSTRALIA": "SA",
    "WESTERN AUSTRALIA": "WA",
    "TASMANIA": "TAS",
    "NORTHERN TERRITORY": "NT",
    "AUSTRALIAN CAPITAL TERRITORY": "ACT",
}
ABBR = set(FULL_TO_ABBR.values())


# ---------------------------
# Loader cho CSV mock (giữ nguyên)
# ---------------------------
def load_sales(csv_path: str | None = None) -> pd.DataFrame:
    path = str(csv_path or DEFAULT_CSV)
    df = pd.read_csv(path, parse_dates=["date"])
    df = standardise_columns(df)
    validate_schema(df)
    return df


# ---------------------------
# Helpers parse ngày & tên bang
# ---------------------------
def _parse_abs_month_series(s: pd.Series) -> pd.Series:
    """
    Trả về Series datetime (đầu tháng) từ:
      - Excel serial numbers (float/int)
      - Strings 'YYYY-MM' / 'YYYY-MM-DD'
      - Strings 'Jan-2024' / 'January 2024'
    """
    s2 = s.copy()

    # 1) Giá trị dạng số (Excel serial)
    num = pd.to_numeric(s2, errors="coerce")
    mask_num = num.notna()
    if mask_num.any():
        s2.loc[mask_num] = pd.to_datetime(num[mask_num], unit="D", origin="1899-12-30")

    # 2) Phần còn lại dạng chuỗi
    mask_str = ~mask_num & s2.astype("string").notna()
    if mask_str.any():
        ss = s2[mask_str].astype("string").str.strip()

        # a) ISO: YYYY-MM hoặc YYYY-MM-DD
        mask_iso = ss.str.match(r"^\d{4}-\d{2}(-\d{2})?$")
        if mask_iso.any():
            s2.loc[mask_str & mask_iso] = pd.to_datetime(ss[mask_iso], errors="coerce")

        # b) 'Jan-2024' / 'January 2024'
        mask_mon = ~mask_iso
        if mask_mon.any():
            ss2 = ss[mask_mon].str.replace("-", " ", regex=False)
            parsed = pd.to_datetime(ss2, format="%b %Y", errors="coerce")
            parsed = parsed.fillna(pd.to_datetime(ss2, format="%B %Y", errors="coerce"))
            s2.loc[mask_str & mask_mon] = parsed

    out = pd.to_datetime(s2, errors="coerce")
    return out.dt.to_period("M").dt.to_timestamp()


def _extract_state(colname: str) -> Optional[str]:
    """
    Bóc tên bang từ tiêu đề series kiểu:
      'Turnover ; New South Wales ; Total (Industry) ; Original ; ...'
    hoặc có chứa NSW/VIC/... hoặc tên đầy đủ.
    """
    s = str(colname)
    u = s.upper()

    # Mẫu '... ; New South Wales ; ...'
    m = re.search(r";\s*([A-Z\s]+?)\s*;", u)
    if m:
        token = m.group(1).strip()
        if token in FULL_TO_ABBR:
            return FULL_TO_ABBR[token]
        if token in ABBR:
            return token

    # Chứa tên đầy đủ
    for full, abbr in FULL_TO_ABBR.items():
        if full in u:
            return abbr

    # Chứa viết tắt
    for abbr in ABBR:
        if re.search(rf"\b{abbr}\b", u):
            return abbr

    return None


# ---------------------------
# Loader ABS Table 3 (Time Series)
# ---------------------------
def load_abs_table3(path: str) -> pd.DataFrame:
    """
    Load ABS Table 3 (Retail turnover by state).
    Chuẩn hóa thành: [date, state, category, sales]
    """

    # 1. Đọc thử file
    xls = pd.ExcelFile(path, engine="openpyxl")
    # Thường dữ liệu nằm trong sheet "Data1" hoặc "Table 3"
    sheet = "Data1" if "Data1" in xls.sheet_names else xls.sheet_names[0]

    # 2. Xác định dòng header (ABS file có phần mô tả, header thật ở khoảng dòng 9–12)
    preview = pd.read_excel(path, sheet_name=sheet, header=None, nrows=30)
    header_row = None
    for i in range(len(preview)):
        row = [str(x).upper() for x in preview.loc[i].tolist()]
        if any("NSW" in v or "NEW SOUTH WALES" in v for v in row):
            header_row = i
            break
    if header_row is None:
        raise ValueError("Không tìm thấy header chứa tên state trong file ABS")

    # 3. Đọc lại với header đúng
    df = pd.read_excel(path, sheet_name=sheet, header=header_row, engine="openpyxl")

    # 4. Xác định cột ngày
    date_col = next((c for c in df.columns if str(c).lower().startswith(("month", "date", "period"))), df.columns[0])

    # 5. Chuẩn hóa cột ngày
    def parse_abs_month(s):
        num = pd.to_numeric(s, errors="coerce")
        mask_num = num.notna()
        out = s.copy()
        if mask_num.any():
            out.loc[mask_num] = pd.to_datetime(num[mask_num], unit="D", origin="1899-12-30")
        mask_str = ~mask_num & out.astype("string").notna()
        if mask_str.any():
            ss = out[mask_str].astype("string").str.strip()
            parsed = pd.to_datetime(ss, errors="coerce")
            out.loc[mask_str] = parsed
        return pd.to_datetime(out, errors="coerce").dt.to_period("M").dt.to_timestamp()

    df[date_col] = parse_abs_month(df[date_col])
    df = df.dropna(subset=[date_col])

    # 6. Chuyển sang long format
    value_cols = [c for c in df.columns if c != date_col]
    long = df.melt(id_vars=[date_col], value_vars=value_cols,
                   var_name="series_name", value_name="sales")
    long["sales"] = pd.to_numeric(long["sales"], errors="coerce")
    long = long.dropna(subset=["sales"])

    # 7. Map tên state
    FULL_TO_ABBR = {
        "NEW SOUTH WALES": "NSW", "VICTORIA": "VIC", "QUEENSLAND": "QLD",
        "SOUTH AUSTRALIA": "SA", "WESTERN AUSTRALIA": "WA",
        "TASMANIA": "TAS", "NORTHERN TERRITORY": "NT",
        "AUSTRALIAN CAPITAL TERRITORY": "ACT",
    }
    ABBR = set(FULL_TO_ABBR.values())

    def extract_state(s):
        u = str(s).upper()
        for full, ab in FULL_TO_ABBR.items():
            if full in u:
                return ab
        for ab in ABBR:
            if re.search(rf"\b{ab}\b", u):
                return ab
        return None

    long["state"] = long["series_name"].map(extract_state)
    long = long.dropna(subset=["state"])

    # 8. Chuẩn schema cuối cùng
    long = long.rename(columns={date_col: "date"})
    long["category"] = "Total"
    final = long[["date", "state", "category", "sales"]].sort_values(["date", "state"]).reset_index(drop=True)

    print("Loaded rows:", len(final))
    print("Date range:", final["date"].min(), "->", final["date"].max())
    print("States:", sorted(final["state"].unique()))

    return final