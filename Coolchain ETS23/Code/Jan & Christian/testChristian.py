import pyodbc
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


# Initialisierung
key = b'mysecretpassword' # 16 Byte Passwort
iv = b'passwort-salzen!' # 16 Byte Initialization Vektor


# Entschlüsselungsfunktion
def decrypt_value(encrypted_data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()


#----------Zugang Datenbank----------
server = 'sc-db-server.database.windows.net'
database = 'supplychain'
username = 'rse'
password = 'Pa$$w0rd'


#Listen
daten_Company = []
daten_Coolchain = []
daten_Temp = []
daten_Transstation = []

cursor = []

# Verbindungsstring
conn_str = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

#--------------------Funktion Fenster Schließen--------------------
def schließe_db():
    #----------if cursor:----------
    cursor.close()
    #----------if conn:----------
    conn.close()

def lade_Company():
    global conn, cursor
    # Verbindung herstellen
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Verbindung zu {server} , Datenbank {database}, nicht möglich!!!")
        print("Fehler", e)

    # Datensätze auslesen
    select_query = f'SELECT * FROM company_crypt'
    cursor.execute(select_query)
    # Für jeden Datensatz die Entschlüsselung durchführen und ausgeben
    cipher = AES.new(key, AES.MODE_CBC, iv) 
    for row in cursor:
        # Da die Daten als binär gespeichert wurden, sollte hier keine Umwandlung mit str() erfolgen
        daten_Company.append({
            "companyID": row[0], 
            "company_name": decrypt_value(row[1]), 
            "strasse": decrypt_value(row[2]), 
            "ort": decrypt_value(row[3]), 
            "plz": decrypt_value(row[4])
            })
        print("")
        print("")
        print("")
        print(daten_Company)
        print("")
        print("")
        print("")
        print("")

def lade_Transstation():
    global cursor, conn
    # Transportstation_db auslesen und entschlüsseln
    #############################################################################################################
    select_query = 'SELECT transportstationID, transportstation, category, plz FROM transportstation_crypt'
    cursor.execute(select_query)
    transportstation_db = cursor
    cipher = AES.new(key, AES.MODE_CBC, iv)  # Verschlüsselung initialisieren, nochmal weil dumme scheisse
    # Abspeichern
    for row in transportstation_db:
        daten_Transstation.append({
            "transportstationID": str(row[0]),
            "transportstation": decrypt_value(row[1]),
            "category": decrypt_value(row[2]),
            "plz": decrypt_value(row[3])
        })

    for i in range(len(daten_Transstation)):
        print(f"Transportstation ID: {daten_Transstation[i]['transportstationID']}, Transportstation: {daten_Transstation[i]['transportstation']}, Kategorie: {daten_Transstation[i]['category']}, PLZ: {daten_Transstation[i]['plz']}")


lade_Company()

lade_Transstation()

schließe_db()