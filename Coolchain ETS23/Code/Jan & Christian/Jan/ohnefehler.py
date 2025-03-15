# -------------------- Bibliotheken --------------------
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import requests
import json

# -------------------- Listen --------------------
daten_Company = []
daten_Coolchain = []
daten_Temp = []
daten_Transstation = []

# -------------------- Initialisierung --------------------
key = b'mysecretpassword'
iv = b'passwort-salzen!'
api_key = "Hier_bitte_Ihren_API-KEY_einfügen"  # <-- Visual Crossing API Key einfügen

# -------------------- Entschlüsselungsfunktion --------------------
def decrypt_value(encrypted_data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()

# -------------------- Datenbankverbindung --------------------
def connect_db():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=sc-db-server.database.windows.net;'
            'DATABASE=supplychain;'
            'UID=rse;'
            'PWD=Pa$$w0rd'
        )
        return conn
    except Exception as e:
        messagebox.showerror("Fehler", "Keine Verbindung zur Datenbank möglich!")
        print("Fehler:", e)
        return None

# -------------------- Temperaturüberwachung --------------------
def temperatur_überwachung():
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute('SELECT transportstationID, datetime, temperature FROM tempdata')
    daten_Temp.clear()
    for row in cursor.fetchall():
        daten_Temp.append({'stationID': row[0], 'datetime': row[1], 'temp': row[2]})
    cursor.close()
    conn.close()

    # Anzeige der kritischen Temperaturen
    fenster_temp = tk.Toplevel(fenster_hauptmenue)
    fenster_temp.title("Temperaturüberwachung")
    tree = ttk.Treeview(fenster_temp, columns=("stationID", "datetime", "temp"), show='headings')
    for col in ["stationID", "datetime", "temp"]:
        tree.heading(col, text=col.capitalize())
    tree.pack(expand=True, fill='both')

    for eintrag in daten_Temp:
        if eintrag['temp'] < 2 or eintrag['temp'] > 4:
            tree.insert("", "end", values=(eintrag['stationID'], eintrag['datetime'], f"{eintrag['temp']} °C"))

# -------------------- Wetterdatenabfrage --------------------
def wetter_abfrage(plz, datum):
    if plz == "0":  # Keine Wetterdaten für Fahrzeuge
        return "N/A"
    datetime_obj = datetime.strptime(str(datum), '%Y-%m-%d %H:%M:%S')
    timestamp = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{plz}/{timestamp}'
    response = requests.get(url, params={'unitGroup': 'metric', 'key': api_key, 'include': 'hours'})
    if response.status_code == 200:
        data = response.json()
        if 'days' in data and len(data['days']) > 0:
            return f"{data['days'][0]['temp']} °C"
    return "Fehler bei Wetterdaten"

# -------------------- Daten laden und entschlüsseln --------------------
def lade_db_daten():
    global db_daten, db_datetime, db_direction, db_zwischenzeit
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    db_daten = []
    db_datetime = []
    db_direction = []
    db_zwischenzeit = []
    
    transport_ids = set()

    # Coolchain
    cursor.execute('SELECT companyid, transportid, transportstationid, direction, datetime FROM coolchain')
    for row in cursor.fetchall():
        db_daten.append({'companyid': row[0], 'transportid': row[1], 'transportstationid': row[2], 'direction': row[3], 'datetime': row[4]})
        transport_ids.add(row[1])

    # Datetime, Direction und Zwischenzeit
    cursor.execute('SELECT transportid, datetime FROM coolchain')  # Angenommene Tabelle für datetime
    for row in cursor.fetchall():
        db_datetime.append({'transportid': row[0], 'datetime': row[1]})

    cursor.execute('SELECT transportid, direction FROM coolchain')  # Angenommene Tabelle für direction
    for row in cursor.fetchall():
        db_direction.append({'transportid': row[0], 'direction': row[1]})

    cursor.execute('SELECT transportid, transportstationid, direction FROM transportstation_crypt')  # Angenommene Tabelle für zwischenzeit
    for row in cursor.fetchall():
        db_zwischenzeit.append({'transportid': row[0], 'transportstationid': row[1], 'direction': row[2]})

    # Transport-ID Dropdown
    combobox_transid['values'] = sorted(transport_ids)
    if transport_ids:
        combobox_transid.current(0)

    cursor.close()
    conn.close()

