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

# Logik: Zeige Login oder Dashboard
if not st.session_state.authenticated:
    login()
else:
    st.title("🚀 Willkommen im IP-Cockpit")
    st.markdown(f"""
    Du bist als **{'Admin' if st.session_state.is_admin else 'Nutzer'}** eingeloggt.
    
    Nutze die **Seitenleiste links**, um zwischen den verschiedenen Anwendungen zu wechseln.
    """)
    
    st.divider()
    
    if st.button("Abmelden"):
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.rerun()

