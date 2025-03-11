import pyodbc
import pandas as pd

def connect_to_db():
    global conn
    #----------Zugang Datenbank----------
    server = 'sc-db-server.database.windows.net'
    database = 'supplychain'
    username = 'rse'
    password = 'Pa$$w0rd'
    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password}'
    )
    #----------Fehler falls keine Verbindung zur Datenbank möglich ist----------
    try:
        conn = pyodbc.connect(conn_str)
    except:
        print("Fehler")

def fetch_data():
    cursor = conn.cursor()
    cursor.execute('SELECT transportID, direction, datetime FROM coolchain')
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]  # Spaltennamen aus dem Cursor extrahieren
    df = pd.DataFrame.from_records(rows, columns=columns)  # DataFrame mit richtigen Spalten erstellen
    df.rename(columns={'direction': 'status', 'datetime': 'timestamp'}, inplace=True)  # Spalten umbenennen
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def check_chronology(entries):
    results = []
    for i in range(1, len(entries)):
        prev_entry = entries[i - 1]
        curr_entry = entries[i]
        if prev_entry['transportID'] == curr_entry['transportID']:
            if prev_entry['direction'] == 'out' and curr_entry['direction'] == 'in':
                time_diff = (curr_entry['datetime'] - prev_entry['datetime']).total_seconds()
            elif prev_entry['direction'] == 'in' and curr_entry['direction'] == 'out':
                time_diff = None  # Kein Zeitraum nötig
            else:
                results.append((curr_entry['transportID'], "Fehlerhafte Reihenfolge", None))
                continue
            results.append((curr_entry['transportID'], "OK", time_diff))
    return pd.DataFrame(results, columns=["transportID", "Status", "Zwischenzeitraum (s)"])

def analyze_data():
    df = fetch_data()
    entries = df.to_dict('records')  # DataFrame in Liste von Dictionaries umwandeln
    entries.sort(key=lambda x: x['timestamp'])  # Sortierung nach datetime
    result_df = check_chronology(entries)
    print(result_df)
    return result_df

# Verbindung zur Datenbank herstellen und Daten analysieren
connect_to_db()
analyze_data()
