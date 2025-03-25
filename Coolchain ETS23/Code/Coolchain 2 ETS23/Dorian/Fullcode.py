#--------------------------------------------------------
# Programm: Coolchain ETS23 Supply Chain Project 2
# Version: 2.0 (Erweiterung Coolchain)
# Erstelldatum: 25.03.2025
# Autoren: Jan Krämer, Max Kohnen, Tim Heikebrügge, Dorian Bohlken, Christian Rudolf, Kilian Tenfelde
#--------------------------------------------------------
# Beschreibung:
# Das Programm dient zur Überprüfung von Transportdaten einer Kühlkette eines FastFood-Lieferanten.
# Es verwendet eine GUI (Graphical User Interface), um Transport-
# IDs zu laden und verschiedene Transportinformationen wie Dauer 
# und Transportverlauf zu überprüfen und eventuelle Fehler zu erkennen.
# Die Erweiterung des Programms ermüberprüft zusätzlich zu den alten Funktionen
# die Wetterlage zu  ungekühlten Zeiten sowie eine ständige Temperaturüberwachung des Transports
# Die Einträge der Datenbank liegen nun im verschlüsselten Zustand vor und werden erst im Programm selbst entschlüsslt
#
# Hauptfunktionen:
# - Verschlüsselte Datenbankzugriffsdaten entschlüsseln.
# - Transportdaten aus einer SQL-Datenbank laden.
# - Überprüfung der Transportlogik ()"in" und "out").
# - Überprüfung der Gesamttransportzeit von maximal 48 Std.
# - Überprüfung der Umladungszeit zwischen den Kühltansportern bzw. Kühlhäusern
# - Überprüfung der Kühltemperartur innerhalb der Kühltransportern und Kühlhäusern
# - Abgleich der Postleitzahl der Kühlhäuser mit den Wetterdaten vor Ort zur Zeit des Umladens
# - Manuelle Auswahl und Überprüfung der Transport-IDs über die GUI.
# - Darstellung der Transportdaten zur ausgewählten TransportID in einer Liste
# - Anzeige aller überprüften Daten und evtl. Fehlern auf der GUI
# - Visualisierung der Transportereignisse (z.B. LKW- und Freeze-Symbole).
#
# Verwendete Bibliotheken:
# - pyodbc: Für den Datenbankzugriff (ODBC-Verbindung).
# - tkinter: Für die GUI-Erstellung.
# - pythoncryptodome: Zur Entschlüsseluung der Daten aus der Datenbank
# - datetime: Für die Zeit- und Datumsoperationen.
# - requests: Abfrage der historischen Wetterdaten aus dem Internet
#
# Voraussetzungen:
# - Eine funktionierende SQL-Server-Datenbank.
# - ODBC-Treiber 18 für SQL-Server.
# - Vorhandene Schlüssel- und Anmeldedaten in verschlüsselten Dateien.
# - Installationen aller verwendeten Bibliotheken (pyodbc, tkinker, pythoncryptodome, requests)
# - Internetverbindung
#
#Verschlüsselungen
# Es wird eine AES-Verschlüsselung (128Bit) verwendet, um die Anmeldedaten der Datenbank zu schützen
#--------------------------------------------------------

# -------------------- Bibliotheken --------------------
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import requests

# -------------------- Initialisierung-Verschlüsselungsdaten --------------------
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
def connect_db(): # Funktioen: Verbindung zur Datenbank mit verschlüsselten Anmeldedaten
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
def lade_stammdaten(): #Funktion: Herunterladen der verschlüsslten Daten und Entschlüsselung
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
def get_coordinates(postal_code: str): #Funktion: Generieren der Koordinaten anhand der Postleitzahl
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

