import streamlit as st

# Füge dies oben in deine check_auth() Funktion in auth.py ein
st.markdown("""
    <style>
        /* Reduziert den Abstand zwischen den Elementen in der Sidebar */
        [data-testid="stSidebarUserContent"] {
            padding-top: 1rem;
        }
        .stButton, .stDivider {
            margin-bottom: -10px; /* Verringert den unteren Abstand von Buttons und Linien */
        }
        [data-testid="stVerticalBlock"] > div {
            gap: 0.5rem; /* Verringert den generellen vertikalen Abstand */
        }
    </style>
""", unsafe_allow_html=True)


def check_auth():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Bitte melde dich zuerst an.")
        if st.button("👉 Zum Login"):
            st.rerun() 
        st.stop()

    # 1. Navigation (Ganz oben)
#    if st.sidebar.button("🏠 Zurück zur Startseite", use_container_width=True):
#        st.switch_page("main_dashboard.py") 

    # 2. Logout (Direkt unter den Zurück-Button geschoben)
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.rerun()


    #col1, col2 = st.sidebar.columns(2)
    #with col1:
        #if st.button("🏠 Home", use_container_width=True):
            #st.switch_page("main_dashboard.py")
    #with col2:
        #if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            #st.session_state.authenticated = False
            #st.rerun()

    # 3. Nutzer-Status (Kleiner formatiert mit st.caption oder kleinerem Markdown)
    is_admin = st.session_state.get("is_admin", False)
    if is_admin:
        st.sidebar.markdown("⚡ Admin-Modus")
    else:
        # st.caption macht den Text deutlich kleiner und dezenter
        st.sidebar.caption("👤 Angemeldet als: Standard-Nutzer")
        
    #st.sidebar.divider()


    return is_admin


