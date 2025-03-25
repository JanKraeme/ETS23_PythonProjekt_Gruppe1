
import pyodbc 
from Crypto.Cipher import AES 
from Crypto.Util.Padding import unpad 
 
# Initialisierung 
key = b'mysecretpassword'                # 16 Byte Passwort 
iv = b'passwort-salzen!'                 # 16 Byte Initialization Vektor 
cipher = AES.new(key, AES.MODE_CBC, iv)  # Verschlüsselung initialisieren 
 
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
    f'DRIVER={{ODBC Driver 17 for SQL Server}};' 
    f'SERVER={server};' 
    f'DATABASE={database};' 
    f'UID={username};' 
    f'PWD={password}' 
) 
 
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
     
   print(f"ID: {companyID}, Company: {decrypted_company}, Strasse: {decrypted_strasse}, Ort: {decrypted_ort}, PLZ: {decrypted_plz}") 
    
# Verbindung schließen 
cursor.close() 
conn.close() 