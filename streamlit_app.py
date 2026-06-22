import streamlit as st
import datetime
import json
import os
import base64
import urllib.parse
import streamlit.components.v1 as components

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="MisterApp - Settore Giovanile", layout="centered")

# --- CSS PER LOOK MOBILE E MENU RESPONSIVE (DARK/LIGHT MODE) ---
st.markdown("""
    <style>
    /* Colori nativi del tema di Streamlit per adattarsi perfettamente alla Dark Mode */
    .card { 
        background-color: var(--secondary-background-color); 
        color: var(--text-color);
        border-radius: 15px; 
        padding: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
        margin-bottom: 20px; 
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Stile specifico per ingrandire e distanziare il menu laterale su smartphone */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 12px 15px !important;
        margin-bottom: 10px !important;
        background-color: var(--secondary-background-color);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: var(--text-color) !important;
    }
    
    /* Tabella Rosa - Responsive CSS */
    .mobile-label { display: none; }
    .desktop-row {
        display: flex;
        align-items: center;
        text-align: center;
    }
    
    @media (max-width: 768px) {
        .hide-on-mobile { display: none !important; }
        .mobile-card { 
            flex-direction: column !important; 
            padding: 15px !important;
            gap: 8px !important;
            align-items: flex-start !important;
            text-align: left !important;
        }
        .mobile-card > div { 
            width: 100%;
            border-bottom: 1px solid rgba(128,128,128,0.2); 
            padding-bottom: 5px;
        }
        .mobile-card > div:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }
        .mobile-label { 
            display: inline-block !important; 
            width: 80px; 
            font-weight: bold; 
            opacity: 0.6; 
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- FILE DI SALVATAGGIO (DATABASE LOCALE) ---
DB_FILE = "misterapp_db.json"

def caricare_dati():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            dati = json.load(f)
            # Controlli di sicurezza per aggiornare file di salvataggio vecchi
            if "storico_minutaggio" not in dati: dati["storico_minutaggio"] = {}
            if "dettagli_ragazzi" not in dati: dati["dettagli_ragazzi"] = {}
            if "storico_gol" not in dati: dati["storico_gol"] = {}
            if "storico_risultati" not in dati: dati["storico_risultati"] = {}
            return dati
    else:
        return {
            "ragazzi": ["Luca R.", "Matteo V.", "Alessandro M.", "Filippo T.", "Gabriele L.", "Tommaso N."],
            "eventi": [
                {"id": "1", "data": "2026-06-23", "tipo": "Allenamento", "nota": "Campo Principale - ore 17:30"},
                {"id": "2", "data": "2026-06-27", "tipo": "Partita", "avversario": "Real City", "luogo": "Trasferta", "ora_partita": "15:00", "ora_convocazione": "14:00", "indirizzo": "Via Stadio 5, Torino", "nota": "Campionato"}
            ],
            "storico_presenze": {},
            "storico_minutaggio": {},
            "dettagli_ragazzi": {},
            "storico_gol": {},
            "storico_risultati": {}
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

# Inizializziamo lo stato di Streamlit e FORZIAMO I CONTROLLI CHIAVI
if "db" not in st.session_state:
    st.session_state.db = caricare_dati()

# Controlli di sicurezza fondamentali se la memoria (session_state) era già attiva con una versione vecchia
if "storico_minutaggio" not in st.session_state.db: st.session_state.db["storico_minutaggio"] = {}
if "dettagli_ragazzi" not in st.session_state.db: st.session_state.db["dettagli_ragazzi"] = {}
if "storico_gol" not in st.session_state.db: st.session_state.db["storico_gol"] = {}
if "storico_risultati" not in st.session_state.db: st.session_state.db["storico_risultati"] = {}

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None
if "edit_evento" not in st.session_state:
    st.session_state.edit_evento = None

# --- MENU LATERALE ---
menu = st.sidebar.radio("Navigazione", [
    "🔵 Calendario Allenamenti",
    "🟢 Calendario e Convocazioni", 
    "📊 Statistiche Allenamenti",
    "🏆 Statistiche Partite",
    "🏃 Anagrafica rosa"
])

st.sidebar.write("---")
st.sidebar.info("MisterApp Cloud - Attiva")

# --- TRUCCO PER CHIUDERE IL MENU SU SMARTPHONE ---
if "last_menu" not in st.session_state:
    st.session_state.last_menu = menu

if st.session_state.last_menu != menu:
    st.session_state.last_menu = menu
    components.html(
        """
        <script>
        setTimeout(function() {
            var doc = window.parent.document;
            if (window.parent.innerWidth <= 768) {
                var closeButtons = doc.querySelectorAll('button[aria-label="Close"]');
                closeButtons.forEach(function(btn) {
                    btn.click();
                });
                var standardClose = doc.querySelector('[data-testid="stSidebarCollapseButton"]');
                if (standardClose) {
                    standardClose.click();
                }
            }
        }, 300);
        </script>
        """,
        height=0, width=0
    )

# ==========================================
# SCHERMATA 1: ALLENAMENTI
# ==========================================
if menu == "🔵 Calendario Allenamenti":
    st.header("🔵 Calendario e Presenze Allenamenti")
    
    st.subheader("I tuoi Allenamenti:")
    eventi_allenamento = [ev for ev in st.session_state.db["eventi"] if ev["tipo"] == "Allenamento"]
    
    if not eventi_allenamento:
        st.info("Nessun allenamento in programma.")
    else:
        for ev in eventi_allenamento:
            if st.session_state.edit_evento == ev["id"]:
                st.write(f"### ✏️ Modifica Allenamento")
                curr_date = datetime.datetime.strptime(ev["data"], "%Y-%m-%d").date()
                mod_data = st.date_input("Data", curr_date, key=f"mod_d_{ev['id']}", format="DD/MM/YYYY")
                mod_nota = st.text_area("Note/Orario", value=ev.get("nota", ""), key=f"mod_n_{ev['id']}")
                
                col_s, col_a = st.columns(2)
                with col_s:
                    if st.button("💾 Salva", key=f"s_mod_{ev['id']}", type="primary"):
                        ev["data"] = str(mod_data)
                        ev["nota"] = mod_nota
                        st.session_state.edit_evento = None
                        salvare_dati()
                        st.rerun()
                with col_a:
                    if st.button("❌ Annulla", key=f"a_mod_{ev['id']}"):
                        st.session_state.edit_evento = None
                        st.rerun()
                st.write("---")
            else:
                data_f = datetime.datetime.strptime(ev["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
                titolo_box = f"🔵 Allenamento del {data_f} ({ev.get('nota', '')})"
                
                with st.expander(titolo_box):
                    col_mod, col_del = st.columns([1, 1])
                    with col_mod:
                        if st.button("✏️ Modifica", key=f"ed_ev_{ev['id']}"):
                            st.session_state.edit_evento = ev["id"]
                            st.rerun()
                    with col_del:
                        if st.button("🗑️ Elimina", key=f"del_ev_{ev['id']}"):
                            st.session_state.db["eventi"] = [e for e in st.session_state.db["eventi"] if e["id"] != ev["id"]]
                            if ev["id"] in st.session_state.db["storico_presenze"]: del st.session_state.db["storico_presenze"][ev["id"]]
                            if ev["id"] in st.session_state.db["storico_minutaggio"]: del st.session_state.db["storico_minutaggio"][ev["id"]]
                            salvare_dati()
                            st.rerun()
                    
                    st.write("---")
                    
                    tab1, tab2 = st.tabs(["📋 Registro Presenze", "📱 Messaggio WhatsApp"])
                    
                    with tab1:
                        if not st.session_state.db["ragazzi"]:
                            st.warning("Rosa vuota.")
                        else:
                            appello_evento = st.session_state.db["storico_presenze"].get(ev["id"], {})
                            resoconto_corrente = {}
                            opzioni = ["🟢 Presente", "🔴 Assente", "🟡 Infortunato"]
                            
                            for ragazzo in st.session_state.db["ragazzi"]:
                                col_nome, col_stato = st.columns([1, 2])
                                with col_nome: st.write(f"**{ragazzo}**")
                                with col_stato:
                                    stato_precedente = appello_evento.get(ragazzo, opzioni[0])
                                    indice_default = opzioni.index(stato_precedente) if stato_precedente in opzioni else 0
                                    stato = st.radio(f"Stato_{ragazzo}_{ev['id']}", opzioni, index=indice_default, horizontal=True, label_visibility="collapsed", key=f"p_{ragazzo}_{ev['id']}")
                                    resoconto_corrente[ragazzo] = stato
                            
                            st.write("")
                            if st.button("💾 Salva Registro", key=f"btn_salva_{ev['id']}", type="primary"):
                                st.session_state.db["storico_presenze"][ev["id"]] = resoconto_corrente
                                salvare_dati()
                                st.success("Presenze salvate!")
                                st.rerun()
                                
                    with tab2:
                        whatsapp_text_all = f"Ciao a tutti,\n\n"
                        whatsapp_text_all += f"🏃‍♂️ *PROSSIMO ALLENAMENTO* 🏃‍♂️\n"
                        whatsapp_text_all += f"📅 *Data:* {data_f}\n"
                        
                        nota_a = ev.get("nota", "").strip()
                        if nota_a:
                            whatsapp_text_all += f"📝 *Dettagli:*\n{nota_a}\n"
                            
                        whatsapp_text_all += f"\n*Vi aspetto puntuali!*\n*Forza USO UNITED!* 💚💙"
                        
                        whatsapp_url_all = urllib.parse.quote(whatsapp_text_all)
                        st.markdown(f'<a href="https://wa.me/?text={whatsapp_url_all}" target="_blank" style="display:block; width:100%; text-align:center; background-color:#25D366; color:white; padding:10px; border-radius:5px; text-decoration:none; font-weight:bold; margin-bottom:10px;">📲 Invia Testo su WhatsApp</a>', unsafe_allow_html=True)
                        st.code(whatsapp_text_all, language="markdown")
                        st.caption("💡 Clicca sull'iconcina dei foglietti in alto a destra per copiare!")

    st.write("---")
    st.subheader("➕ Fissa un nuovo Allenamento")
    col1, col2 = st.columns(2)
    with col1:
        nuova_data = st.date_input("Data", datetime.date.today(), key="new_data_all", format="DD/MM/YYYY")
    with col2:
        nuova_nota = st.text_area("Orario e Luogo (es. '17:30 Campo B')", key="new_nota_all")
        
    if st.button("Aggiungi Allenamento a Calendario"):
        nuovo_id = str(int(max([int(e["id"]) for e in st.session_state.db["eventi"]], default=0)) + 1)
        st.session_state.db["eventi"].append({
            "id": nuovo_id, 
            "data": str(nuova_data), 
            "tipo": "Allenamento", 
            "nota": nuova_nota
        })
        salvare_dati()
        st.rerun()

# ==========================================
# SCHERMATA 2: PARTITE E DISTINTA UFFICIALE
# ==========================================
elif menu == "🟢 Calendario e Convocazioni":
    st.header("🟢 Calendario e Convocazioni")
    
    st.subheader("Le tue Gare:")
    eventi_partita = [ev for ev in st.session_state.db["eventi"] if ev["tipo"] in ["Partita", "Torneo"]]
    
    if not eventi_partita:
        st.info("Nessuna partita in programma.")
    else:
        for ev in eventi_partita:
            if st.session_state.edit_evento == ev["id"]:
                st.write(f"### ✏️ Modifica Partita")
                curr_date = datetime.datetime.strptime(ev["data"], "%Y-%m-%d").date()
                
                col1, col2 = st.columns(2)
                with col1:
                    mod_data = st.date_input("Data", curr_date, key=f"mod_dp_{ev['id']}", format="DD/MM/YYYY")
                    mod_avv = st.text_input("Avversario", value=ev.get("avversario", ""), key=f"mod_avv_{ev['id']}")
                    mod_luogo = st.selectbox("Luogo", ["Casa", "Trasferta"], index=0 if ev.get("luogo", "Casa")=="Casa" else 1, key=f"mod_lu_{ev['id']}")
                    
                    if mod_luogo == "Trasferta":
                        mod_indirizzo = st.text_input("Indirizzo del campo", value=ev.get("indirizzo", ""), key=f"mod_ind_{ev['id']}")
                    else:
                        mod_indirizzo = ""
                with col2:
                    mod_orap = st.text_input("Ora Partita (es. 15:00)", value=ev.get("ora_partita", ""), key=f"mod_op_{ev['id']}")
                    mod_orac = st.text_input("Ora Convocazione (es. 14:00)", value=ev.get("ora_convocazione", ""), key=f"mod_oc_{ev['id']}")
                    mod_nota = st.text_area("Note (es. Campionato)", value=ev.get("nota", ""), key=f"mod_np_{ev['id']}")
                
                col_s, col_a = st.columns(2)
                with col_s:
                    if st.button("💾 Salva Modifiche", key=f"s_modp_{ev['id']}", type="primary"):
                        ev["data"] = str(mod_data)
                        ev["avversario"] = mod_avv
                        ev["luogo"] = mod_luogo
                        ev["indirizzo"] = mod_indirizzo
                        ev["ora_partita"] = mod_orap
                        ev["ora_convocazione"] = mod_orac
                        ev["nota"] = mod_nota
                        st.session_state.edit_evento = None
                        salvare_dati()
                        st.rerun()
                with col_a:
                    if st.button("❌ Annulla", key=f"a_modp_{ev['id']}"):
                        st.session_state.edit_evento = None
                        st.rerun()
                st.write("---")
            else:
                data_f = datetime.datetime.strptime(ev["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
                avv = ev.get("avversario", "Avversario")
                titolo_box = f"🟢 Partita vs {avv} del {data_f}"
                
                with st.expander(titolo_box):
                    col_mod, col_del = st.columns([1, 1])
                    with col_mod:
                        if st.button("✏️ Modifica Gara", key=f"ed_evp_{ev['id']}"):
                            st.session_state.edit_evento = ev["id"]
                            st.rerun()
                    with col_del:
                        if st.button("🗑️ Elimina Gara", key=f"del_evp_{ev['id']}"):
                            st.session_state.db["eventi"] = [e for e in st.session_state.db["eventi"] if e["id"] != ev["id"]]
                            if ev["id"] in st.session_state.db["storico_presenze"]: del st.session_state.db["storico_presenze"][ev["id"]]
                            if ev["id"] in st.session_state.db["storico_minutaggio"]: del st.session_state.db["storico_minutaggio"][ev["id"]]
                            if ev["id"] in st.session_state.db["storico_gol"]: del st.session_state.db["storico_gol"][ev["id"]]
                            if ev["id"] in st.session_state.db["storico_risultati"]: del st.session_state.db["storico_risultati"][ev["id"]]
                            salvare_dati()
                            st.rerun()
                    
                    st.write("---")
                    
                    appello_evento = st.session_state.db["storico_presenze"].get(ev["id"], {})
                    minutaggio_evento = st.session_state.db["storico_minutaggio"].get(ev["id"], {})
                    gol_evento = st.session_state.db["storico_gol"].get(ev["id"], {})
                    ris_evento = st.session_state.db["storico_risultati"].get(ev["id"], {})
                    
                    sq_casa = "USO UNITED" if ev.get("luogo", "Casa") == "Casa" else ev.get("avversario", "Avversario")
                    sq_trasf = ev.get("avversario", "Avversario") if ev.get("luogo", "Casa") == "Casa" else "USO UNITED"
                    ind_campo = ev.get("indirizzo", "Campo di Casa") if ev.get("luogo", "Casa") == "Trasferta" else "Campo di Casa"
                    
                    righe_giocatori = ""
                    convocati_list = []
                    
                    for idx, ragazzo in enumerate(st.session_state.db["ragazzi"]):
                        stato = appello_evento.get(ragazzo, "🟢 Convocato")
                        c_mark = "X" if "Convocato" in stato and "Non" not in stato else ""
                        nc_mark = "X" if "Non Convocato" in stato else ""
                        
                        if c_mark == "X":
                            convocati_list.append(ragazzo)
                            
                        righe_giocatori += f"<tr><td style='border: 1px solid black; padding: 5px;'>{idx+1}</td><td style='border: 1px solid black; padding: 5px; text-align: left;'>{ragazzo}</td><td style='border: 1px solid black; padding: 5px; color: green; font-weight: bold;'>{c_mark}</td><td style='border: 1px solid black; padding: 5px; color: red; font-weight: bold;'>{nc_mark}</td></tr>"
                    
                    logo_immagine = get_logo_html()
                    
                    # Generazione HTML Distinta
                    html_distinta = f"""<div style='background-color: white; color: black; padding: 10px; font-family: Arial, sans-serif; max-width: 600px; margin: auto;'>
<table style='width: 100%; border-collapse: collapse; text-align: center; border: 2px solid black;'>
<tr>
<td rowspan='6' style='width: 30%; border: 1px solid black; vertical-align: middle; padding: 10px;'>{logo_immagine}</td>
<td style='border: 1px solid black; color: #4CAF50; font-weight: bold; font-size: 20px; padding: 5px;'>USO UNITED</td>
</tr>
<tr><td style='border: 1px solid black; font-weight: bold; font-size: 16px; padding: 5px;'>CONVOCAZIONI</td></tr>
<tr><td style='border: 1px solid black; padding: 5px;'>PARTITA: {sq_casa} vs {sq_trasf}</td></tr>
<tr><td style='border: 1px solid black; padding: 5px;'>DATA: {data_f}</td></tr>
<tr><td style='border: 1px solid black; padding: 5px;'>ORA PARTITA: {ev.get("ora_partita", "___")}</td></tr>
<tr><td style='border: 1px solid black; padding: 5px;'>ORA CONVOCAZIONE: {ev.get("ora_convocazione", "___")}</td></tr>
<tr><td colspan='2' style='border: 1px solid black; font-weight: bold; padding: 5px;'>LUOGO: {ind_campo}</td></tr>
</table>
<table style='width: 100%; border-collapse: collapse; text-align: center; border: 2px solid black; border-top: none;'>
<tr style='font-weight: bold; background-color: #f0f0f0;'>
<td style='border: 1px solid black; padding: 5px; width: 10%;'>N°</td>
<td style='border: 1px solid black; padding: 5px; width: 50%;'>Nome e Cognome</td>
<td style='border: 1px solid black; padding: 5px; width: 20%;'>C</td>
<td style='border: 1px solid black; padding: 5px; width: 20%;'>NC</td>
</tr>
{righe_giocatori}
</table>
</div>"""
                    
                    # Generazione testo WhatsApp
                    whatsapp_text = f"Ciao a tutti,\n\n"
                    whatsapp_text += f"⚽ *CONVOCAZIONI* ⚽\n"
                    whatsapp_text += f"⚽ *{sq_casa}-{sq_trasf}*\n"
                    whatsapp_text += f"📅 *Data:* {data_f}\n"
                    whatsapp_text += f"⏰ *Ora Partita:* {ev.get('ora_partita', '___')}\n"
                    whatsapp_text += f"📍 *Ora Ritrovo:* {ev.get('ora_convocazione', '___')}\n"
                    whatsapp_text += f"🏟️ *Luogo:* {ind_campo}\n"
                    
                    nota_p = ev.get("nota", "").strip()
                    if nota_p:
                        whatsapp_text += f"📝 *Note:*\n{nota_p}\n"
                        
                    whatsapp_text += f"\n*ELENCO CONVOCATI:*\n"
                    if convocati_list:
                        for c in convocati_list:
                            whatsapp_text += f"✅ {c}\n"
                    else:
                        whatsapp_text += "*(Nessun convocato ancora selezionato)*\n"
                    whatsapp_text += "\n*Forza USO UNITED!* 💚💙"
                    
                    # Generazione HTML Report Gara
                    r_t1 = ris_evento.get("t1", "-")
                    r_t2 = ris_evento.get("t2", "-")
                    r_t3 = ris_evento.get("t3", "-")
                    
                    righe_report = ""
                    for idx, ragazzo in enumerate(st.session_state.db["ragazzi"]):
                        stato = appello_evento.get(ragazzo, "🟢 Convocato")
                        se_convocato = "Sì" if "Convocato" in stato and "Non" not in stato else "No"
                        m_giocati = minutaggio_evento.get(ragazzo, 0) if se_convocato == "Sì" else "-"
                        g_fatti = gol_evento.get(ragazzo, 0) if se_convocato == "Sì" else "-"
                        
                        colore_riga = "#ffffff" if se_convocato == "Sì" else "#ffe6e6"
                        
                        righe_report += f"<tr style='background-color: {colore_riga};'><td style='border: 1px solid black; padding: 5px; text-align: left;'>{ragazzo}</td><td style='border: 1px solid black; padding: 5px;'>{se_convocato}</td><td style='border: 1px solid black; padding: 5px;'>{m_giocati}</td><td style='border: 1px solid black; padding: 5px;'>{g_fatti}</td></tr>"
                    
                    html_report = f"""<div style='background-color: white; color: black; padding: 20px; font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 2px solid black;'>
<h2 style='text-align: center; color: #4CAF50; margin-top: 0;'>📊 REPORT GARA UFFICIALE</h2>
<div style='margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px;'>
    <p><strong>Partita:</strong> {sq_casa} vs {sq_trasf}</p>
    <p><strong>Data:</strong> {data_f} | <strong>Luogo:</strong> {ind_campo}</p>
</div>
<h3 style='color: #333;'>🏆 Risultato Tempi</h3>
<table style='width: 100%; border-collapse: collapse; text-align: center; border: 1px solid black; margin-bottom: 20px;'>
    <tr style='font-weight: bold; background-color: #f0f0f0;'>
        <td style='border: 1px solid black; padding: 10px;'>1° Tempo</td>
        <td style='border: 1px solid black; padding: 10px;'>2° Tempo</td>
        <td style='border: 1px solid black; padding: 10px;'>3° Tempo</td>
    </tr>
    <tr>
        <td style='border: 1px solid black; padding: 10px; font-size: 18px; font-weight: bold;'>{r_t1}</td>
        <td style='border: 1px solid black; padding: 10px; font-size: 18px; font-weight: bold;'>{r_t2}</td>
        <td style='border: 1px solid black; padding: 10px; font-size: 18px; font-weight: bold;'>{r_t3}</td>
    </tr>
</table>
<h3 style='color: #333;'>🏃‍♂️ Dati Giocatori</h3>
<table style='width: 100%; border-collapse: collapse; text-align: center; border: 1px solid black;'>
    <tr style='font-weight: bold; background-color: #f0f0f0;'>
        <td style='border: 1px solid black; padding: 5px; width: 40%;'>Giocatore</td>
        <td style='border: 1px solid black; padding: 5px; width: 20%;'>Convocato</td>
        <td style='border: 1px solid black; padding: 5px; width: 20%;'>Minuti</td>
        <td style='border: 1px solid black; padding: 5px; width: 20%;'>Gol ⚽</td>
    </tr>
    {righe_report}
</table>
</div>"""

                    # SCHEDE DI NAVIGAZIONE CON 4 TABS
                    tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Compila Elenco", "📄 Modulo Ufficiale", "📱 Messaggio WhatsApp", "📊 Report Gara"])
                    
                    with tab1:
                        if not st.session_state.db["ragazzi"]:
                            st.warning("Rosa vuota.")
                        else:
                            # Sezione Risultato Tempi
                            st.write("#### 🏆 Risultato della Gara")
                            col_t1, col_t2, col_t3 = st.columns(3)
                            with col_t1:
                                ris_t1 = st.text_input("1° Tempo", value=ris_evento.get("t1", ""), key=f"ris_t1_{ev['id']}")
                            with col_t2:
                                ris_t2 = st.text_input("2° Tempo", value=ris_evento.get("t2", ""), key=f"ris_t2_{ev['id']}")
                            with col_t3:
                                ris_t3 = st.text_input("3° Tempo", value=ris_evento.get("t3", ""), key=f"ris_t3_{ev['id']}")
                                
                            st.write("---")
                            st.write("#### 🏃 Convocati, Minuti e Gol")
                            
                            resoconto_corrente = {}
                            resoconto_minuti = {}
                            resoconto_gol = {}
                            opzioni = ["🟢 Convocato", "🔴 Non Convocato"]
                            
                            for ragazzo in st.session_state.db["ragazzi"]:
                                col_nome, col_stato, col_minuti, col_gol = st.columns([1, 1.2, 0.8, 0.8])
                                with col_nome: st.write(f"**{ragazzo}**")
                                with col_stato:
                                    stato_precedente = appello_evento.get(ragazzo, opzioni[0])
                                    indice_default = opzioni.index(stato_precedente) if stato_precedente in opzioni else 0
                                    stato = st.radio(f"Stato_{ragazzo}_{ev['id']}", opzioni, index=indice_default, horizontal=True, label_visibility="collapsed", key=f"p_{ragazzo}_{ev['id']}")
                                    resoconto_corrente[ragazzo] = stato
                                    
                                with col_minuti:
                                    if "Convocato" in stato and "Non" not in stato:
                                        min_prec = minutaggio_evento.get(ragazzo, 0)
                                        minuti = st.number_input("Min", min_value=0, max_value=150, value=min_prec, step=1, label_visibility="collapsed", key=f"m_{ragazzo}_{ev['id']}")
                                        resoconto_minuti[ragazzo] = minuti
                                    else:
                                        resoconto_minuti[ragazzo] = 0
                                        st.write("") 
                                        
                                with col_gol:
                                    if "Convocato" in stato and "Non" not in stato:
                                        gol_prec = gol_evento.get(ragazzo, 0)
                                        gol = st.number_input("Gol", min_value=0, max_value=20, value=gol_prec, step=1, label_visibility="collapsed", key=f"g_{ragazzo}_{ev['id']}")
                                        resoconto_gol[ragazzo] = gol
                                    else:
                                        resoconto_gol[ragazzo] = 0
                                        st.write("")
                            
                            st.write("")
                            if st.button("💾 Salva Dati Gara", key=f"btn_salvap_{ev['id']}", type="primary"):
                                st.session_state.db["storico_presenze"][ev["id"]] = resoconto_corrente
                                st.session_state.db["storico_minutaggio"][ev["id"]] = resoconto_minuti
                                st.session_state.db["storico_gol"][ev["id"]] = resoconto_gol
                                st.session_state.db["storico_risultati"][ev["id"]] = {"t1": ris_t1, "t2": ris_t2, "t3": ris_t3}
                                salvare_dati()
                                st.success("Dati archiviati con successo!")
                                st.rerun()

                    with tab2:
                        st.markdown(html_distinta, unsafe_allow_html=True)
                        st.write("")
                        
                        # Generatore PDF per la Distinta
                        html_to_print_distinta = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                        <title>Convocazioni {sq_casa} - {sq_trasf}</title>
                        </head>
                        <body onload="window.print()" style="padding: 20px;">
                        {html_distinta}
                        </body>
                        </html>
                        """
                        b64_print_distinta = base64.b64encode(html_to_print_distinta.encode('utf-8')).decode('utf-8')
                        st.markdown(f'<a href="data:text/html;base64,{b64_print_distinta}" target="_blank" style="display:block; width:100%; text-align:center; background-color:#FF4B4B; color:white; padding:10px; border-radius:5px; text-decoration:none; font-weight:bold; margin-bottom:10px;">🖨️ Genera PDF (Stampa Modulo)</a>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="⬇️ Scarica File Web (.html)",
                            data=html_distinta,
                            file_name=f"Distinta_{sq_casa}_vs_{sq_trasf}.html",
                            mime="text/html",
                            key=f"dl_html_{ev['id']}"
                        )

                    with tab3:
                        whatsapp_url = urllib.parse.quote(whatsapp_text)
                        st.markdown(f'<a href="https://wa.me/?text={whatsapp_url}" target="_blank" style="display:block; width:100%; text-align:center; background-color:#25D366; color:white; padding:10px; border-radius:5px; text-decoration:none; font-weight:bold; margin-bottom:10px;">📲 Invia Testo su WhatsApp</a>', unsafe_allow_html=True)
                        st.code(whatsapp_text, language="markdown")
                        st.caption("💡 **Suggerimento:** Per allegare il modulo ufficiale, scarica il file dalla scheda 'Modulo Ufficiale' e allegalo come 'Documento' direttamente nella chat WhatsApp!")

                    with tab4:
                        st.markdown(html_report, unsafe_allow_html=True)
                        st.write("")
                        
                        # Generatore PDF per il Report Gara
                        html_to_print_report = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                        <title>Report {sq_casa} - {sq_trasf}</title>
                        </head>
                        <body onload="window.print()" style="padding: 20px;">
                        {html_report}
                        </body>
                        </html>
                        """
                        b64_print_report = base64.b64encode(html_to_print_report.encode('utf-8')).decode('utf-8')
                        st.markdown(f'<a href="data:text/html;base64,{b64_print_report}" target="_blank" style="display:block; width:100%; text-align:center; background-color:#FF4B4B; color:white; padding:10px; border-radius:5px; text-decoration:none; font-weight:bold; margin-bottom:10px;">🖨️ Genera PDF (Stampa Report)</a>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="⬇️ Scarica Report Gara (.html)",
                            data=html_report,
                            file_name=f"Report_{sq_casa}_vs_{sq_trasf}.html",
                            mime="text/html",
                            key=f"dl_rep_{ev['id']}"
                        )

    st.write("---")
    st.subheader("➕ Inserisci una Nuova Partita")
    col1, col2 = st.columns(2)
    with col1:
        nuova_data = st.date_input("Data", datetime.date.today(), key="new_data_p", format="DD/MM/YYYY")
        nuovo_avversario = st.text_input("Avversario (es. Real City)", key="new_avv")
        nuovo_luogo = st.selectbox("Dove si gioca?", ["Casa", "Trasferta"], key="new_luogo")
        
        if nuovo_luogo == "Trasferta":
            nuovo_indirizzo = st.text_input("Indirizzo del campo (es. Via Roma 10)", key="new_indirizzo")
        else:
            nuovo_indirizzo = ""
    with col2:
        nuova_orap = st.text_input("Ora Partita (es. 15:00)", key="new_orap")
        nuova_orac = st.text_input("Ora Convocazione (es. 14:00)", key="new_orac")
        nuova_nota = st.text_area("Note (es. Campionato)", key="new_notap")
        
    if st.button("Aggiungi Partita a Calendario"):
        if nuovo_avversario.strip() == "":
            st.error("Inserisci il nome dell'avversario!")
        else:
            nuovo_id = str(int(max([int(e["id"]) for e in st.session_state.db["eventi"]], default=0)) + 1)
            st.session_state.db["eventi"].append({
                "id": nuovo_id, "data": str(nuova_data), "tipo": "Partita", 
                "avversario": nuovo_avversario, "luogo": nuovo_luogo, 
                "ora_partita": nuova_orap, "ora_convocazione": nuova_orac, 
                "indirizzo": nuovo_indirizzo, "nota": nuova_nota
            })
            salvare_dati()
            st.rerun()

# ==========================================
# SCHERMATA 3: STATISTICHE ALLENAMENTI
# ==========================================
elif menu == "📊 Statistiche Allenamenti":
    st.header("📊 Statistiche Allenamenti")
    
    storico = st.session_state.db["storico_presenze"]
    id_allenamenti = [ev["id"] for ev in st.session_state.db["eventi"] if ev["tipo"] == "Allenamento"]
    totale_allenamenti = sum(1 for ev_id in storico if ev_id in id_allenamenti)
    
    st.metric(label="Totale Allenamenti Svolti", value=totale_allenamenti)
    st.write("---")
    
    if totale_allenamenti == 0:
        st.info("📊 Nessun dato di allenamento registrato.")
    else:
        tabella_all = []
        for ragazzo in st.session_state.db["ragazzi"]:
            presenti, assenti, infortunati = 0, 0, 0
            for ev_id, appello in storico.items():
                if ev_id in id_allenamenti:
                    stato = appello.get(ragazzo, "")
                    if "Presente" in stato: presenti += 1
                    elif "Assente" in stato: assenti += 1
                    elif "Infortunato" in stato: infortunati += 1
            
            pct = (presenti / totale_allenamenti) * 100 if totale_allenamenti > 0 else 0.00
            tabella_all.append({
                "Giocatore": ragazzo,
                "🟢 Presenze": presenti,
                "🔴 Assenze": assenti,
                "🟡 Infortuni": infortunati,
                "📈 % Presenza": f"{pct:.2f}%"
            })
        st.table(tabella_all)

# ==========================================
# SCHERMATA 4: STATISTICHE PARTITE
# ==========================================
elif menu == "🏆 Statistiche Partite":
    st.header("🏆 Statistiche Convocazioni Partite")
    
    storico = st.session_state.db["storico_presenze"]
    id_gare = [ev["id"] for ev in st.session_state.db["eventi"] if ev["tipo"] in ["Partita", "Torneo"]]
    totale_gare = sum(1 for ev_id in storico if ev_id in id_gare)
    
    st.metric(label="Totale Gare Archiviate", value=totale_gare)
    st.write("---")
    
    if totale_gare == 0:
        st.info("📊 Nessun dato sulle partite presente in archivio.")
    else:
        tabella_gare = []
        for ragazzo in st.session_state.db["ragazzi"]:
            convocati, non_convocati = 0, 0
            for ev_id, appello in storico.items():
                if ev_id in id_gare:
                    stato = appello.get(ragazzo, "")
                    if "Convocato" in stato and "Non" not in stato: convocati += 1
                    elif "Non Convocato" in stato: non_convocati += 1
            
            pct_conv = (convocati / totale_gare) * 100 if totale_gare > 0 else 0.00
            min_tot = 0
            gol_tot = 0
            for ev_id in id_gare:
                min_tot += st.session_state.db["storico_minutaggio"].get(str(ev_id), {}).get(ragazzo, 0)
                gol_tot += st.session_state.db["storico_gol"].get(str(ev_id), {}).get(ragazzo, 0)

            tabella_gare.append({
                "Giocatore": ragazzo,
                "🟢 Convocati": convocati,
                "🔴 Non Convocati": non_convocati,
                "📈 % Convocazioni": f"{pct_conv:.2f}%",
                "⏱️ Min. Giocati": min_tot,
                "⚽ Gol Fatti": gol_tot
            })
        st.table(tabella_gare)

# ==========================================
# SCHERMATA 5: GESTIONE ROSA
# ==========================================
elif menu == "🏃 Anagrafica rosa":
    st.header("🏃 Anagrafica e Gestione Rosa")
    
    st.subheader("I tuoi giocatori attuali:")
    if not st.session_state.db["ragazzi"]: 
        st.warning("La rosa è vuota!")
    else:
        if "dettagli_ragazzi" not in st.session_state.db:
            st.session_state.db["dettagli_ragazzi"] = {}
            
        ruoli_lista = ["Portiere", "Difensore centrale", "Difensore esterno", "Centrocampista centrale", "Centrocampista esterno", "Attaccante centrale", "Attaccante esterno"]
        
        # --- INTESTAZIONE TABELLA (Nasconde automaticamente su mobile) ---
        st.markdown("""
            <div class="hide-on-mobile" style="display: flex; font-weight: bold; background-color: rgba(128,128,128,0.1); padding: 10px; border-radius: 5px; margin-bottom: 10px; border: 1px solid rgba(128,128,128,0.3); text-align: center;">
                <div style="flex: 1.5;">Nome</div>
                <div style="flex: 1.5;">Cognome</div>
                <div style="flex: 1.5;">Nascita</div>
                <div style="flex: 2;">Ruolo</div>
                <div style="flex: 1;">Mod</div>
                <div style="flex: 1;">Canc</div>
            </div>
        """, unsafe_allow_html=True)
        
        for i, ragazzo in enumerate(list(st.session_state.db["ragazzi"])):
            if st.session_state.edit_mode == i:
                st.write("---")
                st.markdown(f"**✏️ Modifica Dati per {ragazzo}**")
                dettagli = st.session_state.db["dettagli_ragazzi"].get(ragazzo, {"data_nascita": "2014-01-01", "ruolo": "Portiere"})
                try:
                    dob_val = datetime.datetime.strptime(dettagli.get("data_nascita", "2014-01-01"), "%Y-%m-%d").date()
                except:
                    dob_val = datetime.date(2014, 1, 1)
                    
                nuovo_nome_mod = st.text_input("Nome e Cognome", value=ragazzo, key=f"edit_input_{i}")
                nuova_dob_mod = st.date_input("Data di Nascita", value=dob_val, format="DD/MM/YYYY", key=f"edit_dob_{i}")
                
                curr_ruolo = dettagli.get("ruolo", "Portiere").capitalize()
                ruolo_idx = ruoli_lista.index(curr_ruolo) if curr_ruolo in ruoli_lista else 0
                nuovo_ruolo_mod = st.selectbox("Ruolo", ruoli_lista, index=ruolo_idx, key=f"edit_ruolo_{i}")
                
                col_salva, col_annulla = st.columns(2)
                with col_salva:
                    if st.button("💾 Salva", key=f"save_btn_{i}", type="primary"):
                        nuovo_nome_mod = nuovo_nome_mod.strip()
                        if nuovo_nome_mod:
                            if nuovo_nome_mod != ragazzo and ragazzo in st.session_state.db["dettagli_ragazzi"]:
                                st.session_state.db["dettagli_ragazzi"].pop(ragazzo, None)
                            
                            st.session_state.db["ragazzi"][i] = nuovo_nome_mod
                            st.session_state.db["dettagli_ragazzi"][nuovo_nome_mod] = {
                                "data_nascita": str(nuova_dob_mod),
                                "ruolo": nuovo_ruolo_mod
                            }
                            
                            for ev_id, appello in st.session_state.db["storico_presenze"].items():
                                if ragazzo in appello: appello[nuovo_nome_mod] = appello.pop(ragazzo)
                            for ev_id, min_dict in st.session_state.db["storico_minutaggio"].items():
                                if ragazzo in min_dict: min_dict[nuovo_nome_mod] = min_dict.pop(ragazzo)
                            for ev_id, gol_dict in st.session_state.db["storico_gol"].items():
                                if ragazzo in gol_dict: gol_dict[nuovo_nome_mod] = gol_dict.pop(ragazzo)
                                
                        st.session_state.edit_mode = None
                        salvare_dati()
                        st.rerun()
                with col_annulla:
                    if st.button("❌ Annulla", key=f"cancel_btn_{i}"):
                        st.session_state.edit_mode = None
                        st.rerun()
                st.write("---")
            else:
                dettagli = st.session_state.db["dettagli_ragazzi"].get(ragazzo, {})
                dob_str = "---"
                if "data_nascita" in dettagli:
                    try:
                        dob_str = datetime.datetime.strptime(dettagli["data_nascita"], "%Y-%m-%d").strftime("%d/%m/%Y")
                    except:
                        dob_str = dettagli["data_nascita"]
                ruolo_str = dettagli.get("ruolo", "---").capitalize()
                
                # Suddivido la stringa unica in Nome e Cognome 
                parti_nome = ragazzo.split(" ", 1)
                nome_tab = parti_nome[0]
                cognome_tab = parti_nome[1] if len(parti_nome) > 1 else ""
                
                col_info, col_btn_edit, col_btn_del = st.columns([6.5, 1, 1])
                with col_info:
                    # Su PC è una riga tabellare, su smartphone diventa una comoda Card
                    st.markdown(f"""
                    <div class="desktop-row mobile-card" style="background-color: var(--secondary-background-color); padding: 10px; border: 1px solid rgba(128,128,128,0.3); border-radius: 5px; margin-bottom: 5px;">
                        <div style="flex: 1.5;"><span class="mobile-label">Nome: </span>{nome_tab}</div>
                        <div style="flex: 1.5;"><span class="mobile-label">Cognome: </span>{cognome_tab}</div>
                        <div style="flex: 1.5;"><span class="mobile-label">Nascita: </span>{dob_str}</div>
                        <div style="flex: 2.0;"><span class="mobile-label">Ruolo: </span>{ruolo_str}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn_edit:
                    if st.button("✏️", key=f"edit_btn_{i}", use_container_width=True):
                        st.session_state.edit_mode = i
                        st.rerun()
                with col_btn_del:
                    if st.button("🗑️", key=f"del_btn_{i}", use_container_width=True):
                        st.session_state.db["ragazzi"].remove(ragazzo)
                        st.session_state.db["dettagli_ragazzi"].pop(ragazzo, None)
                        salvare_dati()
                        st.rerun()
                    
    st.write("---")
    st.subheader("➕ Aggiungi un nuovo giocatore")
    nuovo_nome_ins = st.text_input("Nome e Cognome del ragazzo:", key="nuovo_ins_input")
    nuova_dob_ins = st.date_input("Data di Nascita:", value=datetime.date(2014, 1, 1), format="DD/MM/YYYY", key="nuovo_ins_dob")
    ruoli_lista = ["Portiere", "Difensore centrale", "Difensore esterno", "Centrocampista centrale", "Centrocampista esterno", "Attaccante centrale", "Attaccante esterno"]
    nuovo_ruolo_ins = st.selectbox("Ruolo:", ruoli_lista, key="nuovo_ins_ruolo")
    
    if st.button("Inserisci in Squadra"):
        if nuovo_nome_ins.strip() != "" and nuovo_nome_ins.strip() not in st.session_state.db["ragazzi"]:
            nome_pulito = nuovo_nome_ins.strip()
            st.session_state.db["ragazzi"].append(nome_pulito)
            if "dettagli_ragazzi" not in st.session_state.db:
                st.session_state.db["dettagli_ragazzi"] = {}
            st.session_state.db["dettagli_ragazzi"][nome_pulito] = {
                "data_nascita": str(nuova_dob_ins),
                "ruolo": nuovo_ruolo_ins
            }
            salvare_dati()
            st.success(f"⚽ {nome_pulito} aggiunto alla rosa!")
            st.rerun()