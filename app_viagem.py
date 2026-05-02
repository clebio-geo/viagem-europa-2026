#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VIAGEM EUROPA 2026 — APP STREAMLIT AVANÇADO
Versão com Editar/Deletar Gastos, Transportes Detalhados e Seção por Cidade
Roteiro Atualizado: 30/out a 17/nov com cidades e paradas específicas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import json

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

# ============== HEADER ==============
st.title("✈️ VIAGEM EUROPA 2026")
st.markdown("**Controle de Gastos — Clébio & Esposa**")
st.markdown("**30/out a 17/nov — 19 dias de viagem!**")
st.markdown("---")

# ============== ABAS PRINCIPAIS ==============
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
"📊 Painel",
"➕ Adicionar Gasto",
"✈️ Transportes",
"📈 Gráficos",
"📋 Relatório",
"✅ Preparação"
])

# ============== TAB 1: PAINEL ==============
with tab1:
st.subheader("Resumo Geral")

totais = calcular_totais()

col1, col2, col3, col4 = st.columns(4)

with col1:
st.metric("💰 Gasto Registrado", f"R$ {totais['total_gasto']:,.2f}")

with col2:
st.metric("💳 Já Pago", f"R$ {totais['total_ja_pago']:,.2f}")

with col3:
st.metric("🛫 Total", f"R$ {totais['gasto_total_viagem']:,.2f}")

with col4:
saldo = totais['saldo_final']
st.metric(f"💵 Saldo", f"R$ {saldo:,.2f}")

st.markdown("### Progresso do Orçamento")
pct = totais['percentual']
st.progress(min(pct / 100, 1.0))
st.write(f"**{pct:.1f}%** do orçamento utilizado")

st.markdown("### Gastos por Categoria")
df_gastos = calcular_gastos()

if not df_gastos.empty:
df_exibir = df_gastos[["categoria", "gasto", "orcado", "saldo"]].copy()
df_exibir.columns = ["Categoria", "Gasto", "Orçado", "Saldo"]
st.dataframe(
df_exibir,
use_container_width=True,
hide_index=True
)

# ============== SEÇÃO DE CIDADES ==============
st.markdown("---")
st.markdown("### 🌍 Cidades do Roteiro")

cols = st.columns(5)
for idx, cidade in enumerate(CIDADES_ROTEIRO):
with cols[idx % 5]:
if st.button(f"📍 {cidade}", use_container_width=True, key=f"btn_cidade_{cidade}"):
st.session_state.cidade_selecionada = cidade

# Se uma cidade foi selecionada, mostrar detalhes
if "cidade_selecionada" in st.session_state:
cidade_selecionada = st.session_state.cidade_selecionada

st.markdown(f"---")
st.markdown(f"## 📍 Detalhes de {cidade_selecionada}")

# Abas da cidade
tab_cid_1, tab_cid_2, tab_cid_3, tab_cid_4 = st.tabs([
"🏨 Hospedagem",
"✈️ Transportes",
"💰 Gastos",
"🗺️ Roteiro"
])

# ============== ABA: HOSPEDAGEM ==============
with tab_cid_1:
st.subheader(f"Hospedagem em {cidade_selecionada}")

hospedagem = carregar_hospedagem()
dados_atuais = hospedagem.get(cidade_selecionada, {})

col1, col2 = st.columns(2)

with col1:
nome_hotel = st.text_input(
"Nome da Hospedagem:",
value=dados_atuais.get("nome", ""),
key=f"hotel_nome_{cidade_selecionada}"
)
endereco = st.text_input(
"Endereço:",
value=dados_atuais.get("endereco", ""),
key=f"hotel_endereco_{cidade_selecionada}"
)

with col2:
checkin = st.time_input(
"Horário Check-in:",
value=datetime.strptime(dados_atuais.get("checkin", "15:00"), "%H:%M").time(),
key=f"hotel_checkin_{cidade_selecionada}"
)
checkout = st.time_input(
"Horário Check-out:",
value=datetime.strptime(dados_atuais.get("checkout", "11:00"), "%H:%M").time(),
key=f"hotel_checkout_{cidade_selecionada}"
)

