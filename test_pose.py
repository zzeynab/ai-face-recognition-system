"""Manual camera test for head-pose detection.

Run from the project root with: python test_pose.py
Press Esc to close the camera window.
"""

import cv2

from config.settings import POSE_DETAILS
from services.camera_service import CameraService
from services.pose_service import PoseService
from services.recognition_service import RecognitionService
from utils.image_utils import draw_persian_text


def main():
    recognition = RecognitionService()
    pose_service = PoseService()
    camera = CameraService()

    try:
        camera.open_camera()

        while True:
            frame = camera.get_frame()
            if frame is None:
                break

            faces = recognition.detect_faces(frame)

            if len(faces) == 1:
                info = pose_service.get_pose_info(faces[0])
                pose_name = info["pose"]

                if pose_name is None:
                    text = "زاویهٔ سر قابل تشخیص نیست"
                else:
                    title = POSE_DETAILS[pose_name]["title"]
                    text = f"زاویهٔ تشخیص‌داده‌شده: {title}"

                detail = (
                    f"منبع: {info['source']} | "
                    f"Pitch: {info['pitch']:.2f} | Yaw: {info['yaw']:.2f}"
                    if info["pitch"] is not None
                    else ""
                )

                frame = draw_persian_text(
                    frame,
                    text,
                    (frame.shape[1] - 15, 18),
                    font_size=24,
                    color=(0, 255, 0),
                )
                frame = draw_persian_text(
                    frame,
                    detail,
                    (frame.shape[1] - 15, 52),
                    font_size=18,
                    color=(255, 255, 255),
                )

            elif len(faces) == 0:
                frame = draw_persian_text(
                    frame,
                    "یک چهره را روبه‌روی دوربین قرار دهید.",
                    (frame.shape[1] - 15, 18),
                    font_size=24,
                    color=(0, 0, 255),
                )

            else:
                frame = draw_persian_text(
                    frame,
                    "فقط یک چهره باید در تصویر باشد.",
                    (frame.shape[1] - 15, 18),
                    font_size=24,
                    color=(0, 0, 255),
                )

            cv2.imshow("Pose Test - ESC to close", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
