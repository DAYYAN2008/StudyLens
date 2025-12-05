import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.plot_module import create_scatter_figure

def open_plot(parent, data_manager):

    # ---------- Window Setup ----------
    win = ctk.CTkToplevel(parent)
    win.title("Study Performance Plot")
    win.geometry("800x600")          # Larger & proportional
    win.minsize(650, 500)

    # Allow flexible resizing
    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)

    # ---------- Container Frame ----------
    container = ctk.CTkFrame(win, corner_radius=12)
    container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    # Internal layout control
    container.grid_rowconfigure(1, weight=1)
    container.grid_columnconfigure(0, weight=1)

    # ---------- Title Label ----------
    title_label = ctk.CTkLabel(
        container,
        text="📈 Study Hours vs Percentage Plot",
        font=ctk.CTkFont(size=22, weight="bold")
    )
    title_label.grid(row=0, column=0, pady=(10, 5))

    # ---------- Create Figure ----------
    df = data_manager.get_dataframe()
    fig = create_scatter_figure(df)

    # ---------- Canvas Area (Matplotlib Embed) ----------
    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas.draw()

    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    # ---------- Close Button ----------
    close_button = ctk.CTkButton(
        container,
        text="Close",
        width=120,
        command=win.destroy
    )
    close_button.grid(row=2, column=0, pady=(0, 12))

    # Make modal
    win.transient(parent)
    win.grab_set()
