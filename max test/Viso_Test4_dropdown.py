import pyodbc
import tkinter as tk
from tkinter import ttk
from datetime import timedelta

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
    except:
        tk.messagebox.showerror(title="Fehler", message="Keine Verbindung zur Datenbank möglich!")
        return

    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT company, transportid, transportstation, category, direction, datetime FROM coolchain1')
    except:
        tk.messagebox.showerror(title="Fehler", message="Kein Datensatz in der Datenbank gefunden!")
        return
    
    db_daten = []
    for row in cursor:
        db_daten.append({
            'company': row.company, 
            'transportid': row.transportid, 
            'transportstation': row.transportstation, 
            'category': row.category, 
            'direction': row.direction, 
            'datetime': row.datetime
        })

    # Update the dropdown list with the unique transport IDs
    unique_ids = sorted(set(item["transportid"] for item in db_daten))
    combobox_transid['values'] = unique_ids
    if unique_ids:
        combobox_transid.current(0)  # Select the first ID by default

def schließe_db():
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def start_fenster_manuell():
    global combobox_transid, label31, tree, fenster_manuell

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

    label31 = tk.Label(fenster_manuell, text="", bg="#f0f0f0", font=("Helvetica", 12))
    label31.grid(column=1, row=1, padx=10, pady=10)

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

    # Load data to populate the dropdown
    lade_db_daten()

def read_transid():
    transid = combobox_transid.get()  # Get the selected ID from the combobox
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
        daten_id.sort(key=lambda x: x["datetime"])  # Sortiere nach Datum
        last_out = None
        critical_time_exceeded = False
        
        for eintrag in daten_id:
            tree.insert("", "end", values=(eintrag["company"], eintrag["transportstation"], eintrag["category"], eintrag["direction"], eintrag["datetime"]))
            
            if eintrag["direction"] == 'out':
                last_out = eintrag["datetime"]
            elif eintrag["direction"] == 'in' and last_out:
                duration = eintrag["datetime"] - last_out
                
                # Berechnung der Differenz
                if duration > timedelta(minutes=10):
                    critical_time_exceeded = True

                last_out = None  # Zurücksetzen für den nächsten Zyklus

        start_time = daten_id[0]["datetime"]
        end_time = daten_id[-1]["datetime"]
        total_duration = end_time - start_time

        tage = total_duration.days
        stunden, minuten = divmod(total_duration.seconds, 3600)
        minuten //= 60

        if tage == 1:
            zeit_format = f"{tage} Tag, {stunden} Stunden, {minuten} Minuten"
        else:
            zeit_format = f"{tage} Tage, {stunden} Stunden, {minuten} Minuten"

        if total_duration > timedelta(hours=48):
            label31.config(text=f'Transportdauer überschreitet 48 Stunden: {zeit_format}', fg="red")
        else:
            label31.config(text=f'Transportdauer innerhalb von 48 Stunden: {zeit_format}', fg="green")
        
        # Anzeige der kritischen Meldung bei Überschreitung der 10 Minuten Grenze
        if critical_time_exceeded:
            label_critical_time = tk.Label(fenster_manuell, text="Eine Zeitüberschreitung von 10 Minuten wurde festgestellt!", fg="red", font=("Helvetica", 12))
            label_critical_time.grid(column=1, row=2, padx=10, pady=10)
        
    else:
        label31.config(text='Transport-ID nicht vorhanden.', fg="red")

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
