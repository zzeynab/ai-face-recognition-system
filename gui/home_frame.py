import tkinter as tk

from gui.register_frame import RegisterFrame
from gui.recognition_frame import RecognitionFrame
from gui.admin_frame import AdminFrame


class HomeFrame(tk.Frame):

    def __init__(
        self,
        parent,
        controller
    ):

        super().__init__(parent)

        self.controller = controller

        title = tk.Label(
            self,
            text="سیستم تشخیص چهره هوشمند",
            font=("Arial", 20, "bold")
        )

        title.pack(
            pady=40
        )

        subtitle = tk.Label(
            self,
            text="Python + AI Face Recognition System",
            font=("Arial", 12)
        )

        subtitle.pack(
            pady=10
        )

        register_btn = tk.Button(
            self,
            text="ثبت چهره جدید",
            width=30,
            height=2,
            command=lambda: self.controller.show_frame(
                RegisterFrame
            )
        )

        register_btn.pack(
            pady=10
        )

        recognition_btn = tk.Button(
            self,
            text="تشخیص زنده چهره",
            width=30,
            height=2,
            command=lambda: self.controller.show_frame(
                RecognitionFrame
            )
        )

        recognition_btn.pack(
            pady=10
        )

        admin_btn = tk.Button(
            self,
            text="مدیریت دیتابیس",
            width=30,
            height=2,
            command=lambda: self.controller.show_frame(
                AdminFrame
            )
        )

        admin_btn.pack(
            pady=10
        )

        exit_btn = tk.Button(
            self,
            text="خروج",
            width=30,
            height=2,
            command=self.controller.root.destroy
        )

        exit_btn.pack(
            pady=20
        )