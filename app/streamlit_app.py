import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import json
import pandas as pd
import streamlit as st
import plotly.express as px

from src.config import (
    PRODUCTS_PATH, SALES_PATH, SUPPLIERS_PATH, FORECASTS_PATH,
    ALERTS_PATH, SUMMARY_PATH, MONITORING_PATH
)
from src.pipeline import main as run_pipeline
from src.reporting import build_operations_report

st.set_page_config(page_title="RetailOps Intelligence", layout="wide")

def ensure_artifacts():
    required = [PRODUCTS_PATH, SALES_PATH, SUPPLIERS_PATH, FORECASTS_PATH, ALERTS_PATH, SUMMARY_PATH, MONITORING_PATH]
    missing = [p for p in required if not p.exists()]
    if missing:
        with st.spinner("Initializing retail operations data and forecasting engine..."):
            run_pipeline()
        st.rerun()

ensure_artifacts()

products = pd.read_csv(PRODUCTS_PATH)
sales = pd.read_csv(SALES_PATH)
suppliers = pd.read_csv(SUPPLIERS_PATH)
forecasts = pd.read_csv(FORECASTS_PATH)
alerts = pd.read_csv(ALERTS_PATH)
monitoring = pd.read_csv(MONITORING_PATH)
summary = json.loads(Path(SUMMARY_PATH).read_text(encoding="utf-8"))

st.markdown('''
<style>
.block-container {padding-top:1.2rem; max-width:1400px;}
.hero {
  padding:1.45rem 1.65rem;
  border-radius:28px;
  background:linear-gradient(135deg, rgba(15,23,42,0.98), rgba(234,88,12,0.86), rgba(37,99,235,0.82));
  border:1px solid rgba(255,255,255,0.10);
  box-shadow:0 24px 60px rgba(2,6,23,0.30);
  margin-bottom:1rem;
}
.hero h1 {color:white; margin:0; font-size:2.55rem; letter-spacing:-0.03em;}
.hero p {color:#e2e8f0; margin:0.25rem 0 0;}
</style>
<div class="hero">
<h1>RetailOps Intelligence</h1>
<p>AI-powered retail operations command center for inventory, sales, demand forecasting, supplier performance, and stockout-risk decisions.</p>
</div>
''', unsafe_allow_html=True)

m1,m2,m3,m4,m5 = st.columns(5)
m1.metric("Revenue", f"${summary['total_revenue']:,.0f}")
m2.metric("Profit", f"${summary['total_profit']:,.0f}")
m3.metric("Inventory Value", f"${summary['inventory_value']:,.0f}")
m4.metric("High Stockout Risk", summary["high_stockout_products"])
m5.metric("Avg Supplier Score", summary["avg_supplier_score"])

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Dashboard", "Inventory Alerts", "Demand Forecasting", "Supplier Intelligence", "Monitoring & Report"
])

with tab1:
    c1,c2 = st.columns(2)

    sales["date"] = pd.to_datetime(sales["date"])
    daily = sales.groupby("date", as_index=False).agg(revenue=("revenue","sum"), profit=("profit","sum"), quantity=("quantity_sold","sum"))

    with c1:
        fig = px.line(daily, x="date", y="revenue", title="Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        cat = sales.groupby("category", as_index=False).agg(revenue=("revenue","sum"), quantity=("quantity_sold","sum"))
        fig = px.bar(cat, x="category", y="revenue", title="Revenue by Category")
        st.plotly_chart(fig, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        fig = px.pie(products, values="inventory", names="category", title="Inventory Mix by Category")
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.scatter(
            alerts,
            x="days_remaining",
            y="forecast_30d_demand",
            color="stockout_risk",
            size="inventory",
            hover_data=["product_id","product_name","recommended_reorder_qty"],
            title="Stockout Risk Map"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### Low Stock / Reorder Queue")
    st.dataframe(
        alerts[["product_id","product_name","category","inventory","reorder_point","forecast_30d_demand","days_remaining","stockout_risk","recommended_reorder_qty","action"]].sort_values(["stockout_risk","days_remaining"]).head(30),
        use_container_width=True,
        hide_index=True
    )

    selected = st.selectbox("Inspect Product", alerts["product_id"].tolist())
    row = alerts[alerts["product_id"] == selected].iloc[0]
    a,b,c,d = st.columns(4)
    a.metric("Inventory", int(row["inventory"]))
    b.metric("Days Remaining", f"{row['days_remaining']:.1f}")
    c.metric("Risk", row["stockout_risk"])
    d.metric("Reorder Qty", int(row["recommended_reorder_qty"]))
    st.info(f"Recommended action: {row['action']}")

with tab3:
    product_id = st.selectbox("Forecast Product", products["product_id"].tolist(), key="forecast_product")
    hist = sales[sales["product_id"] == product_id].copy()
    fc = forecasts[forecasts["product_id"] == product_id].copy()

    hist["date"] = pd.to_datetime(hist["date"])
    fc["forecast_date"] = pd.to_datetime(fc["forecast_date"])

    fig = px.line(hist.tail(60), x="date", y="quantity_sold", title=f"Historical Demand — {product_id}")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(fc, x="forecast_date", y="predicted_demand", title=f"30-Day Demand Forecast — {product_id}")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(fc, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("### Supplier Performance")
    st.dataframe(suppliers.sort_values("supplier_score"), use_container_width=True, hide_index=True)

    fig = px.bar(suppliers.sort_values("supplier_score"), x="supplier_name", y="supplier_score", title="Supplier Reliability Score")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(
        suppliers,
        x="avg_lead_time_days",
        y="on_time_rate",
        size="fill_rate",
        color="supplier_score",
        hover_data=["supplier_name","defect_rate"],
        title="Supplier Risk Map"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab5:
    st.markdown("### Pipeline / Data Monitoring")
    st.dataframe(monitoring, use_container_width=True, hide_index=True)

    top_alerts = alerts.sort_values(["stockout_risk","days_remaining"]).head(12)
    report = build_operations_report(summary, top_alerts, suppliers, monitoring)

    st.download_button(
        "Download Retail Operations Report",
        data=report,
        file_name="retailops_operations_report.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.download_button(
        "Download Inventory Alerts CSV",
        data=alerts.to_csv(index=False),
        file_name="retailops_inventory_alerts.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.code(report[:2600], language="text")
