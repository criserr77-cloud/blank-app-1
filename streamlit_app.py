import streamlit as st
import datetime
import json
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="MisterApp - Settore Giovanile", layout="centered")

# --- FILE DI SALVATAGGIO (DATABASE LOCALE) ---
DB_FILE = "misterapp_db.json"

def caricare_dati():
    """Carica i dati dal file JSON se esiste, altrimenti usa dati di default."""
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
                {"id": "2", "data": "2026-06-27", "tipo": "Partita", "nota": "Campionato - In Trasferta ore 15:00"}
            ],
            "storico_presenze": {}, # Struttura: {"id_evento": {"Nome Ragazzo": "Stato"}}
            "storico_minutaggio": {} # Struttura: {"id_evento": {"Nome Ragazzo": Minuti}}
        }

def salvare_dati():
    """Salva i dati correnti nel file JSON."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, indent=4, ensure_ascii=False)

# Inizializziamo lo stato di Streamlit caricando i dati dal file
if "db" not in st.session_state:
    st.session_state.db = caricare_dati()
    if "storico_minutaggio" not in st.session_state.db:
        st.session_state.db["storico_minutaggio"] = {}

# Variabili di stato per gestire le modalità di modifica
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None
if "edit_evento" not in st.session_state:
    st.session_state.edit_evento = None

# --- MENU LATERALE ---
menu = st.sidebar.radio("Navigazione", [
    "📅 Calendario & Appelli", 
    "📊 Statistiche Allenamenti",
    "🏆 Statistiche Partite",
    "⏱️ Planner Allenamento",
    "🏃 Gestione Rosa"
])

st.sidebar.write("---")
st.sidebar.info("MisterApp Cloud - Attiva")

# ==========================================
# SCHERMATA 1: CALENDARIO & APPELLI
# ==========================================
if menu == "📅 Calendario & Appelli":
    st.header("📅 Calendario e Registro Presenze/Convocazioni")
    st.write("Seleziona un evento dal calendario per gestire l'appello o i convocati.")
    
    st.subheader("Impegni in agenda:")
    if not st.session_state.db["eventi"]:
        st.info("Nessun evento in calendario. Creane uno qui sotto!")
    else:
        for ev in st.session_state.db["eventi"]:
            # Se questo evento è in modalità modifica, mostriamo il form
            if st.session_state.edit_evento == ev["id"]:
                st.write(f"### ✏️ Modifica Evento")
                curr_date = datetime.datetime.strptime(ev["data"], "%Y-%m-%d").date()
                idx_tipo = ["Allenamento", "Partita", "Torneo"].index(ev["tipo"]) if ev["tipo"] in ["Allenamento", "Partita", "Torneo"] else 0
                
                mod_tipo = st.selectbox("Tipo di evento", ["Allenamento", "Partita", "Torneo"], index=idx_tipo, key=f"mod_t_{ev['id']}")
                mod_data = st.date_input("Data evento", curr_date, key=f"mod_d_{ev['id']}")
                mod_nota = st.text_input("Note", value=ev["nota"], key=f"mod_n_{ev['id']}")
                
                col_s, col_a = st.columns(2)
                with col_s:
                    if st.button("💾 Salva Modifiche", key=f"s_mod_{ev['id']}", type="primary"):
                        ev["tipo"] = mod_tipo
                        ev["data"] = str(mod_data)
                        ev["nota"] = mod_nota
                        st.session_state.edit_evento = None
                        salvare_dati()
                        st.success("Evento aggiornato!")
                        st.rerun()
                with col_a:
                    if st.button("❌ Annulla", key=f"a_mod_{ev['id']}"):
                        st.session_state.edit_evento = None
                        st.rerun()
                st.write("---")
            else:
                # Visualizzazione normale dell'evento
                data_f = datetime.datetime.strptime(ev["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
                is_allenamento = ev["tipo"] == "Allenamento"
                
                emoji = "🔵" if is_allenamento else "🟢"
                titolo_box = f"{emoji} {ev['tipo']} del {data_f} ({ev['nota']})"
                
                with st.expander(titolo_box):
                    # Tasti Modifica e Elimina in cima al box
                    col_mod, col_del = st.columns([1, 1])
                    with col_mod:
                        if st.button("✏️ Modifica Evento", key=f"ed_ev_{ev['id']}"):
                            st.session_state.edit_evento = ev["id"]
                            st.rerun()
                    with col_del:
                        if st.button("🗑️ Elimina Evento", key=f"del_ev_{ev['id']}"):
                            # Rimuoviamo l'evento
                            st.session_state.db["eventi"] = [e for e in st.session_state.db["eventi"] if e["id"] != ev["id"]]
                            # Pulizia dati associati all'evento eliminato
                            if ev["id"] in st.session_state.db["storico_presenze"]:
                                del st.session_state.db["storico_presenze"][ev["id"]]
                            if ev["id"] in st.session_state.db["storico_minutaggio"]:
                                del st.session_state.db["storico_minutaggio"][ev["id"]]
                            salvare_dati()
                            st.rerun()
                    
                    st.write("---")
                    st.write(f"#### 📋 {'Registro Presenze' if is_allenamento else 'Lista Convocazioni e Minutaggio'}")
                    
                    if not st.session_state.db["ragazzi"]:
                        st.warning("Non ci sono giocatori in rosa. Vai alla sezione 'Gestione Rosa'.")
                    else:
                        appello_evento = st.session_state.db["storico_presenze"].get(ev["id"], {})
                        minutaggio_evento = st.session_state.db["storico_minutaggio"].get(ev["id"], {})
                        
                        resoconto_corrente = {}
                        resoconto_minuti = {}
                        
                        opzioni = ["🟢 Presente", "🔴 Assente", "🟡 Infortunato"] if is_allenamento else ["🟢 Convocato", "🔴 Non Convocato"]
                        
                        for ragazzo in st.session_state.db["ragazzi"]:
                            if is_allenamento:
                                col_nome, col_stato = st.columns([1, 2])
                            else:
                                col_nome, col_stato, col_minuti = st.columns([1, 1.5, 1])
                                
                            with col_nome:
                                st.write(f"**{ragazzo}**")
                            with col_stato:
                                stato_precedente = appello_evento.get(ragazzo, opzioni[0])
                                indice_default = opzioni.index(stato_precedente) if stato_precedente in opzioni else 0
                                
                                stato = st.radio(
                                    f"Stato_{ragazzo}_{ev['id']}",
                                    opzioni,
                                    index=indice_default,
                                    horizontal=True,
                                    label_visibility="collapsed",
                                    key=f"p_{ragazzo}_{ev['id']}"
                                )
                                resoconto_corrente[ragazzo] = stato
                                
                            if not is_allenamento:
                                with col_minuti:
                                    if "Convocato" in stato and "Non" not in stato:
                                        min_prec = minutaggio_evento.get(ragazzo, 0)
                                        minuti = st.number_input("Min", min_value=0, max_value=150, value=min_prec, step=1, label_visibility="collapsed", key=f"m_{ragazzo}_{ev['id']}")
                                        resoconto_minuti[ragazzo] = minuti
                                    else:
                                        resoconto_minuti[ragazzo] = 0
                                        st.write("") 
                        
                        st.write("")
                        if st.button("💾 Salva Registro", key=f"btn_salva_{ev['id']}", type="primary"):
                            st.session_state.db["storico_presenze"][ev["id"]] = resoconto_corrente
                            if not is_allenamento:
                                st.session_state.db["storico_minutaggio"][ev["id"]] = resoconto_minuti
                            salvare_dati()
                            st.success("Dati archiviati con successo!")
                            st.rerun()

    st.write("---")
    st.subheader("➕ Programma un Nuovo Evento")
    nuovo_tipo = st.selectbox("Tipo di evento", ["Allenamento", "Partita", "Torneo"], key="new_tipo")
    nuova_data = st.date_input("Data evento", datetime.date.today(), key="new_data")
    nuova_nota = st.text_input("Note (es. 'Campo Principale ore 17:30')", placeholder="Inserisci dettagli...", key="new_nota")
    
    if st.button("Inserisci a Calendario"):
        nuovo_id = str(int(max([int(ev["id"]) for ev in st.session_state.db["eventi"]], default=0)) + 1)
        nuovo_evento = {
            "id": nuovo_id,
            "data": str(nuova_data),
            "tipo": nuovo_tipo,
            "nota": nuova_nota if nuova_nota.strip() != "" else "Nessuna nota"
        }
        st.session_state.db["eventi"].append(nuovo_evento)
        salvare_dati()
        st.success(f"Nuovo {nuovo_tipo} aggiunto correttamente!")
        st.rerun()

# ==========================================
# SCHERMATA 2: STATISTICHE ALLENAMENTI
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
# SCHERMATA 3: STATISTICHE PARTITE
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
# SCHERMATA 4: PLANNER ALLENAMENTO
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
# SCHERMATA 5: GESTIONE ROSA
# ==========================================
elif menu == "🏃 Gestione Rosa":
    st.header("🏃 Anagrafica e Gestione Rosa")
    
    st.subheader("I tuoi giocatori attuali:")
    if not st.session_state.db["ragazzi"]: 
        st.warning("La rosa è vuota!")
    else:
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
                                if ragazzo in appello:
                                    appello[nuovo_nome_mod] = appello.pop(ragazzo)
                                    
                            for ev_id, min_dict in st.session_state.db["storico_minutaggio"].items():
                                if ragazzo in min_dict:
                                    min_dict[nuovo_nome_mod] = min_dict.pop(ragazzo)
                                    
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
                    st.write(f"• **{ragazzo}** *(⏱️ {min_tot_anagrafica}' totali in campo)*")
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