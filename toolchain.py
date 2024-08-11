import tkinter as tk
from tkinter import filedialog

def button_click_1():
    open_new_window()

def button_click_2():
    print("Button 2 wurde gedrückt!")


# Hauptfenster erstellen
root = tk.Tk()
root.geometry("1000x500")
root.title("Coolchain")

label1 = tk.Label(root, text="Willkommen beim ETS-Supplychain-Project" "\n" "Zur Übverprüfung einer Kühlkette einen der beiden Menüpunkte auswählen!")
label1.pack()


# Button 1 erstellen
button1 = tk.Button(root, text="Manuelle Eingabe der Transport-IDs", command=button_click_1)
button1.pack()

# Button 2 erstellen
button2 = tk.Button(root, text="Überprüfung der Transport-IDs anhand einer Datenbank", command=button_click_2)
button2.pack()


def open_new_window():
    new_window = tk.Toplevel(root)
    new_window.title("Neues Fenster")
    new_window.geometry("1000x500")
    new_window.grab_set()


    def read_text():
        text = text_entry.get()  # Liest den gesamten Text
        print(text)

    # Textbox erstellen
    label = tk.Label(new_window, text="Transport-ID")
    label.pack()
    text_entry = tk.Entry(new_window)
    text_entry.pack()
        # Button 3 erstellen
    button3 = tk.Button(new_window, text="ID Überprüfen", command=read_text)
    button3.pack()




# Hauptfenster anzeigen
root.mainloop()


# print("Willkommen beim ETS-Supplychain-Project" "\n" "Zur Übverprüfung einer Kühlkette einen der beiden Menüpunkte mit 1 oder 2 auswählen!")

# def choose_file():
#         file_path = filedialog.askopenfilename(title="Datensatz auswählen", filetypes=[("Text File", ('*.txt')), ("All files", "*.*")])


# def menueMatch():
#     #global file_path
#     menuepunkt = int(input("Menü:" "\n" "1. Manuelle Eingabe der Transport-IDs" "\n" "2. Überprüfung der Transport-IDs anhand einer Datenbank" "\n"))

#     # match case
#     match menuepunkt:
#         # pattern 1
#         case 1:
#             transID = input("Manuelle Eingabe der Transport-IDs" "\n" "Geben Sie die zur überprüfende Transport-ID ein!" "\n")
#             if transID == "exit":
#                 menueMatch()
#         # pattern 2
#         case 2:
#            # print("Überprüfung der Transport-IDs anhand einer Datenbank" "\n" "Wählen Sie eine Datenbank im Explorer aus!")            
#             root = tk.Tk()
#             button = tk.Button(root, text="Datei auswählen", command=choose_file)
#             button.pack()
#             root.mainloop()
#         # default pattern
#         case _:
#             print("Fehlerhafte Eingabe, bitte nochmal versuchen!")
#             menueMatch()


# menueMatch()

