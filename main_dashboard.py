import streamlit as st
from auth import check_auth

# Sicherheits-Check (damit niemand die URL direkt aufruft)
is_admin = check_auth()

st.title("🚀 Willkommen im IP-Cockpit")
st.markdown(f"""
Hier hast du Zugriff auf alle Anwendungen. Nutze die **Seitenleiste**, 
um zwischen den Tools zu wechseln.
            
Du bist aktuell als **{'Admin' if is_admin else 'Nutzer'}** angemeldet.
""")

# Optional: Kurze Anleitung oder Status-Übersicht
st.info("Wähle links eine App aus, um zu starten.")
