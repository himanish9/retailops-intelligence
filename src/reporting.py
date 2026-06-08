def build_operations_report(summary, top_alerts, supplier_df, monitoring_df):
    alert_lines = "\n".join([
        f"- {r['product_id']} | {r['product_name']} | Risk: {r['stockout_risk']} | Days Remaining: {r['days_remaining']:.1f} | Reorder: {r['recommended_reorder_qty']}"
        for _, r in top_alerts.iterrows()
    ])

    supplier_lines = "\n".join([
        f"- {r['supplier_name']} | Score: {r['supplier_score']} | On-Time: {r['on_time_rate']:.1%} | Fill Rate: {r['fill_rate']:.1%}"
        for _, r in supplier_df.sort_values("supplier_score").head(5).iterrows()
    ])

    monitor_lines = "\n".join([
        f"- {r['check']}: {r['status']} ({r['detail']})"
        for _, r in monitoring_df.iterrows()
    ])

    return f"""RETAILOPS INTELLIGENCE — OPERATIONS REPORT

EXECUTIVE SUMMARY
Total Revenue: ${summary['total_revenue']:,.0f}
Total Profit: ${summary['total_profit']:,.0f}
Inventory Value: ${summary['inventory_value']:,.0f}
High Stockout Risk Products: {summary['high_stockout_products']}
Average Supplier Score: {summary['avg_supplier_score']}

TOP STOCKOUT / REORDER ALERTS
{alert_lines}

SUPPLIER RISK WATCH
{supplier_lines}

PIPELINE / DATA MONITORING
{monitor_lines}

RECOMMENDED ACTIONS
- Prioritize purchase orders for high-risk products.
- Review suppliers with low reliability scores.
- Use forecast demand to update reorder points.
- Monitor categories with declining sales momentum.

END OF REPORT
"""
