"""
ETL dal database gestionale al data warehouse

Responsabilità:
  - Estrae i dati da database_gestionale.db
  - Trasforma e carica nelle dimensioni e nella fact table di data_warehouse.db
"""

import sqlite3
import os
from datetime import datetime, timedelta

# ============================================================
# CONFIGURAZIONE
# ============================================================
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
OLTP_PATH = os.path.join(BASE_DIR, "database_gestionale.db")
DW_PATH   = os.path.join(BASE_DIR, "data_warehouse.db")

# ============================================================
# CONNESSIONE
# ============================================================
def apri_connessione(percorso_db):
    conn = sqlite3.connect(percorso_db)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================
# UTILITY
# ============================================================
GIORNI_SETTIMANA = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
MESI = ["","Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno",
        "Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]

def pulisci(val):
    if val is None: return None
    v = str(val).strip()
    return v.title() if v else None

def fascia_durata_ore(h):
    if h is None: return "n/d"
    if h <= 60:   return "breve"
    if h <= 100:  return "medio"
    return "lungo"

def fascia_prezzo_prev(prev):
    if prev is None: return "n/d"
    if prev <= 2000:  return "basso"
    if prev <= 3000:  return "medio"
    return "alto"

def parse_data(dt_str):
    if not dt_str: return None
    return str(dt_str)[:10]

def row_dict(row, cols=None):
    if isinstance(row, sqlite3.Row): return dict(row)
    return dict(zip(cols, row)) if cols else dict(row)

# ============================================================
# FASE 1 — DIM_TEMPO
# ============================================================
def etl_dim_tempo(dw_conn):
    dw = dw_conn.cursor()
    d = datetime(2020, 1, 1)
    fine = datetime(2030, 12, 31)
    n = 0
    while d <= fine:
        dw.execute("""INSERT OR IGNORE INTO DIM_TEMPO
            (data_completa,giorno,giorno_settimana,settimana_anno,
             mese,nome_mese,trimestre,semestre,anno,is_weekend)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", (
            d.strftime("%Y-%m-%d"),
            d.day,
            GIORNI_SETTIMANA[d.weekday()],
            d.isocalendar()[1],
            d.month,
            MESI[d.month],
            (d.month - 1) // 3 + 1,
            1 if d.month <= 6 else 2,
            d.year,
            1 if d.weekday() >= 5 else 0))
        n += 1
        d += timedelta(days=1)
    dw_conn.commit()

# ============================================================
# FASE 2 — DIM_CLIENTE
# ============================================================
def etl_dim_cliente(oltp_conn, dw_conn):
    oltp = oltp_conn.cursor()
    dw   = dw_conn.cursor()
    oltp.execute("SELECT * FROM clienti")
    rows = oltp.fetchall()
    cols = [d[0] for d in oltp.description]
    caricati = scartati = 0

    for row in rows:
        r = row_dict(row, cols)
        if not r.get("codice_cliente"):
            scartati += 1; continue

        anno_reg = mese_reg = None
        if r.get("data_inserimento"):
            try:
                data_str = str(r["data_inserimento"])
                anno_reg = int(data_str[:4])
                mese_reg = int(data_str[5:7])
            except ValueError:
                pass

        dw.execute("""INSERT OR REPLACE INTO DIM_CLIENTE
            (codice_cliente,nome_completo,citta,provincia,regione,nazione,
             mese_registrazione,anno_registrazione,consenso_marketing,stato)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", (
            r["codice_cliente"],
            f"{pulisci(r['nome'])} {pulisci(r['cognome'])}".strip(),
            pulisci(r.get("citta")),
            (r.get("provincia") or "").upper() or None,
            pulisci(r.get("regione")),
            pulisci(r.get("nazione")),
            mese_reg, anno_reg,
            r.get("consenso_marketing", 0),
            r.get("stato", 1)))
        caricati += 1

    dw_conn.commit()

# ============================================================
# FASE 3 — DIM_FORNITORE
# ============================================================
def etl_dim_fornitore(oltp_conn, dw_conn):
    oltp = oltp_conn.cursor()
    dw   = dw_conn.cursor()
    oltp.execute("SELECT * FROM fornitori")
    rows = oltp.fetchall()
    cols = [d[0] for d in oltp.description]
    caricati = scartati = 0

    for row in rows:
        r = row_dict(row, cols)
        if not r.get("codice_fornitore"):
            scartati += 1; continue

        dw.execute("""INSERT OR REPLACE INTO DIM_FORNITORE
            (codice_fornitore,ragione_sociale,citta,provincia,regione,stato)
            VALUES (?,?,?,?,?,?)""", (
            r["codice_fornitore"],
            pulisci(r["ragione_sociale"]),
            pulisci(r.get("citta")),
            (r.get("provincia") or "").upper() or None,
            pulisci(r.get("regione")),
            r.get("stato", 1)))
        caricati += 1

    dw_conn.commit()

# ============================================================
# FASE 4 — DIM_OPERATORE
# ============================================================
def etl_dim_operatore(oltp_conn, dw_conn):
    oltp = oltp_conn.cursor()
    dw   = dw_conn.cursor()
    oltp.execute("SELECT * FROM operatori")
    rows = oltp.fetchall()
    cols = [d[0] for d in oltp.description]
    caricati = scartati = 0

    for row in rows:
        r = row_dict(row, cols)
        if not r.get("codice_operatore"):
            scartati += 1; continue

        dw.execute("""INSERT OR REPLACE INTO DIM_OPERATORE
            (codice_operatore,nome_completo,stato)
            VALUES (?,?,?)""", (
            r["codice_operatore"],
            f"{pulisci(r['nome'])} {pulisci(r['cognome'])}".strip(),
            r.get("stato", 1)))
        caricati += 1

    dw_conn.commit()

