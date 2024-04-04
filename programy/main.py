import threading
import copy
import cv2
import sqlite3
import numpy as np
import os
import customtkinter
import bcrypt

from deepface import DeepFace
from tkinter import *
from tkinter import messagebox

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
               username TEXT NOT NULL,
               password TEXT NOT NULL,
               image BLOB
            )
        ''')
        self.conn.commit()


    def zalozkonto(self):
        username = uzytkownikentry.get()
        password = hasloentry.get()

        if username != '' and password != '':
            self.cursor.execute('SELECT username FROM users WHERE username=?', [username])
            if self.cursor.fetchone() is not None:
                messagebox.showerror('Błąd', 'Nazwa użytkownika zajęta.')
            else:
                try:
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
                    camera_thread.stop()
                    cap.release()
                    cv2.destroyAllWindows()

                _, img_encoded = cv2.imencode('.jpg', face_frame)
                img_bytes = img_encoded.tobytes()

                encoded_password = password.encode('utf-8')
                hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
                print(hashed_password)
                self.cursor.execute('INSERT INTO users (username, password, image) VALUES (?, ?, ?)', [username, hashed_password, img_bytes])
                self.conn.commit()
                messagebox.showinfo('Sukces', 'Twoje konto zostało stworzone.')
        else:
            messagebox.showerror('Błąd', 'Wprowadź nazwę użytkownika i hasło.')


    def flogin(self):
        username = uzytkownikentry2.get()
        password = hasloentry2.get()
        image = db_manager.get_user_image(username)

        if username != '' and password != '':
            self.cursor.execute('SELECT password FROM users WHERE username=?', [username])
            result = self.cursor.fetchone()

            try:
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
                camera_thread.stop()
                cap.release()
                cv2.destroyAllWindows()

            image2 = face_frame

            if result:
                if bcrypt.checkpw(password.encode('utf-8'), result[0]) and face_verification(image, image2):
                    messagebox.showinfo('Sukces', 'Zalogowano się pomyślnie.')

                else:
                    messagebox.showerror('Błąd', 'Wprowadzono niepasujące dane.')
            else:
                messagebox.showerror('Błąd', 'Wprowadź poprawne dane.')


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


def face_verification(img1, img2):

    cv2.imwrite('temp_img1.jpg', img1)
    cv2.imwrite('temp_img2.jpg', img2)
    result = DeepFace.verify('temp_img1.jpg', 'temp_img2.jpg')

    if result:
        os.remove('temp_img1.jpg')
        os.remove('temp_img2.jpg')
        return True
    else:
        os.remove('temp_img1.jpg')
        os.remove('temp_img2.jpg')
        print("Weryfikacja nie powiodła się")
        return False


app = customtkinter.CTk()
app.title("Logowanie")
app.geometry('500x400')
app.config(bg="#64147a")
app.resizable(width=False,height=False)

font1 = ('Verdana',19)
font2 = ('Verdana',15)

db_manager = DatabaseManager("baza.db")

frame1 = customtkinter.CTkFrame(app, bg_color='transparent',fg_color='transparent',width=300,height=400)
frame1.place(x=0,y=0)

bgframe = PhotoImage(file="bg.png")
bglabel = Label(frame1, image=bgframe, bg="#331e38")
bglabel.place(x=0,y=0)


def logowanie():
    signupframe.destroy()
    loginframe = customtkinter.CTkFrame(app,width=200,height=400,
                                        bg_color='transparent')
    loginframe.place(x=300,y=0)

    loginlabel = customtkinter.CTkLabel(loginframe, font=font1, text="Zaloguj się",
                                        text_color="#fff", corner_radius=36)
    loginlabel.place(x=30,y=20)

    global uzytkownikentry2
    global hasloentry2

    uzytkownikentry2 = customtkinter.CTkEntry(loginframe, font=font2,
                                         text_color="#fff",
                                         placeholder_text="Nazwa",
                                         width=100, height=25,
                                         bg_color="transparent", fg_color="#2e2630",
                                         border_width=1, border_color='#38303b')
    uzytkownikentry2.place(x=50,y=60)

    hasloentry2 = customtkinter.CTkEntry(loginframe, font=font2,
                                         text_color="#fff",
                                         placeholder_text="Hasło",
                                         width=100, height=25,
                                         bg_color="transparent", fg_color="#2e2630", show="*",
                                         border_width=1, border_color='#38303b')
    hasloentry2.place(x=50, y=90)

    loginbutton = customtkinter.CTkButton(loginframe, font=font2, text_color="#bf5adb",
                                      text="Zaloguj",
                                      width=75, height=30,
                                      bg_color="transparent", fg_color="#2e2630",
                                      command=db_manager.flogin,
                                      cursor='hand2', border_width=1, border_color='#38303b',
                                      hover_color='#262326')
    loginbutton.place(x=61, y=120)


##
signupframe = customtkinter.CTkFrame(app,width=200,height=400)
signupframe.place(x=300,y=0)

signuplabel = customtkinter.CTkLabel(signupframe, font=font1,
                                     text="Załóż konto",
                                     text_color="#fff",
                                     bg_color="transparent",
                                     corner_radius=36)
signuplabel.place(x=30,y=20)

uzytkownikentry = customtkinter.CTkEntry(signupframe, font=font2,
                                         text_color="#fff",
                                         placeholder_text="Nazwa",
                                         width=100, height=25,
                                         bg_color="transparent", fg_color="#2e2630", border_width=1, border_color='#38303b')
uzytkownikentry.place(x=50, y=60)

hasloentry = customtkinter.CTkEntry(signupframe, font=font2,
                                         text_color="#fff",
                                         placeholder_text="Hasło",
                                         width=100, height=25,
                                         bg_color="transparent", fg_color="#2e2630", show="*", border_width=1, border_color='#38303b')
hasloentry.place(x=50, y=90)

zalozbutton = customtkinter.CTkButton(signupframe, font=font2, text_color="#bf5adb",
                                      text="Załóż",
                                      width=75, height=30,
                                      bg_color="transparent", fg_color="#2e2630",
                                      command=db_manager.zalozkonto,
                                      cursor='hand2', border_width=1, border_color='#38303b',
                                      hover_color='#262326')
zalozbutton.place(x=61, y=120)

maszjuzkonto = customtkinter.CTkLabel(signupframe, font=font2, text_color="#fff",
                                      text="Posiadasz już konto?",
                                      bg_color="transparent", fg_color="transparent",
                                      width=150,height=10)
maszjuzkonto.place(x=25, y=250)

zalogujbutton = customtkinter.CTkButton(signupframe, font=font2, text_color="#bf5adb",
                                      text="Logowanie",
                                      width=60, height=25,
                                      bg_color="transparent", fg_color="transparent",
                                      command=logowanie,
                                      cursor='hand2', hover_color='#262326', border_width=1, border_color='#38303b')
zalogujbutton.place(x=55, y=270)

app.mainloop()
