import pyodbc
import re
import datetime
from datetime import timedelta
import tkinter as tk
from tkinter import filedialog, ttk

def lade_db_daten():
    global cursor, conn, db_daten, db_datetime, db_direction
    # Verbindungsdaten
    server = 'sc-db-server.database.windows.net'
    database = 'supplychain'
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
        return

    # Cursor erstellen
    cursor = conn.cursor()

    # SQL-Statement ausführen
    try:
        cursor.execute('SELECT company, transportid, transportstation, category, direction, datetime FROM coolchain1')
    except:
        tk.messagebox.showerror(title="Fehler", message="Kein Datensatz in der Datenbank gefunden!")
        return

    db_daten = []
    db_datetime = []
    db_direction = []

    for row in cursor:
        # Clean the transportid by removing all non-numeric characters
        clean_id = re.sub(r'\D', '', row.transportid)
        db_daten.append({
            'company': row.company,
            'transportid': clean_id,
            'transportstation': row.transportstation,
            'category': row.category,
            'direction': row.direction,
            'datetime': row.datetime
        })
        db_datetime.append({
            'datetime': row.datetime,
            'direction': row.direction,
            'transportid': clean_id
        })
        db_direction.append({
            'transportid': clean_id,
            'direction': row.direction
        })

    # Update combobox with unique transport IDs
    unique_ids = sorted(set(item["transportid"] for item in db_daten))
    combo_transid['values'] = unique_ids
    if unique_ids:
        combo_transid.current(0)  # Select the first ID by default

def schließe_db():
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def button_click_1():
    start_fenster_manuell()

