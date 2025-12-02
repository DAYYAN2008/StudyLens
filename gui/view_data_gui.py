import customtkinter as ctk
from tkinter import ttk, messagebox

def open_view_data(parent, data_manager):
    win = ctk.CTkToplevel(parent)
    win.title("View Data")
    win.geometry("700x400")

    df = data_manager.get_dataframe()

    # Treeview
    cols = list(df.columns)
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120, anchor="center")
    vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    # insert rows
    for idx, row in df.reset_index().iterrows():
        # keep index hidden but retrievable
        values = [row[c] for c in cols]
        tree.insert("", "end", iid=str(idx), values=values)

    # Functions for update/delete
    def delete_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a row to delete.")
            return
        idx = int(sel[0])
        try:
            data_manager.delete_record(idx)
            tree.delete(sel[0])
            messagebox.showinfo("Deleted", "Record deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_frame = ctk.CTkFrame(win)
    btn_frame.pack(side="bottom", fill="x", pady=8)
    ctk.CTkButton(btn_frame, text="Delete Selected", command=delete_selected).pack(side="left", padx=8)
    ctk.CTkButton(btn_frame, text="Refresh", command=lambda: win.destroy() or open_view_data(parent, data_manager)).pack(side="left", padx=8)

    win.transient(parent)
    win.grab_set()
