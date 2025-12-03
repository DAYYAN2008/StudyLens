import customtkinter as ctk
from tkinter import messagebox

ALLOWED_SUBJECTS = [
    "Calculus and Analytic Geometry",
    "Functional English",
    "Applications of ICT",
    "Applied Physics",
    "Introduction to Aerospace Engineering",
    "Islamic Studies",
]

ALLOWED_ASSESSMENTS = ["Quiz", "Assignment", "Midterm", "Final"]


def open_add_record(parent, data_manager):
    """
    Scrollable Add Record window with fixes:
    - embedded frame width tracks canvas width (no white strip)
    - UI building deferred via `after` to make window appear faster
    - mousewheel works across platforms
    """

    # -------------------------
    # Create top-level and basic layout
    # -------------------------
    win = ctk.CTkToplevel(parent)
    win.title("Add Study Record")
    win.geometry("520x580")
    win.minsize(420, 300)
    win.resizable(True, True)

    # Container for canvas + scrollbar
    container = ctk.CTkFrame(win)
    container.pack(fill="both", expand=True)

    # -------------------------
    # Canvas + Scrollbar + Scrollable Frame
    # -------------------------
    canvas = ctk.CTkCanvas(container, highlightthickness=0)
    vscroll = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)

    # Create the inner frame that will hold all widgets
    scroll_frame = ctk.CTkFrame(canvas)

    # Create a window on the canvas for the scroll_frame and keep its id
    inner_window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    # Pack canvas and scrollbar (canvas first so scrollbar hugs right edge)
    canvas.pack(side="left", fill="both", expand=True)
    vscroll.pack(side="right", fill="y")

    # Configure canvas scrolling
    canvas.configure(yscrollcommand=vscroll.set)

    # Update the scrollregion when the size of the inner frame changes
    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scroll_frame.bind("<Configure>", _on_frame_configure)

    # Make the inner window width follow the canvas width (avoids right-side white strip)
    def _on_canvas_configure(event):
        # set the embedded window width to canvas width (so no horizontal gap remains)
        canvas.itemconfig(inner_window_id, width=event.width)

    canvas.bind("<Configure>", _on_canvas_configure)

    # -------------------------
    # Mousewheel / touchpad scrolling across platforms
    # -------------------------
    def _on_mousewheel(event):
        # Windows / macOS / Linux handling
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")

    # Bind to multiple events to cover platforms
    canvas.bind_all("<MouseWheel>", _on_mousewheel)      # Windows / macOS
    canvas.bind_all("<Button-4>", _on_mousewheel)        # Linux scroll up
    canvas.bind_all("<Button-5>", _on_mousewheel)        # Linux scroll down

    # -------------------------
    # Defer building heavy UI so window appears quickly
    # -------------------------
    def build_ui():
        # Title
        title = ctk.CTkLabel(
            scroll_frame, text="Add New Study Record",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(18, 10))

        # Step label
        step_label = ctk.CTkLabel(scroll_frame, text="Step 1 of 5 — Choose subject")
        step_label.pack(anchor="w", padx=24, pady=(4, 10))

        # Subject
        subject_label = ctk.CTkLabel(scroll_frame, text="Subject")
        subject_label.pack(anchor="w", padx=24, pady=(6, 2))
        subject_menu = ctk.CTkOptionMenu(scroll_frame, values=ALLOWED_SUBJECTS, width=450)
        subject_menu.pack(padx=24, pady=(0, 12))

        # Assessment Type
        assess_label = ctk.CTkLabel(scroll_frame, text="Assessment Type")
        assess_label.pack(anchor="w", padx=24, pady=(6, 2))
        assess_menu = ctk.CTkOptionMenu(scroll_frame, values=ALLOWED_ASSESSMENTS, width=450)
        assess_menu.pack(padx=24, pady=(0, 12))

        # Hours
        hours_label = ctk.CTkLabel(scroll_frame, text="Hours Studied")
        hours_label.pack(anchor="w", padx=24, pady=(6, 2))
        hours_entry = ctk.CTkEntry(scroll_frame, placeholder_text="e.g., 1.5 or 2")
        hours_entry.pack(padx=24, fill="x", pady=(0, 12))

        # Marks obtained
        marks_label = ctk.CTkLabel(scroll_frame, text="Marks Obtained")
        marks_label.pack(anchor="w", padx=24, pady=(6, 2))
        marks_entry = ctk.CTkEntry(scroll_frame, placeholder_text="e.g., 7 (if quiz is out of 10)")
        marks_entry.pack(padx=24, fill="x", pady=(0, 12))

        # Total marks
        total_label = ctk.CTkLabel(scroll_frame, text="Total Marks for this Assessment")
        total_label.pack(anchor="w", padx=24, pady=(6, 2))
        total_entry = ctk.CTkEntry(scroll_frame, placeholder_text="e.g., 10 or 100")
        total_entry.pack(padx=24, fill="x", pady=(0, 12))

        # Percentage helper text
        helper_var = ctk.StringVar(value="")
        helper_label = ctk.CTkLabel(scroll_frame, textvariable=helper_var, anchor="w")
        helper_label.pack(anchor="w", padx=24, pady=(0, 12))

        def update_helper(*_):
            try:
                m = float(marks_entry.get().strip())
                t = float(total_entry.get().strip())
                if t > 0:
                    helper_var.set(f"Percentage: {m/t*100:.2f}%")
                else:
                    helper_var.set("")
            except Exception:
                helper_var.set("")

        marks_entry.bind("<KeyRelease>", update_helper)
        total_entry.bind("<KeyRelease>", update_helper)

        # Buttons frame
        btn_frame = ctk.CTkFrame(scroll_frame)
        btn_frame.pack(fill="x", padx=24, pady=20)

        def on_submit():
            subject = subject_menu.get()
            assess = assess_menu.get()
            hours = hours_entry.get().strip()
            marks = marks_entry.get().strip()
            total = total_entry.get().strip()

            if hours == "" or marks == "" or total == "":
                messagebox.showerror("Missing input", "Please fill all fields.")
                return

            try:
                data_manager.add_record(subject, assess, hours, marks, total)
                messagebox.showinfo("Success", "Record added successfully.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def on_clear():
            # reset entries
            hours_entry.delete(0, "end")
            marks_entry.delete(0, "end")
            total_entry.delete(0, "end")
            helper_var.set("")

        submit_btn = ctk.CTkButton(btn_frame, text="Submit", command=on_submit, width=160)
        submit_btn.pack(side="left", padx=8)

        clear_btn = ctk.CTkButton(btn_frame, text="Clear", command=on_clear, width=120)
        clear_btn.pack(side="left", padx=8)

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=win.destroy, width=120)
        cancel_btn.pack(side="right", padx=8)

        # default selections
        subject_menu.set(ALLOWED_SUBJECTS[0])
        assess_menu.set(ALLOWED_ASSESSMENTS[0])

        # Force an initial update to ensure correct scrollregion and widths
        win.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(inner_window_id, width=canvas.winfo_width())

    # Defer actual heavy widget creation so the window can appear immediately
    win.after(10, build_ui)

    win.transient(parent)
    win.grab_set()
