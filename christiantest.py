import pyodbc
from datetime import datetime


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

def fetch_data():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM coolchain1')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def check_consistency(data):
    for record in data:
        # Überprüfen, ob jede Transportstation einen Ein- und Auscheckeintrag hat
        # Überprüfen, ob die Einträge zeitlich sinnvoll angeordnet sind
        pass

def check_cooling_periods(data):
    for record in data:
        # Überprüfen, ob die Zeit zwischen dem Auschecken und Einchecken 10 min nicht überschreitet
        pass

def check_transport_duration(data):
    # Dictionary, um die Start- und Endzeiten für jede Transport-ID zu speichern
    transport_times = {}

    for record in data:
        transport_id = record.transportid
        direction = record.direction
        timestamp = datetime.strptime(record.datetime, '%Y-%m-%d %H:%M:%S')

        if transport_id not in transport_times:
            transport_times[transport_id] = {'start': None, 'end': None}

        if direction == 'in':
            if not transport_times[transport_id]['start']:
                transport_times[transport_id]['start'] = timestamp
        elif direction == 'out':
            transport_times[transport_id]['end'] = timestamp

    for transport_id, times in transport_times.items():
        start = times['start']
        end = times['end']

        if start and end:
            duration = end - start
            if duration.total_seconds() > 48 * 3600:  # 48 Stunden in Sekunden
                print(f"Transportdauer für ID {transport_id} überschreitet 48 Stunden: {duration}")
                return False
        else:
            print(f"Fehlende Zeitstempel für ID {transport_id}")
            return False

    return True

def main():
    data = fetch_data()
    
    consistency_result = check_consistency(data)
    cooling_periods_result = check_cooling_periods(data)
    transport_duration_result = check_transport_duration(data)
    
    if consistency_result and cooling_periods_result and transport_duration_result:
        print("Alle Bedingungen an die Kühlkette wurden erfüllt.")
    else:
        print("Es wurden Fehler in der Kühlkette gefunden.")
        if not consistency_result:
            print("Fehler: Stimmigkeit der Kühlketteninformationen nicht erfüllt.")
        if not cooling_periods_result:
            print("Fehler: Zeiträume ohne Kühlung überschritten.")
        if not transport_duration_result:
            print("Fehler: Transportdauer überschritten.")

if __name__ == '__main__':
    main()



























































"""
import tkinter as tk
from tkinter import filedialog, ttk
import pyodbc

def button_click_1():
    start_fenster_manuell()

def button_click_2():
    print("Button 2 wurde gedrückt!")
    CoolchainDB_load()

# Hauptfenster erstellen
fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("1000x500")
fenster_hauptmenue.title("Coolchain")

label1 = tk.Label(fenster_hauptmenue, text="Willkommen beim ETS-Supplychain-Project" "\n" "Zur Übverprüfung einer Kühlkette einen der beiden Menüpunkte auswählen!")
label1.pack()


# Button 1 erstellen
button1 = tk.Button(fenster_hauptmenue, text="Manuelle Eingabe der Transport-IDs", command=button_click_1)
button1.pack()

# Button 2 erstellen
button2 = tk.Button(fenster_hauptmenue, text="Datenbank laden", command=button_click_2)
button2.pack()

def CoolchainDB_load():
    # Verbindungsdaten
    server = 'sc-db-server.database.windows.net'
    database = 'supplychain' # Setze den Namen deiner Datenbank hier ein
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
    # SQL-Statement ausführen
    cursor.execute('SELECT * FROM coolchain1')

    
    arr = []
    i = 0
    
    for row in cursor:
 
        a = row.__str__()
        b = a.split(",")
        arr.append([])  # Add a new row to the array

        for j, value in enumerate(b):

            arr[i].append(value)  # Add the value to the current row

            

        i += 1


    print(arr[70][0])


    


       
    
    # Verbindung schließen
    cursor.close()
    conn.close()
    




""" 
"""
def start_fenster_manuell():
    fenster_manuell = tk.Toplevel(fenster_hauptmenue)
    fenster_manuell.title("manuelle Überprüfung")
    fenster_manuell.geometry("1000x500")
    fenster_manuell.grab_set()

    def read_transid():
        transid = combo_transid.get()  # Liest den Wert in der ComboBox
        if transid:
            print(transid)
        else:
            tk.messagebox.showerror(title="Fehler", message="keine Transport-ID ausgewählt!")

    labelTop = tk.Label(fenster_manuell, text="Transport-ID auswählen:")
    labelTop.grid(column=0, row=0)

    combo_transid = ttk.Combobox(fenster_manuell, values=["Hier die Daten aus der Datenbank!"])
    print(dict(combo_transid))
    combo_transid.grid(column=10, row=0)

        # Button 3 erstellen
    button3 = tk.Button(fenster_manuell, text="ID überprüfen", command=read_transid)
    button3.grid(column=50, row=0)
"""
"""
# Hauptfenster anzeigen
fenster_hauptmenue.mainloop()

"""

