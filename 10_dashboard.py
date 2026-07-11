"""
Dashboard BI
"""

import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date as _date

# ──────────────────────────────────────────────
# CONFIGURAZIONE PAGINA
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard BI",
    layout="wide",
)

# ──────────────────────────────────────────────
# CONNESSIONE DB
# ──────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return sqlite3.connect("data_warehouse.db", check_same_thread=False)

conn = get_conn()

# ──────────────────────────────────────────────
# QUERY PRINCIPALE
# ──────────────────────────────────────────────
@st.cache_data
def load_base():
    df = pd.read_sql_query("""
        SELECT
            f.numero_richiesta,
            f.codice_cliente,
            f.codice_fornitore,
            f.codice_servizi_fornitore,
            f.codice_servizio,
            f.stato_richiesta,
            f.pagamento_eseguito,
            f.orario_appuntamento,
            f.data_appuntamento,
            f.data_inserimento               AS data_inserimento_richiesta,

            c.nome_completo                  AS cliente_nome,
            c.provincia                      AS provincia_cliente,
            c.regione                        AS regione_cliente,
            c.nazione                        AS nazione_cliente,
            c.stato                          AS stato_cliente,

            fo.ragione_sociale               AS fornitore_nome,

            sfr.categoria_professionale,

            sv.nome_servizio,
            sv.prezzo_preventivato,
            sv.durata_stimata_in_ore,

            t.anno,
            t.mese,
            t.nome_mese

        FROM FACT_RICHIESTE f
        LEFT JOIN DIM_CLIENTE            c   ON f.codice_cliente           = c.codice_cliente
        LEFT JOIN DIM_FORNITORE          fo  ON f.codice_fornitore         = fo.codice_fornitore
        LEFT JOIN DIM_SERVIZIO_FORNITORE sfr ON f.codice_servizi_fornitore = sfr.codice_servizi_fornitore
        LEFT JOIN DIM_SERVIZI            sv  ON f.codice_servizio          = sv.codice_servizio
        LEFT JOIN DIM_TEMPO              t   ON f.data_appuntamento        = t.data_completa
    """, conn)

    df["data_appuntamento"]          = pd.to_datetime(df["data_appuntamento"],          errors="coerce")
    df["data_inserimento_richiesta"] = pd.to_datetime(df["data_inserimento_richiesta"], errors="coerce")
    return df

df_base = load_base()

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.title("Dashboard BI")
st.caption("")
st.divider()

# ──────────────────────────────────────────────
# FILTRI
# ──────────────────────────────────────────────
st.subheader("Filtri")

_date_series = df_base["data_inserimento_richiesta"].dropna()

if len(_date_series) == 0 or pd.isna(_date_series.min()):
    date_min = _date(2024, 1, 1)
    date_max = _date(2024, 12, 31)
else:
    date_min = _date_series.min().date()
    date_max = _date_series.max().date()

cf1, cf2, cf3, cf4, cf5 = st.columns([2, 1.4, 1.4, 1.4, 1.4])

with cf1:
    range_date = st.date_input("Periodo richieste", value=(date_min, date_max),
                               min_value=date_min, max_value=date_max, key="rdate")
with cf2:
    province = ["Tutte"] + sorted(df_base["provincia_cliente"].dropna().unique().tolist())
    sel_prov = st.selectbox("Provincia cliente", province, key="sprov")

with cf3:
    regioni = ["Tutte"] + sorted(df_base["regione_cliente"].dropna().unique().tolist())
    sel_reg = st.selectbox("Regione cliente", regioni, key="sreg")

with cf4:
    stati = ["Tutti"] + sorted(df_base["stato_richiesta"].dropna().unique().tolist())
    sel_stato = st.selectbox("Stato richiesta", stati, key="sstato")

with cf5:
    categorie = ["Tutte"] + sorted(df_base["categoria_professionale"].dropna().unique().tolist())
    sel_cat = st.selectbox("Categoria professionale", categorie, key="scat")

st.divider()

# ──────────────────────────────────────────────
# APPLICAZIONE FILTRI
# ──────────────────────────────────────────────
df = df_base.copy()

if isinstance(range_date, (list, tuple)) and len(range_date) == 2:
    df = df[df["data_inserimento_richiesta"].between(
        pd.Timestamp(range_date[0]), pd.Timestamp(range_date[1])
    )]

if sel_prov  != "Tutte": df = df[df["provincia_cliente"]      == sel_prov]
if sel_reg   != "Tutte": df = df[df["regione_cliente"]        == sel_reg]
if sel_stato != "Tutti": df = df[df["stato_richiesta"]        == sel_stato]
if sel_cat   != "Tutte": df = df[df["categoria_professionale"]== sel_cat]

# ──────────────────────────────────────────────
# KPI
# ──────────────────────────────────────────────
n_richieste      = int(df["numero_richiesta"].count())
incassi          = float(df["prezzo_preventivato"].sum())
durata_media     = float(df["durata_stimata_in_ore"].sum() / n_richieste) if n_richieste > 0 else 0.0
n_clienti = int(df["codice_cliente"].nunique())

df_comp      = df[df["stato_richiesta"] == "servizio_completato"]
fid          = df_comp.groupby("codice_cliente")["numero_richiesta"].count()
n_fidelizzati = int((fid >= 2).sum())

st.subheader("KPI Principali")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Totale Richieste",        f"{n_richieste:,}")
k2.metric("Incassi Totali (IVA incl.)", f"€ {incassi:,.0f}")
k3.metric("Durata Media Servizio",   f"{durata_media:.1f} h")
k4.metric("Clienti nel periodo",     f"{n_clienti:,}")
k5.metric("Clienti Fidelizzati",     f"{n_fidelizzati:,}")

