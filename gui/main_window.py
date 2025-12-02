import os
import customtkinter as ctk

from core.data_manager import DataManager
from gui.add_record_gui import open_add_record
from gui.view_data_gui import open_view_data
from gui.summary_gui import open_summary
from gui.plot_gui import open_plot

# Appearance settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def run_app():
    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)

    dm = DataManager(csv_path=os.path.join("data", "study_data.csv"), autosave=True)
    dm.load()

    app = ctk.CTk()
    app.title("Study Lens")
    app.geometry("650x500")
    app.minsize(540, 430)

    # ============= GRID LAYOUT FOR FULL CENTERING =============
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)     # top space
    app.grid_rowconfigure(1, weight=0)     # content frame
    app.grid_rowconfigure(2, weight=1)     # bottom space

    # ---------------- MAIN CONTENT (CENTERED) ----------------
    content_frame = ctk.CTkFrame(app, fg_color="transparent")
    content_frame.grid(row=1, column=0, sticky="nsew")

    # Internal centering structure
    content_frame.grid_columnconfigure(0, weight=1)

    # ---------------- HEADER ----------------
    title = ctk.CTkLabel(
        content_frame,
        text="Study Lens",
        font=ctk.CTkFont(size=30, weight="bold")
    )
    title.grid(row=0, column=0, pady=(0, 5), sticky="n")

    subtitle = ctk.CTkLabel(
        content_frame,
        text="analyze your study hours relative to the grade you're getting",
        font=ctk.CTkFont(size=14),
        text_color=("gray60", "gray70")
    )
    subtitle.grid(row=1, column=0, pady=(0, 25), sticky="n")

    # ---------------- BUTTON SECTION ----------------
    button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    button_frame.grid(row=2, column=0, pady=5)

    BTN_WIDTH = 280
    BTN_HEIGHT = 44

    ctk.CTkButton(
        button_frame, text="Add Record",
        width=BTN_WIDTH, height=BTN_HEIGHT,
        command=lambda: open_add_record(app, dm)
    ).pack(pady=6)

    ctk.CTkButton(
        button_frame, text="View Data",
        width=BTN_WIDTH, height=BTN_HEIGHT,
        command=lambda: open_view_data(app, dm)
    ).pack(pady=6)

    ctk.CTkButton(
        button_frame, text="Summary & Insights",
        width=BTN_WIDTH, height=BTN_HEIGHT,
        command=lambda: open_summary(app, dm)
    ).pack(pady=6)

    ctk.CTkButton(
        button_frame, text="Plot Graph",
        width=BTN_WIDTH, height=BTN_HEIGHT,
        command=lambda: open_plot(app, dm)
    ).pack(pady=6)

    ctk.CTkButton(
        button_frame,
        text="Open CSV (data/study_data.csv)",
        width=BTN_WIDTH, height=BTN_HEIGHT,
        command=lambda: os.startfile(os.path.abspath("data/study_data.csv"))
    ).pack(pady=6)

    # ---------------- FOOTER ----------------
    footer = ctk.CTkLabel(
        app,
        text="Created for CS-117 — Study Hours vs Performance",
        font=ctk.CTkFont(size=11),
        text_color=("gray55", "gray65")
    )
    footer.grid(row=3, column=0, pady=10, sticky="s")

    app.mainloop()
