import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from services.database_service import DatabaseService


db = DatabaseService()


# ==========================================
# Load Data
# ==========================================

def load_data():

    for row in tree.get_children():
        tree.delete(row)

    rows = db.get_all_people()

    for row in rows:

        tree.insert(
            "",
            tk.END,
            values=row
        )


# ==========================================
# Search
# ==========================================

def search_person():

    text = search_entry.get().strip()

    for row in tree.get_children():
        tree.delete(row)

    rows = db.search_people(text)

    for row in rows:

        tree.insert(
            "",
            tk.END,
            values=row
        )


# ==========================================
# Delete
# ==========================================

def delete_person():

    selected = tree.focus()

    if not selected:

        messagebox.showerror(
            "Error",
            "Select a person"
        )

        return

    values = tree.item(selected)["values"]

    person_id = values[0]

    answer = messagebox.askyesno(
        "Delete",
        "Are you sure?"
    )

    if not answer:
        return

    db.delete_person(person_id)

    load_data()

    messagebox.showinfo(
        "Success",
        "Person deleted successfully"
    )


# ==========================================
# Edit
# ==========================================

def edit_person():

    selected = tree.focus()

    if not selected:

        messagebox.showerror(
            "Error",
            "Select a person"
        )

        return

    values = tree.item(selected)["values"]

    person_id = values[0]
    first_name = values[1]
    last_name = values[2]

    edit_window = tk.Toplevel(root)

    edit_window.title("Edit Person")
    edit_window.geometry("320x220")
    edit_window.resizable(False, False)

    tk.Label(
        edit_window,
        text="First Name"
    ).pack(pady=10)

    first_entry = tk.Entry(
        edit_window,
        width=30
    )

    first_entry.pack()
    first_entry.insert(0, first_name)

    tk.Label(
        edit_window,
        text="Last Name"
    ).pack(pady=10)

    last_entry = tk.Entry(
        edit_window,
        width=30
    )

    last_entry.pack()
    last_entry.insert(0, last_name)

    def save_changes():

        new_first = first_entry.get().strip()
        new_last = last_entry.get().strip()

        if not new_first or not new_last:

            messagebox.showerror(
                "Error",
                "Fields cannot be empty"
            )

            return

        db.update_person(
            person_id,
            new_first,
            new_last
        )

        load_data()

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
    ).pack(pady=20)


# ==========================================
# GUI
# ==========================================

root = tk.Tk()

root.title("Face Database Manager")
root.geometry("900x500")

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

search_entry = tk.Entry(
    top_frame,
    width=30
)

search_entry.pack(
    side=tk.LEFT,
    padx=5
)

tk.Button(
    top_frame,
    text="Search",
    command=search_person
).pack(
    side=tk.LEFT,
    padx=5
)

tk.Button(
    top_frame,
    text="Refresh",
    command=load_data
).pack(
    side=tk.LEFT,
    padx=5
)

tk.Button(
    top_frame,
    text="Edit",
    command=edit_person
).pack(
    side=tk.LEFT,
    padx=5
)

tk.Button(
    top_frame,
    text="Delete",
    command=delete_person
).pack(
    side=tk.LEFT,
    padx=5
)

tree = ttk.Treeview(
    root,
    columns=(
        "ID",
        "First Name",
        "Last Name",
        "Register Time"
    ),
    show="headings"
)

tree.heading("ID", text="ID")
tree.heading("First Name", text="First Name")
tree.heading("Last Name", text="Last Name")
tree.heading("Register Time", text="Register Time")

tree.column("ID", width=80)
tree.column("First Name", width=180)
tree.column("Last Name", width=180)
tree.column("Register Time", width=250)

tree.pack(
    fill=tk.BOTH,
    expand=True,
    padx=10,
    pady=10
)

load_data()

root.mainloop()