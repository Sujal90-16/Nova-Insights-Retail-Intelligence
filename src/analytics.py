"""Reusable data preparation and analytics for Nova Insights.

The bundled datasets are synthetic. Cleaning choices and fallback assumptions are
reported explicitly so that the pipeline remains auditable and reproducible.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

NUMERIC = ["quantity", "unit_price", "discount_rate", "revenue", "profit"]
RFM_FEATURES = ["recency_days", "frequency", "monetary_value"]


def load_sales(path):
    """Load the raw sales CSV without modifying its source file."""
    df = pd.read_csv(path)
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    return df


def clean_sales(raw):
    """Return a cleaned copy and a transparent quality audit dictionary."""
    required = {"order_date", "quantity", "unit_price", "discount_rate", "revenue", "profit", "category", "product", "region"}
    missing_columns = sorted(required.difference(raw.columns))
    if missing_columns:
        raise ValueError(f"Sales dataset is missing required columns: {', '.join(missing_columns)}")

    df = raw.copy()
    original_rows = len(df)
    duplicates = int(df.duplicated().sum())
    missing_cells = int(df.isna().sum().sum())
    before_missing = df.isna().sum()
    df = df.drop_duplicates().copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    invalid = (
        df["quantity"].isna() | (df["quantity"] <= 0)
        | df["unit_price"].isna() | (df["unit_price"] <= 0)
        | df["order_date"].isna()
    )
    invalid_count = int(invalid.sum())
    df = df.loc[~invalid].copy()

    for col in ["category", "product", "region"]:
        df[col] = df[col].fillna("Unknown").astype(str).replace({"": "Unknown"})
    df["discount_rate"] = df["discount_rate"].fillna(0).clip(0, 1)
    df["revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount_rate"])).round(2)
    df["profit"] = pd.to_numeric(df["profit"], errors="coerce")
    missing_profit = df["profit"].isna()
    missing_profit_count = int(missing_profit.sum())
    # Demonstration-only fallback, documented in the report and dashboard.
    df.loc[missing_profit, "profit"] = df.loc[missing_profit, "revenue"] * 0.20
    df["profit"] = df["profit"].round(2)

    iqr_rows = []
    for col in NUMERIC:
        source = pd.to_numeric(raw[col], errors="coerce").dropna()
        if source.empty:
            q1 = q3 = lower = upper = np.nan
            count = 0
        else:
            q1, q3 = source.quantile(0.25), source.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            count = int(((source < lower) | (source > upper)).sum())
        iqr_rows.append({"column": col, "q1": q1, "q3": q3, "lower_iqr_bound": lower, "upper_iqr_bound": upper, "outlier_count": count})

    field = pd.DataFrame({
        "column": raw.columns,
        "missing_before": before_missing.reindex(raw.columns).fillna(0).astype(int).values,
        "missing_after": df.isna().sum().reindex(raw.columns).fillna(0).astype(int).values,
    })
    field = field.merge(pd.DataFrame(iqr_rows)[["column", "outlier_count"]], on="column", how="left")
    field["outlier_count"] = field["outlier_count"].fillna(0).astype(int)
    issue_count = missing_cells + duplicates + invalid_count
    md = f"""# Data Quality Audit — Nova Insights

## Summary
- Raw rows: **{original_rows:,}**
- Exact duplicate rows flagged: **{duplicates:,}**
- Missing cells in raw file: **{missing_cells:,}**
- Invalid core transaction rows excluded: **{invalid_count:,}**
- Missing profit values filled with the demonstration fallback: **{missing_profit_count:,}**
- Clean rows: **{len(df):,}**

## Cleaning decisions
1. The raw CSV is never modified.
2. Exact duplicate rows are removed.
3. Rows with invalid dates, missing/non-positive quantity, or missing/non-positive unit price are excluded from sales analysis.
4. Missing category/product/region values become `Unknown`; missing discounts become 0 and are clipped to [0, 1].
5. Revenue is recomputed from quantity, unit price, and discount so totals reconcile.
6. Existing profit values are retained; missing profit values use a clearly marked 20% revenue fallback. This is only a synthetic demonstration assumption.
7. IQR outliers are reported for investigation rather than automatically deleted.

