import tkinter as tk
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def open_register():
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "gui.register_gui"
        ],
        cwd=BASE_DIR
    )


def open_recognition():
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "gui.live_recognition"
        ],
        cwd=BASE_DIR
    )


def open_admin():
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "gui.admin_panel"
        ],
        cwd=BASE_DIR
    )


# ----------------- UI -----------------

root = tk.Tk()

root.title("سیستم تشخیص چهره هوشمند - پروژه دانشگاهی")
root.geometry("500x500")
root.resizable(True, True)

title = tk.Label(
    root,
    text="سیستم تشخیص چهره هوشمند",
    font=("Arial", 18, "bold")
)
title.pack(pady=30)

subtitle = tk.Label(
    root,
    text="Python + AI - پروژه تشخیص چهره",
    font=("Arial", 11)
)
subtitle.pack(pady=5)

btn1 = tk.Button(
    root,
    text="ثبت چهره جدید",
    width=25,
    height=2,
    font=("Arial", 11),
    command=open_register
)
btn1.pack(pady=10)

btn2 = tk.Button(
    root,
    text="تشخیص زنده چهره",
    width=25,
    height=2,
    font=("Arial", 11),
    command=open_recognition
)
btn2.pack(pady=10)

btn3 = tk.Button(
    root,
    text="مدیریت دیتابیس",
    width=25,
    height=2,
    font=("Arial", 11),
    command=open_admin
)
btn3.pack(pady=10)

btn4 = tk.Button(
    root,
    text="خروج",
    width=25,
    height=2,
    font=("Arial", 11),
    command=root.destroy
)
btn4.pack(pady=20)

root.mainloop()