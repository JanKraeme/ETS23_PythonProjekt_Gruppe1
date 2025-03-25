# --------------------------------------------------------
# Programm: Coolchain ETS23 Supply Chain Project 2
# Version: 2.0 (Erweiterung Coolchain)
# Erstelldatum: 25.03.2025
# Autoren: Jan Krämer, Max Kohnen, Tim Heikebrügge, Dorian Bohlken, Christian Rudolf, Kilian Tenfelde
# --------------------------------------------------------
 Beschreibung:
 
 Das Programm dient zur Überprüfung von Transportdaten einer Kühlkette eines FastFood-Lieferanten.
 Es verwendet eine GUI (Graphical User Interface), um Transport-
 IDs zu laden und verschiedene Transportinformationen wie Dauer 
 und Transportverlauf zu überprüfen und eventuelle Fehler zu erkennen.
 Die Erweiterung des Programms ermüberprüft zusätzlich zu den alten Funktionen
 die Wetterlage zu  ungekühlten Zeiten sowie eine ständige Temperaturüberwachung des Transports
 Die Einträge der Datenbank liegen nun im verschlüsselten Zustand vor und werden erst im Programm selbst entschlüsslt
# --------------------------------------------------------
# Hauptfunktionen:
 - Verschlüsselte Datenbankzugriffsdaten entschlüsseln.
 - Transportdaten aus einer SQL-Datenbank laden.
 - Überprüfung der Transportlogik ("in" und "out").
 - Überprüfung der Gesamttransportzeit von maximal 48 Std.
 - Überprüfung der Umladungszeit zwischen den Kühltansportern bzw. Kühlhäusern
 - Überprüfung der Kühltemperartur innerhalb der Kühltransportern und Kühlhäusern
 - Abgleich der Postleitzahl der Kühlhäuser mit den Wetterdaten vor Ort zur Zeit des Umladens
 - Manuelle Auswahl und Überprüfung der Transport-IDs über die GUI.
 - Darstellung der Transportdaten zur ausgewählten TransportID in einer Liste
 - Anzeige aller überprüften Daten und evtl. Fehlern auf der GUI
 - Visualisierung der Transportereignisse (z.B. LKW- und Freeze-Symbole).
# --------------------------------------------------------
# Verwendete Bibliotheken:
 - pyodbc: Für den Datenbankzugriff (ODBC-Verbindung).
 - tkinter: Für die GUI-Erstellung.
 - pythoncryptodome: Zur Entschlüsseluung der Daten aus der Datenbank
 - datetime: Für die Zeit- und Datumsoperationen.
 - requests: Abfrage der historischen Wetterdaten aus dem Internet
Folgende Bibliotheken müssen über die Eingabeaufforderung installiert werden:
- pip install pyodbc
- pip install tk
- pip install pycryptodome
- pip install requests

# --------------------------------------------------------
# Voraussetzungen:
 - Eine funktionierende SQL-Server-Datenbank.
 - ODBC-Treiber 18 für SQL-Server.
 - Vorhandene Schlüssel- und Anmeldedaten in verschlüsselten Dateien.
 - Installationen aller verwendeten Bibliotheken (pyodbc, tkinker, pythoncryptodome, requests)
 - Internetverbindung
# --------------------------------------------------------

