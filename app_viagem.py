#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VIAGEM EUROPA 2026 — APP STREAMLIT AVANÇADO
Versão com Dias até Viagem + Seção Clima e Tempo
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import json
import requests

# ============== CONFIGURAÇÃO ==============
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

# ============== DATAS DA VIAGEM ==============
DATA_INICIO_VIAGEM = datetime(2026, 10, 30)
DATA_HOJE = datetime.now()

# ============== ORÇAMENTO ==============
ORCAMENTO_PADRAO = {
    "limite_total": 30000.00,
    "itens_ja_pagos": {
        "Passagem Fortaleza > Madrid": 0.00,
        "Passagem Madrid > Fortaleza": 0.00,
        "Seguro Viagem (casal)": 350.00,
    },
    "categorias": {
        "Transportes Internos": 4475.00,
        "Hospedagem": 6915.00,
        "Alimentação": 6275.00,
        "Passeios e Atrações": 2464.00,
        "Futebol": 697.00,
        "Translado": 500.00,
    },
}

# ============== ROTEIRO DETALHADO ==============
ROTEIRO_VIAGEM = [
    {"data": "30/out", "saida": "Fortaleza", "chegada": "Madrid", "tipo": "Transporte"},
    {"data": "31/out", "saida": "Madrid", "chegada": "Madrid", "tipo": "Hospedagem"},
    {"data": "01/nov", "saida": "Madrid", "chegada": "Barcelona", "tipo": "Transporte"},
    {"data": "02/nov", "saida": "Barcelona", "chegada": "Barcelona", "tipo": "Hospedagem"},
    {"data": "03/nov", "saida": "Barcelona", "chegada": "Bruxelas", "tipo": "Transporte"},
    {"data": "04/nov", "saida": "Bruxelas", "chegada": "Paris", "tipo": "Transporte"},
    {"data": "05/nov", "saida": "Marne-la-Vallée (Disney)", "chegada": "Marne-la-Vallée", "tipo": "Hospedagem"},
    {"data": "06/nov", "saida": "Paris", "chegada": "Paris", "tipo": "Hospedagem"},
    {"data": "07/nov", "saida": "Paris", "chegada": "Milão", "tipo": "Transporte"},
    {"data": "08/nov", "saida": "Milão", "chegada": "Milão", "tipo": "Hospedagem"},
    {"data": "09/nov", "saida": "Milão (Tirano)", "chegada": "Suíça (Poschiavo, St. Moritz)", "tipo": "Transporte"},
    {"data": "10/nov", "saida": "Milão", "chegada": "Veneza", "tipo": "Transporte"},
    {"data": "11/nov", "saida": "Milão", "chegada": "Florença", "tipo": "Transporte"},
    {"data": "12/nov", "saida": "Florença", "chegada": "Pisa", "tipo": "Transporte"},
    {"data": "13/nov", "saida": "Florença", "chegada": "Roma", "tipo": "Transporte"},
    {"data": "14/nov", "saida": "Roma", "chegada": "Vaticano", "tipo": "Hospedagem"},
    {"data": "15/nov", "saida": "Roma", "chegada": "Roma", "tipo": "Hospedagem"},
    {"data": "16/nov", "saida": "Roma", "chegada": "Madrid", "tipo": "Transporte"},
    {"data": "17/nov", "saida": "Madrid", "chegada": "Fortaleza", "tipo": "Transporte"},
]

CIDADES_ROTEIRO = [
    "Fortaleza", "Madrid", "Barcelona", "Bruxelas", "Paris", 
    "Marne-la-Vallée", "Milão", "Tirano", "Suíça (Poschiavo, St. Moritz)", 
    "Veneza", "Florença", "Pisa", "Roma", "Vaticano"
]

