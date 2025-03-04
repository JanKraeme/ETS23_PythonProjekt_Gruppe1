import requests

def get_coordinates_from_postcode(postcode: str):
    """
    Holt die Koordinaten (Breiten- und Längengrad) für eine deutsche Postleitzahl.
    """
    url = f"https://nominatim.openstreetmap.org/search?postalcode={postcode}&country=Germany&format=json"
    try:
        response = requests.get(url, headers={"User-Agent": "temperature-fetcher"})
        response.raise_for_status()
        data = response.json()
        
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        return None, None

def get_past_temperature(postcode: str, date: str, time: str):
    """
    Ruft die Temperatur für eine bestimmte Postleitzahl, ein Datum und eine Uhrzeit ab.
    """
    latitude, longitude = get_coordinates_from_postcode(postcode)
    
    if latitude is None or longitude is None:
        return f"❌ Fehler: Keine Geodaten für Postleitzahl {postcode} gefunden."
    
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
            return f"🌡 Temperatur in {postcode} am {date} um {time}: {temperatures[index]}°C"
        else:
            return f"⚠️ Keine Temperaturdaten für {date} um {time} gefunden."
    
    except requests.exceptions.RequestException as e:
        return f"❌ API-Fehler: {e}"
    except KeyError as e:
        return f"⚠️ Fehlerhafte API-Antwort. Fehlendes Feld: {e}"

# ✅ Test für Berlin (Postleitzahl 10115)
print(get_past_temperature("10115", "2022-09-08", "10:00"))
