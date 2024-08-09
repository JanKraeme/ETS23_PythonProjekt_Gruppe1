import tkinter as tk
from tkinter import filedialog

def choose_file():
    fenster = tk.Tk()
    fenster.withdraw()

filedialog = filedialog.askopenfilename()


choose_file()