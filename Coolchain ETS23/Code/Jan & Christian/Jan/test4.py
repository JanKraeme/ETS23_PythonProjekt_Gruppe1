# -------------------- Bibliotheken --------------------
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import requests

# -------------------- Initialisierung --------------------
key = b'mysecretpassword'
iv = b'passwort-salzen!'

# -------------------- Globale Daten --------------------
company_dict = {}
station_dict = {}

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

# -------------------- Stammdaten laden --------------------
def lade_stammdaten():
    global company_dict, station_dict
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    cursor.execute('SELECT companyID, company FROM company_crypt')
    for row in cursor.fetchall():
        company_dict[row[0]] = decrypt_value(row[1])

    cursor.execute('SELECT transportstationID, transportstation, plz FROM transportstation_crypt')
    for row in cursor.fetchall():
        station_dict[row[0]] = {'station': decrypt_value(row[1]), 'plz': decrypt_value(row[2])}

    cursor.close()
    conn.close()

    # -------------------- Wetterdaten mit Open-Meteo --------------------
def get_coordinates(postal_code: str):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={postal_code}&count=1&language=de&format=json"
    try:
        response = requests.get(geo_url)
        response.raise_for_status()
        data = response.json()
        if "results" in data and data["results"]:
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
        else:
            return None, None
    except requests.exceptions.RequestException:
        return None, None

def get_past_temperature(postal_code: str, date: str, time: str):
    latitude, longitude = get_coordinates(postal_code)
    if latitude is None or longitude is None:
        return "Ungültige Postleitzahl oder keine Daten verfügbar."
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={latitude}&longitude={longitude}"
        f"&start_date={date}&end_date={date}"
        f"&hourly=temperature_2m&timezone=auto"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        timestamps = data["hourly"]["time"]
        temperatures = data["hourly"]["temperature_2m"]
        target_time = f"{date}T{time}"
        if target_time in timestamps:
            index = timestamps.index(target_time)
            return f"{temperatures[index]} °C"
        else:
            return "Keine Temperaturdaten gefunden."
    except requests.exceptions.RequestException:
        return "Fehler: API nicht erreichbar."
    except KeyError:
        return "Fehler: Ungültige API-Antwort."

# -------------------- Temperaturüberwachung --------------------
def temperatur_ueberwachung(transid):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Transportstationen zur Transport-ID sammeln
    cursor.execute('SELECT DISTINCT transportstationID FROM coolchain WHERE transportID = ?', transid)
    station_ids = [row[0] for row in cursor.fetchall()]
    
    if not station_ids:
        cursor.close()
        conn.close()
        return "Keine Temperaturdaten gefunden."
    
    # Temperaturdaten für die gesammelten Stationen abrufen
    query = 'SELECT temperature FROM tempdata WHERE transportstationID IN ({})'.format(','.join('?' * len(station_ids)))
    cursor.execute(query, station_ids)
    temperaturwerte = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    # Überprüfung der Temperaturgrenzen
    for temp in temperaturwerte:
        if temp < 2 or temp > 4:
            return "Achtung: Temperaturabweichung während des Transports festgestellt!"
    return ""

# -------------------- Transport-ID Prüfung --------------------
def start_fenster_manuell():
    def zeiten_auswertung(transid):
        for item in tree.get_children():
            tree.delete(item)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT companyID, transportstationID, direction, datetime FROM coolchain WHERE transportID = ?', transid)
        daten = cursor.fetchall()
        daten.sort(key=lambda x: x[3])
        start, end = daten[0][3], daten[-1][3]
        dauer = end - start
        farbe = "red" if dauer > timedelta(hours=48) else "green"
        label_duration.config(text=f"Transportdauer: {dauer}", fg=farbe)
        in_out_ok, uebergabe_ok = True, True
        for i, row in enumerate(daten):
            company = company_dict.get(row[0], 'Unbekannt')
            station_info = station_dict.get(row[1], {'station': 'Unbekannt', 'plz': '0'})
            temp = get_past_temperature(station_info['plz'], row[3].strftime('%Y-%m-%d'), row[3].strftime('%H:00'))
            tree.insert('', 'end', values=(company, station_info['station'], row[2], row[3], temp))
            if i > 0:
                diff = (row[3] - daten[i-1][3]).total_seconds()
                if daten[i-1][2] == 'out' and row[2] == 'in' and diff > 600:
                    messagebox.showwarning("Warnung", f"Übergabe > 10min ({diff:.0f} min). Wetter: {temp}")
                    uebergabe_ok = False
        label_direction.config(text='In/Out Prüfung: OK' if in_out_ok else 'Fehler in In/Out', fg='green' if in_out_ok else 'red')
        label_uebergabe.config(text='Übergabezeit: OK' if uebergabe_ok else 'Fehler bei Übergabe', fg='green' if uebergabe_ok else 'red')
        
        temperatur_warnung = temperatur_ueberwachung(transid)
        label_temperatur.config(text=temperatur_warnung, fg='red' if temperatur_warnung else 'black')
        cursor.close()
        conn.close()

    fenster = tk.Toplevel(fenster_hauptmenue)
    fenster.title("Manuelle Überprüfung")
    fenster.geometry("1000x600")
    tk.Label(fenster, text="Transport-ID auswählen:").pack()
    transid_box = ttk.Combobox(fenster, state='readonly')
    transid_box.pack()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT transportID FROM coolchain')
    transid_box['values'] = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    tk.Button(fenster, text="Prüfen", command=lambda: zeiten_auswertung(transid_box.get())).pack()
    global label_duration, label_direction, label_uebergabe, label_temperatur
    label_duration, label_direction, label_uebergabe, label_temperatur = tk.Label(fenster), tk.Label(fenster), tk.Label(fenster), tk.Label(fenster)
    label_duration.pack(), label_direction.pack(), label_uebergabe.pack(), label_temperatur.pack()
    global tree
    tree = ttk.Treeview(fenster, columns=("Firma", "Station", "Richtung", "Zeitpunkt", "Wetter"), show='headings')
    for col in ("Firma", "Station", "Richtung", "Zeitpunkt", "Wetter"):
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

# -------------------- Hauptmenü --------------------
fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("800x400")
fenster_hauptmenue.title("Coolchain Überwachung")
lade_stammdaten()
tk.Label(fenster_hauptmenue, text="ETS Supplychain-Projekt", font=("Helvetica", 16)).pack(pady=20)
tk.Button(fenster_hauptmenue, text="Transport-IDs prüfen", command=start_fenster_manuell, bg="#007BFF", fg="white").pack(pady=10)
fenster_hauptmenue.mainloop()
