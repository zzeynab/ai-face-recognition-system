import tkinter as tk
from tkinter import messagebox, ttk

from services.admin_service import AdminService
from gui.theme import COLORS, FONT_FAMILY


class AdminFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["background"])

        self.controller = controller
        self.admin_service = AdminService()

        self.build_ui()
        self.load_data()

    # ==========================================
    # UI
    # ==========================================

    def build_ui(self):
        tk.Label(
            self,
            text="مدیریت اطلاعات ثبت‌شده",
            font=(FONT_FAMILY, 18, "bold"),
            anchor="center",
        ).pack(fill=tk.X, pady=15)

        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=30, pady=10)
        
        self.search_entry = tk.Entry(
                top_frame,
                width=30,
                justify="right",
                )
        self.search_entry.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            top_frame,
            text="جست‌وجو",
            command=self.search_person,
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            top_frame,
            text="بروزرسانی",
            command=self.load_data,
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            top_frame,
            text="ویرایش",
            command=self.edit_person,
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            top_frame,
            text="حذف",
            command=self.delete_person,
        ).pack(side=tk.RIGHT, padx=5)


        self.tree = ttk.Treeview(
            self,
            columns=(
                "Register Time",
                "Last Name",
                "First Name",
                "ID",
            ),
            show="headings",
        )

        self.tree.heading("ID", text="شناسه", anchor=tk.E)
        self.tree.heading("First Name", text="نام", anchor=tk.E)
        self.tree.heading("Last Name", text="نام خانوادگی", anchor=tk.E)
        self.tree.heading("Register Time", text="زمان ثبت", anchor=tk.E)

        self.tree.column("ID", width=80, anchor=tk.E)
        self.tree.column("First Name", width=180, anchor=tk.E)
        self.tree.column("Last Name", width=180, anchor=tk.E)
        self.tree.column("Register Time", width=220, anchor=tk.E)

        self.tree.pack(
            fill=tk.BOTH,
            expand=True,
            padx=30,
            pady=10,
        )
        
        tk.Button(
            self,
            text="بازگشت",
            width=20,
            command=self.back_home,
        ).pack(pady=(5, 20))

    # ==========================================
    # Data display
    # ==========================================

    def show_people(self, people):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for person in people:
            person_id, first_name, last_name, register_time = person

            self.tree.insert(
                "",
                tk.END,
                values=(
                    register_time,
                    last_name,
                    first_name,
                    person_id,
                ),
            )

    def load_data(self):
        try:
            people = self.admin_service.get_people()
            self.show_people(people)

        except Exception as error:
            messagebox.showerror(
                "خطا",
                f"دریافت اطلاعات با خطا مواجه شد:\n{error}",
            )

    def on_show(self):
        """Refresh rows whenever the user opens the management screen."""
        self.search_entry.delete(0, tk.END)
        self.load_data()

    def search_person(self):
        try:
            people = self.admin_service.search_people(
                self.search_entry.get()
            )
            self.show_people(people)

        except Exception as error:
            messagebox.showerror(
                "خطا",
                f"جست‌وجو با خطا مواجه شد:\n{error}",
            )

    # ==========================================
    # Selected person
    # ==========================================

    def get_selected_person(self):
        selected = self.tree.focus()

        if not selected:
            messagebox.showerror(
                "خطا",
                "ابتدا یک شخص را انتخاب کنید.",
            )
            return None

        return self.tree.item(selected)["values"]

    # ==========================================
    # Delete
    # ==========================================

    def delete_person(self):
        person = self.get_selected_person()

        if person is None:
            return

        _, last_name, first_name, person_id = person

        confirmed = messagebox.askyesno(
            "حذف شخص",
            (
                f"آیا از حذف «{first_name} {last_name}» مطمئن هستید؟\n\n"
                "تمام Embeddingهای این شخص نیز حذف می‌شوند."
            ),
        )

        if not confirmed:
            return

        try:
            self.admin_service.delete_person(person_id)

            self.load_data()

            messagebox.showinfo(
                "موفق",
                "شخص با موفقیت حذف شد.",
            )

        except ValueError as error:
            messagebox.showerror("خطا", str(error))

        except Exception as error:
            messagebox.showerror(
                "خطا",
                f"حذف شخص با خطا مواجه شد:\n{error}",
            )

    # ==========================================
    # Edit
    # ==========================================

    def edit_person(self):
        person = self.get_selected_person()

        if person is None:
            return

        _, last_name, first_name, person_id = person

        edit_window = tk.Toplevel(self)
        edit_window.title("ویرایش شخص")
        edit_window.geometry("320x220")
        edit_window.resizable(False, False)

        tk.Label(
            edit_window,
            text="نام",
            anchor="e",
        ).pack(fill=tk.X, padx=30, pady=(15, 5))

        first_entry = tk.Entry(
            edit_window,
            width=30,
            justify="right",
        )
        first_entry.pack()
        first_entry.insert(0, first_name)

        tk.Label(
            edit_window,
            text="نام خانوادگی",
            anchor="e",
        ).pack(fill=tk.X, padx=30, pady=(15, 5))

        last_entry = tk.Entry(
            edit_window,
            width=30,
            justify="right",
        )
        last_entry.pack()
        last_entry.insert(0, last_name)

        def save_changes():
            try:
                self.admin_service.update_person(
                    person_id=person_id,
                    first_name=first_entry.get(),
                    last_name=last_entry.get(),
                )

                self.load_data()
                edit_window.destroy()

                messagebox.showinfo(
                    "موفق",
                    "اطلاعات شخص با موفقیت ویرایش شد.",
                )

            except ValueError as error:
                messagebox.showerror("خطا", str(error))

            except Exception as error:
                messagebox.showerror(
                    "خطا",
                    f"ویرایش اطلاعات با خطا مواجه شد:\n{error}",
                )

        tk.Button(
            edit_window,
            text="ذخیره تغییرات",
            width=15,
            command=save_changes,
        ).pack(pady=20)

    # ==========================================
    # Back
    # ==========================================

    def back_home(self):
        self.search_entry.delete(0, tk.END)
        self.load_data()

        self.controller.show_frame(
            self.controller.home_frame
        )
