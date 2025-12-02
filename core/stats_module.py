"""
Simple stats helpers that other modules (GUI) can call.
"""
from typing import Dict, Any
import pandas as pd

def calculate_stats_from_df(df: pd.DataFrame) -> Dict[str, Any]:
    if df is None or df.empty:
        return {
            "n": 0,
            "mean_hours": None,
            "mean_marks": None,
            "max_hours": None,
            "min_hours": None,
            "correlation": None,
        }
    df = df.copy()
    n = len(df)
    mean_hours = float(df["Study Hours"].mean())
    mean_marks = float(df["Marks"].mean())
    max_hours = float(df["Study Hours"].max())
    min_hours = float(df["Study Hours"].min())
    try:
        corr = float(df["Study Hours"].corr(df["Marks"]))
    except Exception:
        corr = None
    return {
        "n": n,
        "mean_hours": mean_hours,
        "mean_marks": mean_marks,
        "max_hours": max_hours,
        "min_hours": min_hours,
        "correlation": corr,
    }
