from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_expected_project_files_exist():
    assert (ROOT / "app" / "streamlit_app.py").exists()
    assert (ROOT / "src" / "analytics.py").exists()
    assert (ROOT / "data" / "sales_raw.csv").exists()
    assert (ROOT / "README.md").exists()


def test_demo_data_files_are_nonempty():
    assert (ROOT / "data" / "sales_raw.csv").stat().st_size > 0
    assert (ROOT / "data" / "customer_rfm.csv").stat().st_size > 0
