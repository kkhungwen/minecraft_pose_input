import traceback
import cv2
import numpy as np
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage
import mediapipe as mp
from .body import BodyState
from .config import IMAGE_HEIGHT, IMAGE_WIDTH, AppConfig
from .mouse_thread import MouseThread

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

BG_COLOR = (192, 192, 192)  # gray


class Cv2Thread(QThread):
    update_status = Signal(dict)
    update_frame = Signal(QImage)
    update_state = Signal(dict)

    def __init__(
        self,
        parent,
        app_config: AppConfig,
    ):
        QThread.__init__(self, parent)
        self.status = False
        self.cap = None
        self.mouse_thread = MouseThread()
        self.body = BodyState(app_config.body_config, app_config.events_config, self.mouse_thread)
        self.mp_config = app_config.mp_config
        self.camera_port = 0

    def toggle(self):
        self.status = not self.status
        if self.status:
            self.mouse_thread.start()
            self.start()
        else:
            self.mouse_thread.requestInterruption()
            self.mouse_thread.wait()

    def run(self):
        print("run mediapipe", self.mp_config)
        self.update_status.emit(dict(loading=True))
        self.cap = cv2.VideoCapture(self.camera_port)

        with mp_holistic.Holistic(**self.mp_config) as holistic:
            while self.cap.isOpened() and self.status:
                self.update_status.emit(dict(loading=False))
                success, image = self.cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue

                timestamp = self.cap.get(cv2.CAP_PROP_POS_MSEC)

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                # Recolor image to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                results = holistic.process(image)

                # Recolor back to BGR
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if (
                    self.mp_config["enable_segmentation"]
                    and results.segmentation_mask is not None
                ):
                    try:
                        # Draw selfie segmentation on the background image.
                        # To improve segmentation around boundaries, consider applying a joint
                        # bilateral filter to "results.segmentation_mask" with "image".
                        condition = (
                            np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
                        )
                        # The background can be customized.
                        #   a) Load an image (with the same width and height of the input image) to
                        #      be the background, e.g., bg_image = cv2.imread('/path/to/image/file')
                        #   b) Blur the input image by applying image filtering, e.g.,
                        #      bg_image = cv2.GaussianBlur(image,(55,55),0)
                        bg_image = cv2.GaussianBlur(image, (55, 55), 0)
                        if bg_image is None:
                            bg_image = np.zeros(image.shape, dtype=np.uint8)
                            bg_image[:] = BG_COLOR
                        image = np.where(condition, image, bg_image)
                    except Exception:
                        print(traceback.format_exc())

                # Draw landmark annotation on the image.
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
                )

                self.body.calculate(image, results, timestamp)

                # Reading the image in RGB to display it
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Creating and scaling QImage
                h, w, ch = image.shape
                image = QImage(image.data, w, h, ch * w, QImage.Format_RGB888)
                image = image.scaled(IMAGE_WIDTH, IMAGE_HEIGHT, Qt.KeepAspectRatio)

                # Emit signal
                self.update_frame.emit(image)
                self.update_state.emit(dict(body=self.body))

                if cv2.waitKey(5) & 0xFF == 27:
                    break
        
        self.mouse_thread.requestInterruption()
        self.mouse_thread.wait()
        print("stop camera")
        self.cap.release()
        self.update_status.emit(dict(loading=False))
