import customtkinter as ctk
from tkinter import messagebox

def open_add_record(parent, data_manager):
    # parent is main_window frame; data_manager is DataManager instance
    win = ctk.CTkToplevel(parent)
    win.title("Add Record")
    win.geometry("360x260")

    ctk.CTkLabel(win, text="Name").pack(pady=(12,4))
    name_entry = ctk.CTkEntry(win)
    name_entry.pack(fill="x", padx=12)

    ctk.CTkLabel(win, text="Study Hours").pack(pady=(8,4))
    hours_entry = ctk.CTkEntry(win)
    hours_entry.pack(fill="x", padx=12)

    ctk.CTkLabel(win, text="Marks").pack(pady=(8,4))
    marks_entry = ctk.CTkEntry(win)
    marks_entry.pack(fill="x", padx=12)

    def on_add():
        name = name_entry.get().strip()
        hours = hours_entry.get().strip()
        marks = marks_entry.get().strip()
        try:
            data_manager.add_record(name, hours, marks)
            messagebox.showinfo("Success", "Record added.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ctk.CTkButton(win, text="Add", command=on_add).pack(pady=12)
    win.transient(parent)
    win.grab_set()