def get_past_temperature(postal_code: str, date: str, time: str): #Funktion: Abfrage der historischen Wetterdaten anhand von PLZ und Datum/Uhrzeit
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
zeitueberschreitung = 0
def temperatur_ueberwachung(transid): #Funktion: Überprüfung der Temperaturen der Kühltransporte/Kühlhäuser
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
def start_fenster_manuell(): #Funktion: Öffnen des Fensters zur Überprüfung der Transportdaten
    def zeiten_auswertung(transid): #:Funktion: Zeiten- und Logiküberprüfung der Transportdaten
        for item in tree.get_children():
            tree.delete(item)
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT companyID, transportstationID, direction, datetime FROM coolchain WHERE transportID = ?', (transid,))
        daten = cursor.fetchall()
        
        if not daten:
            messagebox.showerror("Fehler", "Keine Daten für diese Transport-ID gefunden.")
            return

        daten.sort(key=lambda x: x[3])  # Sortieren nach Datum & Uhrzeit
        start, end = daten[0][3], daten[-1][3]
        dauer = end - start
        farbe = "red" if dauer > timedelta(hours=48) else "green"
        label_duration.config(text=f"Transportdauer: {dauer}", fg=farbe)

        in_out_ok = True
        uebergabe_ok = True

        last_direction = None
        last_out_time = None  # Speichert das letzte 'out' für die Übergabeprüfung

        for row in daten:
            company = company_dict.get(row[0], 'Unbekannt')
            station_info = station_dict.get(row[1], {'station': 'Unbekannt', 'plz': '0'})
            temp = get_past_temperature(station_info['plz'], row[3].strftime('%Y-%m-%d'), row[3].strftime('%H:00'))
            tree.insert('', 'end', values=(company, station_info['station'], row[2], row[3], temp))

            if last_direction is not None:
                if row[2] == last_direction:
                    in_out_ok = False  # Fehler, wenn sich 'in' oder 'out' wiederholt
                    
            if row[2] == "'out'":
                last_out_time = row[3]  # Speichere Zeitpunkt von 'out'

            if row[2] == "'in'" and last_out_time:
                # Berechne den Zeitunterschied (nur Stunden, Minuten, Sekunden)
                time_diff = (row[3] - last_out_time).total_seconds()

                if time_diff > 600:  
                    #messagebox.showwarning("Warnung", f"Übergabe > 10min ({time_diff:.0f} Sekunden). Wetter: {temp}")
                    uebergabe_ok = False
                    zeitueberschreitung = time_diff

                last_out_time = None  # Nach Prüfung zurücksetzen

            last_direction = row[2]

        label_direction.config(text='In/Out Prüfung: OK' if in_out_ok else 'Fehler in In/Out', fg='green' if in_out_ok else 'red')
        label_uebergabe.config(text=f'Übergabezeit: OK' if uebergabe_ok else f'Fehler bei Übergabe, {zeitueberschreitung:.2f} Sekunden > 600 Sekunden max. zugelassen',fg='green' if uebergabe_ok else 'red')

        temperatur_warnung = temperatur_ueberwachung(transid)
        label_temperatur.config(text=temperatur_warnung, fg='red' if temperatur_warnung else 'black')

        cursor.close()
        conn.close()




    fenster = tk.Toplevel(fenster_hauptmenue)
    fenster.title("Manuelle Überprüfung")
    fenster.geometry("1920x1080")
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

#---------------Ausführen des Programms--------------
# -------------------- Hauptmenü --------------------
fenster_hauptmenue = tk.Tk() #Öffnen des Hauptfensters
fenster_hauptmenue.geometry("500x250")
fenster_hauptmenue.title("Coolchain Überwachung")
lade_stammdaten()
tk.Label(fenster_hauptmenue, text="ETS Supplychain-Projekt", font=("Helvetica", 16)).pack(pady=20)
tk.Button(fenster_hauptmenue, text="Transport-IDs prüfen", command=start_fenster_manuell, bg="#007BFF", fg="white").pack(pady=10)
fenster_hauptmenue.mainloop()
