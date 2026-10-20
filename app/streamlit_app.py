from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.analytics import (
    load_sales, clean_sales, build_rfm, run_clustering,
    evaluate_clusters, segment_profiles, money,
)

st.set_page_config(page_title="Nova Insights | Retail Intelligence", page_icon="✳", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LIME, CYAN, BG, GRID = "#C9F36A", "#70E4F5", "#0A1020", "#27354B"
PALETTE = [LIME, CYAN, "#B4A0FF", "#FF8FAD", "#F7C66A", "#7FA8FF", "#71D6B2"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--ink:#edf2ff;--muted:#9eacc3;--bg:#0a1020;--panel:#121c2d;--line:#293750;--lime:#c9f36a;--cyan:#70e4f5}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:radial-gradient(ellipse at 80% -10%,rgba(60,104,155,.22),transparent 34%),var(--bg);color:var(--ink)}
.block-container{padding-top:1.2rem;padding-bottom:2.5rem;max-width:1580px}
[data-testid="stSidebar"]{background:#0d1525;border-right:1px solid var(--line)}
[data-testid="stSidebar"] *{color:var(--ink)}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:3px 0}
.hero{position:relative;overflow:hidden;padding:31px 34px 27px;border:1px solid #30415c;border-radius:23px;background:linear-gradient(118deg,rgba(29,44,69,.98),rgba(15,25,43,.94));margin-bottom:20px;box-shadow:0 18px 55px rgba(0,0,0,.12)}
.hero:after{content:'✳';position:absolute;right:38px;top:-55px;font-size:205px;line-height:1;color:rgba(201,243,106,.075);transform:rotate(-14deg);pointer-events:none}
.eyebrow{font:500 10px 'DM Mono',monospace;color:var(--lime);letter-spacing:2.1px;text-transform:uppercase}
.hero h1{font:800 clamp(29px,3.7vw,47px) 'Manrope',sans-serif;letter-spacing:-1.8px;line-height:1.1;margin:12px 0 10px;color:#f4f7ff;max-width:850px}
.hero p{color:#adbad0;max-width:790px;font-size:14px;line-height:1.75;margin:0}
.pills{display:flex;gap:8px;flex-wrap:wrap;margin-top:19px}.pill{display:inline-block;border:1px solid #40516c;color:#cbd5e6;padding:6px 10px;border-radius:30px;font:10px 'DM Mono',monospace;letter-spacing:.3px}
.section-kicker{font:500 10px 'DM Mono',monospace;color:#8fa2bf;text-transform:uppercase;letter-spacing:1.8px;margin:23px 0 10px}
.metric{background:linear-gradient(145deg,#172337,#101827);border:1px solid #2a3a53;border-radius:17px;padding:17px 19px;min-height:119px;box-shadow:0 8px 24px rgba(0,0,0,.08)}
.metric .label{font-size:10px;color:#97a7c0;letter-spacing:1px;text-transform:uppercase}.metric .value{font:750 clamp(22px,2vw,29px) 'Manrope',sans-serif;color:#f5f7ff;margin:9px 0 4px;letter-spacing:-.8px}.metric .note{font-size:10px;color:#a1afc5;line-height:1.5}
.card{background:linear-gradient(145deg,#131e30,#101827);border:1px solid #293750;border-radius:17px;padding:19px 20px}.small-muted{font-size:12px;color:#a0aec3;line-height:1.7}.insight-card{background:linear-gradient(120deg,rgba(201,243,106,.09),rgba(112,228,245,.045));border:1px solid rgba(201,243,106,.25);border-radius:16px;padding:17px 19px}
[data-testid="stDataFrame"]{border:1px solid #293750;border-radius:12px;overflow:hidden}
.stTabs [data-baseweb="tab-list"]{gap:7px;border-bottom:1px solid #293750}.stTabs [data-baseweb="tab"]{background:#111a2a;border:1px solid #293750;border-radius:9px 9px 0 0;padding:8px 13px}
.stButton>button,.stDownloadButton>button{border-radius:10px;border:1px solid #3d506b;background:#c9f36a;color:#111827;font-weight:700;transition:transform .15s ease,filter .15s ease}.stButton>button:hover,.stDownloadButton>button:hover{filter:brightness(1.05);transform:translateY(-1px);border-color:#c9f36a;color:#111827}
[data-testid="stMetric"]{background:#121c2d;border:1px solid #293750;padding:12px 14px;border-radius:13px}
hr{border-color:#293750} footer{visibility:hidden}
@media(max-width:800px){.hero{padding:23px 20px}.hero:after{right:-35px;font-size:150px}.metric{padding:14px;min-height:105px}}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_sales():
    raw = load_sales(DATA / "sales_raw.csv")
    clean, audit = clean_sales(raw)
    return raw, clean, audit

@st.cache_data(show_spinner=False)
def get_rfm():
    return build_rfm(DATA / "customer_rfm.csv")

raw, sales, audit = get_sales()

with st.sidebar:
    st.markdown("<div class='eyebrow'>✳ NOVA / INTELLIGENCE</div>", unsafe_allow_html=True)
    st.markdown("## Workspace")
    page = st.radio("Navigate", ["Overview", "Sales explorer", "Data quality lab", "Customer segments", "About the build"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<div class='section-kicker'>DATASET CONTROLS</div>", unsafe_allow_html=True)
    categories = sorted(sales["category"].dropna().unique().tolist())
    selected_categories = st.multiselect("Product categories", categories, default=categories)
    regions = sorted(sales["region"].dropna().unique().tolist())
    selected_regions = st.multiselect("Regions", regions, default=regions)
    valid_dates = pd.to_datetime(sales["order_date"], errors="coerce").dropna()
    dmin, dmax = valid_dates.min().date(), valid_dates.max().date()
    date_range = st.date_input("Order date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)
    st.markdown("---")
    st.caption("DEMO MODE · Synthetic retail data\n\nBuilt for the CodeNova Data Science track.")

filtered = sales[sales["category"].isin(selected_categories) & sales["region"].isin(selected_regions)].copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    dates = pd.to_datetime(filtered["order_date"], errors="coerce").dt.date
    filtered = filtered[(dates >= date_range[0]) & (dates <= date_range[1])]


def metric(label, value, note):
    st.markdown(f"<div class='metric'><div class='label'>{label}</div><div class='value'>{value}</div><div class='note'>{note}</div></div>", unsafe_allow_html=True)


def chart_layout(fig, height=330):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#aebbd0", size=11),
        margin=dict(l=10, r=12, t=48, b=12), legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        title=dict(font=dict(size=14, color="#f0f4ff", family="Manrope"), x=0.02, xanchor="left"),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color="#9aa9c1"), zeroline=False)
    fig.update_yaxes(gridcolor="#243149", zerolinecolor=GRID, tickfont=dict(color="#9aa9c1"))
    return fig


def header(eyebrow, title, description):
    st.markdown(f"<div class='hero'><div class='eyebrow'>{eyebrow}</div><h1>{title}</h1><p>{description}</p><div class='pills'><span class='pill'>FILTER-AWARE ANALYTICS</span><span class='pill'>REPRODUCIBLE PIPELINE</span><span class='pill'>NO PAID APIS</span></div></div>", unsafe_allow_html=True)


def empty_state():
    st.markdown("<div class='card'><div class='eyebrow'>NO MATCHING RECORDS</div><h3 style='margin:8px 0'>Your current filters return an empty view.</h3><p class='small-muted'>Select at least one category and one region, then widen the date range to bring data back into the workspace.</p></div>", unsafe_allow_html=True)


def insight_card(title, body):
    st.markdown(f"<div class='insight-card'><div class='eyebrow'>{title}</div><div class='small-muted' style='margin-top:7px'>{body}</div></div>", unsafe_allow_html=True)

if page == "Overview":
    header("DATA PRODUCT / 01", "Numbers with a point of view.", "A practical retail intelligence workspace: understand performance, catch data quality issues, and turn customer behaviour into segments worth acting on.")
    if filtered.empty:
        empty_state()
    else:
        revenue, profit = float(filtered.revenue.sum()), float(filtered.profit.sum())
        margin = profit / revenue * 100 if revenue else 0
        orders = int(filtered.order_id.nunique()) if "order_id" in filtered else len(filtered)
        aov = revenue / orders if orders else 0
        st.markdown("<div class='section-kicker'>THE BUSINESS AT A GLANCE</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        with cols[0]: metric("Net sales revenue", money(revenue), f"{len(filtered):,} line items in view")
        with cols[1]: metric("Recorded profit", money(profit), f"{margin:.1f}% blended margin")
        with cols[2]: metric("Average order value", money(aov), f"Across {orders:,} distinct orders")
        with cols[3]: metric("Units sold", f"{int(filtered.quantity.sum()):,}", "Quantity across selected records")

        st.markdown("<div class='section-kicker'>PERFORMANCE / OVER TIME</div>", unsafe_allow_html=True)
        left, right = st.columns([1.5, 1])
        monthly = filtered.assign(month=pd.to_datetime(filtered.order_date).dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
        with left:
            fig = px.area(monthly, x="month", y="revenue", markers=True, title="Revenue rhythm", labels={"month": "Month", "revenue": "Revenue (₹)"})
            fig.update_traces(line_color=LIME, fillcolor="rgba(201,243,106,.10)", marker=dict(size=5, color=LIME), hovertemplate="%{x|%b %Y}<br>Revenue: ₹%{y:,.0f}<extra></extra>")
            st.plotly_chart(chart_layout(fig, 350), use_container_width=True)
        with right:
            cat = filtered.groupby("category", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum")).sort_values("revenue")
            fig = px.bar(cat, x="revenue", y="category", orientation="h", title="Category contribution", labels={"revenue": "Revenue (₹)", "category": ""}, color="profit", color_continuous_scale=["#26354d", CYAN, LIME], hover_data={"revenue": ":,.0f", "profit": ":,.0f"})
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(chart_layout(fig, 350), use_container_width=True)

        left, right = st.columns([1, 1])
        with left:
            st.markdown("<div class='section-kicker'>WHAT STANDS OUT</div>", unsafe_allow_html=True)
            category_summary = filtered.groupby("category", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
            if not category_summary.empty:
                leader = category_summary.loc[category_summary.revenue.idxmax()]
                category_summary["margin"] = np.where(category_summary.revenue != 0, category_summary.profit / category_summary.revenue * 100, 0)
                margin_leader = category_summary.loc[category_summary.margin.idxmax()]
                insight_card("LEADING CATEGORY", f"{leader.category} contributes the most revenue in this view ({money(leader.revenue)}). Revenue scale should be read alongside profit and margin.")
                st.write("")
                insight_card("HIGHEST BLENDED MARGIN", f"{margin_leader.category} leads on blended margin at {margin_leader.margin:.1f}%. Treat this as a descriptive signal, not proof of causation.")
        with right:
            st.markdown("<div class='section-kicker'>DATA HEALTH / QUICK SCAN</div>", unsafe_allow_html=True)
            q1, q2, q3 = st.columns(3)
            q1.metric("Raw rows", f"{len(raw):,}")
            q2.metric("Clean rows", f"{len(sales):,}")
            q3.metric("Quality flags", f"{audit['issue_count']:,}")
            st.caption("Flags combine missing cells, exact duplicates and invalid transaction rows; they are not a unique-record count.")

elif page == "Sales explorer":
    header("SALES / 02", "Find the signal in the sales.", "Explore category, region, product, and time patterns. Every visual responds to the filters in the sidebar.")
    if filtered.empty:
        empty_state()
    else:
        revenue, profit = float(filtered.revenue.sum()), float(filtered.profit.sum())
        margin = profit / revenue * 100 if revenue else 0
        a, b, c = st.columns(3)
        with a: metric("Revenue", money(revenue), "Current selection")
        with b: metric("Profit margin", f"{margin:.1f}%", "Recorded profit ÷ revenue")
        with c: metric("Average discount", f"{filtered.discount_rate.mean()*100:.1f}%", "Mean line-item discount")
        x, y = st.columns(2)
        bycat = filtered.groupby("category", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), units=("quantity", "sum"))
        with x:
            fig = px.bar(bycat, x="category", y=["revenue", "profit"], barmode="group", title="Revenue vs profit by category", labels={"value": "Amount (₹)", "category": "Category", "variable": ""}, color_discrete_sequence=[CYAN, LIME])
            st.plotly_chart(chart_layout(fig), use_container_width=True)
        with y:
            byreg = filtered.groupby("region", as_index=False).agg(revenue=("revenue", "sum")).sort_values("revenue", ascending=False)
            fig = px.pie(byreg, values="revenue", names="region", hole=.68, title="Revenue mix by region", color_discrete_sequence=PALETTE)
            fig.update_traces(textposition="outside", textinfo="percent+label", hovertemplate="%{label}<br>₹%{value:,.0f} (%{percent})<extra></extra>")
            st.plotly_chart(chart_layout(fig), use_container_width=True)
        monthly = filtered.assign(month=pd.to_datetime(filtered.order_date).dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
        fig = px.line(monthly, x="month", y=["revenue", "profit"], markers=True, title="Monthly commercial trend", labels={"value": "Amount (₹)", "month": "Month", "variable": ""}, color_discrete_sequence=[LIME, CYAN])
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)
        st.markdown("<div class='section-kicker'>PRODUCT LEADERBOARD / TOP 15 BY REVENUE</div>", unsafe_allow_html=True)
        products = filtered.groupby(["category", "product"], as_index=False).agg(units=("quantity", "sum"), revenue=("revenue", "sum"), profit=("profit", "sum")).sort_values("revenue", ascending=False)
        st.dataframe(products.head(15).style.format({"revenue": "₹{:,.2f}", "profit": "₹{:,.2f}"}), use_container_width=True, hide_index=True)
        st.download_button("Export filtered sales CSV", filtered.to_csv(index=False).encode("utf-8-sig"), "nova_filtered_sales.csv", "text/csv")

elif page == "Data quality lab":
    header("QUALITY / 03", "Trust the data, not the guesswork.", "A reproducible audit of missing values, duplicates, invalid records and outliers—with the original raw file left untouched.")
    a, b, c, d = st.columns(4)
    with a: metric("Raw records", f"{len(raw):,}", "Original input")
    with b: metric("Clean records", f"{len(sales):,}", "After documented rules")
    with c: metric("Duplicate rows", f"{audit['duplicates']:,}", "Exact duplicates flagged")
    with d: metric("Missing cells", f"{audit['missing_cells']:,}", "Before treatment")
    left, right = st.columns(2)
    with left:
        miss = raw.isna().sum().rename_axis("column").reset_index(name="missing").query("missing > 0").sort_values("missing")
        if miss.empty:
            st.info("No missing cells were detected in the raw dataset.")
        else:
            fig = px.bar(miss, x="missing", y="column", orientation="h", title="Missing values by field", labels={"missing": "Missing cells", "column": ""}, color="missing", color_continuous_scale=["#26354d", CYAN, LIME])
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(chart_layout(fig), use_container_width=True)
    with right:
        compare = pd.DataFrame({"Stage": ["Raw", "Clean"], "Rows": [len(raw), len(sales)], "Missing cells": [int(raw.isna().sum().sum()), int(sales.isna().sum().sum())]})
        fig = px.bar(compare, x="Stage", y=["Rows", "Missing cells"], barmode="group", title="Before / after profile", color_discrete_sequence=[CYAN, LIME])
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    st.markdown("<div class='section-kicker'>RULES APPLIED / WHY</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><b>01 · Exact duplicate removal</b><p class='small-muted'>Repeated rows can inflate revenue and unit totals. One copy is retained.</p><hr><b>02 · Type and domain checks</b><p class='small-muted'>Dates are parsed consistently; non-positive quantities/prices and invalid dates are excluded from commercial analysis.</p><hr><b>03 · Missing-value treatment</b><p class='small-muted'>Categorical gaps become 'Unknown'; missing discount values become 0 and are clipped to [0, 1]. This is a transparent assumption, not a universal rule.</p><hr><b>04 · Outlier review</b><p class='small-muted'>IQR outliers are flagged for investigation rather than automatically deleted, since extreme values may be genuine transactions.</p><hr><b>05 · Profit fallback</b><p class='small-muted'>Missing profit values use a 20% revenue fallback only for this synthetic demonstration. Validate margin definitions before applying this to real data.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>FIELD-LEVEL AUDIT</div>", unsafe_allow_html=True)
    st.dataframe(audit["field_profile"], use_container_width=True, hide_index=True)
    st.download_button("Download cleaned dataset", sales.to_csv(index=False).encode("utf-8-sig"), "nova_sales_clean.csv", "text/csv")
    st.download_button("Download audit report (Markdown)", audit["markdown"].encode("utf-8"), "data_quality_audit.md", "text/markdown")

elif page == "Customer segments":
    header("CUSTOMERS / 04", "Different customers. Different stories.", "Build behaviour-led customer groups with scaled RFM features, compare candidate cluster counts, and inspect segment-level actions.")
    try:
        base_rfm = get_rfm()
        diagnostics = evaluate_clusters(base_rfm, 2, min(7, len(base_rfm) - 1))
        best_row = diagnostics.loc[diagnostics.silhouette_score.idxmax()] if diagnostics.silhouette_score.notna().any() else None
        control_left, control_right = st.columns([1, 2])
        with control_left:
            default_k = int(best_row.clusters) if best_row is not None else 4
            k = st.slider("Number of customer segments", 2, min(7, len(base_rfm)-1), default_k, help="Choose a candidate k and compare it with the diagnostics below.")
        with control_right:
            if best_row is not None:
                st.markdown(f"<div class='insight-card' style='margin-top:26px'><div class='eyebrow'>BEST SILHOUETTE IN TESTED RANGE</div><div class='small-muted' style='margin-top:6px'>k = <b>{int(best_row.clusters)}</b> · score <b>{best_row.silhouette_score:.3f}</b>. This is a useful comparison signal, not an automatic business decision.</div></div>", unsafe_allow_html=True)
        model, labels, score, scaled = run_clustering(base_rfm, k)
        rfm = base_rfm.copy()
        rfm["segment"] = labels.astype(str)
        a, b, c = st.columns(3)
        with a: metric("Customers", f"{len(rfm):,}", "Synthetic RFM sample")
        with b: metric("Segments", str(k), "K-Means · standardized features")
        with c: metric("Silhouette score", f"{score:.3f}", "Higher is generally better; context matters")
        st.markdown("<div class='section-kicker'>CLUSTER DIAGNOSTICS</div>", unsafe_allow_html=True)
        x, y = st.columns(2)
        with x:
            fig = px.line(diagnostics, x="clusters", y="inertia", markers=True, title="Elbow method · inertia", labels={"clusters": "Number of clusters (k)", "inertia": "Inertia"})
            fig.add_vline(x=k, line_dash="dot", line_color=LIME, annotation_text=f"Selected k={k}", annotation_position="top right")
            fig.update_traces(line_color=CYAN, marker=dict(size=8))
            st.plotly_chart(chart_layout(fig, 300), use_container_width=True)
        with y:
            fig = px.line(diagnostics, x="clusters", y="silhouette_score", markers=True, title="Silhouette · separation and cohesion", labels={"clusters": "Number of clusters (k)", "silhouette_score": "Silhouette score"})
            fig.add_vline(x=k, line_dash="dot", line_color=LIME, annotation_text=f"Selected k={k}", annotation_position="top right")
            fig.update_traces(line_color=LIME, marker=dict(size=8))
            st.plotly_chart(chart_layout(fig, 300), use_container_width=True)
        st.dataframe(diagnostics.style.format({"silhouette_score": "{:.3f}", "inertia": "{:,.1f}"}), use_container_width=True, hide_index=True)
        left, right = st.columns([1.2, 1])
        with left:
            fig = px.scatter(rfm, x="frequency", y="monetary_value", color="segment", size="monetary_value", hover_data=["customer_id", "recency_days"], title="Customer map · frequency × spend", color_discrete_sequence=PALETTE, labels={"frequency": "Purchase frequency", "monetary_value": "Monetary value (₹)", "segment": "Segment"})
            st.plotly_chart(chart_layout(fig, 380), use_container_width=True)
        with right:
            summary = segment_profiles(rfm)
            fig = px.bar(summary, x="segment", y="customers", title="Segment size", labels={"segment": "Segment", "customers": "Customers"}, color="segment", color_discrete_sequence=PALETTE)
            fig.update_layout(showlegend=False)
            st.plotly_chart(chart_layout(fig, 380), use_container_width=True)
        st.markdown("<div class='section-kicker'>SEGMENT PROFILES & POSSIBLE ACTIONS</div>", unsafe_allow_html=True)
        st.dataframe(summary.style.format({"recency_days": "{:.0f} days", "frequency": "{:.1f}", "monetary_value": "₹{:,.2f}"}), use_container_width=True, hide_index=True)
        median_spend = summary.monetary_value.median()
        for _, row in summary.iterrows():
            if row.recency_days < summary.recency_days.median() and row.frequency >= summary.frequency.median():
                persona, action = "Engaged regulars", "Test loyalty rewards, early access, and referral prompts; measure repeat-purchase lift."
            elif row.monetary_value >= median_spend:
                persona, action = "High-value opportunity", "Explore premium bundles and personalisation while protecting margin."
            elif row.recency_days > summary.recency_days.median():
                persona, action = "Re-engagement candidates", "Test a measured win-back campaign and compare against a holdout group."
            else:
                persona, action = "Growth candidates", "Try relevant cross-sells and helpful onboarding to build repeat behaviour."
            st.markdown(f"<div class='card' style='margin:8px 0'><span class='eyebrow'>SEGMENT {row.segment}</span><h4 style='margin:8px 0'>{persona}</h4><p class='small-muted'>{int(row.customers)} customers · average recency {row.recency_days:.0f} days · average frequency {row.frequency:.1f} · average spend {money(row.monetary_value)}</p><p>{action}</p></div>", unsafe_allow_html=True)
        st.caption("Segment names are heuristic interpretations of synthetic data, not ground truth. K-Means segment IDs are arbitrary and can change when k changes. Silhouette score and elbow diagnostics support judgement; they do not replace business validation.")
        st.download_button("Export segmented customers", rfm.to_csv(index=False).encode("utf-8-sig"), "nova_customer_segments.csv", "text/csv")
        st.download_button("Export cluster diagnostics", diagnostics.to_csv(index=False).encode("utf-8-sig"), "nova_cluster_diagnostics.csv", "text/csv")
    except (ValueError, KeyError) as exc:
        st.error(f"Customer segmentation could not be calculated: {exc}")

else:
    header("PROJECT NOTES / 05", "Built to be inspected, not just admired.", "Nova Insights is a portfolio-ready learning project concept built around transparent analysis, reproducibility, and decisions that can be explained.")
    st.markdown("<div class='card'><div class='eyebrow'>THE DESIGN INTENT</div><h3>Less dashboard wallpaper. More useful signal.</h3><p class='small-muted'>An editorial dark interface, a restrained lime/cyan palette, custom metric cards, interactive charts, and a data-quality view that shows its work. The visual system is consistent across all four internship tasks.</p><hr><div class='eyebrow'>STACK</div><p>Python · Pandas · NumPy · Streamlit · Plotly · scikit-learn</p><div class='eyebrow'>TASK COVERAGE</div><p>01 Sales analysis · 02 Data cleaning audit · 03 Interactive analytics dashboard · 04 RFM customer segmentation</p><div class='eyebrow'>DATA NOTE</div><p>Bundled datasets are synthetic and intended for demonstration and reproducibility. Findings are not claims about a real company.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>REPRODUCIBILITY CHECKLIST</div>", unsafe_allow_html=True)
    st.write("- Raw input is kept separate from cleaned output.\n- Cleaning rules are implemented in a reusable Python module.\n- Filters drive sales metrics and charts consistently.\n- Customer features are standardized before K-Means.\n- Candidate cluster counts are compared with inertia and silhouette scores.\n- No paid API, token, or external database is required.")

st.markdown("<hr><div style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:#71819b;font:10px DM Mono,monospace'><span>NOVA INSIGHTS / CODENOVA DATA SCIENCE</span><span>BUILT FOR CLARITY · NOT JUST PRETTY CHARTS</span></div>", unsafe_allow_html=True)
