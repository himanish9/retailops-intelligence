from src.config import (
    OUTPUTS_DIR, PRODUCTS_PATH, SALES_PATH, SUPPLIERS_PATH,
    FORECASTS_PATH, ALERTS_PATH, SUMMARY_PATH, MONITORING_PATH
)
from src.utils import ensure_dirs, save_json
from src.data_generation import generate_products, generate_sales, generate_suppliers
from src.forecasting import build_forecasts
from src.intelligence import build_inventory_alerts, pipeline_monitoring

def main():
    ensure_dirs([OUTPUTS_DIR])

    products = generate_products()
    suppliers = generate_suppliers()
    sales = generate_sales(products)
    forecasts = build_forecasts(products, sales)
    alerts = build_inventory_alerts(products, forecasts, suppliers)
    monitoring = pipeline_monitoring(products, sales, forecasts, alerts)

    products.to_csv(PRODUCTS_PATH, index=False)
    suppliers.to_csv(SUPPLIERS_PATH, index=False)
    sales.to_csv(SALES_PATH, index=False)
    forecasts.to_csv(FORECASTS_PATH, index=False)
    alerts.to_csv(ALERTS_PATH, index=False)
    monitoring.to_csv(MONITORING_PATH, index=False)

    summary = {
        "total_revenue": float(sales["revenue"].sum()),
        "total_profit": float(sales["profit"].sum()),
        "inventory_value": float((products["inventory"] * products["unit_cost"]).sum()),
        "high_stockout_products": int((alerts["stockout_risk"] == "High").sum()),
        "medium_stockout_products": int((alerts["stockout_risk"] == "Medium").sum()),
        "avg_supplier_score": round(float(suppliers["supplier_score"].mean()), 1),
        "total_products": int(len(products)),
        "total_sales_rows": int(len(sales)),
    }
    save_json(SUMMARY_PATH, summary)

if __name__ == "__main__":
    main()
