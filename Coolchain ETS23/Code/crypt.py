# ETS32 Gruppe 1
# Python Projekt IoT-Kühlkettenüberwachung
# Programmunktion: Tool zur verschlüsselung der Zugangsdaten für das das Programm Coolchain
# Beschreibung:
# Diese Funktion dient zur sicheren Speicherung von Benutzeranmeldeinformationen.
# Die eingegebenen Daten (Benutzername und Passwort) werden mittels des
# Fernet-Verschlüsselungsverfahrens verschlüsselt und lokal gespeichert.
# Ein neuer Fernet-Schlüssel wird generiert und ebenfalls gespeichert.

from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox

trennzeichen = ';'

def erstelle_daten():
    username = username_entry.get()
    password = password_entry.get()
    print("Benutzername:", username)
    print("Passwort:", password)

    if username == "" or password == "":
        messagebox.showerror(title="Fehler", message=f"Eingabe Fehlerhaft!")
    else:
        # Speichere den Schlüssel sicher
        with open('key.key', 'wb') as file:
            file.write(key)

        # Verschlüssele die Zugangsdaten
        data = username + trennzeichen + password   #erstelle simplen String
        databyte = bytes(data, 'utf-8') #umwandlung in datenbyte also Byte
        key_data = Fernet(key)  
        encrypted_databyte = key_data.encrypt(databyte)

        # Speichere die verschlüsselten Daten
        with open('keydata.crypt', 'wb') as file:
            file.write(encrypted_databyte)
            messagebox.showinfo(title="Erfolgreich", message=f"Verschlüsselung erfolgreich!")

        window.quit()




# Hauptfenster erstellen
window = tk.Tk()
window.title("Login")

# Generiere einen Schlüssel
key = Fernet.generate_key()

# Label für den Benutzernamen
username_label = tk.Label(window, text="Benutzername:")
username_label.pack()

# Eingabefeld für den Benutzernamen
username_entry = tk.Entry(window)
username_entry.pack()

# Label für das Passwort
password_label = tk.Label(window, text="Passwort:")
password_label.pack()

# Eingabefeld für das Passwort
password_entry = tk.Entry(window, show="*")
password_entry.pack()

# Button zum Absenden
submit_button = tk.Button(window, text="Key erstellen", command=erstelle_daten)
submit_button.pack()


# Fenster anzeigen
window.mainloop()

