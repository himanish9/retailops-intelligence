import numpy as np
import pandas as pd

CATEGORIES = ["Electronics", "Home", "Grocery", "Fashion", "Sports", "Beauty"]
SUPPLIERS = ["NorthStar Supply", "Prime Wholesale", "Urban Distributors", "MetroTrade", "BlueLine Logistics", "Evergreen Vendors"]

def generate_products(n_products=90, seed=42):
    rng = np.random.default_rng(seed)
    rows = []

    for i in range(1, n_products + 1):
        category = rng.choice(CATEGORIES)
        supplier_id = f"SUP-{rng.integers(1, len(SUPPLIERS)+1):03d}"
        unit_price = float(np.clip(rng.normal({
            "Electronics": 220, "Home": 75, "Grocery": 18, "Fashion": 55, "Sports": 85, "Beauty": 35
        }[category], 25), 5, 850))
        unit_cost = unit_price * rng.uniform(0.45, 0.72)
        inventory = int(np.clip(rng.normal(220, 90), 8, 650))
        reorder_point = int(np.clip(rng.normal(75, 28), 15, 180))
        lead_time_days = int(np.clip(rng.normal(8, 3), 2, 21))

        rows.append({
            "product_id": f"PROD-{i:04d}",
            "product_name": f"{category} Product {i}",
            "category": category,
            "supplier_id": supplier_id,
            "unit_price": round(unit_price, 2),
            "unit_cost": round(unit_cost, 2),
            "inventory": inventory,
            "reorder_point": reorder_point,
            "lead_time_days": lead_time_days,
        })

    return pd.DataFrame(rows)

def generate_suppliers(seed=42):
    rng = np.random.default_rng(seed + 1)
    rows = []

    for i, name in enumerate(SUPPLIERS, start=1):
        on_time_rate = float(np.clip(rng.normal(0.86, 0.08), 0.55, 0.99))
        avg_lead_time = float(np.clip(rng.normal(8, 3), 2, 20))
        defect_rate = float(np.clip(rng.normal(0.035, 0.025), 0.001, 0.15))
        fill_rate = float(np.clip(rng.normal(0.91, 0.06), 0.70, 0.99))
        supplier_score = (
            0.35 * on_time_rate +
            0.30 * fill_rate +
            0.20 * (1 - defect_rate) +
            0.15 * (1 - min(avg_lead_time / 20, 1))
        ) * 100

        rows.append({
            "supplier_id": f"SUP-{i:03d}",
            "supplier_name": name,
            "on_time_rate": round(on_time_rate, 4),
            "avg_lead_time_days": round(avg_lead_time, 1),
            "defect_rate": round(defect_rate, 4),
            "fill_rate": round(fill_rate, 4),
            "supplier_score": round(float(supplier_score), 1),
        })

    return pd.DataFrame(rows)

def generate_sales(products, days=180, seed=42):
    rng = np.random.default_rng(seed + 2)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days)
    rows = []

    for _, p in products.iterrows():
        base_demand = {
            "Electronics": 7, "Home": 11, "Grocery": 28, "Fashion": 14, "Sports": 10, "Beauty": 17
        }[p["category"]]

        trend = rng.normal(0.02, 0.01)
        seasonality_strength = rng.uniform(0.05, 0.25)

        for idx, date in enumerate(dates):
            weekly = 1 + seasonality_strength * np.sin(2 * np.pi * idx / 7)
            trend_factor = 1 + trend * (idx / 30)
            promo = 1.35 if rng.random() < 0.05 else 1.0
            demand = max(0, rng.normal(base_demand * weekly * trend_factor * promo, base_demand * 0.25))
            quantity = int(np.clip(round(demand), 0, 120))
            revenue = quantity * p["unit_price"]
            profit = quantity * (p["unit_price"] - p["unit_cost"])

            rows.append({
                "date": date.date().isoformat(),
                "product_id": p["product_id"],
                "category": p["category"],
                "quantity_sold": quantity,
                "revenue": round(float(revenue), 2),
                "profit": round(float(profit), 2),
                "promo_flag": int(promo > 1.0)
            })

    return pd.DataFrame(rows)
