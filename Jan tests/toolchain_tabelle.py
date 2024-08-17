import pyodbc
import re
import datetime
import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk

# Verbindungsdaten
server = 'sc-db-server.database.windows.net'
database = 'supplychain' # Setze den Namen deiner Datenbank hier ein
username = 'rse'
password = 'Pa$$w0rd'
# Verbindungsstring
conn_str = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

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

    def read_transid():
        transid = combo_transid.get()  # Liest den Wert in der ComboBox
        if transid:
            label21.config(text=transid)
            #return transid
        else:
            tk.messagebox.showerror(title="Fehler", message="keine Transport-ID ausgewählt!")
        
    labelTop = tk.Label(fenster_manuell, text="Transport-ID auswählen:")
    labelTop.grid(column=0, row=0)

    label2 = tk.Label(fenster_manuell, text="Transport ID:")
    label2.grid(column=0, row=10)

    label21 = tk.Label(fenster_manuell, text="")
    label21.grid(column=10, row=10)

    label3 = tk.Label(fenster_manuell, text="Verifikation:")
    label3.grid(column=0, row=20)

    label31 = tk.Label(fenster_manuell, text="Hier ermittelte Verifikation")
    label31.grid(column=10, row=20)

    # Button 3 erstellen
    button3 = tk.Button(fenster_manuell, text="ID überprüfen", command=read_transid)
    button3.grid(column=25, row=0)

    combo_transid = ttk.Combobox(fenster_manuell, width=25)
    #print(dict(combo_transid))
    combo_transid.grid(column=10, row=0)

    # Verbindung herstellen
    try:
        conn = pyodbc.connect(conn_str)
    except:
        tk.messagebox.showerror(title="Fehler", message="Keine Verbindung zur Datenbank möglich!")

    # Cursor erstellen
    cursor = conn.cursor()
    
    # SQL-Statement ausführen
    try:
        cursor.execute('SELECT transportid FROM coolchain1')      #REGEX nicht möglich, da in pyobdc nicht vorhanden!!! wie über "re" gemacht
    except:
        tk.messagebox.showerror(title="Fehler", message="Kein Datensatz in der Datenbank gefunden!")
    # Ergebnisse ausgeben

    transid_cb = []
    for row in cursor:
        transid_cb_st = re.sub('\D', '', str(row))
        if transid_cb_st not in transid_cb:
            transid_cb.append(transid_cb_st)

    combo_transid['values'] = transid_cb

    # Verbindung schließen
    cursor.close()
    conn.close()


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

    # Verbindung herstellen
    try:
        conn = pyodbc.connect(conn_str)
    except:
        tk.messagebox.showerror(title="Fehler", message="Keine Verbindung zur Datenbank möglich!")

    # Cursor erstellen
    cursor = conn.cursor()
    
    # SQL-Statement ausführen
    try:
        cursor.execute('SELECT * FROM coolchain1')      #REGEX nicht möglich, da in pyobdc nicht vorhanden!!! wie über "re" gemacht
    except:
        tk.messagebox.showerror(title="Fehler", message="Kein Datensatz in der Datenbank gefunden!")
    
    # Ergebnisse ausgeben
    #for row in cursor:
    #    print(row)


    transid_nr = 0
    db_liste = []
    db_listenr = []
    df = pd.DataFrame(db_listenr, columns=['company', 'transportid', 'transportstation', 'category', 'direction', 'datetime'])

    for row in cursor:
        db_liste.append(row)

    

    for transid_csv in transid_val:
        transid_nr += 1 #Nr. in der Tabelle zuweisen
        tree.insert("", "end", values=(transid_nr ,transid_csv , "Verifikation"))
        for rows in db_liste:
            if transid_csv in rows:
                db_listenr.append(rows) #db_listenr beinhaltet jetzt nur noch die Daten mit den IDs aus der csv
                print(db_listenr)

#Hier tupple auswerten maybe alles in eine function
# def kategorisiere(row):
#     if row['Status'] == 'out':
#         return 'Versendet'
#     # ... weitere Bedingungen
#     return 'Unbekannt'

# df['Kategorie'] = df.apply(kategorisiere, axis=1)
    # for wert in db_listenr:
    #     if df['transportid'] == transid_csv
            #else:
                #print(transid_csv, "existiert nicht")


    # Füge einen Scrollbalken hinzu
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

        # Verbindung schließen
    cursor.close()
    conn.close()


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

