import streamlit as st

def check_auth():
    """
    Zentrale Sicherheitsprüfung für alle Unterseiten.
    Prüft Login, Admin-Status und bietet Navigation/Logout an.
    """
    
    # 1. Sicherheits-Check: Ist der User eingeloggt?
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Bitte melde dich zuerst an.")
        # Wir leiten zur Hauptdatei zurück, die den Login-Screen zeigt
        if st.button("👉 Zum Login"):
            st.rerun() 
        st.stop()

    # 2. Sidebar: Navigation zurück zur Startseite
    # Da st.navigation die App-Liste anzeigt, setzen wir den Home-Button ganz oben hin
    if st.sidebar.button("🏠 Zurück zum Hauptmenü", use_container_width=True):
        st.switch_page("main.py")

    st.sidebar.divider()
    
    # 3. Admin-Status prüfen & anzeigen
    is_admin = st.session_state.get("is_admin", False)
    
    if is_admin:
        st.sidebar.success("⚡ Admin-Modus: Aktiv")
    else:
        st.sidebar.info("👤 Standard-Nutzer")
        
    st.sidebar.divider()

    # 4. Zentraler Logout-Button am Ende der Sidebar
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
        # Alle Status-Variablen zurücksetzen
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.switch_page("main_dashboard.py")

    
    # Gibt den Status zurück, damit die Unterseite 'if is_admin:' nutzen kann
    return is_admin