# ============== COORDENADAS DAS CIDADES PARA CLIMA ==============
COORDENADAS_CIDADES = {
    "Fortaleza": {"lat": -3.7319, "lon": -38.5267},
    "Madrid": {"lat": 40.4168, "lon": -3.7038},
    "Barcelona": {"lat": 41.3851, "lon": 2.1734},
    "Bruxelas": {"lat": 50.8503, "lon": 4.3517},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Marne-la-Vallée": {"lat": 48.8704, "lon": 2.7788},
    "Milão": {"lat": 45.4642, "lon": 9.1900},
    "Tirano": {"lat": 41.5004, "lon": 8.5625},
    "Suíça (Poschiavo, St. Moritz)": {"lat": 46.4085, "lon": 10.2205},
    "Veneza": {"lat": 45.4408, "lon": 12.3155},
    "Florença": {"lat": 43.7695, "lon": 11.2558},
    "Pisa": {"lat": 43.7228, "lon": 10.3964},
    "Roma": {"lat": 41.9028, "lon": 12.4964},
    "Vaticano": {"lat": 41.9029, "lon": 12.4534},
}

TIPO_TRANSPORTE = ["Avião", "Trem", "Metro", "Ônibus", "Bicicleta"]

CATEGORIAS_GASTO = [
    "Alimentação",
    "Souvenirs",
    "Transporte",
    "Roupas e Acessórios",
    "Passeios/Ingressos",
    "Taxas",
    "Hospedagem",
    "Outros"
]

ITENS_OBRIGATORIOS = [
    "📋 Passaporte",
    "💳 Cartão de Crédito/Débito",
    "💰 Dóleira com valores",
    "🔋 Carregador Portátil (Power Bank)",
    "📱 Carregador de Celular",
    "🛂 Comprovante de Reservas (Hotel/Transporte)",
    "📄 Apólice de Seguro Viagem",
    "🏦 Extrato Bancário",
    "💉 Comprimidos/Medicamentos",
    "🎫 Ingressos (se já comprados)",
    "🗺️ Mapa ou App de Navegação",
    "📧 E-mails de Confirmação",
    "🧳 Mala/Bagagem",
    "👕 Roupas Adequadas",
    "👟 Sapatos Confortáveis",
    "📷 Câmera/Celular com Bateria",
    "🎧 Fone de Ouvido",
    "💼 Adaptador de Energia (tomadas europeia)",
    "🧴 Artigos de Higiene",
    "☂️ Guarda-chuva",
]

# ============== FUNÇÕES DE CLIMA ==============

def obter_clima_cidade(cidade):
    """Busca o clima atual da cidade via OpenWeatherMap API"""
    try:
        if cidade not in COORDENADAS_CIDADES:
            return None
        
        coords = COORDENADAS_CIDADES[cidade]
        
        # Usando API Open-Meteo (gratuita, sem chave necessária)
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current": "temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m",
            "temperature_unit": "celsius",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("current", None)
        return None
    except:
        return None

def interpretar_codigo_clima(code):
    """Interpreta código de clima em descrição e emoji"""
    codigos = {
        0: ("☀️ Céu limpo", "Céu completamente limpo"),
        1: ("🌤️ Parcialmente nublado", "Maiormente céu limpo"),
        2: ("⛅ Nublado", "Parcialmente nublado"),
        3: ("☁️ Nublado", "Céu nublado"),
        45: ("🌫️ Névoa", "Névoa ou nuvem baixa"),
        48: ("🌫️ Névoa congelada", "Névoa congelada ou nuvem baixa"),
        51: ("🌧️ Garoa leve", "Garoa leve"),
        53: ("🌧️ Garoa moderada", "Garoa moderada"),
        55: ("🌧️ Garoa densa", "Garoa densa"),
        61: ("🌧️ Chuva leve", "Chuva leve"),
        63: ("🌧️ Chuva moderada", "Chuva moderada"),
        65: ("⛈️ Chuva forte", "Chuva forte"),
        71: ("❄️ Neve leve", "Neve leve"),
        73: ("❄️ Neve moderada", "Neve moderada"),
        75: ("❄️ Neve forte", "Neve forte"),
        77: ("❄️ Neve em grãos", "Neve em grãos"),
        80: ("🌧️ Pancadas leves", "Pancadas de chuva leve"),
        81: ("⛈️ Pancadas moderadas", "Pancadas de chuva moderada"),
        82: ("⛈️ Pancadas fortes", "Pancadas de chuva forte"),
        85: ("❄️ Pancadas de neve leve", "Pancadas de neve leve"),
        86: ("❄️ Pancadas de neve forte", "Pancadas de neve forte"),
        95: ("⛈️ Tempestade", "Tempestade com chuva"),
        96: ("⛈️ Tempestade com granizo", "Tempestade com granizo leve"),
        99: ("⛈️ Tempestade forte", "Tempestade com granizo forte"),
    }
    return codigos.get(code, ("❓ Desconhecido", "Condição desconhecida"))

