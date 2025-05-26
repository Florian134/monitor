from flask import Flask, jsonify, send_from_directory, request
import requests
import socket
import logging
import os
import sys
import platform
import traceback
import json
import streamlit

# Debug-Logger einrichten
logging.basicConfig(
    filename='MONITOR_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

app = Flask(__name__, static_folder=resource_path('static'))

logging.info(f"Arbeitsverzeichnis: {os.getcwd()}")
logging.info(f"BASE_DIR: {resource_path('')}")
logging.info(f"Static-Folder: {app.static_folder}")

# Logge Systeminfos und Umgebungsvariablen
logging.info(f"Platform: {platform.platform()}")
logging.info(f"Python-Version: {platform.python_version()}")
logging.info(f"Umgebungsvariablen: {os.environ}")
logging.info(f"sys.argv: {sys.argv}")
logging.info(f"_MEIPASS: {getattr(sys, '_MEIPASS', None)}")

# Logge Verzeichnisstruktur und Existenz von static
def log_dir_structure(path, depth=2):
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        if level > depth:
            continue
        indent = ' ' * 2 * level
        logging.info(f"{indent}{os.path.basename(root)}/")
        for f in files:
            logging.info(f"{indent}  {f}")
try:
    static_path = resource_path('static')
    logging.info(f"Prüfe static-Ordner: {static_path}")
    if os.path.exists(static_path):
        logging.info("static-Ordner existiert.")
        log_dir_structure(static_path)
    else:
        logging.error("static-Ordner existiert NICHT!")
except Exception as e:
    logging.error(f"Fehler beim Prüfen des static-Ordners: {e}")

# Globales Exception-Logging
import sys

def log_uncaught_exceptions(exctype, value, tb):
    logging.critical('Unbehandelte Exception:', exc_info=(exctype, value, tb))
    print('Unbehandelte Exception:', value)

sys.excepthook = log_uncaught_exceptions

MAX_LOG_LINES = 100

@app.before_request
def log_request_info():
    # Logfile begrenzen
    try:
        log_path = 'MONITOR_debug.log'
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                # Logfile ist nicht UTF-8, leere es
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write('')
                lines = []
            if len(lines) > MAX_LOG_LINES:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines[-MAX_LOG_LINES:])
    except Exception as e:
        print(f"Fehler beim Begrenzen des Logfiles: {e}")
    logging.info(f"Request: {str(request.method)} {str(request.path)}")

VOWIS_URL = "https://vowis.vorarlberg.at/api/see"

CACHE_FILE_TEMP = "monitor_temp_cache.json"
CACHE_FILE_WATER = "monitor_waterlevel_cache.json"

@app.route('/MONITOR_temperature')
def get_temperature():
    try:
        response = requests.get(VOWIS_URL, timeout=5)
        data = response.json()
        wassertemperatur = data[0]['wTemperatur']['wert']
        wassertemperatur_datum = data[0]['wTemperatur']['datum']
        # Cache speichern
        with open(CACHE_FILE_TEMP, "w", encoding="utf-8") as f:
            json.dump({"temperature": wassertemperatur, "timestamp": wassertemperatur_datum}, f)
        logging.info(f"MONITOR_temperature: {wassertemperatur} ({wassertemperatur_datum})")
        return jsonify({"temperature": wassertemperatur, "timestamp": wassertemperatur_datum})
    except Exception as e:
        logging.error(f"Fehler bei MONITOR_temperature: {e}")
        # Fallback: Cache lesen
        try:
            with open(CACHE_FILE_TEMP, "r", encoding="utf-8") as f:
                cached = json.load(f)
            logging.info("MONITOR_temperature: Fallback auf Cache")
            return jsonify(cached)
        except Exception as e2:
            logging.error(f"Fehler beim Lesen des Temperatur-Caches: {e2}")
            return jsonify({"temperature": "--.-"}), 500

@app.route('/MONITOR_iframe.html')
def iframe():
    try:
        result = send_from_directory(app.static_folder, 'MONITOR_iframe.html')
        logging.info("MONITOR_iframe.html erfolgreich ausgeliefert.")
        return result
    except Exception as e:
        logging.error(f"Fehler beim Senden von MONITOR_iframe.html: {e}\n{traceback.format_exc()}")
        return "Fehler beim Laden des Widgets", 500