telefone = st.text_input(
"Telefone de Contato:",
value=dados_atuais.get("telefone", ""),
key=f"hotel_tel_{cidade_selecionada}"
)

confirmacao = st.text_input(
"Número de Confirmação:",
value=dados_atuais.get("confirmacao", ""),
key=f"hotel_conf_{cidade_selecionada}"
)

if st.button(f"💾 Salvar Hospedagem em {cidade_selecionada}", use_container_width=True):
dados_hotel = {
"nome": nome_hotel,
"endereco": endereco,
"checkin": checkin.strftime("%H:%M"),
"checkout": checkout.strftime("%H:%M"),
"telefone": telefone,
"confirmacao": confirmacao
}
atualizar_hospedagem_cidade(cidade_selecionada, dados_hotel)
st.success(f"✅ Hospedagem salva em {cidade_selecionada}!")

# ============== ABA: TRANSPORTES DA CIDADE ==============
with tab_cid_2:
st.subheader(f"Transportes em/para {cidade_selecionada}")

transportes = carregar_transportes()
transportes_cidade = [t for t in transportes if t.get("origem") == cidade_selecionada or t.get("destino") == cidade_selecionada]

if transportes_cidade:
st.markdown("**Transportes Cadastrados:**")
for idx, t in enumerate(transportes_cidade):
with st.container():
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
st.write(f"**{t.get('origem')} → {t.get('destino')}**")
st.write(f"📅 {t.get('data')} | 🚀 {t.get('tipo')} | {t.get('companhia')}")
st.write(f"⏰ {t.get('saida')} → {t.get('chegada')} ({t.get('duracao')})")
st.write(f"📍 {t.get('local_saida')} → {t.get('local_chegada')}")

if t.get('tipo') == 'Avião':
st.warning("⚠️ **Chegue 2-3 horas antes do voo!**")
elif t.get('tipo') in ['Trem', 'Metro']:
st.info("ℹ️ **Chegue 15-30 minutos antes**")

with col2:
if st.button("✏️ Editar", key=f"edit_transp_{idx}", use_container_width=True):
st.session_state[f"editar_transporte_{idx}"] = True

with col3:
if st.button("🗑️ Deletar", key=f"del_transp_{idx}", use_container_width=True):
deletar_transporte(idx)
st.success("Transporte deletado!")
st.rerun()

st.markdown("---")
else:
st.info(f"Nenhum transporte cadastrado para {cidade_selecionada}")

# ============== ABA: GASTOS DA CIDADE ==============
with tab_cid_3:
st.subheader(f"Gastos em {cidade_selecionada}")

gastos_cidade = obter_gastos_por_cidade(cidade_selecionada)

if not gastos_cidade.empty:
# Resumo por categoria
gastos_por_cat = gastos_cidade.groupby("categoria")["valor"].sum().sort_values(ascending=False)

col1, col2 = st.columns(2)

with col1:
st.markdown("**Gastos por Categoria:**")
for cat, val in gastos_por_cat.items():
st.write(f" • {cat}: R$ {val:,.2f}")

with col2:
st.metric("Total em " + cidade_selecionada, f"R$ {gastos_cidade['valor'].sum():,.2f}")

st.markdown("**Todos os Gastos:**")
df_exibir = gastos_cidade.copy()
df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")
df_exibir.columns = ["Data", "Categoria", "Descrição", "Cidade", "Valor"]

# Adicionar coluna de ações
for idx, row in gastos_cidade.iterrows():
col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

with col1:
st.write(row["data"].strftime("%d/%m/%Y"))
with col2:
st.write(row["descricao"])
with col3:
if st.button("✏️", key=f"edit_gasto_{idx}", help="Editar"):
st.session_state[f"editar_gasto_{idx}"] = True
with col4:
if st.button("🗑️", key=f"del_gasto_{idx}", help="Deletar"):
deletar_despesa(idx)
st.success("Gasto deletado!")
st.rerun()
else:
st.info(f"Nenhum gasto registrado em {cidade_selecionada}")

