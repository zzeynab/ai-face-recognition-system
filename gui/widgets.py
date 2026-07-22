import tkinter as tk

from gui.theme import COLORS


class ElevatedCard(tk.Frame):
    """A reusable surface with a soft bottom-right shadow."""

    def __init__(self, parent, shadow="#C9D5E5", offset=5, **kwargs):
        super().__init__(parent, bg=shadow, **kwargs)
        self.content = tk.Frame(self, bg=COLORS["surface"])
        self.content.pack(
            fill=tk.BOTH,
            expand=True,
            padx=(0, offset),
            pady=(0, offset),
        )


class RtlProgressBar(tk.Canvas):
    """A high-contrast progress bar that fills from right to left."""

    def __init__(self, parent, width=510, height=14, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=COLORS["surface"],
            highlightthickness=0,
            bd=0,
            **kwargs,
        )
        self.value = 0
        self.maximum = 1
        self.bind("<Configure>", lambda _event: self._draw())
        self._draw()

    def set(self, value, maximum):
        self.value = max(0, value)
        self.maximum = max(1, maximum)
        self._draw()

    def _draw(self):
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        ratio = min(1, self.value / self.maximum)
        fill_width = int(width * ratio)

        self.delete("all")
        self.create_rectangle(0, 0, width, height, fill="#DCE5F2", outline="")
        if fill_width:
            self.create_rectangle(
                width - fill_width,
                0,
                width,
                height,
                fill=COLORS["primary"],
                outline="",
            )
