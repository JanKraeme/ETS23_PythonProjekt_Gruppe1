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
        # Bereinige die station-Daten von überflüssigen Anführungszeichen
        station_name = decrypt_value(row[1]).strip("'")
        station_dict[row[0]] = {'station': station_name, 'plz': decrypt_value(row[2])}

    cursor.close()
    conn.close()

    # Ausgabe der station_dict
    print("Station Dictionary:", station_dict)


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


# -------------------- GUI --------------------
def start_fenster_manuell():
    def zeiten_auswertung(transid):
        for item in tree.get_children():
            tree.delete(item)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT companyid, transportid, transportstationid, direction, datetime FROM coolchain WHERE transportID = ?', transid)
        daten = cursor.fetchall()

        # Übernahme der Funktion 'pruefe_transport_kette' ohne Änderungen
        def pruefe_transport_kette(transport_id, daten, transportstation_daten):
            relevante_daten = [eintrag for eintrag in daten if str(eintrag[1]) == str(transport_id)]
            print(f"Gefundene {len(relevante_daten)} Einträge für TransportID {transport_id}")

            if not relevante_daten:
                print(f"❌ Keine Daten für TransportID {transport_id} gefunden.")
                return

            # Datum umwandeln (falls nötig)
            for eintrag in relevante_daten:
                if isinstance(eintrag[4], str):
                    eintrag[4] = datetime.fromisoformat(eintrag[4])

            # Sortierung
            relevante_daten.sort(key=lambda x: x[4])  # Sortiert nach datetime

            # Debug nach Sortierung
            print("\nSortierte Einträge:")
            for row in relevante_daten:
                print(row)

            last_out = None  # Merker für letztes 'out'

            for eintrag in relevante_daten:
                station_id = eintrag[2]
                direction = eintrag[3].replace("'", "").lower()  # <<< WICHTIG: Hochkomma entfernen!
                timestamp = eintrag[4]

                if direction == 'out':
                    last_out = (station_id, timestamp)  # Speichern

                elif direction == 'in' and last_out:
                    out_station_id, out_time = last_out
                    time_diff = (timestamp - out_time).total_seconds()

                    if time_diff > 600:  # Zeitüberschreitung
                        # PLZ suchen
                        plz = station_dict.get(out_station_id, {}).get('plz', None)
                        
                        if plz:
                            datum = timestamp.date().isoformat()  # YYYY-MM-DD
                            uhrzeit = timestamp.time().strftime("%H:%M:%S")  # HH:MM:SS
                            print(f"\n Überschreitung! StationID: {out_station_id}, PLZ: {plz}, "
                                f"Datum: {datum}, Uhrzeit: {uhrzeit}, Differenz: {int(time_diff)} Sekunden")

                            # Temperatur holen
                            temperatur = get_past_temperature(plz, datum, timestamp.time().strftime("%H:00"))
                            print(f"Temperatur um {datum} {timestamp.time().strftime('%H:00')}: {temperatur}°C\n")                        
                        # Last out zurücksetzen
                        last_out = None

        # Aufruf der Funktion, um die Einträge zu prüfen
        pruefe_transport_kette(transid, daten, station_dict)
        


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
    global label_duration, label_direction, label_uebergabe
    label_duration, label_direction, label_uebergabe = tk.Label(fenster), tk.Label(fenster), tk.Label(fenster)
    label_duration.pack(), label_direction.pack(), label_uebergabe.pack()
    global tree
    tree = ttk.Treeview(fenster, columns=("Firma", "Station", "Richtung", "Zeitpunkt", "Wetter"), show='headings')
    for col in ("Firma", "Station", "Richtung", "Zeitpunkt", "Wetter"):
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

# -------------------- Temperaturüberwachung --------------------
def temperatur_überwachung():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT transportstationID, datetime, temperature FROM tempdata')
    daten = cursor.fetchall()
    fenster = tk.Toplevel(fenster_hauptmenue)
    fenster.title("Temperaturüberwachung")
    tree_temp = ttk.Treeview(fenster, columns=("Station", "Datum", "Temperatur"), show='headings')
    for col in ("Station", "Datum", "Temperatur"):
        tree_temp.heading(col, text=col)
    tree_temp.pack(expand=True, fill='both')
    for row in daten:
        if row[2] < 2 or row[2] > 4:
            tree_temp.insert('', 'end', values=(row[0], row[1], f"{row[2]} °C"))
    cursor.close()
    conn.close()

# -------------------- Hauptmenü --------------------
fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("800x400")
fenster_hauptmenue.title("Coolchain Überwachung")
lade_stammdaten()
tk.Label(fenster_hauptmenue, text="ETS Supplychain-Projekt", font=("Helvetica", 16)).pack(pady=20)
tk.Button(fenster_hauptmenue, text="Transport-IDs prüfen", command=start_fenster_manuell, bg="#007BFF", fg="white").pack(pady=10)
tk.Button(fenster_hauptmenue, text="Temperaturüberwachung", command=temperatur_überwachung, bg="#28a745", fg="white").pack(pady=10)
fenster_hauptmenue.mainloop()
