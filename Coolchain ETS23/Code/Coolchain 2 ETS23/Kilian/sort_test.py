import pyodbc

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


connect_to_db()
cursor = conn.cursor()
cursor.execute('SELECT transportID, direction, datetime FROM coolchain')

eintrage = []
for row in cursor:
    eintrage.append({'transportID': row.transportID, 'direction': row.direction, 'datetime': row.datetime})
    

eintrage.sort(key=lambda x: x['datetime'])
for eintrag in eintrage:
    print(eintrag)

for i in range(1, len(eintrage)):
    differenz = eintrage[i]['datetime'] - eintrage[i-1]['datetime']
    differenz_in_minuten = differenz.total_seconds() / 60
    print(f"Differenz zwischen Eintrag {i-1} und {i}: {differenz_in_minuten:.2f} Minuten")
