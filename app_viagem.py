#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VIAGEM EUROPA 2026 — APP STREAMLIT DE CONTROLE DE GASTOS
Versão Completa Corrigida
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
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

# ============== ORÇAMENTO COM TRANSLADO ==============
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

CIDADES = [
    "Madrid", "Barcelona", "Bruxelas", "Paris", "Milão",
    "Suíça", "Veneza", "Florença", "Pisa", "Roma"
]

# ============== ITENS OBRIGATÓRIOS ==============
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
    """Carrega categorias do arquivo ou usa as padrões."""
    if os.path.exists(ARQUIVO_CATEGORIAS):
        with open(ARQUIVO_CATEGORIAS, 'r') as f:
            return json.load(f)
    else:
        salvar_categorias(ORCAMENTO_PADRAO["categorias"])
        return ORCAMENTO_PADRAO["categorias"]


def salvar_categorias(categorias):
    """Salva as categorias em arquivo JSON."""
    with open(ARQUIVO_CATEGORIAS, 'w') as f:
        json.dump(categorias, f, ensure_ascii=False, indent=2)


def adicionar_categoria(nome_categoria, orcamento_categoria=0.0):
    """Adiciona uma nova categoria."""
    categorias = carregar_categorias()
    if nome_categoria not in categorias:
        categorias[nome_categoria] = float(orcamento_categoria)
        salvar_categorias(categorias)
        return True
    return False


def obter_orcamento():
    """Retorna o orçamento com as categorias atualizadas."""
    orcamento = ORCAMENTO_PADRAO.copy()
    orcamento["categorias"] = carregar_categorias()
    return orcamento


# ============== FUNÇÕES DE DESPESAS ==============

def carregar_despesas():
    """Carrega despesas do CSV."""
    if os.path.exists(ARQUIVO_DESPESAS):
        df = pd.read_csv(ARQUIVO_DESPESAS)
        df["data"] = pd.to_datetime(df["data"])
        return df
    return pd.DataFrame(columns=["data", "categoria", "descricao", "cidade", "valor"])


def salvar_despesa(data, categoria, descricao, cidade, valor):
    """Salva uma nova despesa."""
    df = carregar_despesas()
    nova_linha = pd.DataFrame([{
        "data": data,
        "categoria": categoria,
        "descricao": descricao,
        "cidade": cidade,
        "valor": valor
    }])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(ARQUIVO_DESPESAS, index=False)
    return True


# ============== FUNÇÕES DE CHECKLIST ==============

def carregar_checklist():
    """Carrega checklist de preparação."""
    if os.path.exists(ARQUIVO_CHECKLIST):
        df = pd.read_csv(ARQUIVO_CHECKLIST)
        return df
    df = pd.DataFrame({
        "item": ITENS_OBRIGATORIOS,
        "concluido": [False] * len(ITENS_OBRIGATORIOS)
    })
    df.to_csv(ARQUIVO_CHECKLIST, index=False)
    return df


def salvar_checklist(df):
    """Salva o checklist atualizado."""
    df.to_csv(ARQUIVO_CHECKLIST, index=False)


def adicionar_item_checklist(item):
    """Adiciona um novo item ao checklist."""
    df = carregar_checklist()
    novo_item = pd.DataFrame([{"item": item, "concluido": False}])
    df = pd.concat([df, novo_item], ignore_index=True)
    salvar_checklist(df)
    return True


def deletar_item_checklist(index):
    """Deleta um item do checklist."""
    df = carregar_checklist()
    df = df.drop(index).reset_index(drop=True)
    salvar_checklist(df)
    return True


def marcar_concluido(index, valor):
    """Marca um item como concluído."""
    df = carregar_checklist()
    df.loc[index, "concluido"] = valor
    salvar_checklist(df)
    return True


# ============== FUNÇÕES DE CÁLCULO ==============

def calcular_gastos():
    """Calcula gastos por categoria."""
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
    """Calcula totais."""
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


# ============== HEADER ==============
st.title("✈️ VIAGEM EUROPA 2026")
st.markdown("**Controle de Gastos — Clébio & Esposa**")
st.markdown("---")

