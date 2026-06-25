import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="MisterApp Cloud", layout="centered")

# ID DEL FOGLIO
ID_FOGLIO = "135IgLeZCtrVLe3APGqulTYTAX1tQg8SzT3Mw5hjjPC4"

def get_gspread_client():
    try:
        # Carica il JSON dai secrets
        # Se ricevi ancora errore di sintassi, significa che nel box Secrets 
        # c'è un carattere invisibile o una virgoletta fuori posto.
        creds_dict = json.loads(st.secrets["GCP_JSON"])
        
        creds = Credentials.from_service_account_info(
            creds_dict, 
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Errore critico nella connessione: {e}")
        return None

def struttura_base():
    return {
        "ragazzi": ["Luca R.", "Matteo V.", "Alessandro M.", "Filippo T.", "Gabriele L.", "Tommaso N."],
        "eventi": [],
        "storico_presenze": {},
        "storico_minutaggio": {},
        "dettagli_ragazzi": {},
        "storico_gol": {},
        "storico_risultati": {}
    }

def caricare_dati():
    client = get_gspread_client()
    if client:
        try:
            sheet = client.open_by_key(ID_FOGLIO).sheet1
            val = sheet.acell('A1').value
            if val:
                return json.loads(val)
        except Exception as e:
            st.warning(f"Impossibile leggere il database: {e}")
    return struttura_base()

def salvare_dati():
    client = get_gspread_client()
    if client:
        try:
            sheet = client.open_by_key(ID_FOGLIO).sheet1
            sheet.update_acell('A1', json.dumps(st.session_state.db, ensure_ascii=False))
            st.success("Database salvato con successo!")
        except Exception as e:
            st.error(f"Errore durante il salvataggio: {e}")

# Inizializzazione Sessione
if "db" not in st.session_state: 
    st.session_state.db = caricare_dati()

# --- INTERFACCIA ---
st.title("⚽ MisterApp Cloud")
menu = st.sidebar.radio("Navigazione", ["🔵 Allenamenti", "🏃 Rosa"])

if menu == "🔵 Allenamenti":
    st.header("🔵 Gestione Allenamenti")
    if st.button("Salva Database"):
        salvare_dati()

elif menu == "🏃 Rosa":
    st.header("🏃 Rosa Squadra")
    st.write(st.session_state.db["ragazzi"])

st.sidebar.write("---")
st.sidebar.info("Stato: Connesso")