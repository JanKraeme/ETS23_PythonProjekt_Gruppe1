import tkinter as tk
from tkinter import filedialog, ttk

def button_click_1():
    start_fenster_manuell()

def button_click_2():
    global transid_val
    print("Button 2 wurde gedrückt!")
    file_path = filedialog.askopenfilename(title="Datensatz auswählen", filetypes=[("CSV Files",("*.csv")), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            lines = file.readlines()  

            data = []
            for line in lines:
                transid_val = line.strip().split(';')
                data.append(transid_val)
        print(data)
        datenauswertung_csv()
    else:
        tk.messagebox.showerror(title="Fehler", message="keine Datei ausgewählt oder falsches Format!")

# Hauptfenster erstellen
fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("1000x500")
fenster_hauptmenue.title("Coolchain")

label1 = tk.Label(fenster_hauptmenue, text="Willkommen beim ETS-Supplychain-Project" "\n" "Zur Übverprüfung einer Kühlkette einen der beiden Menüpunkte auswählen!")
label1.pack()


# Button 1 erstellen
button1 = tk.Button(fenster_hauptmenue, text="Manuelle Eingabe der Transport-IDs", command=button_click_1)
button1.pack()

# Button 2 erstellen
button2 = tk.Button(fenster_hauptmenue, text="Überprüfung der Transport-IDs anhand einer Datenbank", command=button_click_2)
button2.pack()


def start_fenster_manuell():
    fenster_manuell = tk.Toplevel(fenster_hauptmenue)
    fenster_manuell.title("manuelle Überprüfung")
    fenster_manuell.geometry("1000x500")
    fenster_manuell.grab_set()


    # def read_text():
    #     text = text_entry.get()  # Liest den gesamten Text
    #     print(text)

    # Textbox erstellen
    # label = tk.Label(fenster_manuell, text="Transport-ID")
    # label.pack()
    # text_entry = tk.Entry(fenster_manuell)
    # text_entry.pack()

    def read_transid():
        transid = combo_transid.get()  # Liest den Wert in der ComboBox
        if transid:
            print(transid)
        else:
            tk.messagebox.showerror(title="Fehler", message="keine Transport-ID ausgewählt!")

    labelTop = tk.Label(fenster_manuell, text="Transport-ID auswählen:")
    labelTop.grid(column=0, row=0)

    label2 = tk.Label(fenster_manuell, text="Transport ID:")
    label2.grid(column=0, row=10)

    label21 = tk.Label(fenster_manuell, text="Hier überprüfte ID")
    label21.grid(column=10, row=10)

    label3 = tk.Label(fenster_manuell, text="Verifikation:")
    label3.grid(column=0, row=20)

    label31 = tk.Label(fenster_manuell, text="Hier ermittelte Verifikation")
    label31.grid(column=10, row=20)

    combo_transid = ttk.Combobox(fenster_manuell, values=["Hier die Transport-IDs aus der Datenbank!"])
    print(dict(combo_transid))
    combo_transid.grid(column=10, row=0)

        # Button 3 erstellen
    button3 = tk.Button(fenster_manuell, text="ID überprüfen", command=read_transid)
    button3.grid(column=25, row=0)


def datenauswertung_csv():
    # Erstelle das Hauptfenster
    root = tk.Tk()
    root.title("Tabelle mit drei Spalten")

    # Erstelle einen Frame für die Tabelle
    table_frame = ttk.Frame(root)
    table_frame.pack(fill="both", expand=True)

    # Erstelle die Treeview-Komponente für die Tabelle
    tree = ttk.Treeview(table_frame, columns=("Nr", "ID", "Verifikation"))
    tree.heading("Nr", text="Nr")
    tree.heading("ID", text="ID")
    tree.heading("Verifikation", text="Verifikation")
    tree.pack(fill="both", expand=True)

    transid_nr = 0
    # Füge einige Beispiel-Daten hinzu
    for transid_csv in transid_val:
        transid_nr += 1 #Nr. in der Tabelle zuweisen
        tree.insert("", "end", values=(transid_nr ,transid_csv , "Verifikation"))

    # Füge einen Scrollbalken hinzu
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")


# Hauptfenster anzeigen
fenster_hauptmenue.mainloop()



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
#             fenster_hauptmenue = tk.Tk()
#             button = tk.Button(fenster_hauptmenue, text="Datei auswählen", command=choose_file)
#             button.pack()
#             fenster_hauptmenue.mainloop()
#         # default pattern
#         case _:
#             print("Fehlerhafte Eingabe, bitte nochmal versuchen!")
#             menueMatch()


# menueMatch()

