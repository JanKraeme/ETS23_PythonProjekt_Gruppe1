import tkinter as tk
from tkinter import filedialog, ttk
import pyodbc #Datenbank import


def button_click_1():
    start_fenster_manuell()

def button_click_2():
    datenbank_laden()

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

def datenbank_laden():
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
    # Ergebnisse ausgeben
    for row in cursor:
        firma, transportid,packstation,kategorie,direction,datetime = row
        print("Firma", firma)
        print("Transport ID", transportid)
        
    # Verbindung schließen
    cursor.close()
    conn.close()

def start_fenster_manuell():
    fenster_manuell = tk.Toplevel(fenster_hauptmenue)
    fenster_manuell.title("manuelle Überprüfung")
    fenster_manuell.geometry("1000x500")
    fenster_manuell.grab_set()


    # def read_text():
    #     text = text_entry.get()  # Liest den gesamten Text
    #     print(text)

    # Textbox erstellen
    # label = tk.Label(fenster_manuell, text="Transport-ID")
    # label.pack()
    # text_entry = tk.Entry(fenster_manuell)
    # text_entry.pack()

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


# Hauptfenster anzeigen
fenster_hauptmenue.mainloop()



