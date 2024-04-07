__all__ = ["database_manager"]

import sqlite3
import cv2
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
               username TEXT NOT NULL,
               password TEXT NOT NULL,
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

	def close(self):
		self.conn.close()