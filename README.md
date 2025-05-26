# Bodensee Wasserdaten API Dokumentation

Diese API bietet Zugriff auf Echtzeit-Wasserdaten des Bodensees, einschließlich Wasserstand und Temperatur.

## API Basis-URL
```
http://127.0.0.1:5001
```

## Authentifizierung
Alle API-Endpunkte erfordern einen API-Schlüssel, der im Header mitgesendet werden muss:
```
X-API-Key: DoReMiFaSoLaSiDo134.14
```

## Endpunkte

### 1. Aktuelle Messwerte abrufen
Ruft die neuesten Messwerte ab.

**Endpunkt:** `/api/v1/measurements/latest`  
**Methode:** GET  
**Header erforderlich:** X-API-Key  

**Beispielanfrage:**
```bash
curl -H "X-API-Key: DoReMiFaSoLaSiDo134.14" http://127.0.0.1:5001/api/v1/measurements/latest
```

**Beispielantwort:**
```json
{
    "date": "2025-05-18T16:55:21",
    "level_cm": 313.0,
    "temp_c": 16.5
}
```

### 2. Historische Messwerte abrufen
Ruft historische Messwerte für einen bestimmten Zeitraum ab.

**Endpunkt:** `/api/v1/measurements`  
**Methode:** GET  
**Header erforderlich:** X-API-Key  

**Query Parameter:**
- `days` (optional): Anzahl der Tage in der Vergangenheit (Standard: 7)
- `start_date` (optional): Startdatum im ISO-Format (YYYY-MM-DD)
- `end_date` (optional): Enddatum im ISO-Format (YYYY-MM-DD)

**Beispielanfragen:**
```bash
# Letzte 3 Tage
curl -H "X-API-Key: DoReMiFaSoLaSiDo134.14" http://127.0.0.1:5001/api/v1/measurements?days=3

# Spezifischer Zeitraum
curl -H "X-API-Key: DoReMiFaSoLaSiDo134.14" "http://127.0.0.1:5001/api/v1/measurements?start_date=2025-05-01&end_date=2025-05-18"
```

**Beispielantwort:**
```json
[
    {
        "date": "2025-05-18T16:55:21",
        "level_cm": 313.0,
        "temp_c": 16.5
    },
    {
        "date": "2025-05-17T00:05:00",
        "level_cm": 312.5,
        "temp_c": 16.2
    }
]
```

### 3. Statistische Auswertung
Liefert statistische Daten für einen bestimmten Zeitraum.

**Endpunkt:** `/api/v1/measurements/stats`  
**Methode:** GET  
**Header erforderlich:** X-API-Key  

**Query Parameter:**
- `days` (optional): Anzahl der Tage für die Statistik (Standard: 30)

**Beispielanfrage:**
```bash
curl -H "X-API-Key: DoReMiFaSoLaSiDo134.14" http://127.0.0.1:5001/api/v1/measurements/stats?days=7
```

**Beispielantwort:**
```json
{
    "period": {
        "start_date": "2025-05-11",
        "end_date": "2025-05-18",
        "days": 7
    },
    "water_level": {
        "min": 310.5,
        "max": 313.0,
        "avg": 311.75
    },
    "temperature": {
        "min": 15.8,
        "max": 16.5,
        "avg": 16.15
    },
    "total_measurements": 8
}
```

## Rate Limiting
Die API verwendet ein Rate Limit, um die Anzahl der Anfragen zu begrenzen. Bei Überschreitung des Limits erhalten Sie einen 429 Status-Code.

## Datenaktualisierung
- Die Daten werden automatisch einmal täglich um 00:05 Uhr aktualisiert
- Bei Start des Servers werden die Daten sofort aktualisiert
- Die Messwerte werden in einer SQLite-Datenbank gespeichert

## Fehlermeldungen
Die API gibt folgende HTTP-Statuscodes zurück:
- 200: Erfolgreiche Anfrage
- 400: Ungültige Anfrageparameter
- 401: Fehlender oder ungültiger API-Schlüssel
- 404: Keine Daten gefunden
- 429: Rate Limit überschritten
- 500: Serverfehler

## Code-Beispiele

### Python
```python
import requests

API_KEY = 'DoReMiFaSoLaSiDo134.14'
BASE_URL = 'http://127.0.0.1:5001'
headers = {'X-API-Key': API_KEY}

# Aktuelle Messwerte
response = requests.get(f'{BASE_URL}/api/v1/measurements/latest', headers=headers)
current_data = response.json()

# Historische Daten der letzten 3 Tage
response = requests.get(f'{BASE_URL}/api/v1/measurements?days=3', headers=headers)
historical_data = response.json()

# Statistik der letzten 7 Tage
response = requests.get(f'{BASE_URL}/api/v1/measurements/stats?days=7', headers=headers)
stats_data = response.json()
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const API_KEY = 'DoReMiFaSoLaSiDo134.14';
const BASE_URL = 'http://127.0.0.1:5001';
const headers = { 'X-API-Key': API_KEY };

// Aktuelle Messwerte
axios.get(`${BASE_URL}/api/v1/measurements/latest`, { headers })
    .then(response => console.log(response.data))
    .catch(error => console.error(error));

// Historische Daten der letzten 3 Tage
axios.get(`${BASE_URL}/api/v1/measurements?days=3`, { headers })
    .then(response => console.log(response.data))
    .catch(error => console.error(error));

// Statistik der letzten 7 Tage
axios.get(`${BASE_URL}/api/v1/measurements/stats?days=7`, { headers })
    .then(response => console.log(response.data))
    .catch(error => console.error(error));
``` 