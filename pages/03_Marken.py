import streamlit as st
from github import Github
import pandas as pd
import os
import json
from datetime import datetime
from auth import check_auth

# --- CONFIG ---
GITHUB_TOKEN = st.secrets["github_token"]
REPO_NAME = st.secrets["repo_name"]
BRAND_FILE = "brands.txt"
SEEN_FILE = "seen_status.json" # Wir nutzen JSON für Zeitstempel
RESULT_FILE = "treffer_liste.csv"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def get_github_file(path):
    try:
        content = repo.get_contents(path)
        return content.decoded_content.decode("utf-8"), content.sha
    except:
        return "", None

def save_to_github(path, content_str, sha, message):
    if sha:
        repo.update_file(path, message, content_str, sha)
    else:
        repo.create_file(path, message, content_str)

# --- PASSWORT-SCHUTZ ---
is_admin = check_auth()

# --- DATEN LADEN ---
brands_raw, brands_sha = get_github_file(BRAND_FILE)
watched_brands = [b.strip() for b in brands_raw.splitlines() if b.strip()]
    
seen_raw, seen_sha = get_github_file(SEEN_FILE)
seen_status = json.loads(seen_raw) if seen_raw else {}
    
# --- UI ---
st.set_page_config(page_title="Marken Monitor", layout="wide")
st.title("🛡️ Marken Monitor Cockpit")
    
# Sidebar: Marke hinzufügen
if st.session_state.is_admin:
    st.sidebar.header("Marken-Verwaltung")
    new_brand = st.sidebar.text_input("Neue Marke hinzufügen:")
    if st.sidebar.button("Hinzufügen"):
        if new_brand and new_brand not in watched_brands:
            watched_brands.append(new_brand)
            save_to_github(BRAND_FILE, "\n".join(watched_brands), brands_sha, f"Add {new_brand}")
            st.rerun()
    
# Sidebar: Liste der überwachten Marken mit Löschfunktion
st.sidebar.divider()
st.sidebar.subheader("Überwachte Marken")
if watched_brands:
    for brand in watched_brands:
        col_name, col_del = st.sidebar.columns([4, 1])
        col_name.write(f"`{brand}`")
        if st.session_state.is_admin:
            if col_del.button("❌", key=f"del_{brand}"):
                watched_brands.remove(brand)
                save_to_github(BRAND_FILE, "\n".join(watched_brands), brands_sha, f"Remove {brand}")
                st.rerun()
else:
    st.sidebar.info("Keine Marken in der Liste.")
    
# --- ANALYSE ---
if os.path.exists(RESULT_FILE):
    df = pd.read_csv(RESULT_FILE)
    
# In der Analyse-Schleife:
    for brand in watched_brands:
        brand_data = df[df["Suchbegriff"] == brand]
        if brand_data.empty: continue
            
        current_fingerprint = str(brand_data["Fingerabdruck"].iloc[0])
            
        # seen_status speichert jetzt den Fingerabdruck statt des Datums
        last_seen_fingerprint = seen_status.get(brand, "")
            
        # Status: Neu, wenn Fingerabdruck anders ist UND nicht "error"
        is_new = current_fingerprint != last_seen_fingerprint and current_fingerprint != "error"
            
        title = f"🆕 {brand.upper()} (ÄNDERUNG ERKANNT!)" if is_new else f"✅ {brand.upper()}"
            
        with st.expander(title, expanded=is_new):
            st.dataframe(
                brand_data[["Portal", "Link", "Prüfdatum"]], 
                column_config={
                    "Link": st.column_config.LinkColumn("Register öffnen 🔗", width="medium")
                },
                hide_index=True, 
                use_container_width=True
            )
    
                
            if is_new:
                if st.button(f"Änderung für {brand} bestätigen", key=f"btn_{brand}"):
                    seen_status[brand] = current_fingerprint
                    _, s_sha = get_github_file(SEEN_FILE) # SHA aktuell halten
                    save_to_github(SEEN_FILE, json.dumps(seen_status), s_sha, f"Seen {brand}")
                    st.rerun()
    
else:
    st.info("Bitte starte den GitHub Action Scan, um Links zu generieren.")
