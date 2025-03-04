#--------------------------------------------------------
# Programm: Coolchain ETS23 Supply Chain Project
# Version: 1.0 (Erste Vollversion)
# Datum: 24. September 2024
# Autor: Jan Krämer, Max Kohnen, Tim Heikebrügge, Dorian Bohlken, Christian Rudolf, Kilian Tenfelde
#--------------------------------------------------------
# Beschreibung:
# Dieses Programm ermöglicht es dem Benutzer, Transportdaten 
# einer Supply Chain zu überprüfen. Es verwendet eine GUI 
# (Graphical User Interface), um Transport-
# IDs zu laden und verschiedene Transportinformationen wie Dauer 
# und Transportverlauf zu überprüfen und evenetuelle Fehler zu erkennen.
#
# Hauptfunktionen:
# - Verschlüsselte Datenbankzugriffsdaten entschlüsseln.
# - Transportdaten aus einer SQL-Datenbank laden.
# - Überprüfung der Transportdauer und Logik (z.B. "in" und "out").
# - Manuelle Auswahl und Überprüfung der Transport-IDs über die GUI.
# - Visualisierung der Transportereignisse (z.B. LKW- und Freeze-Symbole).
#
# Verwendete Bibliotheken:
# - pyodbc: Für den Datenbankzugriff (ODBC-Verbindung).
# - tkinter: Für die GUI-Erstellung.
# - cryptography.fernet: Für das Entschlüsseln der Zugangsdaten.
# - datetime: Für die Zeit- und Datumsoperationen.
#
# Voraussetzungen:
# - Eine funktionierende SQL-Server-Datenbank.
# - ODBC-Treiber 18 für SQL-Server.
# - Vorhandene Schlüssel- und Anmeldedaten in verschlüsselten Dateien.
#
#Verschlüsselungen
# Es wird eine AES-Verschlüsselung (128Bit) verwendet, um die Anmeldedaten der Datenbank zu schützen
#--------------------------------------------------------

#--------------------Bibliotheken--------------------
import pyodbc
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

#--------------------Funktion Daten aus datenbank Laden--------------------
def lade_db_daten():


    global cursor, conn, db_daten, db_datetime, db_direction, db_zwischenzeit
    
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
        fenster_manuell.destroy()
        messagebox.showerror(title="Fehler", message=f"Keine Verbindung zur Datenbank möglich!")
        return

    cursor = conn.cursor()
    cursor.execute('SELECT companyid, transportid, transportstationid, direction, datetime FROM coolchain')
#----------Fehler falls keine verwendbaren Daten in Datenbank vorhanden----------

    
#----------Erstellen von benötigten Listen----------
    db_daten = []
    db_datetime = []
    db_direction = []
    db_zwischenzeit = [] 
    transport_ids = set()
    
#----------Daten in erstellte Listen fügen----------
    for row in cursor:
        db_datetime.append({'datetime': row.datetime, 'direction': row.direction, 'transportid': row.transportid})
        db_direction.append({'transportid': row.transportid, 'direction': row.direction})
        db_daten.append({'companyid': row.companyid, 'transportid': row.transportid, 'transportstationid': row.transportstationid, 'direction': row.direction, 'datetime': row.datetime})
        transport_ids.add(row.transportid)
        db_zwischenzeit.append({'transportid':row.transportid,'transportstationid': row.transportstationid,'datetime': row.datetime,'direction': row.direction})

#----------Dropdown-Liste mit allen Transport-IDs aktualisieren----------
    unique_ids = sorted(transport_ids)
    combobox_transid['values'] = unique_ids
    if unique_ids:
        combobox_transid.current(0)  # Standardmäßig die erste ID auswählen
#--------------------Funktion Fenster Schließen--------------------
def schließe_db():
    #----------if cursor:----------
        cursor.close()
    #----------if conn:----------
        conn.close()
#--------------------Funktion erstellung Startfenster--------------------
def start_fenster_manuell():
#----------Variablen global übergeben----------
    global combobox_transid, label_duration, tree, label_direction, label_datetime, fenster_manuell
    
#----------Fenster zur Auswahl manueller Überprüfung erstellen----------
    fenster_manuell = tk.Toplevel(fenster_hauptmenue)
    fenster_manuell.title("Manuelle Überprüfung")
    fenster_manuell.geometry("1000x600")
    fenster_manuell.configure(bg="#f0f0f0")  # Hintergrundfarbe setzen
    
#----------Label für Darstellung der Fehler erstellen----------
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

    tree.heading("companyid", text="Unternehmen")
    tree.heading("transportstationid", text="Transport Station")

    tree.heading("direction", text="Richtung")
    tree.heading("datetime", text="Uhrzeit")

    scrollbar = ttk.Scrollbar(fenster_manuell, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=2, column=3, sticky="ns")

