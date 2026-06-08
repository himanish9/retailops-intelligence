from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

PRODUCTS_PATH = OUTPUTS_DIR / "products.csv"
SALES_PATH = OUTPUTS_DIR / "sales.csv"
SUPPLIERS_PATH = OUTPUTS_DIR / "suppliers.csv"
FORECASTS_PATH = OUTPUTS_DIR / "forecasts.csv"
ALERTS_PATH = OUTPUTS_DIR / "alerts.csv"
SUMMARY_PATH = OUTPUTS_DIR / "summary.json"
MONITORING_PATH = OUTPUTS_DIR / "monitoring.csv"

RANDOM_STATE = 42
