import os
import pandas as pd
from datetime import datetime
import hashlib
from duckduckgo_search import DDGS
import urllib.parse

def get_snapshot(brand_name):
    """Erzeugt einen Fingerabdruck der aktuellen Suchergebnisse."""
    try:
        with DDGS() as ddgs:
            # Wir holen Titel der ersten 5 Treffer als Referenz
            results = list(ddgs.text(f'"{brand_name}" trademark', max_results=5))
            if not results:
                return "no_results"
            fingerprint = "".join([r['title'] for r in results])
            return hashlib.md5(fingerprint.encode()).hexdigest()
    except Exception as e:
        print(f"Fehler beim Snapshot für {brand_name}: {e}")
        return "error"

def generate_links(brand_name):
    """Erstellt die direkten Such-Links für die Register mit korrekter URL-Struktur."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    snapshot = get_snapshot(brand_name)
    brand_encoded = urllib.parse.quote(brand_name)
    
    sources = [
        {
            "Portal": "TM View (Europa)", 
            "Link": f"https://www.tmdn.org/tmview/#/tmview/results?page=1&pageSize=30&criteria=C&basicSearch={brand_encoded}&sortColumn=applicationDate&desc=true"
        },
        {
            "Portal": "WIPO (Global)", 
            "Link": f'https://www3.wipo.int/madrid/monitor/en/?q=%7B"searches":[%7B"te":"{brand_encoded}","fi":"BRAND_ALL,BRAND_ALL_P","df":"MARK_ALL,MARK_P","co":"AND"%7D],"mode":"simple"%7D'
        },
        {
            "Portal": "EUIPO (Europa)", 
            "Link": f"https://euipo.europa.eu/eSearch/#advanced/trademarks/1/100/n1=MarkVerbalElementText&v1={brand_encoded}&o1=AND&c1=CONTAINS&sf=ApplicationDate&so=desc"
        }
    ]
    return [{"Suchbegriff": brand_name, **s, "Prüfdatum": now, "Fingerabdruck": snapshot} for s in sources]


if __name__ == "__main__":
    if os.path.exists("brands.txt"):
        with open("brands.txt", "r") as f:
            targets = [line.strip() for line in f.readlines() if line.strip()]
    else:
        targets = []

    all_data = []
    for brand in targets:
        print(f"Scanne {brand}...")
        all_data.extend(generate_links(brand))

    df = pd.DataFrame(all_data)
    df.to_csv("treffer_liste.csv", index=False)
    print("Scan abgeschlossen.")
