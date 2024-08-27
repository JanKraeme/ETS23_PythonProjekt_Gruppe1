import pyodbc
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta

def lade_db_daten():
    global cursor, conn, db_daten
    server = 'sc-db-server.database.windows.net'
    database = 'supplychain'
    username = 'rse'
    password = 'Pa$$w0rd'
    conn_str = (
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password}'
    )

    try:
        conn = pyodbc.connect(conn_str)
    except Exception as e:
        messagebox.showerror(title="Fehler", message=f"Keine Verbindung zur Datenbank möglich! {e}")
        return

    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT company, transportid, transportstation, category, direction, datetime FROM coolchain1')
    except Exception as e:
        messagebox.showerror(title="Fehler", message=f"Kein Datensatz in der Datenbank gefunden! {e}")
        return
    
    db_daten = []
    transport_ids = set()

    for row in cursor:
        db_daten.append({
            'company': row.company, 
            'transportid': row.transportid, 
            'transportstation': row.transportstation, 
            'category': row.category, 
            'direction': row.direction, 
            'datetime': row.datetime
        })
        transport_ids.add(row.transportid)

    # Dropdown-Liste mit allen Transport-IDs aktualisieren
    unique_ids = sorted(transport_ids)
    combobox_transid['values'] = unique_ids
    if unique_ids:
        combobox_transid.current(0)  # Standardmäßig die erste ID auswählen

def schließe_db():
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def start_fenster_manuell():
    global combobox_transid, label_duration, tree

    fenster_manuell = tk.Toplevel(fenster_hauptmenue)
    fenster_manuell.title("Manuelle Überprüfung")
    fenster_manuell.geometry("1000x600")
    fenster_manuell.configure(bg="#f0f0f0")  # Hintergrundfarbe setzen

    labelTop = tk.Label(fenster_manuell, text="Transport-ID auswählen:", bg="#f0f0f0", font=("Helvetica", 12))
    labelTop.grid(column=0, row=0, padx=10, pady=10)

    combobox_transid = ttk.Combobox(fenster_manuell, width=25, font=("Helvetica", 12), state="readonly")
    combobox_transid.grid(column=1, row=0, padx=10, pady=10)

    button3 = tk.Button(fenster_manuell, text="ID überprüfen", command=read_transid, bg="#007BFF", fg="white", font=("Helvetica", 12))
    button3.grid(column=2, row=0, padx=10, pady=10)

    label_duration = tk.Label(fenster_manuell, text="", bg="#f0f0f0", font=("Helvetica", 12))
    label_duration.grid(column=1, row=1, padx=10, pady=10)

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

    # Canvas für LKW-Symbol und Freeze-Symbol erstellen
    canvas = tk.Canvas(fenster_manuell, width=600, height=100, bg="#f0f0f0", highlightthickness=0)
    canvas.grid(row=3, column=0, columnspan=4, pady=20)

    # LKW-Symbol und Freeze-Symbol als Text hinzufügen
    truck_icon_text = "🚚"  # Unicode LKW-Symbol
    freeze_icon_text = "❄️"  # Unicode Freeze-Symbol
    
    truck_x = 100
    freeze_x = 300
    text_x = freeze_x + 130  # Abstand von 80 Einheiten hinter dem Freeze-Symbol
    
    # Icons und Text im Canvas platzieren
    canvas.create_text(truck_x, 50, text=truck_icon_text, font=("Helvetica", 72), fill="black")
    canvas.create_text(freeze_x, 50, text=freeze_icon_text, font=("Helvetica", 72), fill="blue")
    canvas.create_text(text_x, 50, text="Coolchain-ETS", font=("Helvetica", 24), fill="black")

    # Daten laden, um das Dropdown-Menü zu füllen
    lade_db_daten()

def read_transid():
    transid = combobox_transid.get().strip()  # Die ausgewählte ID aus der Combobox abrufen und Leerzeichen entfernen

    # Überprüfen, ob die ID Sonderzeichen enthält
    if any(char not in "0123456789" for char in transid):
        label_duration.config(text="Fehlerhafte Transport-ID!", fg="red")
        for item in tree.get_children():
            tree.delete(item)
    else:
        verifikation_auswertung(transid)

def verifikation_auswertung(transid):
    for item in tree.get_children():
        tree.delete(item)

    daten_id = list(filter(lambda item: item["transportid"] == transid, db_daten))

    if daten_id:
        daten_id.sort(key=lambda x: x["datetime"])  # Sortiere nach Datum
        for eintrag in daten_id:
            tree.insert("", "end", values=(eintrag["company"], eintrag["transportstation"], eintrag["category"], eintrag["direction"], eintrag["datetime"]))
        
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
            label_duration.config(text=f'Transportdauer überschreitet 48 Stunden: {zeit_format}', fg="red")
        else:
            label_duration.config(text=f'Transportdauer innerhalb von 48 Stunden: {zeit_format}', fg="green")
    else:
        label_duration.config(text='Transport-ID nicht vorhanden.', fg="red")

    schließe_db()

fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("1000x500")
fenster_hauptmenue.title("Coolchain")
fenster_hauptmenue.configure(bg="#f0f0f0")  # Hintergrundfarbe setzen

label1 = tk.Label(fenster_hauptmenue, text="Willkommen beim ETS-Supplychain-Project", bg="#f0f0f0", font=("Helvetica", 14))
label1.pack(pady=20)

button1 = tk.Button(fenster_hauptmenue, text="Manuelle Eingabe der Transport-IDs", command=start_fenster_manuell, bg="#007BFF", fg="white", font=("Helvetica", 12))
button1.pack(pady=10)

fenster_hauptmenue.mainloop()
