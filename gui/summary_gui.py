import customtkinter as ctk

def open_summary(parent, data_manager):
    # --- Window Setup ---
    win = ctk.CTkToplevel(parent)
    win.title("Summary & Insights")
    win.geometry("700x500")  # Bigger, cleaner
    win.minsize(600, 450)

    # Center content when user maximizes
    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)

    # --- Fetch summary text ---
    text = data_manager.generate_summary()  # use DataManager's built-in summary

    # --- Outer frame (centering container) ---
    container = ctk.CTkFrame(win, corner_radius=12)
    container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    # Center inside frame
    container.grid_rowconfigure(1, weight=1)
    container.grid_columnconfigure(0, weight=1)

    # --- Title Label ---
    title_label = ctk.CTkLabel(
        container,
        text="📊 Study Summary & Insights",
        font=ctk.CTkFont(size=22, weight="bold"),
        anchor="center"
    )
    title_label.grid(row=0, column=0, pady=(10, 5))

    # --- Textbox for summary ---
    text_box = ctk.CTkTextbox(
        container,
        wrap="word",
        corner_radius=10,
        width=550,
        height=380,
        font=ctk.CTkFont(size=15)
    )
    text_box.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

    # Insert and lock text
    text_box.insert("1.0", text)
    text_box.configure(state="disabled")

    # --- Close button ---
    close_btn = ctk.CTkButton(
        container,
        text="Close",
        width=120,
        command=win.destroy
    )
    close_btn.grid(row=2, column=0, pady=(0, 12))

    # Modal behavior
    win.transient(parent)
    win.grab_set()
