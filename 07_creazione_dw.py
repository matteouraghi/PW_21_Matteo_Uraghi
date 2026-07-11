"""
Questo programma crea il Data Warehouse (star schema) data_warehouse.db

"""
import sqlite3
import os

dw_path = "data_warehouse.db"

if os.path.exists(dw_path):
    os.remove(dw_path)

conn = sqlite3.connect(dw_path)
cur = conn.cursor()

cur.executescript("""
PRAGMA foreign_keys = ON;

-- ============================================================
-- DIMENSIONE TEMPO  (pre-popolata dall'anno 2020 al 2030)
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_TEMPO (
    data_completa       TEXT NOT NULL PRIMARY KEY,
    giorno              INTEGER NOT NULL,
    giorno_settimana    TEXT NOT NULL,
    settimana_anno      INTEGER NOT NULL,
    mese                INTEGER NOT NULL,
    nome_mese           TEXT NOT NULL,
    trimestre           INTEGER NOT NULL,
    semestre            INTEGER NOT NULL,
    anno                INTEGER NOT NULL,
    is_weekend          INTEGER NOT NULL DEFAULT 0

);

-- ============================================================
-- DIMENSIONE CLIENTE
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_CLIENTE (
    codice_cliente       TEXT NOT NULL PRIMARY KEY,
    nome_completo        TEXT NOT NULL,
    citta                TEXT,
    provincia            TEXT,
    regione              TEXT,
    nazione              TEXT,
    mese_registrazione   INTEGER,
    anno_registrazione   INTEGER,
    consenso_marketing   INTEGER,
    stato                INTEGER
);

-- ============================================================
-- DIMENSIONE FORNITORE
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_FORNITORE (
    codice_fornitore     TEXT NOT NULL PRIMARY KEY,
    ragione_sociale      TEXT NOT NULL,
    citta                TEXT,
    provincia            TEXT,
    regione              TEXT,
    stato                INTEGER
);

-- ============================================================
-- DIMENSIONE OPERATORE
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_OPERATORE (
    codice_operatore     TEXT NOT NULL PRIMARY KEY,
    nome_completo        TEXT NOT NULL,
    stato                INTEGER
);

-- ============================================================
-- DIMENSIONE SERVIZI_FORNITORE
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_SERVIZIO_FORNITORE (
    codice_servizi_fornitore  TEXT NOT NULL PRIMARY KEY,
    categoria_professionale   TEXT NOT NULL,
    stato                     INTEGER

);

-- ============================================================
-- DIMENSIONE SERVIZI
-- ============================================================
CREATE TABLE IF NOT EXISTS DIM_SERVIZI (
    codice_servizio           TEXT NOT NULL PRIMARY KEY,
    nome_servizio             TEXT NOT NULL,

    durata_stimata_in_ore     INTEGER,
    prezzo_base_un_ora        INTEGER,
    prezzo_preventivato       REAL,
    stato                     INTEGER,

    fascia_durata             TEXT,       -- 'breve' <=40h, 'medio' <=100h, 'lungo' >100h
    fascia_prezzo             TEXT        -- 'basso' <=2000€, 'medio' <=3000€, 'alto' >3000€
);

-- ============================================================
-- FACT TABLE — RICHIESTE
-- ============================================================
CREATE TABLE IF NOT EXISTS FACT_RICHIESTE (
    numero_richiesta              TEXT NOT NULL PRIMARY KEY,
    data_inserimento              TEXT NOT NULL DEFAULT '' REFERENCES DIM_TEMPO(data_completa),

    codice_cliente                TEXT NOT NULL REFERENCES DIM_CLIENTE(codice_cliente),
    codice_servizi_fornitore      TEXT NOT NULL REFERENCES DIM_SERVIZIO_FORNITORE(codice_servizi_fornitore),
    codice_operatore              TEXT NOT NULL REFERENCES DIM_OPERATORE(codice_operatore),
    codice_fornitore              TEXT NOT NULL REFERENCES DIM_FORNITORE(codice_fornitore),
    codice_servizio               TEXT NOT NULL REFERENCES DIM_SERVIZI(codice_servizio),

    data_appuntamento             TEXT NOT NULL DEFAULT '' REFERENCES DIM_TEMPO(data_completa),
    orario_appuntamento           TEXT,

    pagamento_eseguito            INTEGER,
    stato_richiesta               TEXT
);
""")

conn.commit()
conn.close()