@app.route('/MONITOR_waterlevel')
def get_waterlevel():
    try:
        response = requests.get(VOWIS_URL, timeout=5)
        data = response.json()
        wasserstand = data[0]['wasserstand']['wert']
        wasserstand_datum = data[0]['wasserstand']['datum']
        # Cache speichern
        with open(CACHE_FILE_WATER, "w", encoding="utf-8") as f:
            json.dump({"waterlevel": wasserstand, "timestamp": wasserstand_datum}, f)
        logging.info(f"MONITOR_waterlevel: {wasserstand} ({wasserstand_datum})")
        return jsonify({"waterlevel": wasserstand, "timestamp": wasserstand_datum})
    except Exception as e:
        logging.error(f"Fehler bei MONITOR_waterlevel: {e}")
        # Fallback: Cache lesen
        try:
            with open(CACHE_FILE_WATER, "r", encoding="utf-8") as f:
                cached = json.load(f)
            logging.info("MONITOR_waterlevel: Fallback auf Cache")
            return jsonify(cached)
        except Exception as e2:
            logging.error(f"Fehler beim Lesen des Wasserstand-Caches: {e2}")
            return jsonify({"waterlevel": "--.-"}), 500

@app.route('/MONITOR_iframe_waterlevel.html')
def iframe_waterlevel():
    try:
        result = send_from_directory(app.static_folder, 'MONITOR_iframe_waterlevel.html')
        logging.info("MONITOR_iframe_waterlevel.html erfolgreich ausgeliefert.")
        return result
    except Exception as e:
        logging.error(f"Fehler beim Senden von MONITOR_iframe_waterlevel.html: {e}\n{traceback.format_exc()}")
        return "Fehler beim Laden des Widgets", 500

def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

@app.errorhandler(404)
def not_found(e):
    logging.warning(f"404 Not Found: {str(e)} - Path: {str(request.path)}")
    return "404 Not Found", 404

@app.errorhandler(500)
def internal_error(e):
    logging.error(f"500 Internal Server Error: {str(e)} - Path: {str(request.path)}")
    return "500 Internal Server Error", 500

