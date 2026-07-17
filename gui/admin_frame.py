import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from services.database_service import DatabaseService


class AdminFrame(tk.Frame):

    def __init__(
        self,
        parent,
        controller
    ):

        super().__init__(parent)

        self.controller = controller
        self.db = DatabaseService()

        self.build_ui()

        self.load_data()

    # ==========================================
    # UI
    # ==========================================

    def build_ui(self):

        title = tk.Label(
            self,
            text="مدیریت دیتابیس",
            font=("Arial", 18, "bold")
        )

        title.pack(
            pady=15
        )

        top_frame = tk.Frame(self)

        top_frame.pack(
            pady=10
        )

        self.search_entry = tk.Entry(
            top_frame,
            width=30
        )

        self.search_entry.pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            top_frame,
            text="Search",
            command=self.search_person
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            top_frame,
            text="Refresh",
            command=self.load_data
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            top_frame,
            text="Edit",
            command=self.edit_person
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            top_frame,
            text="Delete",
            command=self.delete_person
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            top_frame,
            text="بازگشت",
            command=lambda: self.controller.show_frame(
                self.controller.home_frame
            )
        ).pack(
            side=tk.LEFT,
            padx=20
        )

        self.tree = ttk.Treeview(
            self,
            columns=(
                "ID",
                "First Name",
                "Last Name",
                "Register Time"
            ),
            show="headings"
        )

        self.tree.heading(
            "ID",
            text="ID"
        )

        self.tree.heading(
            "First Name",
            text="First Name"
        )

        self.tree.heading(
            "Last Name",
            text="Last Name"
        )

        self.tree.heading(
            "Register Time",
            text="Register Time"
        )

        self.tree.column(
            "ID",
            width=80
        )

        self.tree.column(
            "First Name",
            width=180
        )

        self.tree.column(
            "Last Name",
            width=180
        )

        self.tree.column(
            "Register Time",
            width=250
        )

        self.tree.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

    # ==========================================
    # Load Data
    # ==========================================

    def load_data(self):

        for row in self.tree.get_children():

            self.tree.delete(row)

        rows = self.db.get_all_people()

        for row in rows:

            self.tree.insert(
                "",
                tk.END,
                values=row
            )

    # ==========================================
    # Search
    # ==========================================

    def search_person(self):

        text = self.search_entry.get().strip()

        for row in self.tree.get_children():

            self.tree.delete(row)

        rows = self.db.search_people(text)

        for row in rows:

            self.tree.insert(
                "",
                tk.END,
                values=row
            )
        # ==========================================
    # Delete
    # ==========================================

    def delete_person(self):

        selected = self.tree.focus()

        if not selected:

            messagebox.showerror(
                "Error",
                "Select a person"
            )

            return

        values = self.tree.item(selected)["values"]

        person_id = values[0]

        answer = messagebox.askyesno(
            "Delete",
            "Are you sure?"
        )

        if not answer:
            return

        self.db.delete_person(person_id)

        self.load_data()

        messagebox.showinfo(
            "Success",
            "Person deleted successfully"
        )

    # ==========================================
    # Edit
    # ==========================================

    def edit_person(self):

        selected = self.tree.focus()

        if not selected:

            messagebox.showerror(
                "Error",
                "Select a person"
            )

            return

        values = self.tree.item(selected)["values"]

        person_id = values[0]
        first_name = values[1]
        last_name = values[2]

        edit_window = tk.Toplevel(self)

        edit_window.title("Edit Person")
        edit_window.geometry("320x220")
        edit_window.resizable(False, False)

        tk.Label(
            edit_window,
            text="First Name"
        ).pack(
            pady=10
        )

        first_entry = tk.Entry(
            edit_window,
            width=30
        )

        first_entry.pack()

        first_entry.insert(
            0,
            first_name
        )

        tk.Label(
            edit_window,
            text="Last Name"
        ).pack(
            pady=10
        )

        last_entry = tk.Entry(
            edit_window,
            width=30
        )

        last_entry.pack()

        last_entry.insert(
            0,
            last_name
        )

        def save_changes():

            new_first = first_entry.get().strip()
            new_last = last_entry.get().strip()

            if not new_first or not new_last:

                messagebox.showerror(
                    "Error",
                    "Fields cannot be empty"
                )

                return

            self.db.update_person(
                person_id,
                new_first,
                new_last
            )

            self.load_data()

            edit_window.destroy()

            messagebox.showinfo(
                "Success",
                "Person updated successfully"
            )

        tk.Button(
            edit_window,
            text="Save",
            width=15,
            command=save_changes
        ).pack(
            pady=20
        )

    # ==========================================
    # Reset
    # ==========================================

    def reset(self):

        self.search_entry.delete(
            0,
            tk.END
        )

        self.load_data()