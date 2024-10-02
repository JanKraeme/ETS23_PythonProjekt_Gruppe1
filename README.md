Coolchain ETS23 Supplychain Project
- Dieses Projekt dient zur manuellen Überprüfung von Transportdaten in einer Coolchain-Umgebung. 
- Die Anwendung verbindet sich mit einer Datenbank, lädt Transportdaten und ermöglicht die Überprüfung von Transport-IDs hinsichtlich Dauer, 
  Reihenfolge der Checkpoints und Übergabezeiten zwischen verschiedenen Kühlstationen.

Hauptfunktionen:
- Transport-ID Auswahl: Über eine Dropdown-Liste kann der Benutzer eine Transport-ID auswählen.
- Transportdauer-Überprüfung: Die Anwendung überprüft, ob die Transportdauer die erlaubten 48 Stunden überschreitet.
- Überprüfung der Reihenfolge von Ein- und Auschecken: Sicherstellt, dass die Reihenfolge von Ein- und Auschecken an den Kühlstationen korrekt ist.
- Zeitüberschreitungen bei Übergaben: Überprüft, ob die Übergabe zwischen Kühlstationen weniger als 10 Minuten dauert.

Verwendung des Verzeichnises:
- Im Ordner "Coolchain ETS23" befinden sich zwei .exe Dateien.
- Mit "coolchainsecure.exe" werden die Benutzerzugangsdaten für die hinterlegte Datenbank verschlüsselt.
- Mit "coolchain.exe" verbindet man sich mit der Datenbank und kann ihre Transport-IDs prüfen.
- Im Ordner "Code" befindet sich einmal der Hauptcode des Programms, sowie die "crypt.py" die zum Verschlüsseln der Benutzerdaten benötigt wird.
- Ein Beispielbenutzerkonto ist im Ordner "Code" zum ausführen des Codes in VS-Code.
