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
        return f"{data['days'][0]['temp']} °C"
    return "Fehler bei Wetterdaten"


# -------------------- Daten laden und entschlüsseln --------------------
def lade_db_daten():
    global db_daten
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    db_daten = []
    transport_ids = set()

    # Coolchain
    cursor.execute('SELECT companyid, transportid, transportstationid, direction, datetime FROM coolchain')
    for row in cursor.fetchall():
        db_daten.append({'companyid': row.companyid, 'transportid': row.transportid, 'transportstationid': row.transportstationid, 'direction': row.direction, 'datetime': row.datetime})
        transport_ids.add(row.transportid)

    # Company entschlüsseln
    cursor.execute('SELECT * FROM company_crypt')
    daten_Company.clear()
    for row in cursor.fetchall():
        daten_Company.append({"companyID": row[0], "company_name": decrypt_value(row[1]), "strasse": decrypt_value(row[2]), "ort": decrypt_value(row[3]), "plz": decrypt_value(row[4])})

    # Transportstation entschlüsseln
    cursor.execute('SELECT * FROM transportstation_crypt')
    daten_Transstation.clear()
    for row in cursor.fetchall():
        daten_Transstation.append({"transportstationID": str(row[0]), "transportstation": decrypt_value(row[1]), "category": decrypt_value(row[2]), "plz": decrypt_value(row[3])})

    # Dropdown
    combobox_transid['values'] = sorted(transport_ids)
    if transport_ids:
        combobox_transid.current(0)

    cursor.close()
    conn.close()


# -------------------- Zeitüberschreitungen + Wetter --------------------
def zeiten_auswertung(transid):
    daten_id = [item for item in db_daten if item["transportid"] == transid]
    daten_id.sort(key=lambda x: x["datetime"])

    for i in range(len(daten_id) - 1):
        diff = daten_id[i + 1]['datetime'] - daten_id[i]['datetime']
        if daten_id[i]['direction'] == 'OUT' and diff > timedelta(minutes=10):
            station = daten_id[i]['transportstationid']
            plz = next((t['plz'] for t in daten_Transstation if t['transportstationID'] == station), "0")
            wetter = wetter_abfrage(plz, daten_id[i]['datetime'])
            tree.insert("", "end", values=(daten_id[i]['companyid'], station, diff, wetter))


# -------------------- GUI Fenster für manuelle Überprüfung --------------------
def start_fenster_manuell():
    global combobox_transid, tree

    fenster = tk.Toplevel(fenster_hauptmenue)
    fenster.title("Manuelle Überprüfung")
    fenster.geometry("1000x600")

    tk.Label(fenster, text="Transport-ID auswählen:", font=("Helvetica", 12)).pack(pady=10)
    combobox_transid = ttk.Combobox(fenster, width=30, state="readonly")
    combobox_transid.pack()

    tk.Button(fenster, text="Prüfen", command=lambda: zeiten_auswertung(combobox_transid.get())).pack(pady=10)

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