def calcular_dias_para_viagem():
    """Calcula quantos dias faltam para a viagem"""
    dias_faltantes = (DATA_INICIO_VIAGEM - DATA_HOJE).days
    return dias_faltantes

# ============== FUNÇÕES DE CATEGORIAS ==============

def carregar_categorias():
    if os.path.exists(ARQUIVO_CATEGORIAS):
        with open(ARQUIVO_CATEGORIAS, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        salvar_categorias(ORCAMENTO_PADRAO["categorias"])
        return ORCAMENTO_PADRAO["categorias"]

def salvar_categorias(categorias):
    with open(ARQUIVO_CATEGORIAS, 'w', encoding='utf-8') as f:
        json.dump(categorias, f, ensure_ascii=False, indent=2)

def adicionar_categoria(nome_categoria, orcamento_categoria=0.0):
    categorias = carregar_categorias()
    if nome_categoria not in categorias:
        categorias[nome_categoria] = float(orcamento_categoria)
        salvar_categorias(categorias)
        return True
    return False

def obter_orcamento():
    orcamento = ORCAMENTO_PADRAO.copy()
    orcamento["categorias"] = carregar_categorias()
    return orcamento

# ============== FUNÇÕES DE DESPESAS ==============

def carregar_despesas():
    if os.path.exists(ARQUIVO_DESPESAS):
        df = pd.read_csv(ARQUIVO_DESPESAS)
        df["data"] = pd.to_datetime(df["data"])
        return df
    return pd.DataFrame(columns=["data", "categoria", "descricao", "cidade", "valor"])

def salvar_despesa(data, categoria, descricao, cidade, valor):
    df = carregar_despesas()
    nova_linha = pd.DataFrame([{
        "data": data,
        "categoria": categoria,
        "descricao": descricao,
        "cidade": cidade,
        "valor": valor
    }])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(ARQUIVO_DESPESAS, index=False, encoding='utf-8')
    return True

def deletar_despesa(index):
    df = carregar_despesas()
    df = df.drop(index).reset_index(drop=True)
    df.to_csv(ARQUIVO_DESPESAS, index=False, encoding='utf-8')
    return True

def atualizar_despesa(index, data, categoria, descricao, cidade, valor):
    df = carregar_despesas()
    df.loc[index, "data"] = data
    df.loc[index, "categoria"] = categoria
    df.loc[index, "descricao"] = descricao
    df.loc[index, "cidade"] = cidade
    df.loc[index, "valor"] = valor
    df.to_csv(ARQUIVO_DESPESAS, index=False, encoding='utf-8')
    return True

# ============== FUNÇÕES DE TRANSPORTES ==============

def carregar_transportes():
    if os.path.exists(ARQUIVO_TRANSPORTES):
        with open(ARQUIVO_TRANSPORTES, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_transportes(transportes):
    with open(ARQUIVO_TRANSPORTES, 'w', encoding='utf-8') as f:
        json.dump(transportes, f, ensure_ascii=False, indent=2)

def adicionar_transporte(transporte_dict):
    transportes = carregar_transportes()
    transportes.append(transporte_dict)
    salvar_transportes(transportes)
    return True

def deletar_transporte(index):
    transportes = carregar_transportes()
    transportes.pop(index)
    salvar_transportes(transportes)
    return True

def calcular_duracao(hora_saida, hora_chegada):
    """Calcula a duração entre dois horários"""
    try:
        saida = datetime.strptime(hora_saida, "%H:%M")
        chegada = datetime.strptime(hora_chegada, "%H:%M")
        
        if chegada < saida:
            chegada = chegada + timedelta(days=1)
        
        duracao = chegada - saida
        horas = duracao.seconds // 3600
        minutos = (duracao.seconds % 3600) // 60
        
        return f"{horas}h {minutos}min"
    except:
        return "Inválido"

# ============== FUNÇÕES DE HOSPEDAGEM ==============

def carregar_hospedagem():
    if os.path.exists(ARQUIVO_HOSPEDAGEM):
        with open(ARQUIVO_HOSPEDAGEM, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_hospedagem(hospedagem):
    with open(ARQUIVO_HOSPEDAGEM, 'w', encoding='utf-8') as f:
        json.dump(hospedagem, f, ensure_ascii=False, indent=2)

def atualizar_hospedagem_cidade(cidade, dados_hospedagem):
    hospedagem = carregar_hospedagem()
    hospedagem[cidade] = dados_hospedagem
    salvar_hospedagem(hospedagem)
    return True

# ============== FUNÇÕES DE CHECKLIST ==============

def carregar_checklist():
    if os.path.exists(ARQUIVO_CHECKLIST):
        df = pd.read_csv(ARQUIVO_CHECKLIST)
        return df
    df = pd.DataFrame({
        "item": ITENS_OBRIGATORIOS,
        "concluido": [False] * len(ITENS_OBRIGATORIOS)
    })
    df.to_csv(ARQUIVO_CHECKLIST, index=False, encoding='utf-8')
    return df

def salvar_checklist(df):
    df.to_csv(ARQUIVO_CHECKLIST, index=False, encoding='utf-8')

def adicionar_item_checklist(item):
    df = carregar_checklist()
    novo_item = pd.DataFrame([{"item": item, "concluido": False}])
    df = pd.concat([df, novo_item], ignore_index=True)
    salvar_checklist(df)
    return True

def deletar_item_checklist(index):
    df = carregar_checklist()
    df = df.drop(index).reset_index(drop=True)
    salvar_checklist(df)
    return True

def marcar_concluido(index, valor):
    df = carregar_checklist()
    df.loc[index, "concluido"] = valor
    salvar_checklist(df)
    return True

# ============== FUNÇÕES DE CÁLCULO ==============

def calcular_gastos():
    df = carregar_despesas()
    orcamento = obter_orcamento()
    
    if df.empty:
        return pd.DataFrame(columns=["categoria", "gasto", "orcado", "saldo", "pct"])
    
    gastos = df.groupby("categoria")["valor"].sum().to_dict()
    
    resultado = []
    for cat, orcado in orcamento["categorias"].items():
        gasto = gastos.get(cat, 0)
        saldo = orcado - gasto
        pct = (gasto / orcado * 100) if orcado > 0 else 0
        resultado.append({
            "categoria": cat,
            "gasto": gasto,
            "orcado": orcado,
            "saldo": saldo,
            "pct": pct
        })
    
    return pd.DataFrame(resultado)

def calcular_totais():
    df = carregar_despesas()
    orcamento = obter_orcamento()
    total_gasto = df["valor"].sum() if not df.empty else 0
    total_ja_pago = sum(orcamento["itens_ja_pagos"].values())
    gasto_total_viagem = total_gasto + total_ja_pago
    saldo_final = orcamento["limite_total"] - gasto_total_viagem
    
    return {
        "total_gasto": total_gasto,
        "total_ja_pago": total_ja_pago,
        "gasto_total_viagem": gasto_total_viagem,
        "saldo_final": saldo_final,
        "percentual": (gasto_total_viagem / orcamento["limite_total"] * 100)
    }

def obter_gastos_por_cidade(cidade):
    """Retorna gastos de uma cidade específica"""
    df = carregar_despesas()
    return df[df["cidade"] == cidade]

# ============== HEADER COM CONTADOR DE DIAS ==============
st.title("✈️ VIAGEM EUROPA 2026")
st.markdown("**Controle de Gastos
