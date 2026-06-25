import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
import datetime
import base64
import urllib.parse
import streamlit.components.v1 as components

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="MisterApp Cloud", layout="centered")

# --- CONNESSIONE CLOUD E GESTIONE DATI ---
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
            sheet = client.open("MisterApp_DB").sheet1
            val = sheet.acell('A1').value
            if val:
                dati = json.loads(val)
                # Verifica integrità chiavi
                base = struttura_base()
                for k in base.keys():
                    if k not in dati: dati[k] = base[k]
                return dati
        except Exception:
            pass
    return struttura_base()

def salvare_dati():
    client = get_gspread_client()
    if client:
        try:
            sheet = client.open("MisterApp_DB").sheet1
            sheet.update_acell('A1', json.dumps(st.session_state.db, ensure_ascii=False))
        except Exception as e:
            st.error(f"Errore salvataggio Cloud: {e}")

# Inizializzazione Sessione
if "db" not in st.session_state: st.session_state.db = caricare_dati()

# --- INTERFACCIA E LOGICA ---
menu = st.sidebar.radio("Navigazione", ["🔵 Allenamenti", "🟢 Convocazioni", "🏆 Statistiche Partite", "📈 Statistiche Squadra", "🏃 Rosa"])

# (Qui dovresti incollare le sezioni che avevamo già sviluppato per ogni schermata del menu, 
# avendo cura di usare sempre 'st.session_state.db' per leggere e 'salvare_dati()' per scrivere)

# Esempio di struttura sezione:
if menu == "🔵 Allenamenti":
    st.header("🔵 Calendario Allenamenti")
    # ... inserisci qui la logica degli allenamenti che avevamo ...
    # Ricorda: usa sempre st.session_state.db per i dati e chiama salvare_dati() dopo ogni modifica!

elif menu == "📈 Statistiche Squadra":
    st.header("📈 Statistiche di Squadra")
    # ... inserisci qui la logica della differenza reti e dei gol che abbiamo perfezionato ...

# --- NOTA PER TE ---
st.sidebar.write("---")
st.sidebar.success("Database sincronizzato con Google Sheets")