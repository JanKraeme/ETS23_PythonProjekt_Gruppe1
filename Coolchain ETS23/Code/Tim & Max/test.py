import pyodbc
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta

def lade_db_daten():
    global cursor, conn, db_daten, db_tempdata

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
    except:
        messagebox.showerror(title="Fehler", message="Keine Verbindung zur Datenbank möglich!")
        return

    cursor = conn.cursor()
    cursor.execute('SELECT transportid, transportstationid, companyid, direction, datetime FROM coolchain')
    
    db_daten = {}
    transport_ids = set()

    for row in cursor:
        if row.transportid not in db_daten:
            db_daten[row.transportid] = []
        db_daten[row.transportid].append({'companyid': row.companyid, 'transportstationid': row.transportstationid, 'direction': row.direction, 'datetime': row.datetime})
        transport_ids.add(row.transportid)
    
    cursor.execute('SELECT transportstationid, datetime, temperature FROM tempdata')
    db_tempdata = {row.transportstationid: {'datetime': row.datetime, 'temperature': row.temperature} for row in cursor}

    unique_ids = sorted(transport_ids)
    combobox_transid['values'] = unique_ids
    if unique_ids:
        combobox_transid.current(0)

def read_transid():
    transid = combobox_transid.get().strip()
    label_duration.config(text="", fg="red")
    label_temperature.config(text="", fg="red")
    
    if transid not in db_daten:
        label_duration.config(text="Transport-ID nicht vorhanden.", fg="red")
        return
    
    verifikation_auswertung(transid)

def verifikation_auswertung(transid):
    daten_id = db_daten.get(transid, [])
    
    if not daten_id:
        label_duration.config(text="Keine Daten gefunden.", fg="red")
        return

    daten_id.sort(key=lambda x: x["datetime"])
    for item in tree.get_children():
        tree.delete(item)

    for eintrag in daten_id:
        tree.insert("", "end", values=(eintrag["companyid"], eintrag["transportstationid"], eintrag["direction"], eintrag["datetime"]))
    
    start_time = daten_id[0]["datetime"]
    end_time = daten_id[-1]["datetime"]
    duration = end_time - start_time
    label_duration.config(text=("Transportdauer innerhalb von 48 Stunden." if duration <= timedelta(hours=48) else "Transportdauer überschreitet 48 Stunden!"), fg=("green" if duration <= timedelta(hours=48) else "red"))

    temperatur_fehler = [f"Fehler: {db_tempdata[entry['transportstationid']]['temperature']}°C an Station {entry['transportstationid']} am {db_tempdata[entry['transportstationid']]['datetime']}" for entry in daten_id if entry['transportstationid'] in db_tempdata and not (2.0 <= db_tempdata[entry['transportstationid']]['temperature'] <= 4.0)]
    
    label_temperature.config(text="\n".join(temperatur_fehler) if temperatur_fehler else "Alle Temperaturen im gültigen Bereich.", fg=("red" if temperatur_fehler else "green"))

def start_fenster_manuell():
    global combobox_transid, label_duration, label_temperature, tree, fenster_manuell

    fenster_manuell = tk.Toplevel(fenster_hauptmenue)
    fenster_manuell.title("Manuelle Überprüfung")
    fenster_manuell.geometry("1000x600")
    
    tk.Label(fenster_manuell, text="Transport-ID auswählen:", font=("Helvetica", 12)).grid(column=0, row=0, padx=10, pady=10)
    combobox_transid = ttk.Combobox(fenster_manuell, width=25, font=("Helvetica", 12), state="readonly")
    combobox_transid.grid(column=1, row=0, padx=10, pady=10)
    tk.Button(fenster_manuell, text="ID überprüfen", command=read_transid, bg="#007BFF", fg="white", font=("Helvetica", 12)).grid(column=2, row=0, padx=10, pady=10)
    
    label_duration = tk.Label(fenster_manuell, text="", font=("Helvetica", 12))
    label_duration.grid(column=1, row=1, padx=10, pady=10)
    label_temperature = tk.Label(fenster_manuell, text="", font=("Helvetica", 12))
    label_temperature.grid(column=1, row=3, padx=10, pady=10)
    
    tree = ttk.Treeview(fenster_manuell, columns=("companyid", "transportstationid", "direction", "datetime"), show='headings')
    tree.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    tree.heading("companyid", text="Unternehmen")
    tree.heading("transportstationid", text="Transportstation")
    tree.heading("direction", text="Richtung")
    tree.heading("datetime", text="Uhrzeit")
    
    lade_db_daten()

fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("1000x500")
fenster_hauptmenue.title("Coolchain")

tk.Button(fenster_hauptmenue, text="Transport-IDs prüfen", command=start_fenster_manuell, bg="#007BFF", fg="white", font=("Helvetica", 12)).pack(pady=10)

fenster_hauptmenue.mainloop()
