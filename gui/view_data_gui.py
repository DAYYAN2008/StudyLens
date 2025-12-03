import customtkinter as ctk
from tkinter import ttk, messagebox


def open_view_data(parent, data_manager):

    # Main window
    win = ctk.CTkToplevel(parent)
    win.title("View Data")
    win.geometry("900x500")
    win.resizable(True, True)

    # Outer frame (white background)
    main_frame = ctk.CTkFrame(win, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Title
    title = ctk.CTkLabel(
        main_frame,
        text="Stored Study Records",
        font=ctk.CTkFont(size=22, weight="bold"),
    )
    title.pack(pady=(10, 12))

    # Grab DataFrame
    df = data_manager.get_dataframe()

    # ----------------------------
    # TREEVIEW + SCROLLBAR FRAME
    # ----------------------------

    table_frame = ctk.CTkFrame(main_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # Scrollbar
    vsb = ttk.Scrollbar(table_frame, orient="vertical")

    # Treeview styling
    style = ttk.Style()
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 12, "bold"),
        padding=6
    )
    style.configure(
        "Treeview",
        font=("Segoe UI", 11),
        rowheight=30,
        background="#ffffff",
        fieldbackground="#ffffff"
    )

    cols = list(df.columns)
    tree = ttk.Treeview(
        table_frame,
        columns=cols,
        show="headings",
        yscrollcommand=vsb.set
    )

    vsb.config(command=tree.yview)
    vsb.pack(side="right", fill="y")

    tree.pack(side="left", fill="both", expand=True)

    # Build table headers
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=140, stretch=True)

    # Insert rows
    df_reset = df.reset_index(drop=True)
    for idx, row in df_reset.iterrows():
        values = [row[c] for c in cols]
        tree.insert("", "end", iid=str(idx), values=values)

    # ----------------------------
    # DELETE + REFRESH BUTTONS
    # ----------------------------
    btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    btn_frame.pack(fill="x", pady=10)

    def delete_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Select Row", "Please select a row to delete.")
            return

        idx = int(sel[0])

        try:
            data_manager.delete_record(idx)
            tree.delete(sel[0])
            messagebox.showinfo("Deleted", "Record deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_table():
        win.destroy()
        open_view_data(parent, data_manager)

    delete_btn = ctk.CTkButton(
        btn_frame,
        text="Delete Selected",
        width=150,
        height=40,
        font=ctk.CTkFont(size=15, weight="bold"),
        command=delete_selected
    )
    delete_btn.pack(side="left", padx=10)

    refresh_btn = ctk.CTkButton(
        btn_frame,
        text="Refresh",
        width=120,
        height=40,
        font=ctk.CTkFont(size=15, weight="bold"),
        command=refresh_table
    )
    refresh_btn.pack(side="left", padx=10)

    win.transient(parent)
    win.grab_set()
