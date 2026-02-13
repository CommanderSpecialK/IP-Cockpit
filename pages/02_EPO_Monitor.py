import streamlit as st
import pandas as pd
import requests
import json
import base64
from datetime import datetime
import plotly.express as px
from auth import check_auth

# --- KONFIGURATION & SECRETS ---
USER = "CommanderSpecialK"
REPO = "IP-Cockpit"
FILE = "app_patent_data.json"
ARCHIVE_FILE = "archived_patents.json"
DELETED_FILE = "deleted_patents.json"

API_URL = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
ARCHIVE_API_URL = f"https://api.github.com/repos/{USER}/{REPO}/contents/{ARCHIVE_FILE}"
DELETED_API_URL = f"https://api.github.com/repos/{USER}/{REPO}/contents/{DELETED_FILE}"

is_admin = check_auth()

    # --- CSS: BALKEN-KILLER ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none;}
    [data-testid="stExpander"] [data-testid="stVerticalBlock"] > div { gap: 0rem !important; margin-bottom: 0px !important; }
    .patent-card { background-color: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 10px; margin-bottom: 4px; }
    .neu-border { border-left: 6px solid #007bff; }
    .arch-border { border-left: 6px solid #6c757d; opacity: 0.8; }
    .patent-titel { font-weight: bold; font-size: 1.05rem; margin-bottom: 2px; color: white; }
    .patent-info { font-size: 0.85rem; color: #aaa; margin-bottom: 8px; }
    .stButton > button { margin: 0px !important; border-radius: 4px; height: 2.2em; font-size: 0.85rem; }
    .stMarkdown div p { margin: 0px !important; }
    </style>
""", unsafe_allow_html=True)

headers = {"Authorization": f"token {st.secrets['GH_PAT']}"}

def load_github_file(url):
    res = requests.get(f"{url}?t={datetime.now().timestamp()}", headers=headers)
    if res.status_code == 200:
        content = res.json()
        decoded = base64.b64decode(content['content']).decode('utf-8')
        return json.loads(decoded), content['sha']
    return [], None

def save_to_github(url, data, sha, message):
    updated_content = base64.b64encode(json.dumps(data, indent=4).encode('utf-8')).decode('utf-8')
    payload = {"message": message, "content": updated_content}
    if sha: payload["sha"] = sha
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code

# --- DATEN INITIAL LADEN ---
if "patent_list" not in st.session_state:
    data, sha = load_github_file(API_URL)
    arch_data, arch_sha = load_github_file(ARCHIVE_API_URL)
    archived_ids = [p['id'] for p in arch_data]
    clean_data = [p for p in data if p['id'] not in archived_ids]
        
    try:
        clean_data.sort(key=lambda x: datetime.strptime(x['datum'], '%d.%m.%Y'), reverse=True)
    except: pass

    st.session_state.patent_list = clean_data
    st.session_state.sha = sha
    st.session_state.archive_list = arch_data
    st.session_state.archive_sha = arch_sha
    st.session_state.last_sync = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

# --- SIDEBAR ---
st.sidebar.title("🔍 Steuerung")
#st.sidebar.info(f"Modus: {'Admin 🛠️' if st.session_state.is_admin else 'User 👤'}")
#st.sidebar.info(f"Letzter Sync:\n{st.session_state.last_sync}")
    
view_mode = st.sidebar.radio("Ansicht:", ["Neue Patente", "Archivierte Patente"])
search_query = st.sidebar.text_input("Suche", "").lower()

if view_mode == "Archivierte Patente":
    current_list = st.session_state.archive_list
    mode_prefix = "arch"
else:
    current_list = st.session_state.patent_list
    mode_prefix = "neu"

all_firmen = sorted(list(set(p['firma'] for p in current_list))) if current_list else []
selected_firmen = st.sidebar.multiselect("Firmen filtern", all_firmen, default=all_firmen)

filtered_patents = [
    p for p in current_list 
    if p['firma'] in selected_firmen and 
    (search_query in p['titel'].lower() or search_query in p['id'].lower())
]

# --- DASHBOARD ---
st.title(f"📊 {view_mode}")
if filtered_patents:
    m1, m2, m3 = st.columns(3)
    m1.metric("Anzahl", len(filtered_patents))
    m2.metric("Firmen", len(selected_firmen))
    m3.metric("Neuestes", filtered_patents[0]['datum'])

st.divider()

# --- PATENT LISTE ---
if not filtered_patents:
    st.warning("Keine Einträge gefunden.")
else:
    display_firmen = sorted(list(set(p['firma'] for p in filtered_patents)))
    for firma in display_firmen:
        f_patents = [p for p in filtered_patents if p['firma'] == firma]
        with st.expander(f"📁 {firma} ({len(f_patents)})", expanded=False):
            for p in f_patents:
                border_class = "neu-border" if view_mode == "Neue Patente" else "arch-border"
                    
                st.markdown(f"""
                <div class="patent-card {border_class}">
                    <div class="patent-titel">{p['titel']}</div>
                    <div class="patent-info">{p['id']} | {p['datum']}</div>
                """, unsafe_allow_html=True)
                    
                # Spaltenlayout basierend auf Modus anpassen
                if st.session_state.is_admin:
                    c1, c2, c3 = st.columns([0.4, 0.4, 0.2])
                    with c1:
                        st.link_button("🌐 Link", p['url'], use_container_width=True)
                    with c2:
                        if view_mode == "Neue Patente":
                            if st.button("📦 Archiv", key=f"btn_arch_{p['id']}", use_container_width=True):
                                st.session_state.patent_list.remove(p)
                                st.session_state.archive_list.append(p)
                                save_to_github(API_URL, st.session_state.patent_list, st.session_state.sha, f"Archiviert: {p['id']}")
                                save_to_github(ARCHIVE_API_URL, st.session_state.archive_list, st.session_state.archive_sha, f"Neu im Archiv: {p['id']}")
                                del st.session_state.patent_list 
                                st.rerun()
                        else:
                            st.write("📁 Archiviert")
                    with c3:
                        if st.button("🗑️", key=f"del_{mode_prefix}_{p['id']}", use_container_width=True):
                            current_list.remove(p)
                            del_data, d_sha = load_github_file(DELETED_API_URL)
                            if p['id'] not in del_data:
                                del_data.append(p['id'])
                                save_to_github(DELETED_API_URL, del_data, d_sha, f"Blacklist: {p['id']}")
                            active_url = ARCHIVE_API_URL if view_mode == "Archivierte Patente" else API_URL
                            active_sha = st.session_state.archive_sha if view_mode == "Archivierte Patente" else st.session_state.sha
                            save_to_github(active_url, current_list, active_sha, f"Del: {p['id']}")
                            del st.session_state.patent_list
                            st.rerun()
                else:
                    # User Modus: Nur der Link Button
                    st.link_button("🌐 Link öffnen", p['url'], use_container_width=True)
                    
                st.markdown('</div>', unsafe_allow_html=True)

# --- UPDATE (Nur für Admin) ---
if st.session_state.is_admin:
    st.sidebar.divider()
    if st.sidebar.button("🔄 Globales EPO-Update", use_container_width=True):
        requests.post(f"https://api.github.com/repos/{USER}/{REPO}/actions/workflows/main.yml/dispatches",
                        headers=headers, json={"ref": "main"})
        st.sidebar.success("Update gestartet!")
