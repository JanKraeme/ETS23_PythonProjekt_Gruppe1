import pyodbc
# Verbindungsdaten
server = 'sc-db-server.database.windows.net'
database = 'supplychain' # Setze den Namen deiner Datenbank hier ein
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
# SQL-Statement ausführen
cursor.execute('SELECT * FROM coolchain1')
# Ergebnisse ausgeben
for row in cursor:
    print(row)
# Verbindung schließen
cursor.close()
conn.close()