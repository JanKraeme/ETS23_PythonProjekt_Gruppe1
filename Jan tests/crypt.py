from cryptography.fernet import Fernet
import tkinter as tk

trennzeichen = ';'

def submit():
    username = username_entry.get()
    password = password_entry.get()
    print("Benutzername:", username)
    print("Passwort:", password)

    # Speichere den Schlüssel sicher
    with open('key.key', 'wb') as file:
        file.write(key)

    # Verschlüssele die Zugangsdaten
    data = username + trennzeichen + password
    databyte = bytes(data, 'utf-8')
    cipher_suite = Fernet(key)
    encrypted_databyte = cipher_suite.encrypt(databyte)

    # Speichere die verschlüsselten Daten
    with open('credentials.crypt', 'wb') as file:
        file.write(encrypted_databyte)
        


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
submit_button = tk.Button(window, text="Key erstellen", command=submit)
submit_button.pack()


# Fenster anzeigen
window.mainloop()