# ============== ABA: ROTEIRO ==============
with tab_cid_4:
st.subheader(f"Roteiro em {cidade_selecionada}")
st.info("📌 Seção de Roteiro será preenchida posteriormente com atrações, horários e dicas!")

# ============== TAB 2: ADICIONAR GASTO ==============
with tab2:
st.subheader("Registre um Novo Gasto")

st.markdown("### ➕ Adicionar Nova Categoria (Opcional)")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
nova_categoria = st.text_input(
"Nome da Categoria:",
placeholder="Ex: Translado, Souvenirs, etc",
key="input_nova_cat"
)

with col2:
orcamento_nova = st.number_input(
"Orçamento (R$):",
min_value=0.0,
value=500.0,
step=50.0,
key="input_orcamento_cat"
)

with col3:
if st.button("➕ Criar Categoria", use_container_width=True, key="btn_criar_cat"):
if nova_categoria.strip():
if adicionar_categoria(nova_categoria.strip(), orcamento_nova):
st.success(f"✅ Categoria '{nova_categoria}' criada!")
st.rerun()
else:
st.warning(f"⚠️ Categoria '{nova_categoria}' já existe!")
else:
st.error("⚠️ Digite um nome para a categoria!")

st.markdown("---")
st.markdown("### 💸 Registrar Gasto")

categorias = list(carregar_categorias().keys())

with st.form("form_despesa", clear_on_submit=True):
col1, col2 = st.columns(2)

with col1:
data = st.date_input("📅 Data", value=datetime.now())
categoria = st.selectbox("📂 Categoria", categorias, key="select_cat")

with col2:
cidade = st.selectbox("🏙️ Cidade", CIDADES_ROTEIRO)
valor = st.number_input("💵 Valor (R$)", min_value=0.0, step=0.01)

descricao = st.text_input("📝 Descrição", placeholder="Ex: Café, Hotel, Translado, etc")

submitted = st.form_submit_button("✅ Adicionar Gasto", use_container_width=True)

if submitted:
if not descricao:
st.error("⚠️ Digite uma descrição!")
elif valor <= 0:
st.error("⚠️ Valor deve ser maior que 0!")
else:
salvar_despesa(data, categoria, descricao, cidade, valor)
st.success(f"✅ Gasto registrado: {descricao} — R$ {valor:.2f} em {cidade}")
st.rerun()

# ============== TAB 3: TRANSPORTES ==============
with tab3:
st.subheader("✈️ Transportes Internos")

st.markdown("### ➕ Adicionar Novo Transporte")

with st.form("form_transporte", clear_on_submit=True):
col1, col2 = st.columns(2)

with col1:
data_transp = st.date_input("📅 Data", value=datetime.now(), key="transp_data")
origem = st.selectbox("🛫 Origem", CIDADES_ROTEIRO, key="transp_origem")

with col2:
destino = st.selectbox("🛬 Destino", CIDADES_ROTEIRO, key="transp_destino")
tipo_transp = st.selectbox("🚀 Tipo de Transporte", TIPO_TRANSPORTE, key="transp_tipo")

col1, col2, col3 = st.columns(3)

with col1:
hora_saida = st.time_input("⏰ Hora Saída", key="transp_saida")

with col2:
hora_chegada = st.time_input("⏰ Hora Chegada", key="transp_chegada")

with col3:
duracao = calcular_duracao(hora_saida.strftime("%H:%M"), hora_chegada.strftime("%H:%M"))
st.write(f"**Duração:** {duracao}")

col1, col2 = st.columns(2)

with col1:
companhia = st.text_input("🏢 Companhia", placeholder="Ex: TAP, Lufthansa, Renfe, etc", key="transp_comp")
local_saida = st.text_input("📍 Aeroporto/Estação Saída", placeholder="Ex: MAD - Barajas, Paris CDG", key="transp_saida_loc")

