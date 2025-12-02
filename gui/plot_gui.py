import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.plot_module import create_scatter_figure

def open_plot(parent, data_manager):
    win = ctk.CTkToplevel(parent)
    win.title("Plot")
    win.geometry("640x480")

    df = data_manager.get_dataframe()
    fig = create_scatter_figure(df)

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    win.transient(parent)
    win.grab_set()
