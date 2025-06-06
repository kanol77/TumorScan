import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import tracemalloc
import gc
import time

class Program:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tumour Scan")
        self.root.geometry("800x600")

        # Wczytanie i wyświetlenie logo
        self.logo = Image.open("logo.png")
        self.logo = self.logo.resize((400, 400), Image.LANCZOS)  # Zmiana rozmiaru logo
        self.logo = ImageTk.PhotoImage(self.logo)
        self.logo_label = tk.Label(self.root, image=self.logo)
        self.logo_label.pack(pady=20)

        self.label = tk.Label(self.root, text="Tumour Scan", font=("Helvetica", 24))
        self.label.pack(pady=20)

        self.import_button = tk.Button(self.root, text="Import pliku", command=self.importPliku, font=("Helvetica", 16))
        self.import_button.pack(pady=20)

        self.root.mainloop()

    def importPliku(self):
        file_path = filedialog.askopenfilename(filetypes=[("NII files", "*.nii")])
        if file_path:
            self.root.destroy()
            self.uruchomProgram(file_path)

    def uruchomProgram(self, file_path):
        plik_nii = PlikNii(file_path)
        obraz = Obraz(plik_nii.otworz())
        InterfejsUzytkownika(obraz, file_path)
        plt.show()

class PlikNii:
    def __init__(self, nazwa):
        self.nazwa = nazwa

    def otworz(self):
        return nib.load(self.nazwa).get_fdata()

class Obraz:
    def __init__(self, dane):
        self.dane = dane
        self.typ = 'MRI'
        self.data_scaled = self.dane / np.max(self.dane)
        self.merged_image = np.stack((self.data_scaled[:, :, :, 0], 
                                      self.data_scaled[:, :, :, 1], 
                                      self.data_scaled[:, :, :, 2]), axis=-1)

    def wyswietl(self, warstwa, rzut='coronal'):
        if rzut == 'coronal':
            return self.merged_image[:, warstwa, :, :]
        elif rzut == 'sagittal':
            return self.merged_image[warstwa, :, :, :]
        elif rzut == 'axial':
            return self.merged_image[:, :, warstwa, :]

class Podswietlenie:
    def automatyczne(self, obraz):
        pass  

class Rzut:
    def __init__(self, interfejs):
        self.interfejs = interfejs

    def zmianaRzutu(self, typ_rzutu):
        self.interfejs.rzut = typ_rzutu
        self.interfejs.aktualizujSuwak()  # Aktualizuj suwak dla nowego rzutu
        self.interfejs.aktualizacjaWarstwy(self.interfejs.layer)

class Zaznaczenie:
    def zaznacz(self, punkty):
        pass 

class PowierzchniaPatologii:
    def wyznacz(self, zaznaczenie):
        pass  

class Opis:
    def dodaj(self, tekst):
        pass  

class Kolor:
    def podswietl(self, obraz, kolor):
        pass  

