import pyodbc
import re
import datetime
import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk

def lade_db_daten():
    global cursor, conn, db_daten
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

        # Verbindung herstellen
    try:
        conn = pyodbc.connect(conn_str)
    except:
        tk.messagebox.showerror(title="Fehler", message="Keine Verbindung zur Datenbank möglich!")

    # Cursor erstellen
    cursor = conn.cursor()
    
    # SQL-Statement ausführen
    try:
        cursor.execute('SELECT company, transportid, transportstation, category, direction, datetime FROM coolchain1')      #REGEX nicht möglich, da in pyobdc nicht vorhanden!!! wie über "re" gemacht
        #return cursor
    except:
        tk.messagebox.showerror(title="Fehler", message="Kein Datensatz in der Datenbank gefunden!")
    
    # for row in cursor.tables():
    #     print(row)
    db_daten = []

    for row in cursor:
        db_daten.append({'company':row.company, 'transportid':row.transportid, 'transportstation':row.transportstation, 'category':row.category, 'direction':row.direction, 'datetime':row.datetime})
        print(db_daten['transportid'])
    
 #   global transport_id
#    transport_id = db_daten['transportid']
   
    # for row in cursor:
    #     row_data = tuple(str(value) for value in row)
    #     db_daten.append(row_data)
    #     print(row_data)

    # db_daten_split = []
    # for row in db_daten:
    #     new_row = tuple(item.replace('"', '').replace("'", '') for item in row for item in row)
    #     db_daten_split.append(new_row)

    # print(db_daten_split)
    #db_daten = cursor.fetchall()
    #df = pd.DataFrame(db_daten, columns=['company', 'transportid', 'transportstation', 'category', 'direction', 'datetime'])
    

def schließe_db():
        # Verbindung schließen
    cursor.close()
    conn.close()

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

    global combo_transid, label21

    fenster_manuell = tk.Toplevel(fenster_hauptmenue)
    fenster_manuell.title("manuelle Überprüfung")
    fenster_manuell.geometry("1000x500")
    fenster_manuell.grab_set()

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

    lade_db_daten()

# Ergebnisse ausgeben

    transid_cb = []
    for row in transport_id:
        transid_cb_st = re.sub('\D', '', str(row))
        if transid_cb_st not in transid_cb[1]:
            transid_cb[1].append(transid_cb_st)

    combo_transid['values'] = transid_cb

    schließe_db()
    
    

def read_transid():
    transid = combo_transid.get()  # Liest den Wert in der ComboBox
    if transid:
        label21.config(text=transid)
        #return transid
    else:
        tk.messagebox.showerror(title="Fehler", message="keine Transport-ID ausgewählt!")
        




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
  
    verifikation_auswertung()
    transid_nr = 0
    for transid_csv in transid_val:
        transid_nr += 1 #Nr. in der Tabelle zuweisen
        tree.insert("", "end", values=(transid_nr ,transid_csv , "Verifikation"))
    #     for rows in db_liste:
    #         if transid_csv in rows:
    #             db_listenr.append(rows) #db_listenr beinhaltet jetzt nur noch die Daten mit den IDs aus der csv
                #print(db_listenr)



    # Füge einen Scrollbalken hinzu
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    
    #verifikation_auswertung()
def verifikation_auswertung():
    lade_db_daten()
    #print(cursor)
    #datenauswertung_csv(ergebnis)

    
    db_liste = []
    db_listenr = []

    # for row in cursor:
    #     db_liste.append(row)

    # print(db_liste)

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

    schließe_db()

# Hauptfenster anzeigen
fenster_hauptmenue.mainloop()



