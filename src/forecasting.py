import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

def create_features(product_sales):
    df = product_sales.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["day_index"] = range(len(df))
    df["day_of_week"] = df["date"].dt.dayofweek
    df["lag_1"] = df["quantity_sold"].shift(1)
    df["lag_7"] = df["quantity_sold"].shift(7)
    df["rolling_7"] = df["quantity_sold"].rolling(7).mean()
    df = df.dropna()
    return df

def forecast_product(product_id, sales, horizon=30):
    product_sales = sales[sales["product_id"] == product_id].copy()
    featured = create_features(product_sales)

    if len(featured) < 30:
        avg = product_sales["quantity_sold"].tail(14).mean()
        return [avg] * horizon, None

    features = ["day_index", "day_of_week", "promo_flag", "lag_1", "lag_7", "rolling_7"]
    X = featured[features]
    y = featured["quantity_sold"]

    split = int(len(featured) * 0.8)
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=8)
    model.fit(X.iloc[:split], y.iloc[:split])

    preds_test = model.predict(X.iloc[split:])
    mae = mean_absolute_error(y.iloc[split:], preds_test)

    history = featured.copy()
    future_preds = []

    for step in range(1, horizon + 1):
        next_day_index = int(history["day_index"].iloc[-1] + 1)
        next_day_of_week = int((history["day_of_week"].iloc[-1] + 1) % 7)
        lag_1 = float(history["quantity_sold"].iloc[-1])
        lag_7 = float(history["quantity_sold"].iloc[-7])
        rolling_7 = float(history["quantity_sold"].tail(7).mean())

        row = pd.DataFrame([{
            "day_index": next_day_index,
            "day_of_week": next_day_of_week,
            "promo_flag": 0,
            "lag_1": lag_1,
            "lag_7": lag_7,
            "rolling_7": rolling_7
        }])
        pred = max(0, float(model.predict(row)[0]))
        future_preds.append(pred)

        new_row = history.iloc[-1:].copy()
        new_row["day_index"] = next_day_index
        new_row["day_of_week"] = next_day_of_week
        new_row["quantity_sold"] = pred
        history = pd.concat([history, new_row], ignore_index=True)

    return future_preds, mae

def build_forecasts(products, sales, horizon=30):
    rows = []
    last_date = pd.to_datetime(sales["date"]).max()

    for _, product in products.iterrows():
        preds, mae = forecast_product(product["product_id"], sales, horizon=horizon)
        for i, pred in enumerate(preds, start=1):
            rows.append({
                "product_id": product["product_id"],
                "forecast_date": (last_date + pd.Timedelta(days=i)).date().isoformat(),
                "predicted_demand": round(float(pred), 2),
                "forecast_mae": None if mae is None else round(float(mae), 2)
            })

    return pd.DataFrame(rows)