class InterfejsUzytkownika:
    def __init__(self, obraz, file_path):
        self.obraz = obraz
        self.file_path = file_path
        self.layer = 60  # Domyślna warstwa
        self.rzut = 'coronal'  # Domyślny rzut
        self.figure, self.ax_main = plt.subplots()
        self.figure.canvas.manager.set_window_title(f"Tumour Scan - {self.file_path.split('/')[-1]}")
        self.set_windowed_fullscreen()
        self.slider = None
        self.rzut_manager = Rzut(self)
        self.last_update_time = time.time()  # Track the last update time
        tracemalloc.start()  # Start tracing memory allocation
        self.inicjalizacjaUI()

    def set_windowed_fullscreen(self):
        mng = plt.get_current_fig_manager()
        # Get screen size
        screen_width = mng.window.winfo_screenwidth()
        screen_height = mng.window.winfo_screenheight()
        # Set window size to screen size minus small margins
        mng.window.state('zoomed')
        mng.resize(screen_width - 10, screen_height - 70)

    def inicjalizacjaUI(self):
        self.aktualizacjaWarstwy(self.layer)
        
        # Dodanie przycisku do wyboru innego pliku
        ax_choose_file = plt.axes([0.35, 0.92, 0.3, 0.04])
        self.btn_choose_file = Button(ax_choose_file, 'Wybierz inny plik')
        self.btn_choose_file.on_clicked(self.wybierzInnyPlik)

        # Tworzenie suwaka
        ax_slider = plt.axes([0.2, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')  # Moved down slightly
        self.slider = Slider(ax_slider, 'warstwa', 0, self.obraz.merged_image.shape[1] - 1, valinit=self.layer, valstep=1)
        self.slider.on_changed(self.zmianaWarstwySlider)

        # Dodanie przycisków do zmiany rzutu
        ax_coronal = plt.axes([0.1, 0.01, 0.2, 0.04])
        self.btn_coronal = Button(ax_coronal, 'Wieńcowy')
        self.btn_coronal.on_clicked(self.rzutWiencowy)

        ax_sagittal = plt.axes([0.4, 0.01, 0.2, 0.04])
        self.btn_sagittal = Button(ax_sagittal, 'Strzałkowy')
        self.btn_sagittal.on_clicked(self.rzutStrzalkowy)

        ax_axial = plt.axes([0.7, 0.01, 0.2, 0.04])
        self.btn_axial = Button(ax_axial, 'Osiowy')
        self.btn_axial.on_clicked(self.rzutOsiowy)

    def rzutWiencowy(self, event):
        print("Zmiana rzutu na wieńcowy")
        self.rzut = 'coronal'
        self.aktualizujSuwak()
        self.aktualizacjaWarstwy(self.layer)

    def rzutStrzalkowy(self, event):
        print("Zmiana rzutu na strzałkowy")
        self.rzut = 'sagittal'
        self.aktualizujSuwak()
        self.aktualizacjaWarstwy(self.layer)

    def rzutOsiowy(self, event):
        print("Zmiana rzutu na osiowy")
        self.rzut = 'axial'
        self.aktualizujSuwak()
        self.aktualizacjaWarstwy(self.layer)

    def wybierzInnyPlik(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("NII files", "*.nii")])
        if file_path:
            plt.close(self.figure)
            new_plik_nii = PlikNii(file_path)
            new_obraz = Obraz(new_plik_nii.otworz())
            InterfejsUzytkownika(new_obraz, file_path)

    def aktualizacjaWarstwy(self, warstwa):
        self.layer = int(warstwa)
        print(f"Updating layer to {self.layer}, view: {self.rzut}")
        choose_layer = self.obraz.wyswietl(self.layer, self.rzut)
        self.ax_main.clear()
        self.ax_main.imshow(choose_layer[:, :, 0], cmap='gray')
        if self.rzut == 'coronal':
            polish_rzut = "Wieńcowy"
        elif self.rzut == 'sagittal':
            polish_rzut = "Strzałkowy"
        else:
            polish_rzut = "Osiowy"

        self.ax_main.set_title(f"Widok {polish_rzut}")
        plt.draw()

        # Log memory usage
        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
        tracemalloc.clear_traces()
        gc.collect()  # Force garbage collection

    def zmianaWarstwySlider(self, val):
        current_time = time.time()
        if current_time - self.last_update_time > 0.1:  # Update at most every 0.1 seconds
            self.last_update_time = current_time
            self.aktualizacjaWarstwy(val)

    def aktualizujSuwak(self):
        if self.rzut == 'coronal':
            self.slider.valmax = self.obraz.merged_image.shape[1] - 1
        elif self.rzut == 'sagittal':
            self.slider.valmax = self.obraz.merged_image.shape[0] - 1
        elif self.rzut == 'axial':
            self.slider.valmax = self.obraz.merged_image.shape[2] - 1
        self.slider.ax.set_xlim(self.slider.valmin, self.slider.valmax)
        self.slider.set_val(self.layer)  

if __name__ == "__main__":
    program = Program()
