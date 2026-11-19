"""Write lakehouse/dbt/seeds/dim_date_base.csv from etl.build_dim_date.build_frame() (the same calendar as dw.dim_date, without a database)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from etl.build_dim_date import build_frame  # noqa: E402

df = build_frame()
out = ROOT / "lakehouse" / "dbt" / "seeds" / "dim_date_base.csv"
df.to_csv(out, index=False, lineterminator="\n")
print(f"{len(df)} rows -> {out.relative_to(ROOT)}")