#----------Canvas für LKW-Symbol und Freeze-Symbol erstellen----------
    canvas = tk.Canvas(fenster_manuell, width=600, height=100, bg="#f0f0f0", highlightthickness=0)
    canvas.grid(row=5, column=0, columnspan=4, pady=20)

#---------- LKW-Symbol und Freeze-Symbol als Text hinzufügen----------
    truck_icon_text = "⛟"  # Unicode LKW-Symbol
    freeze_icon_text = "❄️"  # Unicode Freeze-Symbol
    
    truck_x = 100
    freeze_x = 300
    text_x = freeze_x + 130  # Abstand von 80 Einheiten hinter dem Freeze-Symbol
    
#----------Icons und Text im Canvas platzieren----------
    canvas.create_text(truck_x, 50, text=truck_icon_text, font=("Helvetica", 72), fill="black")
    canvas.create_text(freeze_x, 50, text=freeze_icon_text, font=("Helvetica", 72), fill="blue")
    canvas.create_text(text_x, 50, text="Coolchain-ETS", font=("Helvetica", 24), fill="black")

#----------Daten laden, um das Dropdown-Menü zu füllen----------
    lade_db_daten()
#--------------------Funktion Lesen der ID--------------------
def read_transid():
#----------Die ausgewählte ID aus der Combobox abrufen und Leerzeichen entfernen----------
    transid = combobox_transid.get().strip()
    
#----------Bei erneuter Überprüfen die Labels leeren----------
    verifikation_string = ""
    label_duration.config(text=verifikation_string, fg="red")
    label_direction.config(text=verifikation_string, fg="red")
    
#----------Überprüfen, ob die ID Sonderzeichen enthält----------
    if any(char not in "0123456789" for char in transid):
        verifikation_string = "Fehlerhafte Transport-ID!"
        label_duration.config(text=verifikation_string, fg="red")
        for item in tree.get_children():
            tree.delete(item)
    else:
        verifikation_auswertung(transid)
        
#--------------------Funktion Fehleridetifikation--------------------
def verifikation_auswertung(transid):
#----------Variablen global übergeben----------
    global daten_id, daten_zwischenzeit
    for item in tree.get_children():
        tree.delete(item)
        
#----------Erstellte Liste nach eingegebener ID durchsuchen----------
    daten_id = list(filter(lambda item: item["transportid"] == transid, db_daten))
    daten_datetime = list(filter(lambda item: item["transportid"] == transid, db_datetime))
    daten_direction = list(filter(lambda item: item["transportid"] == transid, db_direction))
    daten_zwischenzeit = list(filter(lambda item: item["transportid"] == transid, db_zwischenzeit))
    
#----------Sortieren nach Datum und in Tabelle einfügen----------
    if daten_id:
        daten_id.sort(key=lambda x: x["datetime"])  # Sortiere nach Datum
        for eintrag in daten_id:
            tree.insert("", "end", values=(eintrag["companyid"], eintrag["transportstationid"], eintrag["direction"], eintrag["datetime"]))    

#----------Überprüfung Transportdauer----------
        start_time = daten_id[0]["datetime"]
        end_time = daten_id[-1]["datetime"]
        duration = end_time - start_time

        tage = duration.days
        stunden, minuten = divmod(duration.seconds, 3600)
        minuten //= 60

        if tage == 1:
            zeit_format = f"{tage} Tag, {stunden} Stunden, {minuten} Minuten"
        else:
            zeit_format = f"{tage} Tage, {stunden} Stunden, {minuten} Minuten"

        if duration > timedelta(hours=48):
            verifikation_string = f'Transportdauer überschreitet 48 Stunden: {zeit_format}'
            label_duration.config(text=verifikation_string, fg="red")
        else:
            verifikation_string = f'Transportdauer innerhalb von 48 Stunden: {zeit_format}'
            label_duration.config(text=verifikation_string, fg="green")
    else:
        verifikation_string = 'Transport-ID nicht vorhanden.'
        label_duration.config(text=verifikation_string, fg="red")
        
#----------Prüfung der Direction-Logik----------
    for index, item in enumerate(daten_direction):
        value_in_out = item['direction']
        if index % 2 == 0: # ungerader Index mus IN sein
            if value_in_out == "'in'":
                print(value_in_out, "i.o.")
            else:
                verifikation_string = 'Fehler: Zweimal nacheinander ausgecheckt!'
                label_direction.config(text=verifikation_string, fg="red")
                return False
        else:
            if value_in_out == "'out'":  # gerader Index muss OUT sein
                print(value_in_out, "i.o.")
            else:
                verifikation_string = 'Fehler: Zweimal nacheinander eingecheckt!'
                label_direction.config(text=verifikation_string, fg="red")
                return False

