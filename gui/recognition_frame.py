import tkinter as tk
import threading
import os

import cv2
import numpy as np

from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

from services.recognition_service import RecognitionService
from services.camera_service import CameraService
from gui.theme import COLORS, FONT_FAMILY


THRESHOLD = 0.60

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FONT_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "fonts",
    "Vazirmatn-Regular.ttf"
)


class RecognitionFrame(tk.Frame):

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
            text="تشخیص زنده چهره",
            font=(FONT_FAMILY, 18, "bold")
        ).pack(pady=20)

        self.start_btn = tk.Button(
            self,
            text="شروع تشخیص",
            width=25,
            height=2,
            command=self.start_recognition
        )

        self.start_btn.pack(pady=10)

        self.stop_btn = tk.Button(
            self,
            text="توقف",
            width=25,
            height=2,
            command=self.stop_recognition,
            state="disabled"
        )

        self.stop_btn.pack(pady=10)

        tk.Button(
            self,
            text="بازگشت",
            width=20,
            command=self.back_home
        ).pack(pady=20)


    def put_farsi_text(
        self,
        image,
        text,
        position,
        font_size=28,
        color=(0,255,0)
    ):

        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)

        img = Image.fromarray(
            cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            )
        )

        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(
            FONT_PATH,
            font_size
        )

        draw.text(
            position,
            bidi_text,
            font=font,
            fill=color
        )

        return cv2.cvtColor(
            np.array(img),
            cv2.COLOR_RGB2BGR
        )


    def start_recognition(self):

        if self.running:
            return

        self.running = True

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        threading.Thread(
            target=self.run_recognition,
            daemon=True
        ).start()


    def run_recognition(self):

        try:
            self.camera.open_camera()
        except:
            self.running = False
            return

        while self.running:

            frame = self.camera.get_frame()

            if frame is None:
                break

            faces = self.recognition.detect_faces(frame)

            for face in faces:

                x1,y1,x2,y2 = map(
                    int,
                    face.bbox
                )

                name,score = self.recognition.recognize_face(
                    face.embedding,
                    THRESHOLD
                )

                if name != "Unknown":

                    color = (0,255,0)
                    label = f"{name} ({score:.2f})"

                else:

                    color = (0,0,255)
                    label = f"ناشناس ({score:.2f})"

                cv2.rectangle(
                    frame,
                    (x1,y1),
                    (x2,y2),
                    color,
                    2
                )

                frame = self.put_farsi_text(
                    frame,
                    label,
                    (x1,y1-40),
                    28,
                    color
                )

            cv2.imshow(
                "Face Recognition",
                frame
            )

            if cv2.waitKey(1) == 27:
                break

        self.stop_recognition()


    def stop_recognition(self):

        self.running = False

        self.camera.release()

        cv2.destroyAllWindows()

        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")


    def back_home(self):

        self.stop_recognition()

        self.controller.show_frame(
            self.controller.home_frame
        )
