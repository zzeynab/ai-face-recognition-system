import cv2
import os


class CameraService:

    def __init__(self, camera_id=0):

        self.camera_id = camera_id
        self.camera = None


    # ---------------------------------
    # Open Camera
    # ---------------------------------

    def open_camera(self):

        if self.camera is not None:
            return self.camera


        self.camera = cv2.VideoCapture(
            self.camera_id
        )


        if not self.camera.isOpened():

            self.camera = None

            raise Exception(
                "Camera could not be opened"
            )


        # تنظیم کیفیت تصویر
        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            640
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            480
        )


        return self.camera



    # ---------------------------------
    # Check Camera Status
    # ---------------------------------

    def is_opened(self):

        return self.camera is not None



    # ---------------------------------
    # Get Frame
    # ---------------------------------

    def get_frame(self):

        if self.camera is None:

            return None


        ret, frame = self.camera.read()


        if not ret:

            return None


        return frame



    # ---------------------------------
    # Release Camera
    # ---------------------------------

    def release(self):

        if self.camera is not None:

            self.camera.release()

            self.camera = None



    # ---------------------------------
    # Save Image
    # ---------------------------------

    def save_image(
        self,
        frame,
        path
    ):

        folder = os.path.dirname(path)


        if folder and not os.path.exists(folder):

            os.makedirs(folder)


        cv2.imwrite(
            path,
            frame
        )