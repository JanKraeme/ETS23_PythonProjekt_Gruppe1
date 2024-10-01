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
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
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
    SELECT transportid, transportstation, direction, datetime, category 
    FROM coolchain1 
    ORDER BY transportid, datetime
''')

# Ergebnisse in eine Liste laden
rows = cursor.fetchall()

# Dictionary zur Speicherung der Gesamtzeit ohne Kühlung und der Transportzeit für jede transportid
non_cooling_times = defaultdict(timedelta)
transport_times = defaultdict(timedelta)

# Variablen zur Berechnung der Gesamtzeit ohne Kühlung und Transportzeit
out_times = {}
in_times = {}

# Berechnung der Gesamtzeit ohne Kühlung und Transportzeit für jede transportid
for row in rows:
    transportid, transportstation, direction, timestamp, category = row
    direction = direction.strip("'")  # Entfernen der Anführungszeichen
    category = category.strip("'")  # Entfernen der Anführungszeichen

    if direction == 'out':
        out_times[transportid] = timestamp
        if transportid in in_times:
            transport_time = timestamp - in_times[transportid]
            transport_times[transportid] += transport_time
            del in_times[transportid]  # Entfernen des in_time-Eintrags für die aktuelle transportid

    elif direction == 'in':
        if category == 'KT':
            in_times[transportid] = timestamp
        if transportid in out_times:
            non_cooling_time = timestamp - out_times[transportid]
            non_cooling_times[transportid] += non_cooling_time
            del out_times[transportid]  # Entfernen des out_time-Eintrags für die aktuelle transportid

# Ergebnisse ausgeben
for transportid in non_cooling_times:
    print(f'Gesamtzeit ohne Kühlung für transportid {transportid}: {non_cooling_times[transportid]}')
    print(f'Gesamttransportzeit für transportid {transportid}: {transport_times[transportid]}')

# Verbindung schließen
cursor.close()
conn.close()