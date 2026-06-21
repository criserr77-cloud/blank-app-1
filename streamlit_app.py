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
            "eventi": [
                {"id": "1", "data": "2026-06-23", "tipo": "Allenamento", "nota": "Campo Principale - ore 17:30"},
                {"id": "2", "data": "2026-06-27", "tipo": "Partita", "avversario": "Real City", "luogo": "Trasferta", "ora_partita": "15:00", "ora_convocazione": "14:00", "indirizzo": "Via Stadio 5, Torino", "nota": "Campionato"}
            ],
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

# Inizializziamo lo stato di Streamlit
if "db" not in st.session_state:
    st.session_state.db = caricare_dati()
    if "storico_minutaggio" not in st.session_state.db:
        st.session_state.db["storico_minutaggio"] = {}

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
    "⏱️ Planner Allenamento",
    "🏃 Gestione Rosa"
])

st.sidebar.write("---")
st.sidebar.info("MisterApp Cloud - Attiva")

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
                mod_data = st.date_input("Data", curr_date, key=f"mod_d_{ev['id']}")
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
                    st.write(f"#### 📋 Registro Presenze")
                    
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

    st.write("---")
    st.subheader("➕ Fissa un nuovo Allenamento")
    nuova_data = st.date_input("Data", datetime.date.today(), key="new_data_all")
    nuova_nota = st.text_area("Orario e Luogo (es. '17:30 Campo B')", key="new_nota_all")
    if st.button("Aggiungi Allenamento"):
        nuovo_id = str(int(max([int(e["id"]) for e in st.session_state.db["eventi"]], default=0)) + 1)
        st.session_state.db["eventi"].append({"id": nuovo_id, "data": str(nuova_data), "tipo": "Allenamento", "nota": nuova_nota})
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
                    mod_data = st.date_input("Data", curr_date, key=f"mod_dp_{ev['id']}")
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
                            salvare_dati()
                            st.rerun()
                    
                    st.write("---")
                    
                    appello_evento = st.session_state.db["storico_presenze"].get(ev["id"], {})
                    minutaggio_evento = st.session_state.db["storico_minutaggio"].get(ev["id"], {})
                    
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
                    
                    # Generazione testo WhatsApp con saluto iniziale e note
                    whatsapp_text = f"Ciao a tutti,\n\n"
                    whatsapp_text += f"⚽ *CONVOCAZIONI* ⚽\n"
                    whatsapp_text += f"⚽ *{sq_casa}vs{sq_trasf}*\n"
                    whatsapp_text += f"📅 *Data:* {data_f}\n"
                    whatsapp_text += f"⏰ *Ora Partita:* {ev.get('ora_partita', '___')}\n"
                    whatsapp_text += f"📍 *Ora Ritrovo:* {ev.get('ora_convocazione', '___')}\n"
                    whatsapp_text += f"🏟️ *Luogo:* {ind_campo}\n"
                    
                    # Aggiunta dinamica delle Note se presenti
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

                    # SCHEDE DI NAVIGAZIONE
                    tab1, tab2, tab3 = st.tabs(["⚙️ Compila Elenco", "📄 Modulo Ufficiale", "📱 Messaggio WhatsApp"])
                    
                    with tab1:
                        if not st.session_state.db["ragazzi"]:
                            st.warning("Rosa vuota.")
                        else:
                            resoconto_corrente = {}
                            resoconto_minuti = {}
                            opzioni = ["🟢 Convocato", "🔴 Non Convocato"]
                            
                            for ragazzo in st.session_state.db["ragazzi"]:
                                col_nome, col_stato, col_minuti = st.columns([1, 1.5, 1])
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
                            
                            st.write("")
                            if st.button("💾 Salva Convocazioni", key=f"btn_salvap_{ev['id']}", type="primary"):
                                st.session_state.db["storico_presenze"][ev["id"]] = resoconto_corrente
                                st.session_state.db["storico_minutaggio"][ev["id"]] = resoconto_minuti
                                salvare_dati()
                                st.success("Convocazioni salvate! Controlla la scheda 'Modulo Ufficiale'.")
                                st.rerun()

                    with tab2:
                        st.markdown(html_distinta, unsafe_allow_html=True)
                        st.write("")
                        st.download_button(
                            label="⬇️ Scarica File del Modulo (.html)",
                            data=html_distinta,
                            file_name=f"Distinta_{sq_casa}_vs_{sq_trasf}.html",
                            mime="text/html",
                            key=f"dl_html_{ev['id']}"
                        )

                    with tab3:
                        st.code(whatsapp_text, language="markdown")
                        st.caption("💡 Clicca sull'iconcina dei foglietti in alto a destra in questo riquadro nero per copiare tutto il testo in un colpo solo e incollarlo su WhatsApp!")

    st.write("---")
    st.subheader("➕ Inserisci una Nuova Partita")
    col1, col2 = st.columns(2)
    with col1:
        nuova_data = st.date_input("Data", datetime.date.today(), key="new_data_p")
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
            for ev_id in id_gare:
                min_tot += st.session_state.db["storico_minutaggio"].get(str(ev_id), {}).get(ragazzo, 0)

            tabella_gare.append({
                "Giocatore": ragazzo,
                "🟢 Convocati": convocati,
                "🔴 Non Convocati": non_convocati,
                "📈 % Convocazioni": f"{pct_conv:.2f}%",
                "⏱️ Min. Giocati": min_tot
            })
        st.table(tabella_gare)

