#Bibliotheken
import pyodbc
import re
import datetime
import tkinter as tk
from tkinter import filedialog, ttk

def lade_db_daten():
    global cursor, conn, db_daten, db_datetime, db_direction
    # Verbindungsdaten
    server = 'sc-db-server.database.windows.net'
    database = 'supplychain'  # Setze den Namen deiner Datenbank hier ein
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
        cursor.execute('SELECT company, transportid, transportstation, category, direction, datetime FROM coolchain1')
    except:
        tk.messagebox.showerror(title="Fehler", message="Kein Datensatz in der Datenbank gefunden!")
    
    db_daten = []
    db_datetime = []
    db_direction = []

    for row in cursor:
        db_daten.append({'company': row.company, 'transportid': row.transportid, 'transportstation': row.transportstation, 'category': row.category, 'direction': row.direction, 'datetime': row.datetime})
        db_datetime.append({'datetime': row.datetime, 'direction': row.direction, 'transportid': row.transportid})
        db_direction.append({'transportid': row.transportid, 'direction': row.direction})

def schließe_db():
    # Verbindung schließen
    cursor.close()
    conn.close()

def button_click_1():
    start_fenster_manuell()

def button_click_2():
    global transid_val
    print("Button 2 wurde gedrückt!")
    file_path = filedialog.askopenfilename(title="Datensatz auswählen", filetypes=[("CSV Files", ("*.csv")), ("All files", "*.*")])
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

label1 = tk.Label(fenster_hauptmenue, text="Willkommen beim ETS-Supplychain-Project\nZur Überprüfung einer Kühlkette einen der beiden Menüpunkte auswählen!")
label1.pack()

# Button 1 erstellen
button1 = tk.Button(fenster_hauptmenue, text="Manuelle Eingabe der Transport-IDs", command=button_click_1)
button1.pack()

# Button 2 erstellen
button2 = tk.Button(fenster_hauptmenue, text="Überprüfung der Transport-IDs anhand einer Datenbank", command=button_click_2)
button2.pack()

def start_fenster_manuell():
    global combo_transid, label21, label31

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

    label3 = tk.Label(fenster_manuell, text="Verifikation")
    label3.grid(column=0, row=20)

    label31 = tk.Label(fenster_manuell, text="")
    label31.grid(column=10, row=20)

    # Button 3 erstellen
    button3 = tk.Button(fenster_manuell, text="ID überprüfen", command=read_transid)
    button3.grid(column=25, row=0)

    combo_transid = ttk.Combobox(fenster_manuell, width=25)
    combo_transid.grid(column=10, row=0)

    lade_db_daten()

    # Transport IDs sammeln und in die combobox füllen
    transid_cb = []
    for i in range(len(db_daten)):
        transid_cb_st = re.sub(r'\D', '', str(db_daten[i]['transportid']))  # Überflüssige Zeichen entfernen
        if transid_cb_st not in transid_cb:  # Doppelte Werte ausschließen
            transid_cb.append(transid_cb_st)  # ID in Liste hinzufügen

    combo_transid['values'] = transid_cb  # Werte der ComboBox zuweisen

    schließe_db()

def read_transid():
    global transid
    transid = combo_transid.get()  # Liest den Wert in der ComboBox
    if transid:
        label21.config(text=transid)
        verifikation_auswertung()
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
  
    transid_nr = 0
    for transid_csv in transid_val:
        transid_nr += 1  # Nr. in der Tabelle zuweisen
        tree.insert("", "end", values=(transid_nr, transid_csv, "Verifikation"))

    # Füge einen Scrollbalken hinzu
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

# Function to check the direction sequence
def check_direction(daten_direction):
    for index, item in enumerate(daten_direction):
        value_in_out = item['direction']
        if index % 2 == 0:
            if value_in_out == "'in'":
                print(value_in_out, "i.o.")
            else:
                label31.config(text='Fehler: Zweimal nacheinander ausgecheckt!', fg="red")
                return False
        else:
            if value_in_out == "'out'":
                print(value_in_out, "i.o.")
            else:
                label31.config(text='Fehler: Zweimal nacheinander eingecheckt!', fg="red")
                return False

    last_line = daten_direction[-1]
    last_direction = last_line['direction']
    if last_direction == "'out'":
        print("Am Ende wurde ausgecheckt")
    else:
        label31.config(text='Auschecken am Ende fehlt', fg="red")
        return False

    return True

def verifikation_auswertung():
    print(transid)
    
    daten_id = list(filter(lambda item: item["transportid"] == transid, db_daten))
    daten_datetime = list(filter(lambda item: item["transportid"] == transid, db_datetime))
    daten_direction = list(filter(lambda item: item["transportid"] == transid, db_direction))
    
    # Check direction sequence first
    if not check_direction(daten_direction):
        return  # Exit early if there is a direction error

    if not daten_id:
        label31.config(text='Es gibt gar keinen Eintrag', fg="red")
        return

    daten_datetime.sort(key=lambda x: x['datetime'])

    verification_failed = False

    for i in range(1, len(daten_datetime) - 1, 2):
        out_record = daten_datetime[i] 
        in_record = daten_datetime[i + 1]

        print(f"Comparing OUT: {out_record['datetime']} with IN: {in_record['datetime']}")

        if out_record['direction'] == "'out'" and in_record['direction'] == "'in'":
            if isinstance(out_record['datetime'], str):
                out_record['datetime'] = datetime.datetime.strptime(out_record['datetime'], '%Y-%m-%d %H:%M:%S')
            if isinstance(in_record['datetime'], str):
                in_record['datetime'] = datetime.datetime.strptime(in_record['datetime'], '%Y-%m-%d %H:%M:%S')

            time_diff = (in_record['datetime'] - out_record['datetime']).total_seconds()
            print(f"Time difference: {time_diff} seconds")

            if time_diff > 600:
                verification_failed = True
                break
        else:
            verification_failed = True
            break
    
    if verification_failed:
        label31.config(text='Zeitüberschreitung: Übergabe > 10min', fg="red")
    else:
        label31.config(text='Verifikation erfolgreich', fg="green")

# Hauptfenster anzeigen
fenster_hauptmenue.mainloop()
