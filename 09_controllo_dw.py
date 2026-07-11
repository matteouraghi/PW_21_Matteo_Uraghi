"""
Programma che fa il conteggio record per ogni tabella del data warehouse data_warehouse.db
"""

import sqlite3
import os
from datetime import datetime

# ============================================================
# CONFIGURAZIONE
# ============================================================
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DW_PATH   = os.path.join(BASE_DIR, "data_warehouse.db")
LOG_DIR   = os.path.join(BASE_DIR, "09_LOG")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE  = os.path.join(LOG_DIR, f"09_LOG_{TIMESTAMP}.txt")

TABELLE = [
    "DIM_TEMPO",
    "DIM_CLIENTE",
    "DIM_FORNITORE",
    "DIM_OPERATORE",
    "DIM_SERVIZIO_FORNITORE",
    "DIM_SERVIZI",
    "FACT_RICHIESTE",
]

# ============================================================
# CONNESSIONE
# ============================================================
conn = sqlite3.connect(DW_PATH)
cur = conn.cursor()

# ============================================================
# CONTEGGIO RECORD
# ============================================================
righe_log = []

intestazione = (
    "=" * 70 + "\n"
    f"CONTEGGIO RECORD — data_warehouse.db\n"
    f"Eseguito il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    + "=" * 70
)
righe_log.append(intestazione)
print(intestazione)

sezione1 = "\n[1] CONTEGGIO RECORD PER TABELLA:"
righe_log.append(sezione1)
print(sezione1)

for tabella in TABELLE:
    cur.execute(f"SELECT COUNT(*) FROM {tabella}")
    n = cur.fetchone()[0]
    riga = f"  {tabella:25s}: {n} record"
    righe_log.append(riga)
    print(riga)

conn.close()

# ============================================================
# SCRITTURA FILE LOG
# ============================================================
os.makedirs(LOG_DIR, exist_ok=True)

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(righe_log))