# ==========================================
# SCHERMATA 5: PLANNER ALLENAMENTO
# ==========================================
elif menu == "⏱️ Planner Allenamento":
    st.header("⏱️ Planner della Seduta")
    st.subheader("Raffronto Carico di Lavoro (Target)")
    target_tecnico, target_tattico = 50.00, 50.00
    col_t1, col_t2 = st.columns(2)
    with col_t1: st.metric(label="Target Tecnico / Atletico", value=f"{target_tecnico:.2f}%")
    with col_t2: st.metric(label="Target Tattico / Situazionale", value=f"{target_tattico:.2f}%")
    
    st.write("---")
    tempo_attivazione = st.number_input("1. Attivazione / Riscaldamento (min)", min_value=0, value=15, step=5)
    tempo_tecnico = st.number_input("2. Esercitazione Tecnica (min)", min_value=0, value=30, step=5)
    tempo_partita = st.number_input("3. Partitina Finale (min)", min_value=0, value=25, step=5)
    
    durata_totale = tempo_attivazione + tempo_tecnico + tempo_partita
    st.write("---")
    st.info(f"⏱️ **Durata totale calcolata:** {durata_totale:.2f} minuti")

# ==========================================
# SCHERMATA 6: GESTIONE ROSA
# ==========================================
elif menu == "🏃 Gestione Rosa":
    st.header("🏃 Anagrafica e Gestione Rosa")
    
    st.subheader("I tuoi giocatori attuali:")
    if not st.session_state.db["ragazzi"]: 
        st.warning("La rosa è vuota!")
    else:
        id_allenamenti = [ev["id"] for ev in st.session_state.db["eventi"] if ev["tipo"] == "Allenamento"]
        totale_allenamenti = sum(1 for ev_id in st.session_state.db["storico_presenze"] if ev_id in id_allenamenti)
        
        for i, ragazzo in enumerate(list(st.session_state.db["ragazzi"])):
            if st.session_state.edit_mode == i:
                col_input, col_salva, col_annulla = st.columns([2, 1, 1])
                with col_input:
                    nuovo_nome_mod = st.text_input("Nuovo nome", value=ragazzo, key=f"edit_input_{i}", label_visibility="collapsed")
                with col_salva:
                    if st.button("💾 Salva", key=f"save_btn_{i}", type="primary"):
                        nuovo_nome_mod = nuovo_nome_mod.strip()
                        if nuovo_nome_mod and nuovo_nome_mod != ragazzo and nuovo_nome_mod not in st.session_state.db["ragazzi"]:
                            st.session_state.db["ragazzi"][i] = nuovo_nome_mod
                            for ev_id, appello in st.session_state.db["storico_presenze"].items():
                                if ragazzo in appello: appello[nuovo_nome_mod] = appello.pop(ragazzo)
                            for ev_id, min_dict in st.session_state.db["storico_minutaggio"].items():
                                if ragazzo in min_dict: min_dict[nuovo_nome_mod] = min_dict.pop(ragazzo)
                        st.session_state.edit_mode = None
                        salvare_dati()
                        st.rerun()
                with col_annulla:
                    if st.button("❌ Annulla", key=f"cancel_btn_{i}"):
                        st.session_state.edit_mode = None
                        st.rerun()
            else:
                col_nome, col_modifica, col_cancella = st.columns([2.5, 1, 1])
                with col_nome: 
                    min_tot_anagrafica = sum(st.session_state.db["storico_minutaggio"].get(ev_id, {}).get(ragazzo, 0) for ev_id in st.session_state.db["storico_minutaggio"])
                    
                    presenti = 0
                    for ev_id, appello in st.session_state.db["storico_presenze"].items():
                        if ev_id in id_allenamenti:
                            if "Presente" in appello.get(ragazzo, ""):
                                presenti += 1
                    pct_allenamenti = (presenti / totale_allenamenti) * 100 if totale_allenamenti > 0 else 0.00
                    
                    st.write(f"• **{ragazzo}** *(⏱️ {min_tot_anagrafica}' totali | 📈 {pct_allenamenti:.2f}% presenze All.)*")
                with col_modifica:
                    if st.button("✏️ Modifica", key=f"edit_btn_{i}"):
                        st.session_state.edit_mode = i
                        st.rerun()
                with col_cancella:
                    if st.button("🗑️ Elimina", key=f"del_btn_{i}"):
                        st.session_state.db["ragazzi"].remove(ragazzo)
                        salvare_dati()
                        st.rerun()
                    
    st.write("---")
    st.subheader("➕ Aggiungi un nuovo giocatore")
    nuovo_nome_ins = st.text_input("Nome e Cognome del ragazzo:", key="nuovo_ins_input")
    if st.button("Inserisci in Squadra"):
        if nuovo_nome_ins.strip() != "" and nuovo_nome_ins.strip() not in st.session_state.db["ragazzi"]:
            st.session_state.db["ragazzi"].append(nuovo_nome_ins.strip())
            salvare_dati()
            st.success(f"⚽ {nuovo_nome_ins.strip()} aggiunto alla rosa!")
            st.rerun()