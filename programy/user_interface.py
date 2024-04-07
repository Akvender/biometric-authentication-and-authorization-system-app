__all__ = ["user_interface"]

import customtkinter
import database_manager as db_manager
from tkinter import *
from tkinter import messagebox
import bcrypt
import cv2


class UserInterface:
	def __init__(self, master, db_manager):
		self.master = master
		self.db_manager = db_manager
		self.setup_ui()

	def zalozkonto(self):
		username = self.uzytkownikentry.get()
		password = self.hasloentry.get()

		if username != '' and password != '':
			self.cursor.execute('SELECT username FROM users WHERE username=?', [username])
			if self.cursor.fetchone() is not None:
				messagebox.showerror('Błąd', 'Nazwa użytkownika zajęta.')
			else:
				face_frame = get_frame_from_camera()
				_, img_encoded = cv2.imencode('.jpg', face_frame)
				img_bytes = img_encoded.tobytes()

				encoded_password = password.encode('utf-8')
				hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
				self.cursor.execute('INSERT INTO users (username, password, image) VALUES (?, ?, ?)',
									[username, hashed_password, img_bytes])
				self.conn.commit()
				messagebox.showinfo('Sukces', 'Twoje konto zostało stworzone.')
		else:
			messagebox.showerror('Błąd', 'Wprowadź nazwę użytkownika i hasło.')

	def flogin(self, username, password):
		image = self.db_manager.get_user_image(username)

		if username != '' and password != '':
			self.cursor.execute('SELECT password FROM users WHERE username=?', [username])
			result = self.cursor.fetchone()

			image2 = get_frame_from_camera()
			if result:
				if bcrypt.checkpw(password.encode('utf-8'), result[0]) and face_verification(image, image2):
					messagebox.showinfo('Sukces', 'Zalogowano się pomyślnie.')

				else:
					messagebox.showerror('Błąd', 'Wprowadzono niepasujące dane.')
			else:
				messagebox.showerror('Błąd', 'Wprowadź poprawne dane.')

	def logowanie(self):
		self.signupframe.destroy()
		loginframe = customtkinter.CTkFrame(app, width=200, height=400,
											bg_color='transparent')
		loginframe.place(x=300, y=0)

		loginlabel = customtkinter.CTkLabel(loginframe, font=self.font1, text="Zaloguj się",
											text_color="#fff", corner_radius=36)
		loginlabel.place(x=30, y=20)

		global uzytkownikentry2
		global hasloentry2

		uzytkownikentry2 = customtkinter.CTkEntry(loginframe, font=self.font2,
												  text_color="#fff",
												  placeholder_text="Nazwa",
												  width=100, height=25,
												  bg_color="transparent", fg_color="#2e2630",
												  border_width=1, border_color='#38303b')
		uzytkownikentry2.place(x=50, y=60)

		hasloentry2 = customtkinter.CTkEntry(loginframe, font=self.font2,
											 text_color="#fff",
											 placeholder_text="Hasło",
											 width=100, height=25,
											 bg_color="transparent", fg_color="#2e2630", show="*",
											 border_width=1, border_color='#38303b')
		hasloentry2.place(x=50, y=90)

		loginbutton = customtkinter.CTkButton(loginframe, font=self.font2, text_color="#bf5adb",
											  text="Zaloguj",
											  width=75, height=30,
											  bg_color="transparent", fg_color="#2e2630",
											  command=self.flogin,
											  cursor='hand2', border_width=1, border_color='#38303b',
											  hover_color='#262326')
		loginbutton.place(x=61, y=120)

	def setup_ui(self):
		self.master.title("Logowanie")
		self.master.geometry('500x400')
		self.master.config(bg="#64147a")
		self.master.resizable(width=False, height=False)

		font1 = ('Verdana', 19)
		font2 = ('Verdana', 15)


		frame1 = customtkinter.CTkFrame(app, bg_color='transparent', fg_color='transparent', width=300, height=400)
		frame1.place(x=0, y=0)

		bgframe = PhotoImage(file="bg.png")
		bglabel = Label(frame1, image=bgframe, bg="#331e38")
		bglabel.place(x=0, y=0)

		signupframe = customtkinter.CTkFrame(app, width=200, height=400)
		signupframe.place(x=300, y=0)

		signuplabel = customtkinter.CTkLabel(signupframe, font=font1,
											 text="Załóż konto",
											 text_color="#fff",
											 bg_color="transparent",
											 corner_radius=36)
		signuplabel.place(x=30, y=20)

		uzytkownikentry = customtkinter.CTkEntry(signupframe, font=font2,
												 text_color="#fff",
												 placeholder_text="Nazwa",
												 width=100, height=25,
												 bg_color="transparent", fg_color="#2e2630", border_width=1,
												 border_color='#38303b')
		uzytkownikentry.place(x=50, y=60)

		hasloentry = customtkinter.CTkEntry(signupframe, font=font2,
											text_color="#fff",
											placeholder_text="Hasło",
											width=100, height=25,
											bg_color="transparent", fg_color="#2e2630", show="*", border_width=1,
											border_color='#38303b')
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
											  width=150, height=10)
		maszjuzkonto.place(x=25, y=250)

		zalogujbutton = customtkinter.CTkButton(signupframe, font=font2, text_color="#bf5adb",
												text="Logowanie",
												width=60, height=25,
												bg_color="transparent", fg_color="transparent",
												command=logowanie,
												cursor='hand2', hover_color='#262326', border_width=1,
												border_color='#38303b')
		zalogujbutton.place(x=55, y=270)

	def logowanie(self):
		self.signupframe.destroy()
		loginframe = customtkinter.CTkFrame(app, width=200, height=400,
											bg_color='transparent')
		loginframe.place(x=300, y=0)

		loginlabel = customtkinter.CTkLabel(loginframe, font=font1, text="Zaloguj się",
											text_color="#fff", corner_radius=36)
		loginlabel.place(x=30, y=20)

		global uzytkownikentry2
		global hasloentry2

		uzytkownikentry2 = customtkinter.CTkEntry(loginframe, font=font2,
												  text_color="#fff",
												  placeholder_text="Nazwa",
												  width=100, height=25,
												  bg_color="transparent", fg_color="#2e2630",
												  border_width=1, border_color='#38303b')
		uzytkownikentry2.place(x=50, y=60)

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
											  command=self.flogin,
											  cursor='hand2', border_width=1, border_color='#38303b',
											  hover_color='#262326')
		loginbutton.place(x=61, y=120)
