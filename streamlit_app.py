import streamlit as st
import datetime
import json
import os
import base64

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="MisterApp", layout="centered")

# --- CSS PER LOOK MOBILE ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .card { background-color: white; border-radius: 15px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
    h1, h2, h3 { color: #1e3d59; }
    div.stButton > button { border-radius: 20px; background-color: #4CAF50; color: white; border: none; padding: 10px 20px; }
    </style>
""", unsafe_allow_html=True)

# --- FILE DI SALVATAGGIO ---
DB_FILE = "misterapp_db.json"

def caricare_dati():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "ragazzi": ["Luca R.", "Matteo V.", "Alessandro M.", "Filippo T.", "Gabriele L.", "Tommaso N."],
        "eventi": [],
        "storico_presenze": {},
        "storico_minutaggio": {}
    }

def salvare_dati():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, indent=4, ensure_ascii=False)

def get_logo_html():
    for ext in ["png", "jpg", "jpeg"]:
        if os.path.exists(f"stemma.{ext}"):
            with open(f"stemma.{ext}", "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                return f"<img src='data:image/{ext};base64,{encoded}' style='max-width: 80px; max-height: 80px; object-fit: contain;'>"
    return "<div style='font-size: 40px;'>🛡️</div>"

if "db" not in st.session_state: st.session_state.db = caricare_dati()

# --- MENU ---
menu = st.sidebar.radio("Navigazione", ["🔵 Allenamenti", "🟢 Calendario e Convocazioni", "📊 Statistiche", "⏱️ Planner", "🏃 Gestione Rosa"])

# ==========================================
# SCHERMATA: ALLENAMENTI
# ==========================================
if menu == "🔵 Allenamenti":
    st.header("🔵 Allenamenti")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    eventi_allenamento = [ev for ev in st.session_state.db["eventi"] if ev["tipo"] == "Allenamento"]
    if not eventi_allenamento: st.info("Nessun allenamento.")
    else:
        for ev in eventi_allenamento:
            with st.expander(f"Allenamento del {ev['data']}"):
                st.write(ev.get('nota', ''))
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SCHERMATA: PARTITE (LOGICA COMPLETA)
# ==========================================
elif menu == "🟢 Calendario e Convocazioni":
    st.header("🟢 Calendario e Convocazioni")
    eventi_partita = [ev for ev in st.session_state.db["eventi"] if ev["tipo"] in ["Partita", "Torneo"]]
    
    for ev in eventi_partita:
        with st.markdown("<div class='card'>", unsafe_allow_html=True):
            with st.expander(f"⚽ {ev.get('avversario')} - {ev.get('data')}"):
                
                # CARICAMENTO DATI
                appello = st.session_state.db["storico_presenze"].get(ev["id"], {})
                convocati_list = []
                
                tab1, tab2, tab3 = st.tabs(["⚙️ Compila", "📄 Modulo", "📱 WhatsApp"])
                
                with tab1:
                    resoconto = {}
                    for r in st.session_state.db["ragazzi"]:
                        resoconto[r] = st.radio(r, ["🟢 Convocato", "🔴 Non Convocato"], index=0 if appello.get(r) != "🔴 Non Convocato" else 1, horizontal=True, key=f"p_{r}_{ev['id']}")
                    if st.button("💾 Salva", key=f"s_{ev['id']}"):
                        st.session_state.db["storico_presenze"][ev["id"]] = resoconto
                        salvare_dati()
                        st.rerun()

                with tab2:
                    # Stampa Tabella
                    st.markdown(f"""
                    <table style='width:100%; border:1px solid #ccc;'>
                        <tr><th>Nome</th><th>C</th><th>NC</th></tr>
                        {''.join([f"<tr><td>{r}</td><td>{'X' if resoconto.get(r, '🟢 Convocato') == '🟢 Convocato' else ''}</td><td>{'X' if resoconto.get(r) == '🔴 Non Convocato' else ''}</td></tr>" for r in st.session_state.db["ragazzi"]])}
                    </table>
                    """, unsafe_allow_html=True)

                with tab3:
                    convocati_txt = "\n".join([f"✅ {r}" for r in st.session_state.db["ragazzi"] if resoconto.get(r, '🟢 Convocato') == '🟢 Convocato'])
                    msg = f"Ciao a tutti,\n\n⚽ *CONVOCAZIONI* ⚽\n⚽ *Partita:* {ev.get('avversario')}\n📅 *Data:* {ev.get('data')}\n🏟️ *Luogo:* {ev.get('indirizzo', 'Casa')}\n\n*ELENCO CONVOCATI:*\n{convocati_txt}\n\n*Forza USO UNITED!* 💚💙"
                    st.code(msg)
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SCHERMATA: ROSA
# ==========================================
elif menu == "🏃 Gestione Rosa":
    st.header("🏃 Gestione Rosa")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    for r in st.session_state.db["ragazzi"]:
        st.write(f"• {r}")
    st.markdown("</div>", unsafe_allow_html=True)