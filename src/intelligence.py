import pandas as pd
import numpy as np

def build_inventory_alerts(products, forecasts, suppliers):
    forecast_30 = forecasts.groupby("product_id")["predicted_demand"].sum().reset_index()
    forecast_30.columns = ["product_id", "forecast_30d_demand"]

    df = products.merge(forecast_30, on="product_id", how="left")
    df = df.merge(suppliers, on="supplier_id", how="left")

    df["avg_daily_forecast"] = df["forecast_30d_demand"] / 30
    df["days_remaining"] = df["inventory"] / df["avg_daily_forecast"].replace(0, np.nan)
    df["days_remaining"] = df["days_remaining"].replace([np.inf, -np.inf], np.nan).fillna(999)

    df["recommended_reorder_qty"] = (
        (df["avg_daily_forecast"] * (df["lead_time_days"] + 14)) - df["inventory"]
    ).clip(lower=0).round(0).astype(int)

    def risk(row):
        if row["inventory"] <= row["reorder_point"] or row["days_remaining"] <= row["lead_time_days"]:
            return "High"
        if row["days_remaining"] <= row["lead_time_days"] + 10:
            return "Medium"
        return "Low"

    df["stockout_risk"] = df.apply(risk, axis=1)

    df["action"] = df.apply(
        lambda r: "Reorder Immediately" if r["stockout_risk"] == "High" else (
            "Monitor / Prepare PO" if r["stockout_risk"] == "Medium" else "No Action"
        ),
        axis=1
    )

    return df.sort_values(["stockout_risk", "days_remaining"], ascending=[True, True])

def pipeline_monitoring(products, sales, forecasts, alerts):
    checks = []
    checks.append({
        "check": "Products Loaded",
        "status": "Healthy" if len(products) > 0 else "Alert",
        "detail": f"{len(products)} products"
    })
    checks.append({
        "check": "Sales Rows",
        "status": "Healthy" if len(sales) > 1000 else "Alert",
        "detail": f"{len(sales)} rows"
    })
    checks.append({
        "check": "Forecast Coverage",
        "status": "Healthy" if forecasts["product_id"].nunique() == products["product_id"].nunique() else "Alert",
        "detail": f"{forecasts['product_id'].nunique()} products forecasted"
    })
    checks.append({
        "check": "High Stockout Alerts",
        "status": "Review" if (alerts["stockout_risk"] == "High").sum() > 0 else "Healthy",
        "detail": f"{int((alerts['stockout_risk'] == 'High').sum())} high-risk products"
    })
    return pd.DataFrame(checks)
