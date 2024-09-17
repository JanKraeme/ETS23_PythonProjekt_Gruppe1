import pyodbc
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta

def lade_db_daten():
    global cursor, conn, db_daten
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
    except Exception as e:
        messagebox.showerror(title="Fehler", message=f"Keine Verbindung zur Datenbank möglich! {e}")
        return

    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT company, transportid, transportstation, category, direction, datetime FROM coolchain1')
    except Exception as e:
        messagebox.showerror(title="Fehler", message=f"Kein Datensatz in der Datenbank gefunden! {e}")
        return
    
    db_daten = []
    transport_ids = set()

    for row in cursor:
        db_daten.append({
            'company': row.company, 
            'transportid': row.transportid, 
            'transportstation': row.transportstation, 
            'category': row.category, 
            'direction': row.direction, 
            'datetime': row.datetime
        })
        transport_ids.add(row.transportid)

    # Dropdown-Liste mit allen Transport-IDs aktualisieren
    unique_ids = sorted(transport_ids)

    print(unique_ids)
    
    