with col2:
numero_voo = st.text_input("🎫 Número Voo/Trem", placeholder="Ex: TP100, ICE 900", key="transp_num")
local_chegada = st.text_input("📍 Aeroporto/Estação Chegada", placeholder="Ex: BCN - El Prat, Paris Gare du Nord", key="transp_chegada_loc")

# Aviso de horário
if tipo_transp == "Avião":
st.warning("⚠️ **Lembrete:** Chegar 2-3 horas antes do voo!")
elif tipo_transp == "Trem":
st.info("ℹ️ **Lembrete:** Chegar 15-30 minutos antes!")
elif tipo_transp == "Metro":
st.info("ℹ️ **Lembrete:** Chegar 10 minutos antes!")

submitted = st.form_submit_button("✅ Adicionar Transporte", use_container_width=True)

if submitted:
if not companhia or not local_saida or not local_chegada:
st.error("⚠️ Preencha todos os campos!")
else:
transporte_dict = {
"data": data_transp.strftime("%d/%m/%Y"),
"origem": origem,
"destino": destino,
"tipo": tipo_transp,
"saida": hora_saida.strftime("%H:%M"),
"chegada": hora_chegada.strftime("%H:%M"),
"duracao": duracao,
"companhia": companhia,
"numero": numero_voo,
"local_saida": local_saida,
"local_chegada": local_chegada
}
adicionar_transporte(transporte_dict)
st.success(f"✅ Transporte cadastrado: {origem} → {destino}")
st.rerun()

st.markdown("---")
st.markdown("### 📋 Transportes Cadastrados")

transportes = carregar_transportes()

if transportes:
for idx, t in enumerate(transportes):
with st.container():
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

with col1:
st.write(f"**{t.get('origem')} → {t.get('destino')}**")
st.write(f"📅 {t.get('data')} | 🚀 {t.get('tipo')} | {t.get('companhia')}")
st.write(f"⏰ {t.get('saida')} → {t.get('chegada')} ({t.get('duracao')})")
st.write(f"📍 {t.get('local_saida')} → {t.get('local_chegada')}")
st.write(f"🎫 {t.get('numero')}")

with col2:
if st.button("ℹ️", key=f"info_transp_{idx}", help="Informações"):
st.info(f"Companhia: {t.get('companhia')}\\nVoo/Trem: {t.get('numero')}")

with col3:
if st.button("✏️", key=f"edit_transp_list_{idx}", help="Editar"):
st.session_state[f"editar_transporte_list_{idx}"] = True

with col4:
if st.button("🗑️", key=f"del_transp_list_{idx}", help="Deletar"):
deletar_transporte(idx)
st.success("Transporte deletado!")
st.rerun()

st.markdown("---")
else:
st.info("Nenhum transporte cadastrado ainda.")

# ============== TAB 4: GRÁFICOS ==============
with tab4:
st.subheader("Análise Visual")

df = carregar_despesas()

if not df.empty:
col1, col2 = st.columns(2)

with col1:
st.markdown("**Gastos por Cidade**")
gastos_cidade = df.groupby("cidade")["valor"].sum().sort_values(ascending=False)
fig1 = px.bar(x=gastos_cidade.index, y=gastos_cidade.values)
st.plotly_chart(fig1, use_container_width=True)

with col2:
st.markdown("**Evolução Acumulada**")
df_sorted = df.sort_values("data")
df_sorted["acumulado"] = df_sorted["valor"].cumsum()
fig2 = px.line(df_sorted, x="data", y="acumulado", markers=True)
st.plotly_chart(fig2, use_container_width=True)
else:
st.info("📊 Adicione gastos para ver os gráficos!")

# ============== TAB 5: RELATÓRIO ==============
with tab5:
st.subheader("Relatório Completo")

df = carregar_despesas()

if not df.empty:
st.markdown("### Todas as Despesas")
df_exibir = df.copy()
df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")
df_exibir.columns = ["Data", "Categoria", "Descrição", "Cidade", "Valor"]

