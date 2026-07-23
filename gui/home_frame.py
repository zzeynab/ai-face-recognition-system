import tkinter as tk

from gui.theme import COLORS, FONT_FAMILY
from gui.widgets import ElevatedCard


class HomeFrame(tk.Frame):
    """Landing page and main navigation for the application."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["background"])
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self, bg=COLORS["background"])
        header.pack(fill=tk.X, padx=60, pady=(48, 25))

        tk.Label(
            header,
            text="سامانه تشخیص چهره هوشمند",
            font=(FONT_FAMILY, 24, "bold"),
            fg=COLORS["text"],
            bg=COLORS["background"],
        ).pack()

        tk.Label(
            header,
            text="مدیریت، ثبت و تشخیص چهره با کمک هوش مصنوعی",
            font=(FONT_FAMILY, 11),
            fg=COLORS["muted"],
            bg=COLORS["background"],
        ).pack(pady=(10, 0))

        cards = tk.Frame(self, bg=COLORS["background"])
        cards.pack(expand=True, padx=60, pady=10)

        self.create_card(
            parent=cards,
            icon="۱",
            title="ثبت چهره جدید",
            description="افزودن فرد جدید و ذخیره اطلاعات چهره",
            button_text="شروع ثبت چهره",
            command=lambda: self.controller.show_frame(
                self.controller.register_frame
            ),
        ).grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.create_card(
            parent=cards,
            icon="۲",
            title="تشخیص زنده چهره",
            description="شناسایی افراد از طریق دوربین به‌صورت زنده",
            button_text="شروع تشخیص",
            command=lambda: self.controller.show_frame(
                self.controller.recognition_frame
            ),
        ).grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.create_card(
            parent=cards,
            icon="۳",
            title="مدیریت اطلاعات",
            description="جست‌وجو، ویرایش و حذف افراد ثبت‌شده",
            button_text="مشاهده اطلاعات",
            command=lambda: self.controller.show_frame(
                self.controller.admin_frame
            ),
        ).grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        for column in range(3):
            cards.grid_columnconfigure(column, weight=1)

        footer = tk.Frame(self, bg=COLORS["background"])
        footer.pack(fill=tk.X, padx=60, pady=(10, 30))

        tk.Button(
            footer,
            text="خروج از برنامه",
            font=(FONT_FAMILY, 10),
            bg=COLORS["danger"],
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=18,
            pady=8,
            command=self.controller.root.destroy,
        ).pack()

    def create_card(
        self,
        parent,
        icon,
        title,
        description,
        button_text,
        command,
    ):
        card_shell = ElevatedCard(parent, width=300, height=300)
        card_shell.grid_propagate(False)
        card = card_shell.content
        card.config(padx=24, pady=26)

        tk.Label(
            card,
            text=icon,
            font=(FONT_FAMILY, 17, "bold"),
            fg="white",
            bg=COLORS["primary"],
            width=3,
            height=1,
        ).pack(pady=(0, 18))

        tk.Label(
            card,
            text=title,
            font=(FONT_FAMILY, 14, "bold"),
            fg=COLORS["text"],
            bg=COLORS["surface"],
        ).pack()

        tk.Label(
            card,
            text=description,
            font=(FONT_FAMILY, 10),
            fg=COLORS["muted"],
            bg=COLORS["surface"],
            justify=tk.CENTER,
            wraplength=250,
        ).pack(pady=(10, 22))

        tk.Button(
            card,
            text=button_text,
            font=(FONT_FAMILY, 10, "bold"),
            bg=COLORS["primary"],
            fg="white",
            activebackground=COLORS["primary_dark"],
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=14,
            pady=8,
            command=command,
        ).pack(side=tk.BOTTOM)

        return card_shell
