import cv2


class CameraService:
    """Own the lifecycle of the application camera."""

    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.camera = None

    def open_camera(self):
        if self.camera is not None:
            return self.camera

        self.camera = cv2.VideoCapture(self.camera_id)
        if not self.camera.isOpened():
            self.camera.release()
            self.camera = None
            raise RuntimeError("Camera could not be opened")

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return self.camera

    def is_opened(self):
        return self.camera is not None and self.camera.isOpened()

    def get_frame(self):
        if not self.is_opened():
            return None

        success, frame = self.camera.read()
        return frame if success else None

    def release(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None