# Mostrar com opções de editar/deletar
for idx, row in df.iterrows():
col1, col2, col3, col4, col5 = st.columns([1, 1.5, 1, 1, 1])

with col1:
st.write(row["data"].strftime("%d/%m/%Y"))
with col2:
st.write(row["descricao"])
with col3:
st.write(row["categoria"])
with col4:
st.write(f"R$ {row['valor']:.2f}")
with col5:
col_edit, col_del = st.columns(2)
with col_edit:
if st.button("✏️", key=f"edit_rel_{idx}", help="Editar"):
st.session_state[f"editar_gasto_rel_{idx}"] = True
with col_del:
if st.button("🗑️", key=f"del_rel_{idx}", help="Deletar"):
deletar_despesa(idx)
st.success("Gasto deletado!")
st.rerun()

st.markdown("---")

# Download CSV
csv = df.to_csv(index=False)
st.download_button(
label="📥 Baixar Dados (CSV)",
data=csv,
file_name=f"gastos_europa_{datetime.now().strftime('%Y%m%d')}.csv",
mime="text/csv"
)
else:
st.info("Nenhuma despesa registrada ainda.")

# ============== TAB 6: PREPARAÇÃO ==============
with tab6:
st.subheader("✅ Checklist de Preparação")
st.markdown("Marque os itens obrigatórios conforme prepare para a viagem!")
st.markdown("---")

df_checklist = carregar_checklist()

total_itens = len(df_checklist)
itens_concluidos = df_checklist["concluido"].sum()
percentual_conclusao = (itens_concluidos / total_itens * 100) if total_itens > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
st.metric("📋 Total de Itens", total_itens)
with col2:
st.metric("✅ Concluídos", itens_concluidos)
with col3:
st.metric("📊 Progresso", f"{percentual_conclusao:.1f}%")

st.progress(min(percentual_conclusao / 100, 1.0))
st.markdown("---")

st.markdown("### ➕ Adicionar Novo Item")
col1, col2 = st.columns([4, 1])
with col1:
novo_item = st.text_input("Nome do Item:", placeholder="Ex: Dinheiro em euros, Adaptador, etc")
with col2:
if st.button("➕ Adicionar", use_container_width=True):
if novo_item.strip():
adicionar_item_checklist(novo_item.strip())
st.success(f"✅ Item '{novo_item}' adicionado!")
st.rerun()
else:
st.error("⚠️ Digite um nome para o item!")

st.markdown("---")
st.markdown("### 📝 Lista de Verificação")

col1, col2 = st.columns(2)

for idx, row in df_checklist.iterrows():
col = col1 if idx % 2 == 0 else col2

with col:
novo_estado = st.checkbox(
row["item"],
value=row["concluido"],
key=f"item_{idx}"
)

if novo_estado != row["concluido"]:
marcar_concluido(idx, novo_estado)
st.rerun()

col_delete = st.columns([4, 1])[1]
with col_delete:
if st.button("🗑️", key=f"del_{idx}", help="Deletar item"):
deletar_item_checklist(idx)
st.success("Item removido!")
st.rerun()

st.markdown("---")
st.markdown("### 📊 Resumo")

itens_pendentes = df_checklist[~df_checklist["concluido"]]["item"].tolist()

if itens_pendentes:
st.markdown("**Itens ainda não preparados:**")
for item in itens_pendentes[:5]:
st.write(f" • {item}")
if len(itens_pendentes) > 5:
st.write(f" ... e mais {len(itens_pendentes) - 5} itens")
else:
st.success("🎉 Parabéns! Todos os itens estão preparados!")

# ============== SIDEBAR ==============
with st.sidebar:
st.markdown("---")
st.markdown("### ✈️ Eurotrip 2026")
st.markdown("---")

st.markdown("📅 **30/out a 17/nov/2026**")
st.markdown("**Duração:** 19 dias")
st.markdown("**Início:** 30/out (Fortaleza → Madrid)")

