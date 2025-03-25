import pyodbc
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

# Verbindungsinformationen
server = 'sc-db-server.database.windows.net'
database = 'supplychain'
username = 'rse'
password = 'Pa$$w0rd'

# AES-Verschlüsselungsparameter
key = b'mysecretpassword'  # 16 Byte Passwort
iv = b'passwort-salzen!'   # 16 Byte Initialization Vektor

# Verbindungs-String
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

# Entschlüsselungsfunktion mit Fehlerbehandlung
def decrypt_value(encrypted_data):
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # Sicherstellen, dass die Daten Bytes sind
        if isinstance(encrypted_data, str):
            encrypted_data = bytes.fromhex(encrypted_data)
        elif isinstance(encrypted_data, bytes):
            pass
        else:
            encrypted_data = bytes(encrypted_data)

        return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()
    except ValueError as ve:
        print(f"Fehler beim Entschlüsseln (Padding-Problem): {ve}")
        print(f"Verschlüsselte Daten (hex): {binascii.hexlify(encrypted_data)}")
        return "[Entschlüsselungsfehler]"
    except Exception as e:
        print(f"Allgemeiner Fehler beim Entschlüsseln: {e}")
        return "[Entschlüsselungsfehler]"

# Verbindung zur Datenbank herstellen
try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Verbindung zur Datenbank hergestellt.")

    # Daten aus der Tabelle 'company_crypt' lesen
    select_query = 'SELECT companyID, company, strasse, ort, plz FROM company_crypt'
    cursor.execute(select_query)

    # Ergebnisse entschlüsseln und ausgeben
    for row in cursor.fetchall():
        companyID, encrypted_company, encrypted_strasse, encrypted_ort, encrypted_plz = row

        print(f"\nRohdaten für CompanyID {companyID}:")
        print(f"Company (raw): {binascii.hexlify(encrypted_company)}")
        print(f"Strasse (raw): {binascii.hexlify(encrypted_strasse)}")
        print(f"Ort (raw): {binascii.hexlify(encrypted_ort)}")
        print(f"PLZ (raw): {binascii.hexlify(encrypted_plz)}")

        decrypted_company = decrypt_value(encrypted_company)
        decrypted_strasse = decrypt_value(encrypted_strasse)
        decrypted_ort = decrypt_value(encrypted_ort)
        decrypted_plz = decrypt_value(encrypted_plz)

        print(f"\nEntschlüsselte Daten:")
        print(f"ID: {companyID}, Company: {decrypted_company}, Straße: {decrypted_strasse}, Ort: {decrypted_ort}, PLZ: {decrypted_plz}")

except Exception as e:
    print(f"Fehler bei der Verbindung oder Abfrage: {e}")

finally:
    # Verbindung schließen
    try:
        cursor.close()
        conn.close()
        print("Verbindung geschlossen.")
    except:
        pass
