import requests

def get_past_temperature(latitude: float, longitude: float, date: str, time: str):
    """
    Ruft die Temperatur für ein bestimmtes Datum und eine Uhrzeit aus der Open-Meteo API ab.
    """
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

        # 🔥 Fix: Zeitformat exakt an die API-Daten anpassen (ohne Sekunden)
        target_time = f"{date}T{time}"  # Ohne ":00"

        print("🔍 Verfügbare Zeitstempel von der API:")
        print(timestamps)  # Debugging-Ausgabe
        print(f"\n🎯 Gesuchte Zeit: {target_time}")

        # Prüfe, ob die Zeit exakt übereinstimmt
        if target_time in timestamps:
            index = timestamps.index(target_time)
            return f"🌡 Temperatur am {date} um {time}: {temperatures[index]}°C"
        else:
            return f"⚠️ Keine Temperaturdaten für {date} um {time} gefunden."

    except requests.exceptions.RequestException as e:
        return f"❌ API-Fehler: {e}"
    except KeyError as e:
        return f"⚠️ Fehlerhafte API-Antwort. Fehlendes Feld: {e}"

# ✅ Test für Berlin (52.52°N, 13.41°E)
print(get_past_temperature(52.52, 13.41, "2022-09-08", "10:00"))
