import tkinter as tk
from tkinter import filedialog
import os

print("Willkommen beim ETS-Supplychain-Project" "\n" "Zur Übverprüfung einer Kühlkette einen der beiden Menüpunkte mit 1 oder 2 auswählen!")

def choose_file():
    fenster = tk.Tk()
    fenster.withdraw()
    dateipfad = filedialog.askopenfilename()
    fenster.update()


def menueMatch():
    mnuepunkt = int(input("Menü:" "\n" "1. Manuelle Eingabe der Transport-IDs" "\n" "2. Überprüfung der Transport-IDs anhand einer Datenbank" "\n"))

    # match case
    match mnuepunkt:
        # pattern 1
        case 1:
            transID = input("Manuelle Eingabe der Transport-IDs" "\n" "Geben Sie die zur überprüfende Transport-ID ein!" "\n")
            if transID == "exit":
                menueMatch()
        # pattern 2
        case 2:
            print("Überprüfung der Transport-IDs anhand einer Datenbank" "\n" "Wählen Sie eine Datenbank im Explorer aus!")            
            choose_file()
        # default pattern
        case _:
            print("Fehlerhafte Eingabe, bitte nochmal versuchen!")
            menueMatch()

menueMatch()
