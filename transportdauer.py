import pyodbc
from datetime import datetime, timedelta
from collections import defaultdict

# Verbindungsdaten
server = 'sc-db-server.database.windows.net'
database = 'supplychain'  # Setze den Namen deiner Datenbank hier ein
username = 'rse'
password = 'Pa$$w0rd'

# Verbindungsstring
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

# Verbindung herstellen
conn = pyodbc.connect(conn_str)

# Cursor erstellen
cursor = conn.cursor()

# SQL-Statement ausführen, um alle Einträge zu erhalten
cursor.execute('''
    SELECT transportid, transportstation, direction, datetime 
    FROM coolchain1 
    ORDER BY transportid, datetime
''')

# Ergebnisse in eine Liste laden
rows = cursor.fetchall()

# Debugging: Anzahl der geladenen Zeilen anzeigen
print(f'Anzahl der geladenen Zeilen: {len(rows)}')

# Dictionary zur Speicherung der Gesamtzeit ohne Kühlung für jede transportid
non_cooling_times = defaultdict(timedelta)

# Variablen zur Berechnung der Gesamtzeit ohne Kühlung
out_times = {}

# Berechnung der Gesamtzeit ohne Kühlung für jede transportid
for row in rows:
    transportid, transportstation, direction, timestamp = row
    direction = direction.strip("'")  # Entfernen der Anführungszeichen
    #print(f'Verarbeite Zeile: {row}')  # Debugging: Zeile anzeigen
    if direction == 'out':
        out_times[transportid] = timestamp
    elif direction == 'in' and transportid in out_times:
        non_cooling_time = timestamp - out_times[transportid]
        non_cooling_times[transportid] += non_cooling_time
        del out_times[transportid]  # Entfernen des out_time-Eintrags für die aktuelle transportid

# Ergebnisse ausgeben
for transportid, total_non_cooling_time in non_cooling_times.items():
    print(f'Gesamtzeit ohne Kühlung für transportid {transportid}: {total_non_cooling_time}')

# Verbindung schließen
cursor.close()
conn.close()