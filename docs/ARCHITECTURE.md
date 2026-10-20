# Architecture

- `app/streamlit_app.py`: Streamlit presentation layer and interactive exploration.
- `src/analytics.py`: loading, cleaning, data-quality profiling, RFM clustering utilities, and formatting helpers.
- `src/sales_analysis.py`: sales-oriented analytical calculations and figures.
- `src/customer_segmentation.py`: clustering workflow and segment summaries.
- `notebooks/`: notebook-based analysis for review and reproducibility.
- `data/`: raw demonstration inputs and processed outputs.
- `reports/`: generated audit, diagnostic tables, summaries, and figures.

Keep presentation logic separate from reusable transformations where practical. Raw inputs should remain unchanged; generated files should be reproducible from the documented workflow.
