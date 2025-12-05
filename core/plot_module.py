"""
Plotting utilities using matplotlib — updated for DataManager structure.
Plots Study Hours vs Percentage Score.
"""
import matplotlib.pyplot as plt
import pandas as pd

def create_scatter_figure(df: pd.DataFrame,
                          title: str = "Study Hours vs Percentage Score"):
    """
    Create a scatter plot of Hours vs Percentage using the new data schema:
    hours, marks, total_marks → percentage = marks/total * 100
    Returns a Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    if df is None or df.empty:
        ax.text(0.5, 0.5, "No data to plot",
                ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        return fig

    # Clean numeric values
    df = df.copy()
    df["hours"] = pd.to_numeric(df["hours"], errors="coerce")
    df["marks"] = pd.to_numeric(df["marks"], errors="coerce")
    df["total_marks"] = pd.to_numeric(df["total_marks"], errors="coerce")

    # Calculate percentage safely
    df["percentage"] = (df["marks"] / df["total_marks"]) * 100
    df = df.dropna(subset=["hours", "percentage"])

    if df.empty:
        ax.text(0.5, 0.5, "Insufficient numeric data to plot",
                ha="center", va="center", fontsize=14)
        ax.set_axis_off()
        return fig

    # Plot
    ax.scatter(df["hours"], df["percentage"], s=50, alpha=0.75)

    ax.set_xlabel("Study Hours", fontsize=12)
    ax.set_ylabel("Percentage Score (%)", fontsize=12)
    ax.set_title(title, fontsize=14, weight="bold")

    ax.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()
    return fig
