"""
Generate readable insights from stats.
"""
from typing import Dict, Any

def generate_insight_text(stats: Dict[str, Any]) -> str:
    if not stats or stats.get("n", 0) == 0:
        return "No data available. Add some records to generate insights."

    n = stats["n"]
    mean_h = stats["mean_hours"]
    mean_m = stats["mean_marks"]
    corr = stats["correlation"]

    s = [
        f"Records: {n}",
        f"Average study hours: {mean_h:.2f}",
        f"Average marks: {mean_m:.2f}",
        f"Max study hours: {stats['max_hours']}",
        f"Min study hours: {stats['min_hours']}",
    ]
    if corr is None:
        s.append("Correlation: Not available")
    else:
        s.append(f"Correlation (hours vs marks): {corr:.2f}")
        if corr > 0.5:
            s.append("Insight: Strong positive relationship — more hours tend to relate to higher marks.")
        elif corr > 0.2:
            s.append("Insight: Mild positive relationship.")
        elif corr < -0.5:
            s.append("Insight: Strong negative relationship — investigate data quality.")
        else:
            s.append("Insight: No clear relationship observed.")
    return "\n".join(s)