if __name__ == "__main__":
    port = find_free_port()
    print(f"MONITOR-App läuft auf Port {port}")
    logging.info(f"MONITOR-App läuft auf Port {port}")

    # Sicherstellen, dass static-Ordner und HTML-Dateien existieren
    STATIC_DIR = os.path.join(os.getcwd(), 'static')
    HTML_TEMP = '''<!DOCTYPE html>
    <html lang="de">
    <head>
      <meta charset="UTF-8">
      <title>Wassertemperatur Bodensee</title>
      <style>
        @font-face {
          font-family: 'Greta Sans Pro';
          src: local('Greta Sans Pro');
          font-weight: 400;
        }
        @font-face {
          font-family: 'Greta Sans Pro';
          src: local('Greta Sans Pro Bold');
          font-weight: 700;
        }
        html, body {
          margin: 0;
          padding: 0;
          background: transparent;
          width: 500px;
          height: 120px;
          overflow: hidden;
        }
        .MONITOR_container {
          background: #6ea0f6;
          border-radius: 12px;
          color: #fff;
          font-family: 'Greta Sans Pro', Arial, sans-serif;
          display: flex;
          align-items: center;
          padding: 24px 32px;
          width: 500px;
          height: 120px;
          box-sizing: border-box;
          overflow: hidden;
        }
        .MONITOR_left {
          flex: 1;
        }
        .MONITOR_title {
          font-size: 1.3em;
          font-weight: 400;
        }
        .MONITOR_bold {
          font-weight: 700;
        }
        .MONITOR_temp {
          font-size: 2.8em;
          font-weight: 400;
          margin-top: 8px;
        }
        .MONITOR_divider {
          width: 1px;
          background: #fff;
          height: 60px;
          margin: 0 24px;
          opacity: 0.5;
        }
        .MONITOR_right {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          justify-content: center;
        }
        .MONITOR_weathercheck {
          font-size: 1.4em;
          font-weight: 700;
          letter-spacing: 1px;
          margin-bottom: 4px;
        }
        .MONITOR_yellow-line {
          width: 100%;
          height: 4px;
          background: #ffe000;
          margin-top: 2px;
        }
      </style>
    </head>
    <body>
      <div class="MONITOR_container">
        <div class="MONITOR_left">
          <div class="MONITOR_title">Wassertemperatur <span class="MONITOR_bold">Bodensee</span></div>
          <div class="MONITOR_temp" id="MONITOR_temp">--.-°</div>
        </div>
        <div class="MONITOR_divider"></div>
        <div class="MONITOR_right">
          <div class="MONITOR_weathercheck">ZUM WETTERCHECK</div>
          <div class="MONITOR_yellow-line"></div>
        </div>
      </div>
      <script>
        async function fetchTemp() {
          try {
            const res = await fetch('/MONITOR_temperature');
            const data = await res.json();
            let temp = data.temperature.replace(/['\"]/g, '');
            document.getElementById('MONITOR_temp').textContent = temp + '°';
          } catch (e) {
            document.getElementById('MONITOR_temp').textContent = '--.-°';
          }
        }
        fetchTemp();
        setInterval(fetchTemp, 60000); // alle 60 Sekunden aktualisieren
      </script>
    </body>
    </html> 
    '''
    HTML_WATER = '''<!DOCTYPE html>
    <html lang="de">
    <head>
      <meta charset="UTF-8">
      <title>Wasserstand Bodensee</title>
      <style>
        @font-face {
          font-family: 'Greta Sans Pro';
          src: local('Greta Sans Pro');
          font-weight: 400;
        }
        @font-face {
          font-family: 'Greta Sans Pro';
          src: local('Greta Sans Pro Bold');
          font-weight: 700;
        }
        html, body {
          margin: 0;
          padding: 0;
          background: transparent;
          width: 500px;
          height: 120px;
          overflow: hidden;
        }
        .MONITOR_container {
          background: #6ea0f6;
          border-radius: 12px;
          color: #fff;
          font-family: 'Greta Sans Pro', Arial, sans-serif;
          display: flex;
          align-items: center;
          padding: 24px 32px;
          width: 500px;
          height: 120px;
          box-sizing: border-box;
          overflow: hidden;
        }
        .MONITOR_left {
          flex: 1;
        }
        .MONITOR_title {
          font-size: 1.3em;
          font-weight: 400;
        }
        .MONITOR_bold {
          font-weight: 700;
        }
        .MONITOR_value {
          font-size: 2.4em;
          font-weight: 400;
          margin-top: 8px;
          word-break: break-all;
          overflow-wrap: anywhere;
        }
        .MONITOR_divider {
          width: 1px;
          background: #fff;
          height: 60px;
          margin: 0 24px;
          opacity: 0.5;
        }
        .MONITOR_right {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          justify-content: center;
        }
        .MONITOR_weathercheck {
          font-size: 1.4em;
          font-weight: 700;
          letter-spacing: 1px;
          margin-bottom: 4px;
        }
        .MONITOR_yellow-line {
          width: 100%;
          height: 4px;
          background: #ffe000;
          margin-top: 2px;
        }
      </style>
    </head>
    <body>
      <div class="MONITOR_container">
        <div class="MONITOR_left">
          <div class="MONITOR_title">Wasserstand <span class="MONITOR_bold">Bodensee</span></div>
          <div class="MONITOR_value" id="MONITOR_value">--.-cm</div>
        </div>
        <div class="MONITOR_divider"></div>
        <div class="MONITOR_right">
          <div class="MONITOR_weathercheck">ZUM WETTERCHECK</div>
          <div class="MONITOR_yellow-line"></div>
        </div>
      </div>
      <script>
        async function fetchWaterlevel() {
          try {
            const res = await fetch('/MONITOR_waterlevel');
            const data = await res.json();
            let value = (data.waterlevel.match(/[\d,.]+/g) || ['--.-'])[0];
            document.getElementById('MONITOR_value').textContent = value + 'cm';
          } catch (e) {
            document.getElementById('MONITOR_value').textContent = '--.-cm';
          }
        }
        fetchWaterlevel();
        setInterval(fetchWaterlevel, 60000); // alle 60 Sekunden aktualisieren
      </script>
    </body>
    </html> 
    '''
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)
        logging.info(f"static-Ordner wurde neu erstellt: {STATIC_DIR}")

    html_temp_path = os.path.join(STATIC_DIR, 'MONITOR_iframe.html')
    if not os.path.exists(html_temp_path):
        with open(html_temp_path, 'w', encoding='utf-8') as f:
            f.write(HTML_TEMP)
        logging.info("MONITOR_iframe.html wurde neu erstellt.")

    html_water_path = os.path.join(STATIC_DIR, 'MONITOR_iframe_waterlevel.html')
    if not os.path.exists(html_water_path):
        with open(html_water_path, 'w', encoding='utf-8') as f:
            f.write(HTML_WATER)
        logging.info("MONITOR_iframe_waterlevel.html wurde neu erstellt.")

    iframe_code_temp = f'<iframe src="http://localhost:{port}/MONITOR_iframe.html" style="border:none;width:500px;height:120px;border-radius:12px;overflow:hidden;"></iframe>'
    iframe_code_water = f'<iframe src="http://localhost:{port}/MONITOR_iframe_waterlevel.html" style="border:none;width:500px;height:120px;border-radius:12px;overflow:hidden;"></iframe>'
    print("Schreibe MONITOR_iframe_codes.txt in:", os.getcwd())
    try:
        with open(os.path.join(os.getcwd(), "MONITOR_iframe_codes.txt"), "w", encoding="utf-8") as f:
            f.write(iframe_code_temp + "\n" + iframe_code_water + "\n")
        logging.info("MONITOR_iframe_codes.txt mit aktuellen iframe-Codes erstellt.")
    except Exception as e:
        logging.error(f"Fehler beim Schreiben von MONITOR_iframe_codes.txt: {e}")
        print(f"Fehler beim Schreiben von MONITOR_iframe_codes.txt: {e}")

    app.run(port=port) 
