#--------------------Bibliotheken--------------------
import pyodbc
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta

#--------------------Funktion Daten aus Datenbank Laden--------------------
def lade_db_daten():
    global cursor, conn, db_daten, db_datetime, db_direction, db_zwischenzeit, db_tempdata  

    #----------Zugang Datenbank----------
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

    #----------Fehler falls keine Verbindung zur Datenbank möglich ist----------
    try:
        conn = pyodbc.connect(conn_str)
    except:
        messagebox.showerror(title="Fehler", message="Keine Verbindung zur Datenbank möglich!")
        return

    cursor = conn.cursor()
    cursor.execute('SELECT companyid, transportid, transportstationid, direction, datetime FROM coolchain')

    #----------Erstellen von benötigten Listen----------
    db_daten = []
    db_datetime = []
    db_direction = []
    db_zwischenzeit = []
    db_tempdata = []  # Temperaturdaten hinzufügen
    transport_ids = set()

    #----------Daten in erstellte Listen fügen----------
    for row in cursor:
        db_daten.append({'companyid': row.companyid, 'transportid': row.transportid, 'transportstationid': row.transportstationid, 'direction': row.direction, 'datetime': row.datetime})
        transport_ids.add(row.transportid)

    # **Temperaturdaten aus tempdata abrufen**
    cursor.execute('SELECT transportstationid, datetime, temperature FROM tempdata')
    for row in cursor:
        db_tempdata.append({'transportstationid': row.transportstationid, 'datetime': row.datetime, 'temperature': row.temperature})

    #----------Dropdown-Liste mit allen Transport-IDs aktualisieren----------
    unique_ids = sorted(transport_ids)
    combobox_transid['values'] = unique_ids
    if unique_ids:
        combobox_transid.current(0)

#--------------------Funktion Lesen der ID & Temperaturprüfung--------------------
def read_transid():
    transid = combobox_transid.get().strip()
    label_duration.config(text="", fg="red")
    label_direction.config(text="", fg="red")
    label_temperature.config(text="", fg="red")  # Temperaturanzeige leeren

    if any(char not in "0123456789" for char in transid):
        label_duration.config(text="Fehlerhafte Transport-ID!", fg="red")
        for item in tree.get_children():
            tree.delete(item)
    else:
        verifikation_auswertung(transid)

#--------------------Funktion zur Überprüfung aller Kriterien--------------------
def verifikation_auswertung(transid):
    global tree  # **Globale Definition von `tree` sicherstellen**

    # **Daten für die ausgewählte Transport-ID abrufen**
    daten_id = list(filter(lambda item: item["transportid"] == transid, db_daten))
    daten_temp = list(filter(lambda item: item["transportstationid"] in [entry["transportstationid"] for entry in daten_id], db_tempdata))

    # **Falls keine Daten vorhanden sind, Fehlermeldung anzeigen**
    if not daten_id:
        label_duration.config(text="Transport-ID nicht vorhanden.", fg="red")
        return

    # **Sortiere und zeige die Transportstationen in der GUI**
    daten_id.sort(key=lambda x: x["datetime"])
    for item in tree.get_children():
        tree.delete(item)

    for eintrag in daten_id:
        tree.insert("", "end", values=(eintrag["companyid"], eintrag["transportstationid"], eintrag["direction"], eintrag["datetime"]))

    # **Transportdauer prüfen**
    start_time = daten_id[0]["datetime"]
    end_time = daten_id[-1]["datetime"]
    duration = end_time - start_time

    if duration > timedelta(hours=48):
        label_duration.config(text="Transportdauer überschreitet 48 Stunden!", fg="red")
    else:
        label_duration.config(text="Transportdauer innerhalb von 48 Stunden.", fg="green")

    # **Temperaturprüfung**
    temperatur_fehler = []
    for eintrag in daten_temp:
        if not (2.0 <= eintrag["temperature"] <= 4.0):
            temperatur_fehler.append(f"Fehler: {eintrag['temperature']}°C an Station {eintrag['transportstationid']} am {eintrag['datetime']}")

    if temperatur_fehler:
        label_temperature.config(text="\n".join(temperatur_fehler), fg="red")
    else:
        label_temperature.config(text="Alle Temperaturen im gültigen Bereich.", fg="green")

#--------------------Funktion Erstellung Startfenster--------------------
def start_fenster_manuell():
    global combobox_transid, label_duration, label_direction, label_temperature, tree, fenster_manuell

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

    label_temperature = tk.Label(fenster_manuell, text="", bg="#f0f0f0", font=("Helvetica", 12))
    label_temperature.grid(column=1, row=3, padx=10, pady=10)

    # **Treeview für Transportstationsanzeige**
    tree = ttk.Treeview(fenster_manuell, columns=("companyid", "transportstationid", "direction", "datetime"), show='headings')
    tree.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    tree.heading("companyid", text="Unternehmen")
    tree.heading("transportstationid", text="Transportstation")
    tree.heading("direction", text="Richtung")
    tree.heading("datetime", text="Uhrzeit")

    lade_db_daten()

#--------------------Startfenster erstellen--------------------
fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("1000x500")
fenster_hauptmenue.title("Coolchain")
fenster_hauptmenue.configure(bg="#f0f0f0")

button1 = tk.Button(fenster_hauptmenue, text="Transport-IDs prüfen", command=start_fenster_manuell, bg="#007BFF", fg="white", font=("Helvetica", 12))
button1.pack(pady=10)

fenster_hauptmenue.mainloop()

