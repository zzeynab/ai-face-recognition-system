import tkinter as tk

from gui.admin_frame import AdminFrame
from gui.home_frame import HomeFrame
from gui.recognition_frame import RecognitionFrame
from gui.register_frame import RegisterFrame
from gui.theme import COLORS, apply_theme


class MainWindow:

    def __init__(self):
        self.root = tk.Tk()
        apply_theme(self.root)

        self.root.title("سامانه تشخیص چهره هوشمند")
        self.root.geometry("980x680")
        self.root.minsize(880, 600)
        self.root.state("zoomed")

        self.container = tk.Frame(
            self.root,
            bg=COLORS["background"],
        )
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

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

    def add_frame(self, frame_class):
        frame = frame_class(self.container, self)
        self.frames[frame_class] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        on_show = getattr(frame, "on_show", None)

        if callable(on_show):
            on_show()

        frame.tkraise()

    def run(self):
        self.root.mainloop()
