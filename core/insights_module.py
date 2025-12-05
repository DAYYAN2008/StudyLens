"""
Generate readable insights from the updated DataManager statistics.
"""

from typing import Dict, Any

def _correlation_insight(corr: float) -> str:
    """Return a small human-readable interpretation for a correlation value."""
    if corr is None:
        return "Correlation: Not enough data."

    if corr > 0.6:
        return "Strong positive relationship — more study hours tend to relate to higher performance."
    if corr > 0.3:
        return "Moderate positive relationship — some improvement with more study hours."
    if corr > 0.1:
        return "Weak positive relationship."
    if corr < -0.6:
        return "Strong negative relationship — unusual pattern; review study strategy or data."
    if corr < -0.3:
        return "Moderate negative relationship."
    if corr < -0.1:
        return "Weak negative relationship."
    return "No clear relationship."

def generate_insight_text(stats: Dict[str, Any]) -> str:
    """
    Converts the new DataManager.summary_statistics() dictionary
    into readable, GUI-friendly text.
    """
    if not stats or stats.get("n", 0) == 0:
        return "No data available. Add records to generate insights."

    lines = []
    lines.append("STUDY INSIGHTS")
    lines.append("-----------------------------\n")
    lines.append(f"Total Records: {stats['n']}\n")

    # Overall stats
    lines.append("=== Overall Performance ===")
    lines.append(f"Average Hours Studied: {stats['overall_avg_hours']:.2f}")
    lines.append(f"Average Percentage: {stats['overall_avg_percentage']:.2f}%\n")

    # SUBJECT-WISE INSIGHTS
    lines.append("=== Subject Insights ===")
    for key in stats:
        if key.endswith("_avg_percentage") and key.replace("_avg_percentage", ""):
            subj = key.replace("_avg_percentage", "")
            pct = stats[key]
            corr = stats.get(f"{subj}_correlation")

            lines.append(f"\n{subj}")
            lines.append(f"  Avg Percentage: {pct:.2f}%")
            if corr is None:
                lines.append("  Correlation: N/A")
            else:
                lines.append(f"  Correlation: {corr:.3f}")
                lines.append(f"  Insight: {_correlation_insight(corr)}")

    # ASSESSMENT-WISE INSIGHTS
    lines.append("\n=== Assessment Insights ===")
    for key in stats:
        if key.endswith("_avg_percentage"):
            base = key.replace("_avg_percentage", "")
            if base in ["Quiz", "Assignment", "Midterm", "Final"]:
                pct = stats[key]
                corr = stats.get(f"{base}_correlation")

                lines.append(f"\n{base}")
                lines.append(f"  Avg Percentage: {pct:.2f}%")
                if corr is None:
                    lines.append("  Correlation: N/A")
                else:
                    lines.append(f"  Correlation: {corr:.3f}")
                    lines.append(f"  Insight: {_correlation_insight(corr)}")

    return "\n".join(lines)
