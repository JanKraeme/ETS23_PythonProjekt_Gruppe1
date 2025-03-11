# -------------------- Bibliotheken --------------------
import pyodbc
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# -------------------- Listen --------------------
daten_Company = []
daten_Coolchain = []
daten_Temp = []
daten_Transstation = []

# -------------------- Initialisierung --------------------
key = b'mysecretpassword'                # 16 Byte Passwort
iv = b'passwort-salzen!'                 # 16 Byte Initialization Vektor


# -------------------- Entschlüsselungsfunktion --------------------
def decrypt_value(encrypted_data):
    cipher = AES.new(key, AES.MODE_CBC, iv)  # Verschlüsselung initialisieren
    return unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()


# -------------------- Funktion Datenbankverbindung --------------------
def connect_db():
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
        return conn
    except Exception as e:
        messagebox.showerror(title="Fehler", message="Keine Verbindung zur Datenbank möglich!")
        print("Fehler bei Datenbankverbindung:", e)
        return None


# -------------------- Funktion Daten aus Datenbank Laden --------------------
def lade_db_daten():
    global db_daten, db_datetime, db_direction, db_zwischenzeit

    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()

    # ---------- Coolchain Daten ----------
    cursor.execute('SELECT companyid, transportid, transportstationid, direction, datetime FROM coolchain')

    db_daten = []
    db_datetime = []
    db_direction = []
    db_zwischenzeit = []
    transport_ids = set()

    for row in cursor.fetchall():
        db_daten.append({'companyid': row.companyid, 'transportid': row.transportid, 'transportstationid': row.transportstationid, 'direction': row.direction, 'datetime': row.datetime})
        db_datetime.append({'datetime': row.datetime, 'direction': row.direction, 'transportid': row.transportid})
        db_direction.append({'transportid': row.transportid, 'direction': row.direction})
        db_zwischenzeit.append({'transportid': row.transportid, 'transportstationid': row.transportstationid, 'datetime': row.datetime, 'direction': row.direction})
        transport_ids.add(row.transportid)

    # ---------- company_crypt entschlüsseln ----------
    cursor.execute('SELECT * FROM company_crypt')
    for row in cursor.fetchall():
        daten_Company.append({
            "companyID": row[0],
            "company_name": decrypt_value(row[1]),
            "strasse": decrypt_value(row[2]),
            "ort": decrypt_value(row[3]),
            "plz": decrypt_value(row[4])
        })

    # ---------- transportstation_crypt entschlüsseln ----------
    cursor.execute('SELECT transportstationID, transportstation, category, plz FROM transportstation_crypt')
    for row in cursor.fetchall():
        daten_Transstation.append({
            "transportstationID": str(row[0]),
            "transportstation": decrypt_value(row[1]),
            "category": decrypt_value(row[2]),
            "plz": decrypt_value(row[3])
        })

    # ---------- Dropdown mit Transport-IDs füllen ----------
    unique_ids = sorted(transport_ids)
    combobox_transid['values'] = unique_ids
    if unique_ids:
        combobox_transid.current(0)

    cursor.close()
    conn.close()


# -------------------- GUI Fenster schließen --------------------
def schließe_db():
    pass  # Nicht notwendig, da Verbindung direkt geschlossen wird


# -------------------- Startfenster für manuelle Überprüfung --------------------
def start_fenster_manuell():
    global combobox_transid, label_duration, tree, label_direction, label_datetime, fenster_manuell

    fenster_manuell = tk.Toplevel(fenster_hauptmenue)
    fenster_manuell.title("Manuelle Überprüfung")
    fenster_manuell.geometry("1000x600")
    fenster_manuell.configure(bg="#f0f0f0")

    labelTop = tk.Label(fenster_manuell, text="Transport-ID auswählen:", bg="#f0f0f0", font=("Helvetica", 12))
    labelTop.grid(column=0, row=0, padx=10, pady=10)

    combobox_transid = ttk.Combobox(fenster_manuell, width=25, font=("Helvetica", 12), state="readonly")
    combobox_transid.grid(column=1, row=0, padx=10, pady=10)

    button3 = tk.Button(fenster_manuell, text="ID überprüfen", command=read_transid, bg="#007BFF", fg="white", font=("Helvetica", 12))
    button3.grid(column=2, row=0, padx=10, pady=10)

    label_duration = tk.Label(fenster_manuell, text="", bg="#f0f0f0", font=("Helvetica", 12))
    label_duration.grid(column=1, row=1, padx=10, pady=10)

    label_direction = tk.Label(fenster_manuell, text="", bg="#f0f0f0", font=("Helvetica", 12))
    label_direction.grid(column=1, row=2, padx=10, pady=10)

    label_datetime = tk.Label(fenster_manuell, text="", bg="#f0f0f0", font=("Helvetica", 12))
    label_datetime.grid(column=1, row=3, padx=10, pady=10)

    tree = ttk.Treeview(fenster_manuell, columns=("companyid", "transportstationid", "direction", "datetime"), show='headings')
    tree.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    for col in ["companyid", "transportstationid", "direction", "datetime"]:
        tree.heading(col, text=col.capitalize())

    scrollbar = ttk.Scrollbar(fenster_manuell, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=4, column=3, sticky="ns")

    # Lade Daten für Dropdown
    lade_db_daten()


# -------------------- Funktion Lesen der ID --------------------
def read_transid():
    transid = combobox_transid.get().strip()
    label_duration.config(text="", fg="red")
    label_direction.config(text="", fg="red")
    for item in tree.get_children():
        tree.delete(item)
    if not transid.isdigit():
        label_duration.config(text="Fehlerhafte Transport-ID!", fg="red")
    else:
        verifikation_auswertung(transid)


# -------------------- Funktion Verifikation --------------------
def verifikation_auswertung(transid):
    daten_id = list(filter(lambda item: item["transportid"] == transid, db_daten))
    if daten_id:
        daten_id.sort(key=lambda x: x["datetime"])
        for eintrag in daten_id:
            tree.insert("", "end", values=(eintrag["companyid"], eintrag["transportstationid"], eintrag["direction"], eintrag["datetime"]))
        label_duration.config(text="Transportdaten geladen", fg="green")
    else:
        label_duration.config(text="Transport-ID nicht vorhanden.", fg="red")


# -------------------- Hauptmenü Fenster --------------------
fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("500x250")
fenster_hauptmenue.title("Coolchain")
fenster_hauptmenue.configure(bg="#f0f0f0")

label1 = tk.Label(fenster_hauptmenue, text="Willkommen beim ETS23-Supplychain-Project", bg="#f0f0f0", font=("Helvetica", 14))
label1.pack(pady=20)

button1 = tk.Button(fenster_hauptmenue, text="Transport-IDs prüfen", command=start_fenster_manuell, bg="#007BFF", fg="white", font=("Helvetica", 12))
button1.pack(pady=10)

# -------------------- Mainloop --------------------
fenster_hauptmenue.mainloop()
