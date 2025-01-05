import cv2
import base64
from threading import Lock, Thread
import numpy as np
import mss

class ScreenStream:
    def __init__(self):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        self.running = False
        self.lock = Lock()
        self.frame = None

    def start(self):
        if self.running:
            return self

        self.running = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.running:
            screenshot = self.sct.grab(self.monitor)
            frame = np.array(screenshot)
            frame = frame[..., :3]  # Remove alpha channel if it exists

            self.lock.acquire()
            self.frame = frame
            self.lock.release()

    def read(self, encode=False):
        self.lock.acquire()
        frame = self.frame.copy() if self.frame is not None else None
        self.lock.release()

        if frame is None:
            return None

        if encode:
            _, buffer = cv2.imencode(".jpeg", frame)
            return base64.b64encode(buffer)

        return frame

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.sct.close()
