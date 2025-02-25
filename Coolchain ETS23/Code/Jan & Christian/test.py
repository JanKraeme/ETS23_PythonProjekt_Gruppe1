import pyodbc
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

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
        # Stelle sicher, dass die Daten als Bytes vorliegen
        if isinstance(encrypted_data, str):
            encrypted_data = bytes.fromhex(encrypted_data)
        return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()
    except ValueError as ve:
        print(f"Fehler beim Entschlüsseln (Padding-Problem): {ve}")
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

        decrypted_company = decrypt_value(encrypted_company)
        decrypted_strasse = decrypt_value(encrypted_strasse)
        decrypted_ort = decrypt_value(encrypted_ort)
        decrypted_plz = decrypt_value(encrypted_plz)

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