# ============== ABAS ==============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Painel",
    "➕ Adicionar Gasto",
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

    # Barra de progresso
    st.markdown("### Progresso do Orçamento")
    pct = totais['percentual']
    st.progress(min(pct / 100, 1.0))
    st.write(f"**{pct:.1f}%** do orçamento utilizado")

    # Tabela por categoria
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

# ============== TAB 2: ADICIONAR GASTO ==============
with tab2:
    st.subheader("Registre um Novo Gasto")

    # Seção para adicionar nova categoria
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
                    st.success(f"✅ Categoria '{nova_categoria}' criada com orçamento R$ {orcamento_nova}!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ Categoria '{nova_categoria}' já existe!")
            else:
                st.error("⚠️ Digite um nome para a categoria!")

    st.markdown("---")

    # Formulário para adicionar gasto
    st.markdown("### 💸 Registrar Gasto")

    categorias = list(carregar_categorias().keys())

    with st.form("form_despesa", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            data = st.date_input("📅 Data", value=datetime.now())
            categoria = st.selectbox("📂 Categoria", categorias, key="select_cat")

        with col2:
            cidade = st.selectbox("🏙️ Cidade", CIDADES)
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
                st.success(f"✅ Gasto registrado: {descricao} — R$ {valor:.2f}")
                st.rerun()

# ============== TAB 3: GRÁFICOS ==============
with tab3:
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

# ============== TAB 4: RELATÓRIO ==============
with tab4:
    st.subheader("Relatório Completo")

    df = carregar_despesas()

    if not df.empty:
        st.markdown("### Todas as Despesas")
        df_exibir = df.copy()
        df_exibir["data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")
        df_exibir.columns = ["Data", "Categoria", "Descrição", "Cidade", "Valor"]
        st.dataframe(df_exibir, use_container_width=True, hide_index=True)

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

# ============== TAB 5: PREPARAÇÃO ==============
with tab5:
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
            item_container = st.container()

            with item_container:
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
            st.write(f"  • {item}")
        if len(itens_pendentes) > 5:
            st.write(f"  ... e mais {len(itens_pendentes) - 5} itens")
    else:
        st.success("🎉 Parabéns! Todos os itens estão preparados!")

# ============== SIDEBAR MELHORADO ==============
with st.sidebar:
    st.markdown("---")

    st.markdown("### ✈️ Eurotrip 2026")
    st.markdown("---")

    st.markdown("📅 **30/out a 17/nov/2026**")
    st.markdown("**Duração:** 18 dias")

    st.markdown("---")

    st.markdown("### 🌍 Roteiro (10 Cidades)")

    cidades_detalhes = [
        ("🇪🇸 Madrid", "Espanha"),
        ("🏛️ Barcelona", "Espanha"),
        ("🇧🇪 Bruxelas", "Bélgica"),
        ("🗼 Paris", "França"),
        ("🇮🇹 Milão", "Itália"),
        ("⛰️ Suíça", "Suíça"),
        ("🚤 Veneza", "Itália"),
        ("🎨 Florença", "Itália"),
        ("📐 Pisa", "Itália"),
        ("🏛️ Roma", "Itália"),
    ]

    for cidade, pais in cidades_detalhes:
        st.markdown(f"**{cidade}** • {pais}")

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
    **Passagens:** ✅ Compradas  
    **Seguro:** ✅ Pago (R$ 350)  
    """)

    st.markdown("---")

    st.markdown("### 📂 Categorias")
    categorias_atuais = carregar_categorias()
    for cat, valor in categorias_atuais.items():
        st.write(f"  • {cat}: R$ {valor:,.0f}")

    st.markdown("---")

    st.markdown("### 💡 Dicas")
    st.markdown("""
    📱 Use o app no celular  
    📊 Acompanhe em tempo real  
    💾 Baixe dados regularmente  
    ✅ Prepare com antecedência  
    """)

    st.markdown("---")

    st.markdown("""
    <div style='text-align: center; font-size: 0.8rem; color: #888;'>
    <p>Viagem inteligente 🚀</p>
    <p>Orçamento 2026</p>
    </div>
    """, unsafe_allow_html=True)