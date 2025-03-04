import pyodbc
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


# Initialisierung
key = b'mysecretpassword' # 16 Byte Passwort
iv = b'passwort-salzen!' # 16 Byte Initialization Vektor
cipher = AES.new(key, AES.MODE_CBC, iv)

# Entschlüsselungsfunktion
#def decrypt_value(encrypted_data):
#    return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()

def decrypt_value(encrypted_data):
    try:
        unpadded_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        return unpadded_data.decode("utf-8", errors="ignore")  # Fehlerbehandlung bei ungültigen Zeichen
    except ValueError as e:
        print(f"Fehler bei der Entschlüsselung: {e}")
        return None

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
 #   cursor.close()

def lade_Transportdaten():

    select_query = 'SELECT transportstationID, transportstation, category, plz FROM transportstation_crypt'
    cursor.execute(select_query)
    results = cursor.fetchall()
    for row in results:
        deprypted_transportstation = decrypt_value(row.transportstation)
        deprypted_category = decrypt_value(row.category)
        deprypted_plz = decrypt_value(row.plz)
        print("")
        print(f"ID: {row.transportstationID}, Transportstation: {deprypted_transportstation}, Kategorie: {deprypted_category}, PLZ: {deprypted_plz}")
        print("")
    cursor.close()
    conn.close()   

load_Company()
lade_Transportdaten()




# Bibliotheken
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
# Initialisierung
key = b'mysecretpassword' # 16 Byte Passwort
iv = b'passwort-salzen!' # 16 Byte Initialization Vektor
cipher = AES.new(key, AES.MODE_CBC, iv) # Verschlüsselung initialisieren
# Entschlüsselung
#ciphertext = b'\xe0\xdc*\x84l\x87;p\xd22\xd9\x94\xabH6\xcd\xf0&\xeduO\x19\x17$+K*wke\x81\xdf'
ciphertext = b'N\xc8\x17\x95\xdd\xaeY\xa4P\x8e\xd8\x10\xd7P\t#h\xc7z\xd6\x16\xf9\xc6*\x0e8\xb1\x89r\xd1U@'
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size) # Text entschlüsseln
# Ausgabe
print ('--------------------------------------------------------------------------')
print ("Entschlüsselter Text als Bytewert: ", plaintext)
print ("Entschlüsselter Text als String: ", plaintext.decode())
print ('--------------------------------------------------------------------------')

