/**
 * @file Coolchain_IoT.py
 * @brief IoT-Kühlkettenüberwachung - Phase 2
 * @author Jan Krämer, Max Kohnen, Tim Heikebrügge, Dorian Bohlken, Christian Rudolf, Kilian Tenfelde
 * @date 18. Februar 2025
 * @version 2.0
 *
 * Dieses Programm erweitert die IoT-Kühlkettenüberwachung um:
 * - Temperaturüberwachung der Kühlstationen
 * - Verschlüsselung & Entschlüsselung der Lieferdaten
 * - Wetterdatenabfrage an den Auslagerorten
 */

#-------------------- Bibliotheken --------------------
import pyodbc
import requests
import json
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# API-Schlüssel für Wetterdaten (bitte ersetzen)
API_KEY = "Ihr_API_Schlüssel"

# AES Schlüssel und IV
KEY = b'mysecretpassword'
IV = b'passwort-salzen!'

def temperatur_ueberwachung():
    """
    @brief Überwacht die Temperatur in Kühlstationen.
    
    Diese Funktion liest Temperaturdaten aus der Datenbank und überprüft, 
    ob die Werte zwischen +2°C und +4°C liegen.
    """
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=sc-db-server.database.windows.net;DATABASE=supplychain;UID=user;PWD=pass')
    cursor = conn.cursor()
    cursor.execute("SELECT stationID, temperatur FROM tempdata")
    for row in cursor.fetchall():
        stationID, temp = row
        if temp < 2 or temp > 4:
            print(f"⚠ WARNUNG: Kühlstation {stationID} hat eine Temperaturabweichung: {temp}°C")
    cursor.close()
    conn.close()

def entschluessel_lieferdaten():
    """
    @brief Entschlüsselt Lieferdaten mit AES-CBC.
    
    Diese Funktion entschlüsselt die in `v_coolchain_crypt` gespeicherten Lieferdaten.
    """
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=sc-db-server.database.windows.net;DATABASE=supplychain;UID=user;PWD=pass')
    cursor = conn.cursor()
    cursor.execute("SELECT transportID, encrypted_data FROM v_coolchain_crypt")
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    for row in cursor.fetchall():
        transportID, encrypted_data = row
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        print(f"Transport {transportID}: {decrypted_data.decode()}")
    cursor.close()
    conn.close()

def wetterdaten_abfrage(plz, zeitpunkt):
    """
    @brief Holt Wetterdaten von VisualCrossing.
    
    @param plz Postleitzahl des Auslagerortes
    @param zeitpunkt Zeitpunkt der Abfrage im Format 'YYYY-MM-DD HH:MM:SS'
    """
    timestamp = datetime.strptime(zeitpunkt, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{plz}/{timestamp}?unitGroup=metric&key={API_KEY}&include=hours"
    response = requests.get(url)
    data = response.json()
    temp = data['days'][0]['temp']
    print(f"📍 Wetter am Ort {plz} um {zeitpunkt}: {temp}°C")
    return temp

if __name__ == "__main__":
    temperatur_ueberwachung()
    entschluessel_lieferdaten()
    wetterdaten_abfrage("26127", "2025-02-18 13:00:00")
