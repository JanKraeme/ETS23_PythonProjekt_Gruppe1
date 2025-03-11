"""
ID´s zum testen:
13456783852887496020345
15668407856331648336231
23964376768701928340034
"""
#############################################################################################################

import pyodbc
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Initialisierung
key = b'mysecretpassword'                # 16 Byte Passwort
iv = b'passwort-salzen!'                 # 16 Byte Initialization Vektor


# Entschlüsselungsfunktion
def decrypt_value(encrypted_data):
    cipher = AES.new(key, AES.MODE_CBC, iv)  # Verschlüsselung initialisieren
    return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()
    
# Verbindungsdaten
server = 'sc-db-server.database.windows.net'
database = 'supplychain'
username = 'rse'
password = 'Pa$$w0rd'

coolchain_db_sort = []
company_db_sort = []
transportstation_db_sort = []
data = []

# Verbindungsstring
conn_str = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

transportID = "13456783852887496020345"
#####################################################################################################################################################
# Verbindung herstellen
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Campany Name auslesen und entschlüsseln
#############################################################################################################
select_query = f'SELECT * FROM company_crypt'
cursor.execute(select_query)
company_db = cursor
cipher = AES.new(key, AES.MODE_CBC, iv)  # Verschlüsselung initialisieren
# Abspeichern
for row in company_db:
    company_db_sort.append({
        "companyID": row[0],
        "company": decrypt_value(row[1]),
        "strasse": decrypt_value(row[2]),
        "ort": decrypt_value(row[3]),
        "plz": decrypt_value(row[4])
    })

# Transportstation_db auslesen und entschlüsseln
#############################################################################################################
select_query = 'SELECT transportstationID, transportstation, category, plz FROM transportstation_crypt'
cursor.execute(select_query)
transportstation_db = cursor
cipher = AES.new(key, AES.MODE_CBC, iv)  # Verschlüsselung initialisieren, nochmal weil dumme scheisse
# Abspeichern
for row in transportstation_db:
    transportstation_db_sort.append({
        "transportstationID": str(row[0]),
        "transportstation": decrypt_value(row[1]),
        "category": decrypt_value(row[2]),
        "plz": decrypt_value(row[3])
    })

# Verbindung schließen
cursor.close()
conn.close()

print(company_db_sort)
print(transportstation_db_sort)