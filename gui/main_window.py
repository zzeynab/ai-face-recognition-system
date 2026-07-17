import tkinter as tk

from gui.home_frame import HomeFrame
from gui.register_frame import RegisterFrame
from gui.recognition_frame import RecognitionFrame
from gui.admin_frame import AdminFrame

class MainWindow:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title(
            "سیستم تشخیص چهره هوشمند"
        )

        self.root.geometry(
            "900x600"
        )

        self.root.resizable(
            True,
            True
        )

        self.container = tk.Frame(
            self.root
        )

        self.container.pack(
            fill="both",
            expand=True
        )

        self.frames = {}

        self.add_frame(HomeFrame)
        self.add_frame(RegisterFrame)
        self.add_frame(RecognitionFrame)
        self.add_frame(AdminFrame)

        self.home_frame = HomeFrame
        self.register_frame = RegisterFrame
        self.recognition_frame = RecognitionFrame
        self.admin_frame = AdminFrame

        self.show_frame(HomeFrame)


    def add_frame(
        self,
        frame_class
    ):

        frame = frame_class(
            self.container,
            self
        )

        self.frames[frame_class] = frame

        frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )


    def show_frame(
        self,
        frame_class
    ):

        frame = self.frames[frame_class]

        frame.tkraise()


    def run(self):

        self.root.mainloop()