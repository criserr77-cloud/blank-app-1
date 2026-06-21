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
            if "storico_minutaggio" not in dati:
                dati["storico_minutaggio"] = {}
            return dati
    else:
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
    return "<div style='font-size: 50px;'>🛡️</div><div style='color: red; font-weight: bold; font-size: 14px;'>USO</div><div style='color: green; font-weight: bold; font-size: 14px;'>UNITED</div>"

# Inizializziamo lo stato
if "db" not in st.session_state:
    st.session_state.db = caricare_dati()
if "edit_mode" not in st.session_state: st.session_state.edit_mode = None
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
    eventi_allenamento = [ev for ev in st.session_state.db["eventi"] if ev["tipo"] == "Allenamento"]
    if not eventi_allenamento: st.info("Nessun allenamento.")
    else:
        for ev in eventi_allenamento:
            with st.expander(f"🔵 Allenamento del {ev['data']} ({ev.get('nota', '')})"):
                appello_evento = st.session_state.db["storico_presenze"].get(ev["id"], {})
                resoconto_corrente = {}
                for ragazzo in st.session_state.db["ragazzi"]:
                    resoconto_corrente[ragazzo] = st.radio(ragazzo, ["🟢 Presente", "🔴 Assente", "🟡 Infortunato"], index=["🟢 Presente", "🔴 Assente", "🟡 Infortunato"].index(appello_evento.get(ragazzo, "🟢 Presente")), horizontal=True, key=f"p_{ragazzo}_{ev['id']}")
                if st.button("💾 Salva", key=f"btn_salva_{ev['id']}"):
                    st.session_state.db["storico_presenze"][ev["id"]] = resoconto_corrente
                    salvare_dati()
                    st.rerun()

    st.subheader("➕ Fissa un nuovo Allenamento")
    nuova_data = st.date_input("Data", datetime.date.today(), key="new_data_all")
    nuova_nota = st.text_input("Orario e Luogo", key="new_nota_all")
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
    eventi_partita = [ev for ev in st.session_state.db["eventi"] if ev["tipo"] in ["Partita", "Torneo"]]
    for ev in eventi_partita:
        with st.expander(f"🟢 Partita vs {ev.get('avversario')} del {ev['data']}"):
            appello = st.session_state.db["storico_presenze"].get(ev.get("id"), {})
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
                logo_html = get_logo_html()
                st.markdown(f"""<div style='background-color:white; color:black; padding:10px; border:2px solid black;'>
                    <table style='width:100%'><tr><td>{logo_html}</td><td>USO UNITED 2014<br>CONVOCAZIONI<br>Partita: {sq_casa} vs {sq_trasf}</td></tr></table>
                    <table style='width:100%; border:1px solid black;'><tr><th>Nome</th><th>C</th><th>NC</th></tr>
                    {''.join([f"<tr><td>{r}</td><td>{'X' if resoconto.get(r, '🟢 Convocato') == '🟢 Convocato' else ''}</td><td>{'X' if resoconto.get(r) == '🔴 Non Convocato' else ''}</td></tr>" for r in st.session_state.db["ragazzi"]])}
                    </table></div>""", unsafe_allow_html=True)
            
            with tab3:
                convocati_txt = "\n".join([f"✅ {r}" for r in st.session_state.db["ragazzi"] if resoconto.get(r, '🟢 Convocato') == '🟢 Convocato'])
                msg = f"Ciao a tutti,\n\n⚽ *CONVOCAZIONI* ⚽\n⚽ *Partita:*{sq_casa}vs{sq_trasf}\n📅 *Data:* {ev.get('data')}\n⏰ *Ora:* {ev.get('ora_partita', '___')}\n📍 *Ritrovo:* {ev.get('ora_convocazione', '___')}\n🏟️ *Luogo:* {ev.get('indirizzo', 'Campo')}\n\n📝 *Note:*\n{ev.get('nota', '')}\n\n*ELENCO CONVOCATI:*\n{convocati_txt}\n\n*Forza USO UNITED!* 💚💙"
                st.code(msg)

    st.subheader("➕ Inserisci Nuova Partita")
    nuovo_avv = st.text_input("Avversario")
    nuova_nota = st.text_area("Note")
    if st.button("Aggiungi Partita"):
        nuovo_id = str(int(max([int(e["id"]) for e in st.session_state.db["eventi"]], default=0)) + 1)
        st.session_state.db["eventi"].append({"id": nuovo_id, "data": str(datetime.date.today()), "tipo": "Partita", "avversario": nuovo_avv, "nota": nuova_nota})
        salvare_dati()
        st.rerun()

# ==========================================
# SEZIONI STATISTICHE E ROSA
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