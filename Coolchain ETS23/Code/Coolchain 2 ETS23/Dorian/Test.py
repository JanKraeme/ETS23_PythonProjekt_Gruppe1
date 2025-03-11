import pyodbc

def lade_db_daten():
    # Verbindung zur Datenbank herstellen
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

        # Verbindung schließen
        cursor.close()
        conn.close()

        return daten_liste_1, daten_liste_2

    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return [], []

# Testaufruf
coolchain_daten, transportstation_daten = lade_db_daten()
print(coolchain_daten)
print(transportstation_daten)
