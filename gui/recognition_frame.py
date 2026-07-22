import threading
import tkinter as tk
from tkinter import messagebox

import cv2

from config.settings import RECOGNITION_THRESHOLD
from gui.theme import COLORS, FONT_FAMILY
from gui.widgets import ElevatedCard
from services.camera_service import CameraService
from services.recognition_service import RecognitionService
from utils.image_utils import draw_persian_text


class RecognitionFrame(tk.Frame):
    """Live face-recognition controls and camera workflow."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["background"])

        self.controller = controller
        self.recognition = RecognitionService()
        self.camera = CameraService()
        self.running = False

        self.build_ui()

    def build_ui(self):
        tk.Label(
            self,
            text="تشخیص زندهٔ چهره",
            font=(FONT_FAMILY, 22, "bold"),
            fg=COLORS["text"],
            bg=COLORS["background"],
        ).pack(pady=(42, 6))

        tk.Label(
            self,
            text="برای شروع تشخیص، دوربین را فعال کنید.",
            font=(FONT_FAMILY, 11),
            fg=COLORS["muted"],
            bg=COLORS["background"],
        ).pack(pady=(0, 24))

        card_shell = ElevatedCard(self)
        card_shell.pack(padx=20, pady=10)
        card = card_shell.content
        card.config(padx=55, pady=35)

        self.status_label = tk.Label(
            card,
            text="وضعیت: آمادهٔ شروع",
            font=(FONT_FAMILY, 12, "bold"),
            fg=COLORS["primary"],
            bg=COLORS["surface"],
        )
        self.status_label.pack(pady=(0, 20))

        self.start_btn = tk.Button(
            card,
            text="شروع تشخیص زنده",
            font=(FONT_FAMILY, 11, "bold"),
            bg=COLORS["primary"],
            fg="white",
            activebackground=COLORS["primary_dark"],
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=32,
            pady=11,
            command=self.start_recognition,
        )
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(
            card,
            text="توقف تشخیص",
            font=(FONT_FAMILY, 11, "bold"),
            bg="#DC2626",
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=36,
            pady=11,
            command=self.stop_recognition,
            state="disabled",
        )
        self.stop_btn.pack(pady=5)

        tk.Label(
            card,
            text="در پنجرهٔ دوربین، کلید Esc نیز تشخیص را متوقف می‌کند.",
            font=(FONT_FAMILY, 9),
            fg=COLORS["muted"],
            bg=COLORS["surface"],
        ).pack(pady=(16, 0))

        tk.Button(
            self,
            text="بازگشت به صفحهٔ اصلی",
            font=(FONT_FAMILY, 10),
            bg=COLORS["background"],
            fg=COLORS["muted"],
            activebackground="#EAF0FA",
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=18,
            pady=8,
            command=self.back_home,
        ).pack(pady=(18, 25))

    def on_show(self):
        if not self.running:
            self.recognition.load_database()

    def start_recognition(self):
        if self.running:
            return

        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="وضعیت: تشخیص فعال است", fg="#16A34A")

        threading.Thread(target=self.run_recognition, daemon=True).start()

    def run_recognition(self):
        try:
            self.camera.open_camera()
            cv2.namedWindow("Live Face Recognition", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Live Face Recognition", 660, 500)
            cv2.moveWindow("Live Face Recognition", 25, 55)
            try:
                cv2.setWindowProperty(
                    "Live Face Recognition",
                    cv2.WND_PROP_TOPMOST,
                    1,
                )
            except cv2.error:
                pass
        except Exception as error:
            self.after(0, self._show_camera_error, str(error))
            return

        try:
            while self.running:
                frame = self.camera.get_frame()
                if frame is None:
                    self.after(0, self._set_status, "دریافت تصویر دوربین ناموفق بود.", "#DC2626")
                    break

                for face in self.recognition.detect_faces(frame):
                    x1, y1, x2, y2 = map(int, face.bbox)
                    name, score = self.recognition.recognize_face(
                        face.embedding,
                        RECOGNITION_THRESHOLD,
                    )

                    if name == "Unknown":
                        color = (0, 0, 255)
                        label = f"ناشناس ({score:.2f})"
                    else:
                        color = (0, 255, 0)
                        label = f"{name} ({score:.2f})"

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    frame = draw_persian_text(
                        frame,
                        label,
                        (x2, max(y1 - 35, 30)),
                        font_size=24,
                        color=color,
                    )

                cv2.imshow("Live Face Recognition", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    self.running = False

        finally:
            self.camera.release()
            cv2.destroyAllWindows()
            self.after(0, self._recognition_stopped)

    def stop_recognition(self):
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()
        self._recognition_stopped()

    def _show_camera_error(self, error):
        self._recognition_stopped()
        messagebox.showerror("خطای دوربین", error)

    def _set_status(self, text, color):
        self.status_label.config(text=f"وضعیت: {text}", fg=color)

    def _recognition_stopped(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="وضعیت: آمادهٔ شروع", fg=COLORS["primary"])

    def back_home(self):
        self.stop_recognition()
        self.controller.show_frame(self.controller.home_frame)
