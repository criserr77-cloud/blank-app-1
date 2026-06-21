import streamlit as st
import datetime
import json
import os
import base64

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="MisterApp - Settore Giovanile", layout="centered")

# --- FILE DI SALVATAGGIO (DATABASE LOCALE) ---
DB_FILE = "misterapp_db.json"

def caricare_dati():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            dati = json.load(f)
            if "storico_minutaggio" not in dati: dati["storico_minutaggio"] = {}
            return dati
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
                return f"<img src='data:image/{ext};base64,{encoded}' style='max-width: 100px; max-height: 120px; object-fit: contain;'>"
    return "<div style='font-size: 50px;'>🛡️</div>"

# Inizializzazione Stato
if "db" not in st.session_state: st.session_state.db = caricare_dati()
if "edit_evento" not in st.session_state: st.session_state.edit_evento = None

# --- MENU LATERALE ---
menu = st.sidebar.radio("Navigazione", [
    "🔵 Calendario Allenamenti",
    "🟢 Calendario e Convocazioni", 
    "📊 Statistiche Allenamenti",
    "🏆 Statistiche Partite",
    "⏱️ Planner Allenamento",
    "🏃 Gestione Rosa"
])

# ==========================================
# SCHERMATA 1: ALLENAMENTI
# ==========================================
if menu == "🔵 Calendario Allenamenti":
    st.header("🔵 Calendario e Presenze Allenamenti")
    for ev in [e for e in st.session_state.db["eventi"] if e["tipo"] == "Allenamento"]:
        with st.expander(f"🔵 Allenamento {ev['data']} - {ev.get('nota', '')}"):
            appello = st.session_state.db["storico_presenze"].get(ev["id"], {})
            for r in st.session_state.db["ragazzi"]:
                appello[r] = st.radio(r, ["🟢 Presente", "🔴 Assente", "🟡 Infortunato"], index=["🟢 Presente", "🔴 Assente", "🟡 Infortunato"].index(appello.get(r, "🟢 Presente")), horizontal=True, key=f"p_{r}_{ev['id']}")
            if st.button("💾 Salva", key=f"s_{ev['id']}"):
                st.session_state.db["storico_presenze"][ev["id"]] = appello
                salvare_dati()
                st.rerun()

    st.subheader("➕ Nuovo Allenamento")
    nuova_data = st.date_input("Data", datetime.date.today(), key="d_all")
    nuova_nota = st.text_area("Orario e Luogo", key="n_all")
    if st.button("Aggiungi Allenamento"):
        nuovo_id = str(int(max([int(e["id"]) for e in st.session_state.db["eventi"]], default=0)) + 1)
        st.session_state.db["eventi"].append({"id": nuovo_id, "data": str(nuova_data), "tipo": "Allenamento", "nota": nuova_nota})
        salvare_dati()
        st.rerun()

# ==========================================
# SCHERMATA 2: PARTITE E CONVOCAZIONI
# ==========================================
elif menu == "🟢 Calendario e Convocazioni":
    st.header("🟢 Calendario e Convocazioni")
    for ev in [e for e in st.session_state.db["eventi"] if e["tipo"] in ["Partita", "Torneo"]]:
        with st.expander(f"🟢 Partita {ev.get('avversario')} - {ev.get('data')}"):
            appello = st.session_state.db["storico_presenze"].get(ev["id"], {})
            sq_casa = "USO UNITED" if ev.get("luogo", "Casa") == "Casa" else ev.get("avversario", "Avversario")
            sq_trasf = ev.get("avversario", "Avversario") if ev.get("luogo", "Casa") == "Casa" else "USO UNITED"
            
            tab1, tab2, tab3 = st.tabs(["⚙️ Compila", "📄 Modulo", "📱 WhatsApp"])
            with tab1:
                resoconto = {}
                for r in st.session_state.db["ragazzi"]:
                    resoconto[r] = st.radio(r, ["🟢 Convocato", "🔴 Non Convocato"], index=0 if appello.get(r) != "🔴 Non Convocato" else 1, horizontal=True, key=f"r_{r}_{ev['id']}")
                if st.button("💾 Salva", key=f"s_{ev['id']}"):
                    st.session_state.db["storico_presenze"][ev["id"]] = resoconto
                    salvare_dati()
                    st.rerun()
            with tab2:
                st.markdown(f"<div style='border:1px solid black; padding:10px;'>{get_logo_html()} <b>Partita:</b> {ev.get('avversario')}</div>", unsafe_allow_html=True)
            with tab3:
                convocati_txt = "\n".join([f"✅ {r}" for r in st.session_state.db["ragazzi"] if resoconto.get(r, '🟢 Convocato') == '🟢 Convocato'])
                # Formattazione richiesta: Partita:SquadraAvsSquadraB
                msg = f"Ciao a tutti,\n\n⚽ *CONVOCAZIONI* ⚽\n⚽ *Partita:*{sq_casa}vs{sq_trasf}\n📅 *Data:* {ev.get('data')}\n⏰ *Ora:* {ev.get('ora_partita', '___')}\n📍 *Ritrovo:* {ev.get('ora_convocazione', '___')}\n🏟️ *Luogo:* {ev.get('indirizzo', 'Campo')}\n\n📝 *Note:*\n{ev.get('nota', '')}\n\n*ELENCO CONVOCATI:*\n{convocati_txt}\n\n*Forza USO UNITED!* 💚💙"
                st.code(msg)

    st.subheader("➕ Nuova Partita")
    nuovo_avv = st.text_input("Avversario")
    nuova_nota = st.text_area("Note")
    if st.button("Aggiungi Partita"):
        nuovo_id = str(int(max([int(e["id"]) for e in st.session_state.db["eventi"]], default=0)) + 1)
        st.session_state.db["eventi"].append({"id": nuovo_id, "data": str(datetime.date.today()), "tipo": "Partita", "avversario": nuovo_avv, "nota": nuova_nota})
        salvare_dati()
        st.rerun()

# ==========================================
# ALTRE SCHERMATE (Statistiche, Planner, Rosa)
# ==========================================
elif menu == "📊 Statistiche Allenamenti":
    st.header("📊 Statistiche Allenamenti")
elif menu == "🏆 Statistiche Partite":
    st.header("🏆 Statistiche Partite")
elif menu == "⏱️ Planner Allenamento":
    st.header("⏱️ Planner")
elif menu == "🏃 Gestione Rosa":
    st.header("🏃 Gestione Rosa")
    for r in st.session_state.db["ragazzi"]: st.write(f"• {r}")