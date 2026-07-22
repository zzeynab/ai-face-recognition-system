"""Paths that work both during development and in a PyInstaller build."""

import sys
from pathlib import Path


def project_root():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def resource_path(*parts):
    return project_root().joinpath(*parts)
