"""Shared visual settings for the application."""

import ctypes
import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk


COLORS = {
    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "primary": "#2563EB",
    "primary_dark": "#1D4ED8",
    "text": "#172033",
    "muted": "#64748B",
    "border": "#D9E2F0",
    "danger": "#DC2626",
}

FONT_FAMILY = "Vazirmatn"


def _project_root():
    """Return the project root in development and PyInstaller builds."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def load_project_fonts():
    """Register bundled Vazirmatn fonts for this process on Windows."""
    if os.name != "nt":
        return

    add_font = ctypes.windll.gdi32.AddFontResourceExW
    private_font_flag = 0x10
    fonts_dir = _project_root() / "assets" / "fonts"

    for font_file in ("Vazirmatn-Regular.ttf", "Vazirmatn-Bold.ttf"):
        font_path = fonts_dir / font_file
        if font_path.exists():
            add_font(str(font_path), private_font_flag, None)


def apply_theme(root):
    """Apply shared colors and ttk styles before creating application frames."""
    load_project_fonts()
    root.configure(bg=COLORS["background"])
    root.option_add("*Font", f"{FONT_FAMILY} 10")
    root.option_add("*Frame.Background", COLORS["background"])
    root.option_add("*Label.Background", COLORS["background"])
    root.option_add("*Label.Foreground", COLORS["text"])
    root.option_add("*Entry.Background", COLORS["surface"])
    root.option_add("*Entry.Foreground", COLORS["text"])
    root.option_add("*Entry.InsertBackground", COLORS["text"])
    root.option_add("*Button.Font", f"{FONT_FAMILY} 10")
    root.option_add("*Button.Background", COLORS["primary"])
    root.option_add("*Button.Foreground", "white")
    root.option_add("*Button.ActiveBackground", COLORS["primary_dark"])
    root.option_add("*Button.ActiveForeground", "white")
    root.option_add("*Button.Relief", "flat")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        rowheight=32,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "Treeview.Heading",
        background="#EAF0FA",
        foreground=COLORS["text"],
        font=(FONT_FAMILY, 10, "bold"),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", "#DBEAFE")],
        foreground=[("selected", COLORS["text"])],
    )