st.markdown("---")
st.markdown("### 🌍 Roteiro Detalhado (14 Cidades)")

cidades_detalhes = [
("🇧🇷 Fortaleza", "Brasil"),
("🇪🇸 Madrid", "Espanha"),
("🏛️ Barcelona", "Espanha"),
("🇧🇪 Bruxelas", "Bélgica"),
("🗼 Paris", "França"),
("🎡 Marne-la-Vallée", "França - Disney"),
("🇮🇹 Milão", "Itália"),
("🚂 Tirano", "Itália"),
("⛰️ Suíça (Poschiavo, St. Moritz)", "Suíça"),
("🚤 Veneza", "Itália"),
("🎨 Florença", "Itália"),
("🗼 Pisa", "Itália"),
("🏛️ Roma", "Itália"),
("⛪ Vaticano", "Vaticano"),
]

for cidade, pais in cidades_detalhes:
st.markdown(f"**{cidade}** • {pais}")

st.markdown("---")
st.markdown("### 📅 Cronograma da Viagem")

st.markdown("""
- **30/out**: Fortaleza → Madrid
- **31/out**: Madrid
- **01/nov**: Madrid → Barcelona
- **02/nov**: Barcelona
- **03/nov**: Barcelona → Bruxelas
- **04/nov**: Bruxelas → Paris
- **05/nov**: Marne-la-Vallée (Disney)
- **06/nov**: Paris
- **07/nov**: Paris → Milão
- **08/nov**: Milão
- **09/nov**: Milão (Tirano) → Suíça (Poschiavo, St. Moritz)
- **10/nov**: Milão → Veneza
- **11/nov**: Milão → Florença
- **12/nov**: Florença → Pisa
- **13/nov**: Florença → Roma
- **14/nov**: Roma → Vaticano
- **15/nov**: Roma
- **16/nov**: Roma → Madrid
- **17/nov**: Madrid → Fortaleza
""")

st.markdown("---")
st.markdown("### 💰 Orçamento")

totais = calcular_totais()
orcamento = obter_orcamento()
orcamento_total = orcamento["limite_total"]
gasto_total = totais["gasto_total_viagem"]
percentual = totais["percentual"]
saldo = totais["saldo_final"]

st.metric("💵 Orçamento Total", f"R$ {orcamento_total:,.0f}")
st.markdown("**Progresso:**")
st.progress(min(percentual / 100, 1.0))

col1, col2 = st.columns(2)
with col1:
st.metric("Gasto", f"{percentual:.1f}%", f"R$ {gasto_total:,.0f}")
with col2:
cor = "🟢" if saldo >= 0 else "🔴"
st.metric("Saldo", f"{cor} R$ {saldo:,.0f}")

st.markdown("---")
st.markdown("### ✅ Preparação")
df_check = carregar_checklist()
check_concluidos = df_check["concluido"].sum()
check_total = len(df_check)
check_pct = (check_concluidos / check_total * 100) if check_total > 0 else 0

st.metric("Itens Prontos", f"{check_concluidos}/{check_total}", f"{check_pct:.0f}%")
st.progress(min(check_pct / 100, 1.0))

st.markdown("---")
st.markdown("### 📋 Informações da Viagem")
st.markdown("""
**Estilo:** Econômico
**Acompanhantes:** Casal
**Início:** 30/out (Fortaleza → Madrid)
**Término:** 17/nov (Madrid → Fortaleza)
**Passagens Int:** ✅ Compradas
**Seguro:** ✅ Pago (R$ 350)
""")

st.markdown("---")
st.markdown("### 📂 Categorias")
categorias_atuais = carregar_categorias()
for cat, valor in categorias_atuais.items():
st.write(f" • {cat}: R$ {valor:,.0f}")

st.markdown("---")
st.markdown("### 💡 Dicas")
st.markdown("""
📱 Use o app no celular
📊 Acompanhe em tempo real
💾 Baixe dados regularmente
✅ Prepare com antecedência
""")
