import pyodbc
from datetime import datetime, timedelta

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

# transportid für die Berechnung der Gesamtzeit ohne Kühlung
transportid = '99346757838434834886542'

# SQL-Statement ausführen
cursor.execute(f'''
    SELECT transportstation, direction, datetime 
    FROM coolchain1 
    WHERE transportid = '{transportid}' 
    ORDER BY datetime
''')

# Ergebnisse in eine Liste laden
rows = cursor.fetchall()

# Variablen zur Berechnung der Gesamtzeit ohne Kühlung
total_non_cooling_time = timedelta()
out_time = None

# Berechnung der Gesamtzeit ohne Kühlung
for row in rows:
    transportstation, direction, timestamp = row
    if direction == 'out':
        out_time = timestamp
    elif direction == 'in' and out_time is not None:
        total_non_cooling_time += timestamp - out_time
        out_time = None

# Ergebnisse ausgeben
print(f'Gesamtzeit ohne Kühlung für transportid {transportid}: {total_non_cooling_time}')

# Verbindung schließen
cursor.close()
conn.close()