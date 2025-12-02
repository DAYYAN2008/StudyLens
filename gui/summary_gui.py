import customtkinter as ctk
from tkinter import scrolledtext

from core.stats_module import calculate_stats_from_df
from core.insights_module import generate_insight_text

def open_summary(parent, data_manager):
    win = ctk.CTkToplevel(parent)
    win.title("Summary & Insights")
    win.geometry("480x360")

    df = data_manager.get_dataframe()
    stats = calculate_stats_from_df(df)
    text = generate_insight_text(stats)

    st = scrolledtext.ScrolledText(win, wrap="word", state="normal")
    st.insert("1.0", text)
    st.configure(state="disabled")
    st.pack(fill="both", expand=True, padx=8, pady=8)

    win.transient(parent)
    win.grab_set()
