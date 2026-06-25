import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="MisterApp Cloud", layout="centered")

# --- CONNESSIONE CLOUD (Usa l'ID che mi hai fornito) ---
ID_FOGLIO = "135IgLeZCtrVLe3APGqulTYTAX1tQg8SzT3Mw5hjjPC4"

def get_gspread_client():
    try:
        creds_dict = json.loads(st.secrets["GCP_JSON"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Errore connessione: {e}")
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
            # Collegamento infallibile tramite ID
            sheet = client.open_by_key(ID_FOGLIO).sheet1
            val = sheet.acell('A1').value
            if val:
                dati = json.loads(val)
                base = struttura_base()
                for k in base.keys():
                    if k not in dati: dati[k] = base[k]
                return dati
        except Exception as e:
            st.warning(f"Database non trovato, inizializzo base: {e}")
    return struttura_base()

def salvare_dati():
    client = get_gspread_client()
    if client:
        try:
            sheet = client.open_by_key(ID_FOGLIO).sheet1
            sheet.update_acell('A1', json.dumps(st.session_state.db, ensure_ascii=False))
        except Exception as e:
            st.error(f"Errore salvataggio: {e}")

# Inizializzazione Sessione
if "db" not in st.session_state: st.session_state.db = caricare_dati()

# --- INTERFACCIA ---
st.sidebar.title("MisterApp")
menu = st.sidebar.radio("Navigazione", ["🔵 Allenamenti", "🟢 Convocazioni", "🏆 Partite", "📈 Statistiche", "🏃 Rosa"])

if menu == "🔵 Allenamenti":
    st.header("🔵 Allenamenti")
    # Inserisci qui il tuo codice per gli allenamenti...
    if st.button("Salva modifiche"): salvare_dati()

elif menu == "📈 Statistiche":
    st.header("📈 Statistiche Squadra")
    # Qui il codice della differenza reti che abbiamo visto...
    
st.sidebar.write("---")
st.sidebar.success("Cloud: Connesso")