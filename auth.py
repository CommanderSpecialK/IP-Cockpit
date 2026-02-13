import streamlit as st

def check_auth():
    """
    Diese Funktion prüft, ob der User eingeloggt ist.
    Sie wird oben in jeder Unterseite aufgerufen.
    """
    # 1. Prüfen, ob der User eingeloggt ist
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.warning("⚠️ Zugriff verweigert. Bitte logge dich auf der Startseite ein.")
        if st.button("👉 Zum Login"):
            st.switch_page("main.py") 
        st.stop()

    # 2. Wenn eingeloggt: Sidebar-Navigation anzeigen
    if st.sidebar.button("🏠 Zurück zum Hauptmenü", use_container_width=True):
        st.switch_page("main.py")

    st.sidebar.divider()
    
    # 3. Admin-Status in der Sidebar visualisieren
    is_admin = st.session_state.get("is_admin", False)
    if is_admin:
        st.sidebar.success("⚡ Admin-Modus: Aktiv")
    else:
        st.sidebar.info("👤 Standard-Nutzer")
        
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.rerun()
    
    # Gibt den Admin-Status zurück, damit die App ihn nutzen kann
    return is_admin
