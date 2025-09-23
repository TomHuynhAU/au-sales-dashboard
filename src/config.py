from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DEFAULT_CSV = DATA_RAW / "sales_mock.csv"          # vẫn giữ để demo nhanh
ABS_TABLE3_XLSX = DATA_RAW / "ABS_Table3_State.xlsx"  # đổi đúng tên file của bạn
