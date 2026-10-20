from pathlib import Path
from analytics import load_sales, clean_sales
ROOT=Path(__file__).resolve().parents[1]
raw=load_sales(ROOT/'data'/'sales_raw.csv')
clean,audit=clean_sales(raw)
(ROOT/'data'/'processed').mkdir(exist_ok=True)
clean.to_csv(ROOT/'data'/'processed'/'sales_clean.csv',index=False)
(ROOT/'reports'/'data_quality_audit.md').write_text(audit['markdown'],encoding='utf-8')
print(f"Raw rows: {len(raw):,}; clean rows: {len(clean):,}; exact duplicates: {audit['duplicates']:,}; invalid rows excluded: {audit['invalid_rows']:,}")
print('Wrote data/processed/sales_clean.csv and reports/data_quality_audit.md')
