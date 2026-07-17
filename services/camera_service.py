import cv2
import os


class CameraService:

    def __init__(self):

        self.camera = None


    # -----------------------------
    # Open Camera
    # -----------------------------

    def open_camera(self):

        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            raise Exception("Camera could not be opened")

        return self.camera


    # -----------------------------
    # Read Frame
    # -----------------------------

    def get_frame(self):

        if self.camera is None:
            return None

        ret, frame = self.camera.read()

        if not ret:
            return None

        return frame


    # -----------------------------
    # Release Camera
    # -----------------------------

    def release(self):

        if self.camera:

            self.camera.release()

            self.camera = None


    # -----------------------------
    # Save Image
    # -----------------------------

    def save_image(
        self,
        frame,
        path
    ):

        folder = os.path.dirname(path)

        if not os.path.exists(folder):

            os.makedirs(folder)

        cv2.imwrite(
            path,
            frame
        )