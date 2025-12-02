"""
Plotting utilities using matplotlib and return a Figure object.
"""
import matplotlib.pyplot as plt
import pandas as pd

def create_scatter_figure(df: pd.DataFrame, title: str = "Study Hours vs Marks"):
    fig, ax = plt.subplots(figsize=(6,4))
    if df is None or df.empty:
        ax.text(0.5, 0.5, "No data to plot", ha="center", va="center")
    else:
        ax.scatter(df["Study Hours"], df["Marks"])
        ax.set_xlabel("Study Hours")
        ax.set_ylabel("Marks")
        ax.set_title(title)
        ax.grid(True)
    fig.tight_layout()
    return fig
