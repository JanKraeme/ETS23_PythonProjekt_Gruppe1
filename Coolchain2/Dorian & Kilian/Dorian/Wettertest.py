import requests

def get_coordinates(postal_code: str):
    """
    Holt die Koordinaten (Breiten- und Längengrad) einer Postleitzahl mit der Open-Meteo API.
    """
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
    """
    Ruft die Temperatur für eine bestimmte Postleitzahl, ein Datum und eine Uhrzeit ab.
    """
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
            return temperatures[index]  # Gibt nur die Temperatur als Zahl zurück
        else:
            return "Keine Temperaturdaten gefunden."
    
    except requests.exceptions.RequestException:
        return "Fehler: API nicht erreichbar."
    except KeyError:
        return "Fehler: Ungültige API-Antwort."

# Beispielaufruf: Temperatur für Postleitzahl 10115 (Berlin), Datum 2022-09-08, Uhrzeit 10:00
print(get_past_temperature("10115", "2022-09-08", "10:00"))
