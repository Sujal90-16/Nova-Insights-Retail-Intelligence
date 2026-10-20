# Reproducibility

## Local setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the app with `streamlit run app/streamlit_app.py`. Review the notebook in `notebooks/01_sales_analysis.ipynb` and the generated outputs under `reports/`.

The clustering workflow uses a fixed random seed for repeatable K-Means initialization. Library-version differences may still cause small numerical changes. Re-run reports after changing source data or analytical logic.

## Publish to GitHub

Create an empty repository named `Nova-Insights-Retail-Intelligence` under your GitHub account. In PowerShell from the project folder, run `./PUSH_TO_GITHUB.ps1` and paste the repository URL when prompted. GitHub authentication is handled by your configured Git credential manager or SSH key.
