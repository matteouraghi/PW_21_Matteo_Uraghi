"""
Popola il db database_gestionale.db con i dati dai 6 file CSV.
Ogni file CSV corrisponde a una tabella del db.
"""
import sqlite3
import os
import csv
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database_gestionale.db")

FILES = {
    "fornitori":         "file_fornitori.csv",
    "clienti":           "file_clienti.csv",
    "servizi":           "file_servizi.csv",
    "operatori":         "file_operatori.csv",
    "servizi_fornitore": "file_servizi_fornitore.csv",
    "richieste":         "file_richieste.csv",
}

# ============================================================
# UTILITY
# ============================================================
def conv_date(val):
    """dd/mm/yyyy [HH:MM] → yyyy-mm-dd [HH:MM:SS] | None"""
    if val is None: return None
    s = str(val).strip()
    if not s: return None
    for fmt_in, fmt_out in [
        ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S"),
        ("%d/%m/%Y",       "%Y-%m-%d"),
    ]:
        try:
            return datetime.strptime(s, fmt_in).strftime(fmt_out)
        except ValueError:
            continue
    return s  # fallback: lascia invariato

def conv_num(val):
    """Converte stringa numerica con virgola decimale in float (es. da 1431,06 a 1431.06)."""
    if val is None: return None
    s = str(val).strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None

def read_rows(filename):
    """Legge un CSV con separatore ; e restituisce (headers, rows)."""
    path = os.path.join(BASE_DIR, filename)
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        headers = [h.strip() for h in next(reader) if h.strip()]
        n = len(headers)
        for row in reader:
            if not row or not row[0].strip(): continue
            if row[0].strip().lower().startswith("legenda"): break
            row = (row[:n] + [""] * n)[:n]
            row = [v.strip() if v.strip() != "" else None for v in row]
            rows.append(row)
    return headers, rows

# ============================================================
# CONNESSIONE
# ============================================================
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# ============================================================
# 1. FORNITORI
# ============================================================
headers, rows = read_rows(FILES["fornitori"])
n = 0
for r in rows:
    d = dict(zip(headers, r))
    cur.execute("""INSERT OR REPLACE INTO fornitori
        (id_fornitore,codice_fornitore,ragione_sociale,partita_iva,indirizzo,
         cap,citta,provincia,regione,nazione,telefono,email,pec,
         data_inserimento,data_ultima_modifica,stato)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
        d["id_fornitore"], d["codice_fornitore"], d["ragione_sociale"], d["partita_iva"],
        d["indirizzo"], d["cap"], d["citta"], d["provincia"], d["regione"], d["nazione"],
        d["telefono"], d["email"], d["pec"],
        conv_date(d["data_inserimento"]), conv_date(d["data_ultima_modifica"]), d["stato"]))
    n += 1

# ============================================================
# 2. CLIENTI
# ============================================================
headers, rows = read_rows(FILES["clienti"])
n = 0
for r in rows:
    d = dict(zip(headers, r))
    cur.execute("""INSERT OR REPLACE INTO clienti
        (id_cliente,codice_cliente,nome,cognome,data_nascita,codice_fiscale,
         email,telefono,indirizzo,cap,citta,provincia,regione,nazione,
         data_inserimento,stato,consenso_privacy,consenso_marketing,data_ultima_modifica)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
        d["id_cliente"], d["codice_cliente"], d["nome"], d["cognome"],
        conv_date(d["data_nascita"]), d["codice_fiscale"], d["email"], d["telefono"],
        d["indirizzo"], d["cap"], d["citta"], d["provincia"], d["regione"], d["nazione"],
        conv_date(d["data_inserimento"]), d["stato"], d["consenso_privacy"],
        d["consenso_marketing"], conv_date(d["data_ultima_modifica"])))
    n += 1

# ============================================================
# 3. SERVIZI
# ============================================================
headers, rows = read_rows(FILES["servizi"])
n = 0
for r in rows:
    d = dict(zip(headers, r))
    cur.execute("""INSERT OR REPLACE INTO servizi
        (id_servizio,codice_servizio,nome_servizio,descrizione,
         durata_stimata_in_ore,prezzo_base_un_ora,iva_percentuale,prezzo_preventivato,
         stato,data_inserimento,data_ultima_modifica)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (
        d["id_servizio"], d["codice_servizio"], d["nome_servizio"], d["descrizione"],
        d["durata_stimata_in_ore"], d["prezzo_base_un_ora"], d["iva_percentuale"],
        conv_num(d["prezzo_preventivato"]),
        d["stato"],
        conv_date(d["data_inserimento"]), conv_date(d["data_ultima_modifica"])))
    n += 1

# ============================================================
# 4. SERVIZI_FORNITORE
# ============================================================
headers, rows = read_rows(FILES["servizi_fornitore"])
n = 0
for r in rows:
    d = dict(zip(headers, r))
    cur.execute("""INSERT OR REPLACE INTO servizi_fornitore
        (id_servizi_fornitore,codice_servizi_fornitore,codice_fornitore,codice_servizio,
         categoria_professionale,stato,data_inserimento,data_ultima_modifica)
        VALUES (?,?,?,?,?,?,?,?)""", (
        d["id_servizi_fornitore"], d["codice_servizi_fornitore"], d["codice_fornitore"],
        d["codice_servizio"], d["categoria_professionale"], d["stato"],
        conv_date(d["data_inserimento"]), conv_date(d["data_ultima_modifica"])))
    n += 1

# ============================================================
# 5. OPERATORI
# ============================================================
headers, rows = read_rows(FILES["operatori"])
n = 0
for r in rows:
    d = dict(zip(headers, r))
    cur.execute("""INSERT OR REPLACE INTO operatori
        (id_operatore,codice_operatore,codice_fornitore,nome,cognome,data_nascita,
         codice_fiscale,telefono_aziendale,email,data_inserimento,stato,data_ultima_modifica)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", (
        d["id_operatore"], d["codice_operatore"], d["codice_fornitore"], d["nome"], d["cognome"],
        conv_date(d["data_nascita"]), d["codice_fiscale"], d["telefono_aziendale"], d["email"],
        conv_date(d["data_inserimento"]), d["stato"], conv_date(d["data_ultima_modifica"])))
    n += 1

# ============================================================
# 6. RICHIESTE
# ============================================================
headers, rows = read_rows(FILES["richieste"])
n = 0
for r in rows:
    d = dict(zip(headers, r))
    cur.execute("""INSERT OR REPLACE INTO richieste
        (id_richiesta,numero_richiesta,codice_cliente,codice_servizi_fornitore,codice_operatore,
         stato_richiesta,data_inserimento,data_conferma_richiesta,data_appuntamento,
         orario_appuntamento,pagamento_eseguito)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (
        d["id_richiesta"], d["numero_richiesta"], d["codice_cliente"],
        d["codice_servizi_fornitore"], d["codice_operatore"], d["stato_richiesta"],
        conv_date(d["data_inserimento"]), conv_date(d["data_conferma_richiesta"]),
        conv_date(d["data_appuntamento"]), d["orario_appuntamento"], d["pagamento_eseguito"]))
    n += 1

conn.commit()
conn.close()
