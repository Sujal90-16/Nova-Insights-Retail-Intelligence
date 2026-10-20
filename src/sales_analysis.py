"""Reproducible sales analysis for CodeNova Task 1."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from analytics import load_sales, clean_sales
ROOT=Path(__file__).resolve().parents[1]
raw=load_sales(ROOT/'data'/'sales_raw.csv')
df,audit=clean_sales(raw)
(ROOT/'reports'/'figures').mkdir(parents=True,exist_ok=True)
revenue=df.revenue.sum(); profit=df.profit.sum(); orders=df.order_id.nunique()
summary={'rows':len(df),'orders':orders,'gross_revenue':round(revenue,2),'profit':round(profit,2),'profit_margin_pct':round(profit/revenue*100,2) if revenue else 0,'average_order_value':round(revenue/orders,2) if orders else 0,'units':int(df.quantity.sum())}
print(pd.Series(summary).to_string())
cat=df.groupby('category',as_index=False).agg(revenue=('revenue','sum'),profit=('profit','sum')).sort_values('revenue',ascending=False)
fig,ax=plt.subplots(figsize=(10,5)); cat.plot(kind='bar',x='category',y='revenue',legend=False,ax=ax); ax.set_title('Revenue by product category'); ax.set_ylabel('Revenue (₹)'); ax.set_xlabel(''); plt.xticks(rotation=20,ha='right'); plt.tight_layout(); fig.savefig(ROOT/'reports'/'figures'/'revenue_by_category.png',dpi=180); plt.close(fig)
monthly=df.assign(month=pd.to_datetime(df.order_date).dt.to_period('M').dt.to_timestamp()).groupby('month',as_index=False).revenue.sum()
fig,ax=plt.subplots(figsize=(10,5)); ax.plot(monthly.month,monthly.revenue,marker='o',linewidth=2); ax.set_title('Monthly revenue trend'); ax.set_ylabel('Revenue (₹)'); ax.set_xlabel('Month'); ax.grid(axis='y',alpha=.25); plt.tight_layout(); fig.savefig(ROOT/'reports'/'figures'/'monthly_revenue.png',dpi=180); plt.close(fig)
(ROOT/'reports'/'sales_executive_summary.md').write_text('# Sales Analysis — Executive Summary\n\n'+'\n'.join(f'- **{k.replace("_"," ").title()}:** {v}' for k,v in summary.items())+'\n\n## Category view\n\n'+cat.to_markdown(index=False)+'\n\n## Interpretation guardrails\n\nThe sample is synthetic. Findings demonstrate analytical workflow and are not claims about a real company. Margin depends on the profit definition embedded in the source data.\n',encoding='utf-8')
print('Figures and executive summary written to reports/.')
