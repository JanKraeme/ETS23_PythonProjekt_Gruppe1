import pyodbc
import requests
from datetime import datetime

# ---- 1. Datenbankfunktion ----
def lade_db_daten():
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
        cursor = conn.cursor()

        # Erste SQL-Abfrage
        query1 = "SELECT companyid, transportid, transportstationid, direction, datetime FROM coolchain"
        cursor.execute(query1)
        daten_liste_1 = [list(row) for row in cursor.fetchall()]

        # Zweite SQL-Abfrage
        query2 = "SELECT transportstationID, transportstation, plz FROM transportstation"
        cursor.execute(query2)
        daten_liste_2 = [
            {'transportstationID': row.transportstationID, 'transportstation': row.transportstation, 'plz': row.plz}
            for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        return daten_liste_1, daten_liste_2

    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return [], []


# ---- 2. Geo- und Temperatur-API ----
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
        return "Fehler: Ungültige Postleitzahl oder keine Daten verfügbar."
    
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
            return temperatures[index]
        else:
            return "Keine Temperaturdaten gefunden."
    
    except requests.exceptions.RequestException:
        return "Fehler: API nicht erreichbar."
    except KeyError:
        return "Fehler: Ungültige API-Antwort."


# ---- 3. Prüfung (sortiert + logisch korrekt) ----
def pruefe_transport_kette(transport_id, coolchain_daten, transportstation_daten):
    # TransportID Filter + Debug
    relevante_daten = [eintrag for eintrag in coolchain_daten if str(eintrag[1]) == str(transport_id)]
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
            print(f"[OUT] Gefunden an Station {station_id} um {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            last_out = (station_id, timestamp)  # Speichern

        elif direction == 'in' and last_out:
            out_station_id, out_time = last_out
            time_diff = (timestamp - out_time).total_seconds()
            print(f"[IN] Gefunden an Station {station_id} um {timestamp.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"Differenz zu letztem OUT: {int(time_diff)} Sekunden")

            if time_diff > 600:  # Zeitüberschreitung
                # PLZ suchen
                plz = next((item['plz'] for item in transportstation_daten if item['transportstationID'] == out_station_id), None)
                
                if plz:
                    datum = timestamp.date().isoformat()  # YYYY-MM-DD
                    uhrzeit = timestamp.time().strftime("%H:%M:%S")  # HH:MM:SS
                    print(f"\n⚠️ Überschreitung! StationID: {out_station_id}, PLZ: {plz}, "
                        f"Datum: {datum}, Uhrzeit: {uhrzeit}, Differenz: {int(time_diff)} Sekunden")

                    # Temperatur holen
                    temperatur = get_past_temperature(plz, datum, timestamp.time().strftime("%H:00"))
                    print(f"🌡️ Temperatur um {datum} {timestamp.time().strftime('%H:00')}: {temperatur}°C\n")
                else:
                    print(f"⚠️ Keine PLZ für StationID {out_station_id} gefunden.")
                
                # Last out zurücksetzen
                last_out = None
            else:
                print(f"✅ Zeit zwischen OUT und IN ist in Ordnung ({int(time_diff)} Sekunden).\n")
                last_out = None

# ---- 4. Anwendung ----
if __name__ == "__main__":
    # Daten holen
    coolchain_daten, transportstation_daten = lade_db_daten()

    # TransportID eingeben
    transport_id_input = input("Bitte geben Sie die TransportID ein: ")

    # Start der Prüfung
    pruefe_transport_kette(transport_id_input, coolchain_daten, transportstation_daten)
