"""
# Bibliotheken
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
# Initialisierung
key = b'mysecretpassword' # 16 Byte Passwort
iv = b'passwort-salzen!' # 16 Byte Initialization Vektor
cipher = AES.new(key, AES.MODE_CBC, iv) # Verschlüsselung initialisieren
# Entschlüsselung
ciphertext = b'\xe0\xdc*\x84l\x87;p\xd22\xd9\x94\xabH6\xcd\xf0&\xeduO\x19\x17$+K*wke\x81\xdf'
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size) # Text entschlüsseln
# Ausgabe
print ('--------------------------------------------------------------------------')
print ("Entschlüsselter Text als Bytewert: ", plaintext)
print ("Entschlüsselter Text als String: ", plaintext.decode())
print ('--------------------------------------------------------------------------')
"""
"""
import pyodbc
# Verbindungsdaten
server = 'sc-db-server.database.windows.net'
database = 'supplychain'
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
print("Verbindung zur Datenbank hergestellt.")
# SQL-Statement ausführen
cursor.execute('SELECT companyID, company, strasse, ort, plz FROM company_crypt')
# Ergebnisse ausgeben
for row in cursor:
    print(row)
# Verbindung schließen
cursor.close()
conn.close()
"""

import pyodbc
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
# Initialisierung
key = b'mysecretpassword' # 16 Byte Passwort
iv = b'passwort-salzen!' # 16 Byte Initialization Vektor
cipher = AES.new(key, AES.MODE_CBC, iv) # Verschlüsselung initialisieren
# Entschlüsselungsfunktion
def decrypt_value(encrypted_data):
    return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()
# Verbindungsdaten
server = 'sc-db-server.database.windows.net'
database = 'supplychain'
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


def load_Company():
    global cursor, conn
    # Verbindung herstellen
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    # Datensätze auslesen
    select_query = 'SELECT companyID, company, strasse, ort, plz FROM company_crypt'
    cursor.execute(select_query)
    # Für jeden Datensatz die Entschlüsselung durchführen und ausgeben

    for row in cursor.fetchall():
        companyID, encrypted_company, encrypted_strasse, encrypted_ort, encrypted_plz = row
        # Da die Daten als binär gespeichert wurden, sollte hier keine Umwandlung mit str() erfolgen
        decrypted_company = decrypt_value(encrypted_company)
        decrypted_strasse = decrypt_value(encrypted_strasse)
        decrypted_ort = decrypt_value(encrypted_ort)
        decrypted_plz = decrypt_value(encrypted_plz)
        print("")
        print("")
        print("")
        print(f"ID: {companyID}, Company: {decrypted_company}, Strasse: {decrypted_strasse}, Ort: {decrypted_ort}, PLZ: {decrypted_plz}")

        print("")
        print("")
        print("")
        print("")
    #Verbindung schließen
    cursor.close()
    conn.close()
    
def lade_Transportdaten():
    #test
    # Verbindung herstellen
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    select_query = 'SELECT transportstationID, transportstation, category, plz FROM transportstation_crypt'
    cursor.execute(select_query)
    for row in cursor.fetchall():
        transportstationID, encrypted_transportstation, encrypted_category, encrypted_plz = row
        deprypted_transportstation = decrypt_value(encrypted_transportstation)
        deprypted_category = decrypt_value(encrypted_category)
        deprypted_plz = decrypt_value(encrypted_plz)
        print("")
        print("")
        print("")
        print(f"ID: {transportstationID}, Transportstation: {deprypted_transportstation}, Kategorie: {deprypted_category}, PLZ: {deprypted_plz}")
        print("")
        print("")
        print("")
        print("")
    cursor.close()
    conn.close()        

load_Company()
lade_Transportdaten()
