import threading
import copy
import cv2
import sqlite3
from deepface import Deepface
import numpy as np

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

# Klasa CameraReaderThread z usprawnieniami
class CameraReaderThread(threading.Thread):
    def __init__(self, camera):
        self.lock = threading.Lock()
        self.loop = threading.Event()
        self.camera = camera
        self.curr_frame = None
        self.last_frame = None
        super(CameraReaderThread, self).__init__()

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



# Utworzenie instancji klasy DatabaseManager
db_manager = DatabaseManager("Baza_osób_upoważnionych.db")

# Sprawdzenie ilości użytkowników w bazie
if db_manager.how_many_users_in_db() == 0:
	print("Witaj użytkowniku, wprowadź swoje dane do programu")
	username = input("Podaj swoją nazwę: ")
else:
	print("Witaj użytkowniku\n")
	username = input("Podaj nazwę: ")
	image_from_db_to_compare = db_manager.get_user_image(username)

# Inicjalizacja modelu do wykrywania twarzy
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Ustalenie adresu strumienia wideo
address = 0
cap = cv2.VideoCapture(address)
if not cap.isOpened():
	print("Nie można otworzyć strumienia wideo.")
	exit(0)

# Uruchomienie wątku do czytania ramek z kamery
camera_thread = CameraReaderThread(cap)
camera_thread.start_thread()

# Główna pętla programu
try:
	while True:
		# Pobranie ostatniej ramki
		frame = camera_thread.get()
		if frame is not None:
			gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faces = face_detector.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

			for (x, y, w, h) in faces:
				cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

			cv2.imshow("Camera Feed", frame)

			key = cv2.waitKey(1) & 0xFF
			if key == ord('q'):
				break
			elif key == ord('s') and len(faces) > 0:
				for (x, y, w, h) in faces:
					face_frame = frame[y:y + h, x:x + w]
					if db_manager.how_many_users_in_db() == 0:
						db_manager.save_new_user(face_frame, username)
					else:
						result_of_comparing = Deepface.verify(img1_path=saved_face_frame, img2_path=image_from_db_to_compare)
						pass
except Exception as e:
	print(f"Wystąpił błąd: {e}")
finally:
	# Zakończenie pracy wątku, zwolnienie zasobów kamery i zamknięcie wszystkich okien
	camera_thread.stop()
	cap.release()
	cv2.destroyAllWindows()
	db_manager.close()
print(result_of_comparing)
