# Bodensee Wasserdaten-Monitoring System

## Projektübersicht
Dieses System sammelt, speichert und visualisiert Wasserdaten des Bodensees (Wasserstand und Temperatur) über eine Web-API und Benutzeroberfläche.

## Systemarchitektur

### Hauptkomponenten

1. **Datenerfassung**
   - `scraper.py`: Hauptmodul für das Web-Scraping der Bodensee-Daten
   - `collect_data.py`: Hilfsskript für die manuelle Datenerfassung
   - `scheduler.py`: Automatisierte tägliche Datenerfassung (00:05 Uhr)

2. **Datenspeicherung**
   - `db.py`: Datenbankmodell und SQLite-Operationen
   - `reset_and_fetch.py`: Hilfsskript zum Zurücksetzen und Neuladen der Daten

3. **API-Server**
   - `api.py`: RESTful API-Implementierung
   - `config.py`: Konfigurationseinstellungen
   - `test_api.py`: API-Testfälle

4. **Web-Interface**
   - `app.py`: Flask-Webanwendung
   - `templates/`: HTML-Templates für die Weboberfläche

5. **Sicherheit**
   - `generate_cert.py`: SSL-Zertifikatsgenerierung
   - `certificates/`: SSL-Zertifikate

### Modulabhängigkeiten

```
scraper.py → db.py → config.py
scheduler.py → scraper.py
api.py → db.py → config.py
app.py → api.py
```

## Modul-Details

### scraper.py
- Hauptfunktionalität: Web-Scraping der Bodensee-Daten
- Abhängigkeiten: requests, beautifulsoup4
- Funktionen: Datenextraktion, Parsing, Validierung

### db.py
- Hauptfunktionalität: Datenbankoperationen
- Technologie: SQLite mit SQLAlchemy
- Modelle: Measurement (Wasserstand, Temperatur, Zeitstempel)

### scheduler.py
- Hauptfunktionalität: Automatisierte Datenerfassung
- Technologie: APScheduler
- Zeitplan: Täglich um 00:05 Uhr
- Zusätzlich: Sofortige Datenaktualisierung bei verpasstem Schedule

### api.py
- Hauptfunktionalität: RESTful API
- Framework: Flask-RESTful
- Endpunkte:
  * /api/v1/measurements/latest
  * /api/v1/measurements
  * /api/v1/measurements/stats
- Sicherheit: API-Key-Authentifizierung

### app.py
- Hauptfunktionalität: Web-Interface
- Framework: Flask
- Features: Aktuelle Daten, Historische Ansicht, Grafische Darstellung

## Technische Abhängigkeiten
```
Flask==3.0.0
Flask-RESTful==0.3.10
Flask-Cors==4.0.0
Flask-Limiter==3.5.0
Flask-Caching==2.1.0
SQLAlchemy==2.0.25
APScheduler==3.10.4
requests==2.31.0
python-dotenv==1.0.0
beautifulsoup4==4.12.2
pyOpenSSL==24.0.0
pytest==7.4.3
```

## Datenfluss
1. Der Scheduler triggert die tägliche Datenerfassung
2. Der Scraper extrahiert die Daten von der Bodensee-Website
3. Die Daten werden in der SQLite-Datenbank gespeichert
4. Die API stellt die Daten über verschiedene Endpunkte bereit
5. Das Web-Interface visualisiert die Daten

## Sicherheitsaspekte
- API-Authentifizierung über X-API-Key
- Rate Limiting für API-Zugriffe
- CORS-Konfiguration für Web-Interface
- Optional: SSL/TLS-Verschlüsselung

## Entwicklungsumgebung
- Python 3.8+
- Virtual Environment empfohlen
- Windows/Linux kompatibel

## Installation und Start
1. Virtual Environment erstellen und aktivieren
2. Dependencies installieren: `pip install -r requirements.txt`
3. Datenbank initialisieren: `python reset_and_fetch.py`
4. API-Server starten: `python api.py`
5. Web-Interface starten: `python app.py`

## Monitoring und Wartung
- Logs für Scraping-Aktivitäten
- Automatische Fehlerbehandlung bei Scraping-Fehlern
- Tägliche Datenaktualisierung um 00:05 Uhr
- Backup-Mechanismus für verpasste Aktualisierungen 