#----------Prüfung der OUT Zeit des aktuellen gegen IN Zeit im nächsten Kühlabteil----------
    for i in range(1, len(daten_zwischenzeit)):
        previous_entry = daten_zwischenzeit[i - 1]
        current_entry = daten_zwischenzeit[i]

#----------Nur Einträge prüfen, die in der Reihenfolge Out -> In gehen----------
        if previous_entry['direction'] == "'out'" and current_entry['direction'] == "'in'":
            
#----------Prüfen, ob die Zeit des Eincheckens nach der Zeit des vorherigen Auscheckens liegt----------
            if current_entry['datetime'] < previous_entry['datetime']:
                verifikation_string = 'Fehler: Einchecken vor Auschecken im nächsten Kühlhaus!'
                label_direction.config(text=verifikation_string, fg="red")
                return False
            
#----------Überprüfen ob am Ende Ausgecheckt wird----------
    last_line = daten_direction[-1]
    last_direction = last_line['direction']
    if last_direction == "'out'":
        print("Am Ende wurde ausgecheckt")
    else:
        verifikation_string = 'Auscheckzeitpunt fehlt am Ende(kein Fehler da Transport noch nicht abgeschlossen!)'
        label_direction.config(text='Auscheckzeitpunt fehlt am Ende(kein Fehler da Transport noch nicht abgeschlossen!)', fg="green")
        return False

#----------Überprüfen ob Übergabe < 10min----------
    daten_datetime.sort(key=lambda x: x['datetime'])

    verification_failed = False
    
    for i in range(1, len(daten_datetime) - 1, 2):
        out_record = daten_datetime[i] 
        in_record = daten_datetime[i + 1]

        print(f"Comparing OUT: {out_record['datetime']} with IN: {in_record['datetime']}")

        if out_record['direction'] == "'out'" and in_record['direction'] == "'in'":
            if isinstance(out_record['datetime'], str):
                out_record['datetime'] = datetime.datetime.strptime(out_record['datetime'], '%Y-%m-%d %H:%M:%S')
            if isinstance(in_record['datetime'], str):
                in_record['datetime'] = datetime.datetime.strptime(in_record['datetime'], '%Y-%m-%d %H:%M:%S')

            time_diff = (in_record['datetime'] - out_record['datetime']).total_seconds()
            print(f"Time difference: {time_diff} seconds")

            if time_diff > 600:
                verification_failed = True
                break
        else:
            verification_failed = True
            break
    
    if verification_failed:
        verifikation_string = 'Zeitüberschreitung: Übergabe > 10min'
        label_direction.config(text=verifikation_string, fg="red")
    else:
        verifikation_string = 'Verifikation erfolgreich'
        label_direction.config(text=verifikation_string, fg="green")

        letzte_station = {}
    letzte_aktion = {}

    for i in range(1, len(daten_zwischenzeit)):
        aktueller_eintrag = daten_zwischenzeit[i]
        transportid = aktueller_eintrag['transportid']
        station = aktueller_eintrag['transportstationid']
        aktion = aktueller_eintrag['direction']

#----------Überprüfen, ob im gleichen Kühllager zweimal Eingecheckt wurde----------
        if transportid in letzte_station:
            #Wenn die letzte Aktion 'out' war und die aktuelle Aktion 'in' ist,
            # überprüfen, ob die Station die Gleiche ist
            if letzte_aktion[transportid] == "'out'" and aktion == "'in'":
                if letzte_station[transportid] == station:
                    verifikation_string = f"Aus und wieder Einchecken im gleichen Kühllager"
                    label_direction.config(text=verifikation_string, fg="red")

#----------Aktualisiere die zuletzt besuchte Station und die letzte Aktion----------
        letzte_station[transportid] = station
        letzte_aktion[transportid] = aktion
        
    schließe_db()
    
#--------------------Startfenster erstellen--------------------
fenster_hauptmenue = tk.Tk()
fenster_hauptmenue.geometry("1000x500")
fenster_hauptmenue.title("Coolchain")
fenster_hauptmenue.configure(bg="#f0f0f0")  # Hintergrundfarbe setzen

label1 = tk.Label(fenster_hauptmenue, text="Willkommen beim ETS23-Supplychain-Project", bg="#f0f0f0", font=("Helvetica", 14))
label1.pack(pady=20)

button1 = tk.Button(fenster_hauptmenue, text="Transport-IDs prüfen", command=start_fenster_manuell, bg="#007BFF", fg="white", font=("Helvetica", 12))
button1.pack(pady=10)
#--------------------Mainloop--------------------
fenster_hauptmenue.mainloop()
