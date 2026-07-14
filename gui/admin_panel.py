import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

# -----------------------
# Load Data
# -----------------------

def load_data():

    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("database/faces.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            first_name,
            last_name,
            register_time
        FROM faces
    """)

    rows = cursor.fetchall()

    conn.close()

    for row in rows:
        tree.insert(
            "",
            tk.END,
            values=row
        )

# -----------------------
# Delete Record
# -----------------------

def delete_person():

    selected = tree.focus()

    if not selected:
        messagebox.showerror(
            "Error",
            "Select a person"
        )
        return

    data = tree.item(selected)

    person_id = data["values"][0]

    answer = messagebox.askyesno(
        "Delete",
        "Are you sure?"
    )

    if not answer:
        return

    conn = sqlite3.connect("database/faces.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM faces WHERE id=?",
        (person_id,)
    )

    conn.commit()
    conn.close()

    load_data()

# -----------------------
# Search
# -----------------------

def search_person():

    text = search_entry.get().strip()

    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("database/faces.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            first_name,
            last_name,
            register_time
        FROM faces
        WHERE first_name LIKE ?
           OR last_name LIKE ?
    """,
    (
        f"%{text}%",
        f"%{text}%"
    ))

    rows = cursor.fetchall()

    conn.close()

    for row in rows:
        tree.insert(
            "",
            tk.END,
            values=row
        )

# -----------------------
# EDIT
# -----------------------
def edit_person():

    selected = tree.focus()

    if not selected:
        messagebox.showerror(
            "Error",
            "Select a person"
        )
        return

    data = tree.item(selected)["values"]

    person_id = data[0]
    first_name = data[1]
    last_name = data[2]

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Person")
    edit_window.geometry("300x200")

    tk.Label(
        edit_window,
        text="First Name"
    ).pack(pady=5)

    first_entry = tk.Entry(edit_window)
    first_entry.pack()
    first_entry.insert(0, first_name)

    tk.Label(
        edit_window,
        text="Last Name"
    ).pack(pady=5)

    last_entry = tk.Entry(edit_window)
    last_entry.pack()
    last_entry.insert(0, last_name)

    def save_changes():

        new_first = first_entry.get().strip()
        new_last = last_entry.get().strip()

        conn = sqlite3.connect("database/faces.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE faces
            SET first_name=?,
                last_name=?
            WHERE id=?
            """,
            (
                new_first,
                new_last,
                person_id
            )
        )

        conn.commit()
        conn.close()

        load_data()

        edit_window.destroy()

        messagebox.showinfo(
            "Success",
            "Record updated successfully"
        )

    tk.Button(
        edit_window,
        text="Save",
        command=save_changes
    ).pack(pady=15)

# -----------------------
# GUI
# -----------------------

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
    text="Delete",
    command=delete_person
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

tree.column("ID", width=60)
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