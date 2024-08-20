import pyodbc
from datetime import timedelta
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

# Dictionary zur Speicherung der Gesamttransportzeit für jede transportid
total_transport_times = defaultdict(timedelta)

# Liste zur Speicherung der offenen 'GVZ in'-Einträge
gvt_in_times = defaultdict(list)

# Berechnung der Gesamttransportzeit für jede transportid
for row in rows:
    transportid, transportstation, direction, timestamp, category = row
    direction = direction.strip("'")  # Entfernen der Anführungszeichen
    category = category.strip("'")  # Entfernen der Anführungszeichen

    if direction == 'in' and category == 'GVZ':
        # Jeden 'in' für 'GVZ' speichern
        gvt_in_times[transportid].append(timestamp)

    elif direction == 'out' and category == 'KT':
        # Berechne die Zeitdifferenz, wenn wir einen vorherigen 'GVZ'-Eintrag haben
        if transportid in gvt_in_times and gvt_in_times[transportid]:
            gvt_in_time = gvt_in_times[transportid].pop(0)  # Nimm den ältesten 'GVZ in'-Eintrag
            time_difference = timestamp - gvt_in_time
            total_transport_times[transportid] += time_difference  # Addiere die Zeitdifferenz zur Gesamtzeit

# Ergebnisse ausgeben
for transportid, total_time in total_transport_times.items():
    # Transportzeit in Stunden berechnen
    total_time_hours = total_time.total_seconds() / 3600  # Umwandlung von Sekunden in Stunden
    
    # Überprüfung, ob die Transportzeit über 48 Stunden liegt
    transport_time_exceeded = total_time_hours > 48
    
    # Ausgabe der Ergebnisse
    print(f'Gesamttransportzeit für transportid {transportid}: {total_time}')
    print(f'Transportzeit in Stunden für transportid {transportid}: {total_time_hours:.2f} Stunden')
    print(f'Transportzeit überschritten (> 48 Stunden) für transportid {transportid}: {transport_time_exceeded}')

# Verbindung schließen
cursor.close()
conn.close()
