# Nova Insights — Retail Intelligence Studio

> A custom-designed, reproducible data-science portfolio project for the CodeNova Data Science Internship (Batch 01).

Nova Insights brings all four assignment areas into one coherent workspace: sales analysis, a data-quality audit, an interactive analytics dashboard, and customer segmentation using RFM-style features and K-Means. It runs locally with free Python tooling and bundled synthetic data.

## Product highlights

- **Editorial dashboard UI:** deep navy surfaces, restrained lime/cyan accents, custom typography, responsive metric cards, and interactive Plotly visuals.
- **Business performance:** revenue, recorded profit, blended margin, average order value, unit volume, category contribution, monthly trends, regional mix, and product leaderboard.
- **Global filters:** category, region, and order-date controls drive the sales metrics and charts. Empty selections show a friendly recovery message.
- **Transparent data quality:** missing cells, duplicates, invalid transaction rows, IQR outlier flags, before/after profiles, cleaning decisions, and downloadable audit artifacts.
- **Cluster diagnostics:** compare K-Means `k=2..7` using inertia (Elbow Method) and silhouette score; the UI defaults to the highest silhouette among tested candidates but lets the user explore alternatives.
- **Actionable customer profiles:** segment size and RFM averages, customer scatter plot, heuristic personas, and CSV exports.
- **Reproducibility:** scripts regenerate cleaned data, reports, charts, cluster diagnostics, and segment assignments. No paid APIs, tokens, or external database are required.

## Project structure

```text
codenova_nova_insights/
├── app/
│   └── streamlit_app.py           # Multi-page interactive dashboard
├── data/
│   ├── sales_raw.csv              # Synthetic transactions with quality issues
│   ├── customer_rfm.csv           # Synthetic customer RFM sample
│   ├── processed/                 # Generated cleaned sales CSV
│   └── processed_customer_segments.csv
├── notebooks/
│   └── 01_sales_analysis.ipynb    # Exploratory notebook
├── reports/
│   ├── data_quality_audit.md
│   ├── sales_executive_summary.md
│   ├── cluster_diagnostics.csv
│   ├── segment_profiles.csv
│   └── figures/                   # Generated chart exports
├── src/
│   ├── analytics.py               # Shared data validation, cleaning, and clustering
│   ├── run_cleaning.py            # CodeNova Task 2 pipeline
│   ├── sales_analysis.py          # CodeNova Task 1 pipeline
│   └── customer_segmentation.py   # CodeNova Task 4 pipeline + diagnostics
├── requirements.txt
└── README.md
```

## Run locally — Windows PowerShell

Open PowerShell in the project root (the folder containing `requirements.txt`):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Open the local URL Streamlit prints, usually `http://localhost:8501`. Keep the terminal running while using the dashboard. If PowerShell blocks environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again.

## Regenerate the analysis deliverables

Run from the project root:

```powershell
python src/run_cleaning.py
python src/sales_analysis.py
python src/customer_segmentation.py
```

The scripts write outputs to `data/processed/`, `data/processed_customer_segments.csv`, and `reports/`. The raw sales CSV is never overwritten.

## CodeNova task coverage

### Task 1 — Sales Data Analysis
- Revenue, recorded profit, margin, AOV, units, category performance, and monthly trends.
- High-resolution charts and a Markdown executive summary.
- Interpretation guardrails for synthetic data and profit definitions.

### Task 2 — Data Cleaning Report
- Missing-value and exact-duplicate scan.
- Invalid date/quantity/price checks and documented treatment choices.
- Before/after field profile and IQR outlier flags.
- Clean output is separate from the raw file; every transformation can be rerun.

### Task 3 — Interactive Analytics Dashboard
- Category, region, and date filters.
- Reactive KPI cards and Plotly charts.
- Regional revenue mix, product leaderboard, filtered CSV export, and graceful empty-state messaging.

### Task 4 — Customer Segmentation Study
- RFM-style recency, frequency, and monetary features.
- StandardScaler before distance-based K-Means.
- Elbow/inertia and silhouette comparison for candidate cluster counts.
- Cluster profiles, customer map, heuristic personas, and exportable assignments.

## Data dictionary

### `sales_raw.csv`
`order_id`, `order_date`, `customer_id`, `category`, `product`, `region`, `quantity`, `unit_price`, `discount_rate`, `revenue`, `profit`.

The sample intentionally includes some missing values, duplicate rows, zero quantities, and non-positive prices so the audit has issues to detect. Do not edit it manually; rerun the pipeline instead.

### `customer_rfm.csv`
`customer_id`, `recency_days`, `frequency`, `monetary_value`. This is a synthetic RFM-like sample for learning and demonstration.

## Methodology and limitations

- Sales revenue is recomputed as `quantity × unit_price × (1 − discount_rate)` after transaction validation.
- Missing discounts are treated as 0 for this demonstration; missing category/product/region values become `Unknown`. These assumptions must be reviewed for real data.
- Existing profit values are retained. Missing profit values use a 20% revenue fallback only to keep this synthetic example runnable; this is not a verified profit calculation.
- IQR outliers are flagged for investigation rather than automatically deleted. Unusual values can be legitimate transactions.
- K-Means features are standardized because distance calculations are scale-sensitive. Silhouette and inertia are diagnostics, not guarantees of the best business segmentation. Cluster IDs are arbitrary.
- The highest silhouette among tested `k` values is selected as a transparent default; inspect the elbow curve and segment usefulness before making a final choice.
- All bundled records are synthetic. Do not present the metrics or personas as real company or customer findings.

## Before submission

- Run the app locally and test every navigation item, filter, chart, and download.
- Capture genuine screenshots from your own running app and add them here.
- Push the source to a public GitHub repository and verify repository visibility and README setup instructions.
- If you deploy, use an available free hosting option and test the public URL in a private browser window.
- Be prepared to explain cleaning assumptions, metric definitions, and why the cluster diagnostics are useful.
- Never commit API keys, passwords, personal data, or secrets.

## Tech stack

Python · Pandas · NumPy · Streamlit · Plotly · scikit-learn · Matplotlib · Jupyter

## License

Educational portfolio project. Add an explicit license before accepting external contributions.
