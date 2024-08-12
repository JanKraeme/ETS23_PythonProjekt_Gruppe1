import tkinter as tk
from tkinter import ttk

def create_table():
    # Erstelle das Hauptfenster
    root = tk.Tk()
    root.title("Tabelle mit drei Spalten")

    # Erstelle einen Frame für die Tabelle
    table_frame = ttk.Frame(root)
    table_frame.pack(fill="both", expand=True)

    # Erstelle die Treeview-Komponente für die Tabelle
    tree = ttk.Treeview(table_frame, columns=("Spalte1", "Spalte2", "Spalte3"))
    tree.heading("Spalte1", text="Spalte 1")
    tree.heading("Spalte2", text="Spalte 2")
    tree.heading("Spalte3", text="Spalte 3")
    tree.pack(fill="both", expand=True)

    # Füge einige Beispiel-Daten hinzu
    for i in range(10):
        tree.insert("", "end", values=("Wert1", f"Wert2_{i}", "Wert3"))

    # Füge einen Scrollbalken hinzu
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()

if __name__ == "__main__":
    create_table()
