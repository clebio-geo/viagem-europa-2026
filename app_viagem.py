#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VIAGEM EUROPA 2026 — APP STREAMLIT AVANÇADO
Atualizado com Dias até Viagem + Seção Clima
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import json
import requests

# ===CONFIGURAÇÃO===========
st.set_page_config(
    page_title="Viagem Europa 2026 💶",
    page_icon="✈️",
    layout="wide"
)

ARQUIVO_DESPESAS = "despesas_viagem.csv"
ARQUIVO_CHECKLIST = "checklist_preparacao.csv"
ARQUIVO_CATEGORIAS = "categorias.json"
ARQUIVO_HOSPEDAGEM = "hospedagem.json"
ARQUIVO_TRANSPORTES = "transportes.json"

DATA_INICIO = datetime(2026, 10, 30)
HOJE = datetime.now()

COORDENADAS = {
    "Fortaleza": (-3.7319, -38.5267),
    "Madrid": (40.4168, -3.7038),
    "Barcelona": (41.3851, 2.1734),
    "Bruxelas": (50.8503, 4.3517),
    "Paris": (48.8566, 2.3522),
    "Marne-la-Vallée": (48.8704, 2.7788),
    "Milão": (45.4642, 9.1900),
    "Tirano": (41.5004, 8.5625),
    "Suíça (Poschiavo, St. Moritz)": (46.4085, 10.2205),
    "Veneza": (45.4408, 12.3155),
    "Florença": (43.7695, 11.2558),
    "Pisa": (43.7228, 10.3964),
    "Roma": (41.9028, 12.4964),
    "Vaticano": (41.9029, 12.4534),
}

ORCAMENTO_PATH = 30000.00
ORCAMENTO_CATEGORIAS = {
    "Transportes Internos": 4475.00,
    "Hospedagem": 6915.00,
    "Alimentação": 6275.00,
    "Passeios e Atrações": 2464.00,
    "Futebol": 697.00,
    "Translado": 500.00,
}

CIDADES = [
    "Fortaleza", "Madrid", "Barcelona", "Bruxelas", "Paris",
    "Marne-la-Vallée", "Milão", "Tirano", "Suíça (Poschiavo, St. Moritz)",
    "Veneza", "Florença", "Pisa", "Roma", "Vaticano"
]

TRANSPORTE_TIPO = ["Avião", "Trem", "Metro", "Ônibus", "Bicicleta"]

GASTO_CATEGORIA = [
    "Alimentação", "Souvenirs", "Transporte", "Roupas e Acessórios",
    "Passeios/Ingressos", "Taxas", "Hospedagem", "Outros"
]

# ===FUNCOES CLMA===========
def dias_para_viagem():
    return (DATA_INICIO - HOJE).days

def buscar_clima(cidade):
    try:
        if cidade not in COORDENADAS:
            return None
        lat, lon = COORDENADAS[cidade]
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "timezone": "auto"
        }
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            return r.json().get("current")
    except:
        pass
    return None

def interpretar_clima(code):
    mapa = {
        0: ("☀️ Céu limpo", "Céu completamente limpo"),
        1: ("🌤️ Parcialmente nublado", "Maiormente limpo"),
        2: ("⛅ Nublado", "Parcialmente nublado"),
        3: ("☁️ Nublado", "Céu nublado"),
        61: ("🌧️ Chuva leve", "Chuva leve"),
        65: ("⛈️ Chuva forte", "Chuva forte"),
        80: ("🌧️ Pancadas", "Pancadas de chuva"),
        95: ("⛈️ Tempestade", "Tempestade"),
    }
    return mapa.get(code, ("❓ Desconhecido", "Sem previsão"))

# ===FUNCOES DE CARREGAMENTO===========
def carregar_despesas():
    if os.path.exists(ARQUIVO_DESPESAS):
        df = pd.read_csv(ARQUIVO_DESPESAS)
        df["data"] = pd.to_datetime(df["data"])
        return df
    return pd.DataFrame(columns=["data","categoria","descricao","cidade","valor"])

def salvar_despesa(data, categoria, descricao, cidade, valor):
    df = carregar_despesas()
    nova = pd.DataFrame([{"data":data,"categoria":categoria,"descricao":descricao,"cidade":cidade,"valor":valor}])
    pd.concat([df,nova], ignore_index=True).to_csv(ARQUIVO_DESPESAS, index=False, encoding="utf-8")

def deletar_despesa(idx):
    df = carregar_despesas()
    df.drop(idx).reset_index(drop=True).to_csv(ARQUIVO_DESPESAS, index=False, encoding="utf-8")