# ============================================================
# FASE 5 — DIM_SERVIZIO_FORNITORE
# ============================================================
def etl_dim_servizio_fornitore(oltp_conn, dw_conn):
    oltp = oltp_conn.cursor()
    dw   = dw_conn.cursor()
    oltp.execute("SELECT * FROM servizi_fornitore")
    rows = oltp.fetchall()
    cols = [d[0] for d in oltp.description]
    caricati = scartati = 0

    for row in rows:
        r = row_dict(row, cols)
        if not r.get("codice_servizi_fornitore"):
            scartati += 1; continue

        dw.execute("""INSERT OR REPLACE INTO DIM_SERVIZIO_FORNITORE
            (codice_servizi_fornitore,categoria_professionale,stato)
            VALUES (?,?,?)""", (
            r["codice_servizi_fornitore"],
            r["categoria_professionale"],
            r.get("stato", 1)))
        caricati += 1

    dw_conn.commit()

# ============================================================
# FASE 6 — DIM_SERVIZI
# ============================================================
def etl_dim_servizi(oltp_conn, dw_conn):
    oltp = oltp_conn.cursor()
    dw   = dw_conn.cursor()
    oltp.execute("SELECT * FROM servizi")
    rows = oltp.fetchall()
    cols = [d[0] for d in oltp.description]
    caricati = scartati = 0

    for row in rows:
        r = row_dict(row, cols)
        if not r.get("codice_servizio"):
            scartati += 1; continue

        dw.execute("""INSERT OR REPLACE INTO DIM_SERVIZI
            (codice_servizio,nome_servizio,durata_stimata_in_ore,
             prezzo_base_un_ora,prezzo_preventivato,stato,
             fascia_durata,fascia_prezzo)
            VALUES (?,?,?,?,?,?,?,?)""", (
            r["codice_servizio"],
            r["nome_servizio"],
            r["durata_stimata_in_ore"],
            r["prezzo_base_un_ora"],
            r["prezzo_preventivato"],
            r.get("stato", 1),
            fascia_durata_ore(r.get("durata_stimata_in_ore")),
            fascia_prezzo_prev(r.get("prezzo_preventivato"))))
        caricati += 1

    dw_conn.commit()

# ============================================================
# FASE 7 — FACT_RICHIESTE
# ============================================================
def etl_fact_richieste(oltp_conn, dw_conn):
    oltp = oltp_conn.cursor()
    dw   = dw_conn.cursor()
    oltp.execute("""
        SELECT r.*,
               c.codice_cliente            AS fk_cliente,
               sf.codice_servizi_fornitore AS fk_sfr,
               f.codice_fornitore          AS fk_fornitore,
               s.codice_servizio           AS fk_servizio,
               o.codice_operatore          AS fk_operatore
        FROM richieste r
        JOIN clienti            c   ON r.codice_cliente           = c.codice_cliente
        JOIN servizi_fornitore  sf  ON r.codice_servizi_fornitore = sf.codice_servizi_fornitore
        JOIN fornitori          f   ON sf.codice_fornitore        = f.codice_fornitore
        JOIN servizi            s   ON sf.codice_servizio         = s.codice_servizio
        JOIN operatori          o   ON r.codice_operatore         = o.codice_operatore
    """)
    rows = oltp.fetchall()
    cols = [d[0] for d in oltp.description]
    caricati = scartati = 0

    for row in rows:
        r = row_dict(row, cols)

        if not r.get("fk_cliente") or not r.get("fk_sfr") or \
           not r.get("fk_fornitore") or not r.get("fk_servizio") or \
           not r.get("fk_operatore"):
            scartati += 1; continue

        data_app = parse_data(r.get("data_appuntamento")) or ""
        data_ins = parse_data(r.get("data_inserimento"))  or ""

        dw.execute("""INSERT OR REPLACE INTO FACT_RICHIESTE
            (numero_richiesta,data_inserimento,
             codice_cliente,codice_fornitore,codice_operatore,
             codice_servizi_fornitore,codice_servizio,
             data_appuntamento,orario_appuntamento,pagamento_eseguito,stato_richiesta)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (
            r["numero_richiesta"],
            data_ins,
            r["fk_cliente"], r["fk_fornitore"], r["fk_operatore"],
            r["fk_sfr"], r["fk_servizio"],
            data_app,
            r.get("orario_appuntamento"),
            r.get("pagamento_eseguito", 0),
            r.get("stato_richiesta")))
        caricati += 1

    dw_conn.commit()

# ============================================================
# ESECUZIONE
# ============================================================
if __name__ == "__main__":

    oltp_conn = apri_connessione(OLTP_PATH)
    dw_conn   = apri_connessione(DW_PATH)

    print("Fase 1 — Dimensioni:")
    etl_dim_tempo(dw_conn)
    etl_dim_cliente(oltp_conn, dw_conn)
    etl_dim_fornitore(oltp_conn, dw_conn)
    etl_dim_operatore(oltp_conn, dw_conn)
    etl_dim_servizio_fornitore(oltp_conn, dw_conn)
    etl_dim_servizi(oltp_conn, dw_conn)

    print("\nFase 2 — Fact table:")
    etl_fact_richieste(oltp_conn, dw_conn)

    oltp_conn.close()
    dw_conn.close()
