MONITOR Widget - Deployment als .exe
====================================

1. Voraussetzungen
------------------
- Windows-Rechner mit Python (nur für das Packen, nicht für den Zielserver)
- PyInstaller installiert (`pip install pyinstaller`)
- Alle Projektdateien (MONITOR_app.py, static/..., etc.)

2. Anwendung als .exe bauen
---------------------------
1. Stelle sicher, dass alles lokal funktioniert:
   - Starte `python MONITOR_app.py` und prüfe die Widgets im Browser.
2. Baue die .exe:
   - Öffne die Kommandozeile im Projektordner.
   - Führe aus:
     pyinstaller --onefile --add-data "static;static" MONITOR_app.py
   - Die fertige .exe findest du im Ordner `dist/`.

3. Anwendung auf dem Zielserver starten
---------------------------------------
- Kopiere die .exe (und ggf. den Ordner `static`, falls nicht im Bundle) auf den Server.
- Starte die Anwendung:
  MONITOR_app.exe
- Die App sucht sich automatisch einen freien Port und gibt ihn in der Konsole aus (z.B. "MONITOR-App läuft auf Port 54321").
- Greife im Browser zu über:
  http://<SERVER-IP>:<PORT>/MONITOR_iframe.html
  (bzw. .../MONITOR_iframe_waterlevel.html)

4. Dauerbetrieb: Task Scheduler (Windows Aufgabenplanung)
--------------------------------------------------------
**Variante 1: Zugriff auf Server-Konsole möglich**
- Öffne Aufgabenplanung (Task Scheduler) auf dem Server.
- "Neue Aufgabe erstellen" > "Aktion: Programm starten" > Pfad zur .exe angeben.
- "Trigger": Beim Systemstart oder nach Zeitplan.
- "Optionen": "Unabhängig von Benutzeranmeldung ausführen" aktivieren.
- Aufgabe speichern und testen.

**Variante 2: Nur Remote-Zugriff (kein Desktop/GUI)**
- Per Remote Desktop (RDP) oder Remote PowerShell auf den Server verbinden.
- Mit PowerShell eine geplante Aufgabe anlegen:
  Beispiel:
  ```powershell
  $Action = New-ScheduledTaskAction -Execute "C:\Pfad\zu\MONITOR_app.exe"
  $Trigger = New-ScheduledTaskTrigger -AtStartup
  Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName "MONITOR Widget" -RunLevel Highest
  ```
- Die Aufgabe startet die .exe beim Systemstart automatisch.

**Alternativen:**
- Die .exe kann auch als Windows-Dienst laufen (z.B. mit NSSM: https://nssm.cc/)
- Oder per "geplante Aufgabe" regelmäßig neu gestartet werden.

5. Hinweise
-----------
- Der Port wird bei jedem Start neu gewählt. Prüfe die Konsole oder logge den Port in eine Datei, falls du ihn remote brauchst.
- Stelle sicher, dass die Firewall den gewählten Port für eingehende Verbindungen freigibt.
- Für den externen Zugriff muss die Server-IP und der Port im Browser erreichbar sein.

6. Fehlerbehebung
-----------------
- Wird kein Port ausgegeben, prüfe die Logdatei oder aktiviere die Konsolenausgabe.
- Bei Problemen mit statischen Dateien: Stelle sicher, dass der Ordner `static` im gleichen Verzeichnis wie die .exe liegt (oder korrekt im Bundle ist).

--- 