def button_click_2():
    global transid_val
    file_path = filedialog.askopenfilename(title="Datensatz auswählen", filetypes=[("CSV Files", ("*.csv")), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            lines = file.readlines()  

            data = []
            for line in lines:
                transid_val = line.strip().split(';')
                data.append(transid_val)
        datenauswertung_csv()
    else:
        tk.messagebox.showerror(title="Fehler", message="keine Datei ausgewählt oder falsches Format!")

def start_fenster_manuell():
    global combo_transid, label31, label32, tree

    fenster_manuell = tk.Toplevel(fenster_hauptmenue)
    fenster_manuell.title("Manuelle Überprüfung")
    fenster_manuell.geometry("1000x600")
    fenster_manuell.configure(bg="#f0f0f0")

    labelTop = tk.Label(fenster_manuell, text="Transport-ID auswählen:", bg="#f0f0f0", font=("Helvetica", 12))
    labelTop.grid(column=0, row=0, padx=10, pady=10)

    combo_transid = ttk.Combobox(fenster_manuell, width=25, font=("Helvetica", 12), state="readonly")
    combo_transid.grid(column=1, row=0, padx=10, pady=10)

    button3 = tk.Button(fenster_manuell, text="ID überprüfen", command=read_transid, bg="#007BFF", fg="white", font=("Helvetica", 12))
    button3.grid(column=2, row=0, padx=10, pady=10)

    label31 = tk.Label(fenster_manuell, text="", bg="#f0f0f0", font=("Helvetica", 12))
    label31.grid(column=1, row=1, padx=10, pady=10)
    label32 = tk.Label(fenster_manuell, text="", bg="#f0f0f0", font=("Helvetica", 12))
    label32.grid(column=1, row=2, padx=10, pady=10)

    tree = ttk.Treeview(fenster_manuell, columns=("company", "transportstation", "category", "direction", "datetime"), show='headings')
    tree.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    tree.heading("company", text="Unternehmen")
    tree.heading("transportstation", text="Transport Station")
    tree.heading("category", text="Kategorie")
    tree.heading("direction", text="Richtung")
    tree.heading("datetime", text="Uhrzeit")

    scrollbar = ttk.Scrollbar(fenster_manuell, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=2, column=3, sticky="ns")

    # Load data and populate combobox
    lade_db_daten()

def read_transid():
    transid = combo_transid.get().strip()  # Get the selected ID from the combobox
    if transid:
        label31.config(text=transid)
        verifikation_auswertung(transid)
    else:
        tk.messagebox.showerror(title="Fehler", message="Keine Transport-ID ausgewählt!")

def verifikation_auswertung(transid):
    for item in tree.get_children():
        tree.delete(item)

    daten_id = list(filter(lambda item: item["transportid"] == transid, db_daten))

    if daten_id:
        daten_id.sort(key=lambda x: x["datetime"])  # Sort by datetime

        # First, check if the transport duration exceeds 48 hours
        start_time = daten_id[0]["datetime"]
        end_time = daten_id[-1]["datetime"]
        duration = end_time - start_time

        tage = duration.days
        stunden, minuten = divmod(duration.seconds, 3600)
        minuten //= 60

        if tage == 1:
            zeit_format = f"{tage} Tag, {stunden} Stunden, {minuten} Minuten"
        else:
            zeit_format = f"{tage} Tage, {stunden} Stunden, {minuten} Minuten"

        if duration > timedelta(hours=48):
            label31.config(text=f'Transportdauer überschreitet 48 Stunden: {zeit_format}', fg="red")
        else:
            label31.config(text=f'Transportdauer innerhalb von 48 Stunden: {zeit_format}', fg="green")

        # Insert data into treeview
        for eintrag in daten_id:
            tree.insert("", "end", values=(eintrag["company"], eintrag["transportstation"], eintrag["category"], eintrag["direction"], eintrag["datetime"]))

        # Check direction sequence
        daten_direction = list(filter(lambda item: item["transportid"] == transid, db_direction))
        if not check_direction(daten_direction):
            return

    else:
        label31.config(text='Transport-ID nicht vorhanden.', fg="red")

    schließe_db()

def check_direction(daten_direction):
    for index, item in enumerate(daten_direction):
        value_in_out = item['direction']
        if index % 2 == 0:
            if value_in_out != "'in'":
                label32.config(text='Fehler: Zweimal nacheinander ausgecheckt!', fg="red")
                return False
        else:
            if value_in_out != "'out'":
                label32.config(text='Fehler: Zweimal nacheinander eingecheckt!', fg="red")
                return False

    last_line = daten_direction[-1]
    last_direction = last_line['direction']
    if last_direction != "'out'":
        label32.config(text='Auschecken am Ende fehlt', fg="red")
        return False

    return True

def datenauswertung_csv():
    root = tk.Tk()
    root.title("Tabelle mit drei Spalten")

    table_frame = ttk.Frame(root)
    table_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(table_frame, columns=("Nr", "ID", "Verifikation"))
    tree.heading("Nr", text="Nr")
    tree.heading("ID", text="ID")
    tree.heading("Verifikation", text="Verifikation")
    tree.pack(fill="both", expand=True)

    transid_nr = 0
    for transid_csv in transid_val:
        transid_nr += 1
        tree.insert("", "end", values=(transid_nr, transid_csv, "Verifikation"))

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

# Hauptfenster erstellen
fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("1000x500")
fenster_hauptmenue.title("Coolchain")
fenster_hauptmenue.configure(bg="#f0f0f0")

label1 = tk.Label(fenster_hauptmenue, text="Willkommen beim ETS-Supplychain-Project", bg="#f0f0f0", font=("Helvetica", 14))
label1.pack(pady=20)

button1 = tk.Button(fenster_hauptmenue, text="Manuelle Eingabe der Transport-IDs", command=button_click_1, bg="#007BFF", fg="white", font=("Helvetica", 12))
button1.pack(pady=10)

button2 = tk.Button(fenster_hauptmenue, text="Überprüfung der Transport-IDs anhand einer Datei", command=button_click_2, bg="#007BFF", fg="white", font=("Helvetica", 12))
button2.pack(pady=10)

fenster_hauptmenue.mainloop()
