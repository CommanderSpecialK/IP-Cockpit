import streamlit as st

def check_auth():
    """
    Zentrale Sicherheitsprüfung.
    """
    # 1. Sicherheits-Check: Wenn nicht eingeloggt, zeige Warnung und Stopp
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Bitte melde dich zuerst an.")
        # WICHTIG: rerun() statt switch_page("main.py")
        if st.button("👉 Zum Login"):
            st.rerun() 
        st.stop()

    # 2. Sidebar: Zurück zum Dashboard
    # Hier nutzen wir den DATEINAMEN der Dashboard-Datei
    if st.sidebar.button("🏠 Zurück zur Startseite", use_container_width=True):
        st.switch_page("main_dashboard.py") 

    st.sidebar.divider()
    
    # 3. Admin-Status prüfen
    is_admin = st.session_state.get("is_admin", False)
    if is_admin:
        st.sidebar.success("⚡ Admin-Modus: Aktiv")
    else:
        st.sidebar.info("👤 Standard-Nutzer")
        
    st.sidebar.divider()

    # 4. Logout-Button
    if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        # WICHTIG: Auch hier rerun() nutzen
        st.rerun() 
    
    return is_admin

