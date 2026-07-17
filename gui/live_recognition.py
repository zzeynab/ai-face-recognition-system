import os

import cv2
import numpy as np

from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

from services.recognition_service import RecognitionService


# ==========================================
# Settings
# ==========================================

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
    "arial.ttf"
)


# ==========================================
# Recognition Service
# ==========================================

recognition = RecognitionService()


# ==========================================
# Persian Text
# ==========================================

def put_farsi_text(
    image,
    text,
    position,
    font_size=28,
    color=(0, 255, 0)
):

    reshaped_text = arabic_reshaper.reshape(text)

    bidi_text = get_display(
        reshaped_text
    )

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


# ==========================================
# Main
# ==========================================

def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print("Camera Error")
        return


    while True:

        ret, frame = cap.read()

        if not ret:
            break


        faces = recognition.detect_faces(
            frame
        )


        for face in faces:


            x1, y1, x2, y2 = map(
                int,
                face.bbox
            )


            name, score = recognition.recognize_face(
                face.embedding,
                THRESHOLD
            )


            # ----------------------------
            # Known Person
            # ----------------------------

            if name != "Unknown":

                color = (
                    0,
                    255,
                    0
                )

                label = (
                    f"{name} "
                    f"({score:.2f})"
                )


            # ----------------------------
            # Unknown Person
            # ----------------------------

            else:

                color = (
                    0,
                    0,
                    255
                )

                label = (
                    f"ناشناس "
                    f"({score:.2f})"
                )


            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                2
            )


            frame = put_farsi_text(
                frame,
                label,
                (
                    x1,
                    y1 - 40
                ),
                28,
                color
            )


        cv2.imshow(
            "Face Recognition System",
            frame
        )


        key = cv2.waitKey(1)


        if key == 27:
            break


    cap.release()

    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()