st.divider()

# ──────────────────────────────────────────────
# PALETTE
# ──────────────────────────────────────────────
PAL = ["#2d4a8a","#4a7fd4","#6fb3e0","#a8d8ea","#f0a500",
       "#e06b3a","#c94b4b","#7c3aed","#059669","#10b981"]

# ──────────────────────────────────────────────
# GRAFICI — RIGA 1: Andamento temporale richieste per giorno
# ──────────────────────────────────────────────
st.subheader("Grafici")

df_temp = (
    df.dropna(subset=["data_inserimento_richiesta"])
      .copy()
)
# Raggruppa per mese (primo giorno del mese come chiave)
df_temp["mese_dt"] = df_temp["data_inserimento_richiesta"].dt.to_period("M").dt.to_timestamp()

andamento = (
    df_temp.groupby("mese_dt")["numero_richiesta"]
           .count()
           .reset_index()
           .rename(columns={"mese_dt": "Mese", "numero_richiesta": "Richieste"})
           .sort_values("Mese")
)

fig_trend = px.line(
    andamento,
    x="Mese",
    y="Richieste",
    title="Andamento Mensile delle Richieste",
    markers=True,
    color_discrete_sequence=["#2d4a8a"],
)
fig_trend.update_traces(
    line=dict(width=2),
    marker=dict(size=6),
)
fig_trend.update_layout(
    xaxis=dict(
        title="Mese",
        tickformat="%b %Y",       # es. Gen 2024, Feb 2024
        dtick="M1",               # un tick per ogni mese
        tickangle=-45,
        showgrid=True,
        gridcolor="rgba(0,0,0,0.07)",
    ),
    yaxis=dict(
        title="Numero Richieste",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.07)",
    ),
    margin=dict(t=55, b=80, l=40, r=20),
    title_font_size=13,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_trend, use_container_width=True)

# ──────────────────────────────────────────────
# GRAFICI — RIGA 2: Top 5 fornitori + Richieste per provincia
# ──────────────────────────────────────────────
st.subheader("")
g3, g4 = st.columns(2)

with g3:
    top5 = (df.groupby("fornitore_nome")["prezzo_preventivato"]
              .sum().reset_index()
              .rename(columns={"fornitore_nome":"Fornitore","prezzo_preventivato":"Incassi"})
              .sort_values("Incassi", ascending=False)
              .head(5))
    fig3 = px.bar(top5, x="Incassi", y="Fornitore", orientation="h",
                  title="Top 5 Fornitori per Incassi",
                  color="Incassi", color_continuous_scale=["#a8c4f0","#1a2744"],
                  text="Incassi")
    fig3.update_traces(texttemplate="€ %{text:,.0f}", textposition="outside")
    fig3.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                       margin=dict(t=50,b=20,l=20,r=90), title_font_size=13)
    st.plotly_chart(fig3, use_container_width=True)

with g4:
    rp = (df.groupby("provincia_cliente")["numero_richiesta"]
            .count().reset_index()
            .rename(columns={"provincia_cliente":"Provincia","numero_richiesta":"Richieste"})
            .sort_values("Richieste", ascending=False)
            .head(20))
    fig4 = px.bar(rp, x="Provincia", y="Richieste",
                  title="Numero Richieste per Provincia (top 20)",
                  color="Richieste", color_continuous_scale=["#a8d8ea","#1a2744"],
                  text="Richieste")
    fig4.update_traces(textposition="outside")
    fig4.update_layout(coloraxis_showscale=False,
                       margin=dict(t=50,b=60,l=20,r=20),
                       xaxis_tickangle=-35, title_font_size=13)
    st.plotly_chart(fig4, use_container_width=True)

# ──────────────────────────────────────────────
# GRAFICI — RIGA 3: Richieste per regione + per categoria
# ──────────────────────────────────────────────
st.subheader("")
g5, g6 = st.columns(2)

with g5:
    rr = (df.groupby("regione_cliente")["numero_richiesta"]
            .count().reset_index()
            .rename(columns={"regione_cliente":"Regione","numero_richiesta":"Richieste"})
            .sort_values("Richieste", ascending=False))
    fig5 = px.bar(rr, x="Regione", y="Richieste",
                  title="Numero Richieste per Regione",
                  color="Richieste", color_continuous_scale=["#c4b5fd","#5b21b6"],
                  text="Richieste")
    fig5.update_traces(textposition="outside")
    fig5.update_layout(coloraxis_showscale=False,
                       margin=dict(t=50,b=60,l=20,r=20),
                       xaxis_tickangle=-30, title_font_size=13)
    st.plotly_chart(fig5, use_container_width=True)

with g6:
    rc = (df.groupby("categoria_professionale")["numero_richiesta"]
            .count().reset_index()
            .rename(columns={"categoria_professionale":"Categoria","numero_richiesta":"Richieste"})
            .sort_values("Richieste", ascending=False))
    fig6 = px.bar(rc, x="Categoria", y="Richieste",
                  title="Richieste per Categoria Professionale",
                  color="Categoria", color_discrete_sequence=PAL,
                  text="Richieste")
    fig6.update_traces(textposition="outside")
    fig6.update_layout(showlegend=False,
                       margin=dict(t=50,b=60,l=20,r=20),
                       xaxis_tickangle=-10, title_font_size=13)
    st.plotly_chart(fig6, use_container_width=True)
