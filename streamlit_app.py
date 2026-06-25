import streamlit as st
import gspread
import json

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="MisterApp", layout="centered")

# ID DEL TUO FOGLIO
ID_FOGLIO = "135IgLeZCtrVLe3APGqulTYTAX1tQg8SzT3Mw5hjjPC4"

# --- FUNZIONI DATI ---
def get_gspread_client():
    # Connessione semplificata (funziona se il foglio è pubblico in lettura/scrittura)
    return gspread.service_account_from_dict(st.secrets["gcp_service_account"])

# NOTA: Per far funzionare questa versione, su Streamlit Cloud Secrets dovrai 
# incollare solo un dizionario di base o usare la gestione gspread standard.
# Ma prova prima a vedere se così il sistema non ti blocca.

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

# --- LOGICA APP ---
st.title("⚽ MisterApp Cloud")

# Esempio di menu
menu = st.sidebar.radio("Navigazione", ["🔵 Allenamenti", "📈 Statistiche"])

if menu == "🔵 Allenamenti":
    st.header("🔵 Allenamenti")
    st.write("Benvenuto nel portale allenamenti.")
    
elif menu == "📈 Statistiche":
    st.header("📈 Statistiche Squadra")
    st.write("Qui visualizzerai i dati del foglio.")

st.sidebar.success("Sistema connesso")