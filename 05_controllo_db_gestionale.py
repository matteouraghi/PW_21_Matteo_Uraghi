"""
Programma che nel db database_gestionale.db:
- fa il conteggio record per ogni tabella
"""

import sqlite3
import os
from datetime import datetime

# ============================================================
# CONFIGURAZIONE
# ============================================================
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(BASE_DIR, "database_gestionale.db")
LOG_DIR   = os.path.join(BASE_DIR, "05_LOG")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE  = os.path.join(LOG_DIR, f"05_LOG_{TIMESTAMP}.txt")

TABELLE = [
    "clienti",
    "fornitori",
    "operatori",
    "servizi",
    "servizi_fornitore",
    "richieste",
]

# ============================================================
# CONNESSIONE
# ============================================================
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ============================================================
# CONTEGGIO RECORD
# ============================================================
righe_log = []

intestazione = (
    "=" * 70 + "\n"
    f"CONTEGGIO RECORD — database_gestionale.db\n"
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