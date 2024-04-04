import customtkinter
import sqlite3
import bcrypt

from tkinter import *
from tkinter import messagebox

app = customtkinter.CTk()
app.title("Logowanie")
app.geometry('500x400')
app.config(bg="#64147a")
app.resizable(width=False,height=False)

font1 = ('Verdana',19)
font2 = ('Verdana',15)

baza = sqlite3.connect("baza.db")
cursor = baza.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS users (
               username TEXT NOT NULL,
               password TEXT NOT NULL)''')

frame1 = customtkinter.CTkFrame(app, bg_color='transparent',fg_color='transparent',width=300,height=400)
frame1.place(x=0,y=0)

bgframe = PhotoImage(file="bg.png")
bglabel = Label(frame1, image=bgframe, bg="#331e38")
bglabel.place(x=0,y=0)

## Funkcje
def zalozkonto():
    username = uzytkownikentry.get()
    password = hasloentry.get()

    if username != '' and password != '':
        cursor.execute('SELECT username FROM users WHERE username=?', [username])
        if cursor.fetchone() is not None:
            messagebox.showerror('Błąd', 'Nazwa użytkownika zajęta.')
        else:
            #####tu skan twarzy
            encoded_password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
            print(hashed_password)
            cursor.execute('INSERT INTO users VALUES (?, ?, ?)', [username, hashed_password])
            baza.commit()
            messagebox.showinfo('Sukces', 'Twoje konto zostało stworzone.')
    else:
        messagebox.showerror('Błąd', 'Wprowadź nazwę użytkownika i hasło.')

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
                                      command=flogin,
                                      cursor='hand2', border_width=1, border_color='#38303b',
                                      hover_color='#262326')
    loginbutton.place(x=61, y=120)

def flogin():
    username = uzytkownikentry2.get()
    password = hasloentry2.get()

    if username != '' and password != '':
        cursor.execute('SELECT password FROM users WHERE username=?', [username])
        result = cursor.fetchone()

        if result:
            if bcrypt.checkpw(password.encode('utf-8'), result[0]):
                messagebox.showinfo('Sukces', 'Zalogowano się pomyślnie.')
            else:
                messagebox.showerror('Błąd', 'Wprowadzono niepasujące dane.')
        else:
            messagebox.showerror('Błąd', 'Wprowadź poprawne dane.')

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
                                      command=zalozkonto,
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

###
app.mainloop()