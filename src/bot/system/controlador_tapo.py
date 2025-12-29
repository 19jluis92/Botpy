import cv2
import os
import time

class TapoController:
    def __init__(self, name, rtsp_url):
        self.name = name
        self.rtsp_url = rtsp_url

    def capture_image(self, output_dir="captures"):
        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(self.rtsp_url)
        time.sleep(6)  # dar tiempo a conectar

        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise Exception("No se pudo capturar imagen RTSP zona " + self.name)

        filename = f"{self.name}_{int(time.time())}.jpg"
        path = os.path.join(output_dir, filename)

        cv2.imwrite(path, frame)
        return path