import threading  # Importowanie modułu do obsługi wątków
import copy  # Importowanie modułu do kopiowania obiektów
import cv2  # Importowanie biblioteki OpenCV do przetwarzania obrazów

# Klasa CameraReaderThread służy do ciągłego czytania ramek z kamery w osobnym wątku
class CameraReaderThread(threading.Thread):
   def __init__(self, camera, name='camera-reader-thread'):
      # Zainicjalizowanie zmiennej lock do synchronizacji dostępu do zasobów w wielowątkowości
      self.lock = threading.Lock()
      # Zmienna loop do kontrolowania działania pętli w wątku
      self.loop = threading.Event()
      # Zmienna camera przechowuje instancję obiektu kamery
      self.camera = camera
      # Zmienne curr_frame i last_frame do przechowywania bieżącej i ostatniej ramki
      self.curr_frame = None
      self.last_frame = None
      # Wywołanie konstruktora klasy bazowej i uruchomienie wątku
      super(CameraReaderThread, self).__init__(name=name)
      self.start()

   def run(self):
      # Nieskończona pętla do ciągłego czytania ramek z kamery
      while not self.loop.is_set():
         # Czytanie bieżącej ramki z kamery
         ret, self.curr_frame = self.camera.read()
         # Zablokowanie dostępu do zasobów podczas aktualizacji ostatniej ramki
         if not ret:
            break
         if self.lock.acquire(timeout=0):
            try:
               # Kopiowanie bieżącej ramki do ostatniej ramki
               self.last_frame = copy.copy(self.curr_frame)
            finally:
               # Odblokowanie dostępu do zasobów
               self.lock.release()

   def get(self):
      # Bezpieczne pobranie ostatniej ramki
      self.lock.acquire()
      try:
         return copy.copy(self.last_frame)
      finally:
         self.lock.release()

   def stop(self):
      # Zatrzymanie działania wątku
      self.loop.set()

# Tworzenie modelu do wykrywania twarzy z wykorzystaniem klasyfikatora Haar'a
model = cv2.CascadeClassifier('haarcascade_frontalface_alt_tree.xml')

# Ustalenie adresu strumienia wideo
address = 0    #zmieniamy wartość w zależności do ilu urządzeń jesteśmy podłączeni
# Nawiązanie połączenia ze strumieniem wideo
cap = cv2.VideoCapture(address)
if not cap.isOpened():
   # Komunikat o błędzie w przypadku niepowodzenia
   print("Video stream is not opened.")
   exit(0)

# Uruchomienie wątku do czytania ramek z kamery
reader = CameraReaderThread(cap)

# Główna pętla programu
while True:
   # Pobranie ostatniej ramki z wątku czytającego ramki
   frame = reader.get()
   if frame is not None:
      # Konwersja ramki na skalę szarości
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      # Wykrywanie twarzy w ramce
      faces = model.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5)
      # Rysowanie prostokątów wokół wykrytych twarzy
      for (x, y, w, h) in faces:
         cv2.rectangle(frame, (x, y), (x + w, y + h), (190, 0, 0), 2)
      # Wyświetlanie ramki z zaznaczonymi twarzami z nazwą okna
      cv2.imshow("Camera Feed", frame)
   # Oczekiwanie na naciśnięcie klawisza 'q' do zakończenia
   if cv2.waitKey(30) & 0xFF == ord('q'):
      break

# Zakończenie pracy wątku, zwolnienie zasobów kamery i zamknięcie wszystkich okien
reader.stop()
cap.release()
cv2.destroyAllWindows()