## Before/after field profile

{field.to_markdown(index=False)}

## Limitations
The bundled dataset is synthetic. For real data, confirm revenue, profit, returns, taxes, and discounts with the data owner before reporting results. The combined issue count is not a count of unique affected records.
"""
    return df, {
        "original_rows": original_rows,
        "clean_rows": len(df),
        "duplicates": duplicates,
        "missing_cells": missing_cells,
        "invalid_rows": invalid_count,
        "missing_profit_filled": missing_profit_count,
        "issue_count": issue_count,
        "field_profile": field,
        "markdown": md,
    }


def build_rfm(path):
    """Load and validate the customer-level RFM dataset."""
    df = pd.read_csv(path)
    required = {"customer_id", *RFM_FEATURES}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"RFM dataset is missing required columns: {', '.join(missing)}")
    for col in RFM_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if df[RFM_FEATURES].isna().any().any():
        raise ValueError("RFM data contains missing or non-numeric feature values.")
    if not np.isfinite(df[RFM_FEATURES].to_numpy(dtype=float)).all():
        raise ValueError("RFM data contains infinite values.")
    if len(df) < 3:
        raise ValueError("At least three customers are required for clustering.")
    if (df["recency_days"] < 0).any() or (df["frequency"] < 0).any() or (df["monetary_value"] < 0).any():
        raise ValueError("RFM values must not be negative.")
    return df


def run_clustering(rfm, k=4):
    """Fit scaled K-Means and return model, labels, silhouette, and scaled data."""
    features = rfm[RFM_FEATURES].astype(float)
    if features.isna().any().any() or not np.isfinite(features.to_numpy()).all():
        raise ValueError("RFM features must be complete and finite before clustering.")
    k = int(k)
    if not 2 <= k < len(features):
        raise ValueError(f"Cluster count must be between 2 and {len(features) - 1}.")
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    model = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = model.fit_predict(scaled)
    unique_labels = len(np.unique(labels))
    score = float(silhouette_score(scaled, labels)) if 1 < unique_labels < len(scaled) else float("nan")
    return model, labels, score, scaled


def evaluate_clusters(rfm, min_k=2, max_k=7):
    """Compare candidate K values using silhouette score and inertia."""
    features = rfm[RFM_FEATURES].astype(float)
    if features.isna().any().any() or not np.isfinite(features.to_numpy()).all():
        raise ValueError("RFM features must be complete and finite before cluster evaluation.")
    if len(features) < 3:
        raise ValueError("At least three customers are required to evaluate clustering.")
    if min_k < 2 or max_k < min_k:
        raise ValueError("Cluster range must start at 2 or above.")
    max_k = min(int(max_k), len(features) - 1)
    scaled = StandardScaler().fit_transform(features)
    results = []
    for k in range(int(min_k), max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(scaled)
        unique_labels = len(np.unique(labels))
        score = float(silhouette_score(scaled, labels)) if 1 < unique_labels < len(scaled) else float("nan")
        results.append({"clusters": k, "silhouette_score": score, "inertia": float(model.inertia_), "customers": len(features)})
    return pd.DataFrame(results)


def segment_profiles(rfm):
    """Summarize segment-level size and average RFM metrics."""
    if "segment" not in rfm:
        raise ValueError("A 'segment' column is required to build profiles.")
    return rfm.groupby("segment", as_index=False).agg(
        customers=("customer_id", "count"),
        recency_days=("recency_days", "mean"),
        frequency=("frequency", "mean"),
        monetary_value=("monetary_value", "mean"),
    )


def money(value):
    """Format a numeric value as Indian rupees, with safe handling for NaN."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "₹—"
    return f"₹{number:,.0f}" if np.isfinite(number) else "₹—"