def gastos_por_cidade(cidade):
    return carregar_despesas()[carregar_despesas()["cidade"] == cidade]

def calcular_gastos():
    df = carregar_despesas()
    if df.empty:
        return pd.DataFrame(["Categoria","Gasto","Orçado","Saldo"]).columns.tolist()
    gastos = df.groupby("categoria")["valor"].sum()
    resultado = []
    for cat, orçado in ORCAMENTO_CATEGORIAS.items():
        gasto = gastos.get(cat, 0)
        resultado.append((cat, gasto, orçado, orçado - gasto))
    return pd.DataFrame(resultado, columns=["Categoria","Gasto","Orçado","Saldo"])

# ===FUNCOES DE TRANSMISSAO===========
def carregar_hospedagem():
    with open(ARQUIVO_HOSPEDAGEM,"r",encoding="utf-8") as f:
        return json.load(f)

def salvar_hospedagem(cidade, dados):
    h = carregar_hospedagem()
    h[cidade] = dados
    with open(ARQUIVO_HOSPEDAGEM,"w",encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False)

# ===FUNCOES DE TRANSMISSAO 2===========
def carregar_checklist():
    return pd.DataFrame(columns=["item","concluido"])

# ===HEADER COM CONTADOR===========
st.title("✈️ VIAGEM EUROPA 2026")
st.markdown("**Controle de Gastos — Clébio & Esposa**")

dias = dias_para_viagem()
col1, col2 = st.columns([3, 1])
with col1:
    if dias > 0:
        st.balloons()
        st.markdown(f"## 📅 **Faltam {dias} dias para a Viagem!**\n**Início:** 30/out/2026 | **Duração:** 19 dias")
    elif dias == 0:
        st.markdown("## 🎉 **A viagem começa HOJE!** ✈️ Boa viagem!")
    else:
        st.markdown(f"## ✈️ **Você está viajando! Dia {-dias+1} de 19**")
with col2:
    if dias > 0:
        st.metric("🔴 Dias restantes", dias)
    else:
        st.metric("VIAJANDO!", f"Dia {-dias+1}")

st.markdown("---")

# ===ABAS===========
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Painel", "➕ Adicionar Gasto", "✈️ Transportes",
    "📈 Gráficos", "📋 Relatório", "✅ Preparação"
])

# ===TAB 1: PAINEL===========
with tab1:
    st.subheader("Resumo Geral")
    totais = calcular_totais()
    col1,col2,col3,col4 = st.columns(4)
    with col1: st.metric("💰 Gasto Registrado", f"R$ {totais['total_gasto']:,.2f}")
    with col2: st.metric("💳 Já Pago", f"R$ {totais['total_ja_pago']:,.2f}")
    with col3: st.metric("🛫 Total", f"R$ {totais['gasto_total_viagem']:,.2f}")
    with col4: st.metric(f"💵 Saldo", f"R$ {totais['saldo_final']:,.2f}")
    
    st.markdown("### Progresso do Orçamento")
    pct = totais['percentual']
    st.progress(min(pct/100, 1.0))
    st.write(f"**{pct:.1f}%** do orçamento utilizado")

# ===CIDADES===========
st.markdown("---")
st.markdown("### 🌍 Cidades do Roteiro")
cols = st.columns(5)
for idx, cidade in enumerate(CIDADES):
    with cols[idx % 5]:
        if st.button(f"📍 {cidade}", use_container_width=True):
            st.session_state.cidade_sel = cidade

if "cidade_sel" in st.session_state:
    cidade = st.session_state.cidade_sel
    st.markdown("---")
    st.markdown(f"## 📍 Detalhes de {cidade}")
    
    tab_h, tab_t, tab_g, tab_c = st.tabs(["🏨 Hospedagem","✈️ Transportes","💰 Gastos","🌤️ Clima"])
    
    with tab_c:
        st.subheader(f"Clima em {cidade}")
        clima = buscar_clima(cidade)
        if clima:
            temp = clima.get("temperature_2m", "N/D")
            code = clima.get("weather_code", 0)
            vento = clima.get("wind_speed_10m", "N/D")
            desc, dica = interpretar_clima(code)
            col1,col2,col3 = st.columns(3)
            with col1: st.metric("Temperatura", f"{temp}°C")
            with col2: st.metric("Vento", f"{vento} km/h")
            with col3: st.metric("Condição", desc)
            st.info(f"💡 {dica}")
            if temp != "N/D" and float(temp) < 15: st.warning("🧥 **Clima frio!** Leve casaco.")
            else: st.success("👍 **Clima bom para passeios!**")
        else:
            st.warning("⚠️ Sem dados de clima. Tente novamente.")
