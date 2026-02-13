import os
import json
import epo_ops
import xml.etree.ElementTree as ET
import urllib.parse
import re
import csv
from datetime import datetime

# --- KONFIGURATION ---
WATCHLIST_FILE = 'firmen_watchlist.csv'
DATA_FILE = 'app_patent_data.json'
BLACKLIST_FILE = 'deleted_patents.json'

def get_watchlist():
    """Lädt Firmen und deren Startdatum aus der CSV."""
    watchlist = []
    if not os.path.exists(WATCHLIST_FILE):
        print(f"HINWEIS: {WATCHLIST_FILE} nicht gefunden. Erstelle Standard-Eintrag.")
        return [{'firma': 'WFL Millturn', 'start': '20240101'}]
    
    with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Firma'):
                watchlist.append({
                    'firma': row['Firma'].strip(),
                    'start': row.get('Startdatum', '20200101').strip()
                })
    return watchlist

def load_json_file(filename):
    """Lädt eine JSON-Datei sicher als Liste oder Set."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def build_espacenet_url(cc, nr, kc):
    """Erzeugt den Link für das neue Espacenet (v2) Interface."""
    # Radikale Bereinigung der Nummer
    clean_nr = re.sub(r'[^a-zA-Z0-9]', '', nr)
    # Vermeide doppelte Kind-Codes
    query_id = f"{cc}{clean_nr}" if clean_nr.endswith(kc) else f"{cc}{clean_nr}{kc}"
    # Der stabilste Pfad für die neue v2 Webapp
    return f"https://worldwide.espacenet.com/patent/search?q=pn%3D{query_id}"

def run_monitor():
    # 1. API Credentials laden
    key = os.environ.get('EPO_KEY')
    secret = os.environ.get('EPO_SECRET')
    if not key or not secret:
        print("FEHLER: EPO_KEY oder EPO_SECRET Umgebungsvariablen fehlen!")
        return

    # 2. Bestehende Daten und Blacklist laden
    watchlist = get_watchlist()
    all_patents = load_json_file(DATA_FILE)
    deleted_ids = set(load_json_file(BLACKLIST_FILE)) # Set für schnellere Suche
    
    seen_ids = {p['id'] for p in all_patents}
    new_found = False
    
    client = epo_ops.Client(key=key, secret=secret)

    # 3. Firmen-Abfrage
    for entry in watchlist:
        firma = entry['firma']
        start_date = entry['start']
        print(f"Suche nach: {firma} ab {start_date}...")
        
        try:
            # EPO Query: pa=Anmelder UND pd=Publication Date
            query = f'pa="{firma}" and pd>={start_date}'
            response = client.published_data_search(query, 1, 100, constituents=['biblio'])
            
            if response.status_code != 200:
                print(f"  -> API Fehler {response.status_code}")
                continue

            root = ET.fromstring(response.content)
            # Suche nach exchange-document Elementen
            results = root.findall('.//{*}exchange-document')
            
            for doc in results:
                pub_ref = doc.find('.//{*}publication-reference')
                if pub_ref is None: continue

                country = pub_ref.find('.//{*}country')
                doc_num = pub_ref.find('.//{*}doc-number')
                kind = pub_ref.find('.//{*}kind')
                
                if doc_num is not None and country is not None:
                    cc = country.text.strip()
                    nr = doc_num.text.strip()
                    kc = kind.text.strip() if kind is not None else ""
                    
                    # ID generieren (Land + Nummer + Kind)
                    doc_id = f"{cc}{nr}{kc}"
                    
                    # LOGIK-CHECK: Neu? Und nicht bereits gelöscht?
                    if doc_id not in seen_ids and doc_id not in deleted_ids:
                        # Titel-Extraktion (DE bevorzugt, EN als Fallback)
                        title = "Titel nicht verfügbar"
                        titles = doc.findall('.//{*}invention-title')
                        for t in titles:
                            lang = t.get('lang')
                            if lang == 'de':
                                title = t.text
                                break
                            elif lang == 'en':
                                title = t.text

                        # Datum formatieren
                        date_elem = pub_ref.find('.//{*}date')
                        raw_date = date_elem.text if date_elem is not None else ""
                        try:
                            datum_anzeige = datetime.strptime(raw_date, '%Y%m%d').strftime('%d.%m.%Y')
                        except:
                            datum_anzeige = raw_date if raw_date else "Unbekannt"

                        # URL erstellen
                        clean_url = build_espacenet_url(cc, nr, kc)

                        all_patents.append({
                            "id": doc_id,
                            "firma": firma,
                            "titel": title,
                            "datum": datum_anzeige,
                            "sort_key": raw_date if raw_date else "00000000",
                            "url": clean_url,
                            "timestamp_added": datetime.now().isoformat()
                        })
                        seen_ids.add(doc_id)
                        new_found = True
                        print(f"  [NEU] {doc_id} - {title[:50]}...")

        except Exception as e:
            print(f"  [FEHLER] bei Firma {firma}: {str(e)}")

    # 4. Speichern bei Änderungen
    if new_found:
        # Sortieren nach Datum absteigend (YYYYMMDD)
        all_patents.sort(key=lambda x: x.get('sort_key', '00000000'), reverse=True)
        # Sort_key entfernen
        for p in all_patents: p.pop('sort_key', None)
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_patents, f, indent=4, ensure_ascii=False)
        print(f"\nUpdate beendet. {len(all_patents)} Patente insgesamt.")
    else:
        print("\nKeine neuen Patente gefunden.")

if __name__ == "__main__":
    run_monitor()
