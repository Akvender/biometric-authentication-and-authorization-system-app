import threading
import copy
import cv2
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from deepface import DeepFace
import os

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username STRING,   
            image BLOB 
            )
        ''')
        self.conn.commit()

    def get_user_image(self, name):
        try:
            self.cursor.execute("SELECT image FROM users WHERE username = ?", (name,))
            result = self.cursor.fetchone()
            if result:
                img_blob = result[0]
                np_img = np.frombuffer(img_blob, dtype=np.uint8)
                image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                return image
            else:
                print("Użytkownik nie znaleziony.")
                return None
        except sqlite3.Error as e:
            print(f"Błąd bazy danych: {e}")
            return None

    def save_new_user(self, image, username):
        try:
            _, img_encoded = cv2.imencode('.jpg', image)
            img_bytes = img_encoded.tobytes()
            self.cursor.execute("INSERT INTO users (username, image) VALUES (?, ?)", (username, img_bytes))
            self.conn.commit()
            print("Zapisano nowego użytkownika.")
        except sqlite3.Error as e:
            print(f"Błąd bazy danych: {e}")

    def how_many_users_in_db(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM users")
            count = self.cursor.fetchone()[0]
            return count
        except sqlite3.Error as e:
            print(f"Błąd bazy danych: {e}")
            return 0

    def close(self):
        self.conn.close()

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

def main():
    db_manager = DatabaseManager("Baza_osób_upoważnionych.db")

    print("1: Zaloguj się\n2: Dodaj nowego użytkownika")
    user_input = int(input("Podaj numer instrukcji: "))
    username = input("Podaj nazwę: ")

    if user_input == 1:
        print(f"Witaj, zaraz nastąpi próba logowania na konto użytkownika {username}")
        img1 = db_manager.get_user_image(username)
    elif user_input == 2:
        print(f"Witaj {username}, wprowadź skan swojej twarzy do systemu, aby zarejestrować się w systemie")
    else:
        print("Podaj poprawny numer instrukcji")

    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    address = 0
    cap = cv2.VideoCapture(address)
    if not cap.isOpened():
        print("Nie można otworzyć strumienia wideo.")
        exit(0)

    camera_thread = CameraReaderThread(cap)
    camera_thread.start_thread()

    try:
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
                    if user_input == 1:
                        face_frame = frame[y:y + h, x:x + w]
                        img2 = face_frame

                        plt.imshow(img1[:, :, ::-1])
                        plt.show()
                        plt.imshow(img2[:, :, ::-1])
                        plt.show()

                        cv2.imwrite('temp_img1.jpg', img1)
                        cv2.imwrite('temp_img2.jpg', img2)

                        try:
                            result = DeepFace.verify('temp_img1.jpg', 'temp_img2.jpg')
                            print("Czy to ta sama twarz: ", result['verified'])
                            os.remove('temp_img1.jpg')
                            os.remove('temp_img2.jpg')
                        except Exception as e:
                            print(f"Wystąpił błąd podczas weryfikacji: {e}")

                    elif user_input == 2:
                        face_frame = frame[y:y + h, x:x + w]
                        db_manager.save_new_user(face_frame, username)
                    else:
                        break
                break

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

    finally:
        # Zakończenie pracy wątku, zwolnienie zasobów kamery i zamknięcie wszystkich okien
        camera_thread.stop()
        cap.release()
        cv2.destroyAllWindows()
        db_manager.close()

if __name__ == "__main__":
    main()
