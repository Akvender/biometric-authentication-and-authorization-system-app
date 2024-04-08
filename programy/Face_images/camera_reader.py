__all__ = ["camera_reader", "get_frame_from_camera"]

import threading
import copy
import cv2
import programy.tools as tools
import os


class CameraReaderThread(threading.Thread):
    def __init__(self, camera):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.loop = threading.Event()
        self.camera = camera
        self.curr_frame = None
        self.last_frame = None

    def start_thread(self):
        self.start()

    def run(self):
        while not self.loop.is_set():
            ret, self.curr_frame = self.camera.read()
            if not ret:
                break
            with self.lock:
                self.last_frame = copy.copy(self.curr_frame)

    def get(self):
        with self.lock:
            return copy.copy(self.last_frame)

    def stop(self):
        self.loop.set()


def get_frame_from_camera():
    face_frame = None
    camera_thread = None
    cap = None
    faces = None
    try:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        tools.find("haarcascade_frontalface_alt_tree.xml", root_dir)

        face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_alt_tree.xml')
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Nie można otworzyć strumienia wideo.")
            exit(0)

        camera_thread = CameraReaderThread(cap)
        camera_thread.start_thread()
        while True:

            frame = camera_thread.get()
            if frame is not None:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.05, minNeighbors=5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                cv2.imshow("Camera Feed", frame)

            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and len(faces) > 0:
                for (x, y, w, h) in faces:
                    face_frame = frame[y:y + h, x:x + w]
                break

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

    finally:
        # Zakończenie pracy wątku, zwolnienie zasobów kamery i zamknięcie wszystkich okien
        if camera_thread:
            camera_thread.stop()
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        return face_frame
