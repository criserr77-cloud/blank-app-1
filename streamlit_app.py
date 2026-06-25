import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

ID_FOGLIO = "135IgLeZCtrVLe3APGqulTYTAX1tQg8SzT3Mw5hjjPC4"

def get_gspread_client():
    # Ricostruiamo il dizionario con le variabili singole prese dai Secrets
    creds_dict = {
        "type": st.secrets["TYPE"],
        "project_id": st.secrets["PROJECT_ID"],
        "private_key_id": st.secrets["PRIVATE_KEY_ID"],
        "private_key": st.secrets["PRIVATE_KEY"],
        "client_email": st.secrets["CLIENT_EMAIL"],
        "client_id": st.secrets["CLIENT_ID"],
        "auth_uri": st.secrets["AUTH_URI"],
        "token_uri": st.secrets["TOKEN_URI"],
        "auth_provider_x509_cert_url": st.secrets["AUTH_PROVIDER"],
        "client_x509_cert_url": st.secrets["CLIENT_CERT"]
    }
    
    creds = Credentials.from_service_account_info(
        creds_dict, 
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    )
    return gspread.authorize(creds)

# --- FUNZIONI DATI ---
def caricare_dati():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(ID_FOGLIO).sheet1
        val = sheet.acell('A1').value
        return json.loads(val) if val else {}
    except Exception as e:
        return {"error": str(e)}

# --- INTERFACCIA ---
st.title("⚽ MisterApp Cloud")

if "db" not in st.session_state:
    st.session_state.db = caricare_dati()

if "error" in st.session_state.db:
    st.error(f"Errore: {st.session_state.db['error']}")
else:
    st.success("Connessione stabilita!")
    if st.button("Aggiorna dati"):
        st.experimental_rerun()