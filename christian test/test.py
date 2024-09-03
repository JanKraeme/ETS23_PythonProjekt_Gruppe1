import tkinter as tk
from tkinter import ttk

# Erstelle das Hauptfenster
root = tk.Tk()
root.title("Tabelle mit aufklappbaren und einklappbaren Zeilen")

# Erstelle die Tabelle
tree = ttk.Treeview(root)

# Definiere die Spalten
tree["columns"] = ("Name", "Alter", "Stadt")

# Formatieren der Spalten
tree.column("#0", width=0, stretch=tk.NO)
tree.column("Name", anchor=tk.W, width=100)
tree.column("Alter", anchor=tk.W, width=50)
tree.column("Stadt", anchor=tk.W, width=100)

# Erstelle die Überschriften
tree.heading("#0", text="", anchor=tk.W)
tree.heading("Name", text="Name", anchor=tk.W)
tree.heading("Alter", text="Alter", anchor=tk.W)
tree.heading("Stadt", text="Stadt", anchor=tk.W)

# Füge einige Beispiel-Daten hinzu
tree.insert("", "end", values=("Max Mustermann", 25, "Berlin"))
tree.insert("", "end", values=("Anna Müller", 30, "München"))

# Funktion, um den erweiterten Inhalt zu erstellen
def erstelle_erweiterung(event):
    # Hole die ausgewählte Zeile
    ausgewählte_zeile = tree.identify_row(event.y)
    # Hole die Daten der ausgewählten Zeile
    zeile_daten = tree.item(ausgewählte_zeile, "values")
    # Erstelle den erweiterten Inhalt
    erweiterung_frame = tk.Frame(root)
    erweiterung_frame.place(x=event.x, y=event.y)
    tk.Label(erweiterung_frame, text="Erweiterter Inhalt:").pack()
    tk.Label(erweiterung_frame, text=f"Name: {zeile_daten[0]}").pack()
    tk.Label(erweiterung_frame, text=f"Alter: {zeile_daten[1]}").pack()
    tk.Label(erweiterung_frame, text=f"Stadt: {zeile_daten[2]}").pack()
    # Button zum Einklappen
    einklappen_button = tk.Button(erweiterung_frame, text="Einklappen", command=lambda: einklappen(erweiterung_frame))
    einklappen_button.pack()

# Funktion, um den erweiterten Inhalt einzuklappen
def einklappen(frame):
    frame.destroy()

# Funktion, um den erweiterten Inhalt aufzuklappen
def aufklappen(event):
    erstelle_erweiterung(event)

# Funktion, um den erweiterten Inhalt umzuschalten
def umschalten(event):
    # Hole die ausgewählte Zeile
    ausgewählte_zeile = tree.identify_row(event.y)
    # Hole die Daten der ausgewählten Zeile
    zeile_daten = tree.item(ausgewählte_zeile, "values")
    # Überprüfe, ob der erweiterte Inhalt bereits existiert
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame) and widget.winfo_x() == event.x and widget.winfo_y() == event.y:
            # Einklappen
            einklappen(widget)
            return
    # Aufklappen
    aufklappen(event)

# Binden Sie die Funktion an die Tabelle
tree.bind("<Double-1>", umschalten)

# Zeige die Tabelle an
tree.pack()

# Starte die Tkinter-Event-Schleife
root.mainloop()