import streamlit as st

st.set_page_config(page_title="IP Cockpit", layout="wide", page_icon="🚀")

# Initialisierung der Session States
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

def login():
    st.title("🔐 Login")
    st.write("Bitte gib dein Passwort ein, um fortzufahren.")
    
    with st.form("login_area"):
        password = st.text_input("Passwort", type="password")
        submit = st.form_submit_button("Anmelden")
        
        if submit:
            # Hier kannst du die Passwörter anpassen oder st.secrets nutzen
            if password == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.authenticated = True
                st.session_state.is_admin = True
                st.success("Erfolgreich als Admin angemeldet!")
                st.rerun()
            elif password == st.secrets["USER_PASSWORD"]:
                st.session_state.authenticated = True
                st.session_state.is_admin = False
                st.success("Erfolgreich als Nutzer angemeldet!")
                st.rerun()
            else:
                st.error("Falsches Passwort. Bitte versuche es erneut.")

login_page = st.Page(login, title="Anmeldung", icon="🔒")
dashboard = st.Page("main_dashboard.py", title="Startseite", icon="🏠", default=True)
news_app = st.Page("pages/01_WIPO_RSS.py", title="WIPO RSS", icon="📰")
epo_app = st.Page("pages/02_EPO_Monitor.py", title="EPO Monitor", icon="⚖️")
marken_app = st.Page("pages/03_Marken.py", title="Marken Monitor", icon="📜")
# Hier weitere Apps hinzufügen...

# 4. Logik: Welche Seiten sind sichtbar?
if st.session_state.authenticated:
    # Nur wenn eingeloggt, sind Dashboard und Apps sichtbar
    pg = st.navigation({
        "Startseite": [dashboard],
        "Anwendungen": [news_app, epo_app, marken_app]
    })
else:
    # Wenn nicht eingeloggt, existiert nur die Login-Seite
    pg = st.navigation([login_page], position="hidden") # "hidden" blendet Sidebar komplett aus!

pg.run()
