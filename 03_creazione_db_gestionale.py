"""
Questo programma crea il database operativo database_gestionale.db
"""
import sqlite3
import os

db_path = "database_gestionale.db"

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.executescript("""
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. CLIENTI
-- ============================================================
CREATE TABLE IF NOT EXISTS clienti (
    id_cliente           INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_cliente       TEXT NOT NULL UNIQUE,
    nome                 TEXT NOT NULL,
    cognome              TEXT NOT NULL,
    data_nascita         TEXT,
    codice_fiscale       TEXT UNIQUE,
    email                TEXT NOT NULL UNIQUE,
    telefono             TEXT NOT NULL,
    indirizzo            TEXT,
    cap                  INTEGER,
    citta                TEXT,
    provincia            TEXT,
    regione              TEXT,
    nazione              TEXT NOT NULL DEFAULT 'Italia',
    data_inserimento     TEXT NOT NULL DEFAULT (datetime('now')),
    stato                INTEGER NOT NULL DEFAULT 1 CHECK(stato IN (0,1)),
    consenso_privacy     INTEGER NOT NULL DEFAULT 0 CHECK(consenso_privacy IN (0,1)),
    consenso_marketing   INTEGER NOT NULL DEFAULT 0 CHECK(consenso_marketing IN (0,1)),
    data_ultima_modifica TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- 2. FORNITORI
-- ============================================================
CREATE TABLE IF NOT EXISTS fornitori (
    id_fornitore         INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_fornitore     TEXT NOT NULL UNIQUE,
    ragione_sociale      TEXT NOT NULL,
    partita_iva          TEXT NOT NULL UNIQUE,
    indirizzo            TEXT NOT NULL,
    cap                  INTEGER NOT NULL,
    citta                TEXT NOT NULL,
    provincia            TEXT NOT NULL,
    regione              TEXT NOT NULL,
    nazione              TEXT NOT NULL DEFAULT 'Italia',
    telefono             TEXT,
    email                TEXT NOT NULL UNIQUE,
    pec                  TEXT,
    data_inserimento     TEXT NOT NULL DEFAULT (datetime('now')),
    stato                INTEGER NOT NULL DEFAULT 1 CHECK(stato IN (0,1)),
    data_ultima_modifica TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- 3. OPERATORI
-- ============================================================
CREATE TABLE IF NOT EXISTS operatori (
    id_operatore         INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_operatore     TEXT NOT NULL UNIQUE,
    codice_fornitore     TEXT NOT NULL REFERENCES fornitori(codice_fornitore),
    nome                 TEXT NOT NULL,
    cognome              TEXT NOT NULL,
    data_nascita         TEXT,
    codice_fiscale       TEXT UNIQUE,
    telefono_aziendale   TEXT,
    email                TEXT UNIQUE,
    data_inserimento     TEXT NOT NULL DEFAULT (datetime('now')),
    stato                INTEGER NOT NULL DEFAULT 1 CHECK(stato IN (0,1)),
    data_ultima_modifica TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- 4. SERVIZI
-- ============================================================
CREATE TABLE IF NOT EXISTS servizi (
    id_servizio            INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_servizio        TEXT NOT NULL UNIQUE,
    nome_servizio          TEXT NOT NULL,
    descrizione            TEXT,
    durata_stimata_in_ore  INTEGER NOT NULL,
    prezzo_base_un_ora     INTEGER NOT NULL,
    iva_percentuale        INTEGER NOT NULL DEFAULT 22,
    prezzo_preventivato    REAL NOT NULL,
    stato                  INTEGER NOT NULL DEFAULT 1 CHECK(stato IN (0,1)),
    data_inserimento       TEXT NOT NULL DEFAULT (datetime('now')),
    data_ultima_modifica   TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- 5. SERVIZI_FORNITORE
-- ============================================================
CREATE TABLE IF NOT EXISTS servizi_fornitore (
    id_servizi_fornitore      INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_servizi_fornitore  TEXT NOT NULL UNIQUE,
    codice_fornitore          TEXT NOT NULL REFERENCES fornitori(codice_fornitore),
    codice_servizio           TEXT NOT NULL REFERENCES servizi(codice_servizio),
    categoria_professionale   TEXT NOT NULL
                              CHECK(categoria_professionale IN
                              ('Idraulico','Elettricista','Muratore','Imbianchino')),
    stato                     INTEGER NOT NULL DEFAULT 1 CHECK(stato IN (0,1)),
    data_inserimento          TEXT NOT NULL DEFAULT (datetime('now')),
    data_ultima_modifica      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(codice_fornitore, codice_servizio)
);

-- ============================================================
-- 6. RICHIESTE
-- ============================================================
CREATE TABLE IF NOT EXISTS richieste (
    id_richiesta              INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_richiesta          TEXT NOT NULL UNIQUE,
    codice_cliente            TEXT NOT NULL REFERENCES clienti(codice_cliente),
    codice_servizi_fornitore  TEXT NOT NULL REFERENCES servizi_fornitore(codice_servizi_fornitore),
    codice_operatore          TEXT REFERENCES operatori(codice_operatore),
    stato_richiesta           TEXT NOT NULL DEFAULT 'richiesta_in_bozza'
                              CHECK(stato_richiesta IN (
                                'richiesta_in_bozza',
                                'richiesta_registrata',
                                'richiesta_scaduta',
                                'servizio_completato'
                              )),
    data_inserimento          TEXT NOT NULL DEFAULT (datetime('now')),
    data_conferma_richiesta   TEXT,
    data_appuntamento         TEXT,
    orario_appuntamento       TEXT,
    pagamento_eseguito        INTEGER NOT NULL DEFAULT 0 CHECK(pagamento_eseguito IN (0,1))
);

""")

conn.commit()
conn.close()