# -------------------- Zeitüberschreitungen + Logikprüfung --------------------
def zeiten_auswertung(transid):
    # -------------------- Treeview leeren --------------------
    for item in tree.get_children():
        tree.delete(item)

    # -------------------- Transport-ID prüfen --------------------
    if not transid.strip():
        messagebox.showwarning("Achtung", "Bitte eine gültige Transport-ID auswählen!")
        return

    # -------------------- Daten zur Transport-ID laden --------------------
    daten_id = list(filter(lambda item: str(item["transportid"]) == str(transid), db_daten))
    daten_datetime_values = list(filter(lambda item: str(item["transportid"]) == str(transid), db_datetime))
    daten_direction = list(filter(lambda item: str(item["transportid"]) == str(transid), db_direction))
    daten_zwischenzeit = list(filter(lambda item: str(item["transportid"]) == str(transid), db_zwischenzeit))

    if not daten_id:
        messagebox.showinfo("Info", "Keine Daten zur ausgewählten Transport-ID gefunden.")
        return

    # -------------------- Tabelle füllen --------------------
    daten_id.sort(key=lambda x: x["datetime"])
    for eintrag in daten_id:
        tree.insert("", "end", values=(eintrag["companyid"], eintrag["transportstationid"], eintrag["direction"], eintrag["datetime"]))

    # -------------------- Transportdauer prüfen --------------------
    start_time = daten_id[0]["datetime"]
    end_time = daten_id[-1]["datetime"]
    duration = end_time - start_time
    tage = duration.days
    stunden, minuten = divmod(duration.seconds, 3600)
    minuten //= 60

    zeit_format = f"{tage} Tage, {stunden} Stunden, {minuten} Minuten" if tage != 1 else f"{tage} Tag, {stunden} Stunden, {minuten} Minuten"

    if duration > timedelta(hours=48):
        label_duration.config(text=f"Transportdauer überschreitet 48 Stunden: {zeit_format}", fg="red")
    else:
        label_duration.config(text=f"Transportdauer innerhalb von 48 Stunden: {zeit_format}", fg="green")

    # -------------------- In/Out Logik prüfen --------------------
    for index, item in enumerate(daten_direction):
        direction = item['direction'].strip("'")
        if index % 2 == 0 and direction != 'in':
            label_direction.config(text='Fehler: Zweimal nacheinander ausgecheckt!', fg="red")
            return
        elif index % 2 == 1 and direction != 'out':
            label_direction.config(text='Fehler: Zweimal nacheinander eingecheckt!', fg="red")
            return
    label_direction.config(text="In/Out Reihenfolge korrekt.", fg="green")

    # -------------------- Auschecken am Ende prüfen --------------------
    last_direction = daten_direction[-1]['direction'].strip("'")
    if last_direction == 'out':
        label_datetime.config(text="Am Ende wurde korrekt ausgecheckt.", fg="green")
    else:
        label_datetime.config(text="Warnung: Kein finaler Auscheckzeitpunkt (Transport evtl. noch aktiv).", fg="orange")

    # -------------------- Übergabe < 10min prüfen --------------------
    daten_datetime_values.sort(key=lambda x: x['datetime'])
    for i in range(1, len(daten_datetime_values) - 1, 2):
        out_record = daten_datetime_values[i]
        in_record = daten_datetime_values[i + 1]

        if out_record['direction'].strip("'") == 'out' and in_record['direction'].strip("'") == 'in':
            time_diff = (in_record['datetime'] - out_record['datetime']).total_seconds()
            if time_diff > 600:
                label_direction.config(text='Fehler: Übergabe > 10min (Kühlkette evtl. unterbrochen!)', fg="red")
                return

    # -------------------- Letzte Station vs. Aktion prüfen (gleiche Station mehrmals?) --------------------
    letzte_station = {}
    letzte_aktion = {}

    for eintrag in daten_zwischenzeit:
        transportid = eintrag['transportid']
        station = eintrag['transportstationid']
        aktion = eintrag['direction'].strip("'")

        if transportid in letzte_station:
            if letzte_aktion[transportid] == 'out' and aktion == 'in' and letzte_station[transportid] == station:
                label_direction.config(text=f"Fehler: Aus und wieder Einchecken im gleichen Kühllager (Station: {station})", fg="red")
                return

        letzte_station[transportid] = station
        letzte_aktion[transportid] = aktion

    # -------------------- Alles okay, Erfolgsmeldung --------------------
    label_direction.config(text='Verifikation erfolgreich abgeschlossen.', fg="green")

# -------------------- GUI Fenster für manuelle Überprüfung --------------------
def start_fenster_manuell():
    global combobox_transid, tree, label_duration, label_direction, label_datetime

    fenster = tk.Toplevel(fenster_hauptmenue)
    fenster.title("Manuelle Überprüfung")
    fenster.geometry("1000x600")

    tk.Label(fenster, text="Transport-ID auswählen:", font=("Helvetica", 12)).pack(pady=10)
    combobox_transid = ttk.Combobox(fenster, width=30, state="readonly")
    combobox_transid.pack()

    tk.Button(fenster, text="Prüfen", command=lambda: zeiten_auswertung(combobox_transid.get())).pack(pady=10)

    label_duration = tk.Label(fenster, text="Transportdauer: ", font=("Helvetica", 12))
    label_duration.pack(pady=10)

    label_direction = tk.Label(fenster, text="In/Out Logik: ", font=("Helvetica", 12))
    label_direction.pack(pady=10)

    label_datetime = tk.Label(fenster, text="Letzte Auscheckzeit: ", font=("Helvetica", 12))
    label_datetime.pack(pady=10)

    tree = ttk.Treeview(fenster, columns=("companyid", "station", "Zeitüberschreitung", "Wetter"), show='headings')
    for col in ["companyid", "station", "Zeitüberschreitung", "Wetter"]:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

    lade_db_daten()

# -------------------- Hauptmenü --------------------
fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("800x400")
fenster_hauptmenue.title("Coolchain Überwachung")

tk.Label(fenster_hauptmenue, text="ETS Supplychain-Projekt", font=("Helvetica", 16)).pack(pady=20)
tk.Button(fenster_hauptmenue, text="Transport-IDs prüfen", command=start_fenster_manuell, bg="#007BFF", fg="white").pack(pady=10)
tk.Button(fenster_hauptmenue, text="Temperaturüberwachung", command=temperatur_überwachung, bg="#28a745", fg="white").pack(pady=10)

fenster_hauptmenue.mainloop()
