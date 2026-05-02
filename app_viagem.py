import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Viagem Europa 2026",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO_GASTOS = Path("gastos_viagem.csv")
ARQUIVO_ROTEIRO = Path("roteiro_viagem.json")
ARQUIVO_PREPARACAO = Path("checklist_preparacao.json")

ORCAMENTO_TOTAL = 30000.0
DATA_INICIO = date(2026, 10, 30)
DATA_FIM = date(2026, 11, 17)

# =========================
# CSS
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* Sidebar */
[data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
    width: 320px;
}
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
    width: 320px;
    margin-left: -320px;
}

/* Métricas */
div[data-testid="metric-container"] {
    padding-top: 0.20rem !important;
    padding-bottom: 0.20rem !important;
    margin-bottom: 0.10rem !important;
}

div[data-testid="metric-container"] label[data-testid="stMetricLabel"] {
    white-space: normal !important;
    overflow-wrap: break-word !important;
    line-height: 1.1 !important;
}

div[data-testid="metric-container"] label[data-testid="stMetricLabel"] p {
    font-size: 0.72rem !important;
    line-height: 1.1 !important;
    margin: 0 !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.55rem !important;
    line-height: 1.05 !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.08rem !important;
    line-height: 1.0 !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] div[data-testid="metric-container"] label[data-testid="stMetricLabel"] p {
    font-size: 0.68rem !important;
    line-height: 1.0 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.72rem !important;
    line-height: 1 !important;
}

section[data-testid="stSidebar"] div[data-testid="metric-container"] {
    overflow: visible !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    font-size: 0.88rem;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 0.92rem !important;
}

/* Mobile */
@media (max-width: 768px) {
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 260px;
    }

    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 260px;
        margin-left: -260px;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.12rem !important;
    }

    div[data-testid="metric-container"] label[data-testid="stMetricLabel"] p {
        font-size: 0.64rem !important;
    }

    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.60rem !important;
    }

    section[data-testid="stSidebar"] div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 0.92rem !important;
    }

    section[data-testid="stSidebar"] div[data-testid="metric-container"] label[data-testid="stMetricLabel"] p {
        font-size: 0.60rem !important;
    }

    .block-container {
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }

    h1 {
        font-size: 1.9rem !important;
    }

    h2 {
        font-size: 1.4rem !important;
    }

    h3 {
        font-size: 1.15rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================
# DADOS PADRÃO
# =========================
roteiro_padrao = [
    {"data": "30/10/2026", "trecho": "Fortaleza > Madrid", "tipo": "Aéreo"},
    {"data": "31/10/2026", "trecho": "Madrid", "tipo": "Estadia"},
    {"data": "01/11/2026", "trecho": "Madrid > Barcelona", "tipo": "Trem/Aéreo"},
    {"data": "02/11/2026", "trecho": "Barcelona", "tipo": "Estadia"},
    {"data": "03/11/2026", "trecho": "Barcelona > Bruxelas", "tipo": "Aéreo"},
    {"data": "04/11/2026", "trecho": "Bruxelas > Paris", "tipo": "Trem"},
    {"data": "05/11/2026", "trecho": "Paris (Disney)", "tipo": "Passeio"},
    {"data": "06/11/2026", "trecho": "Paris", "tipo": "Estadia"},
    {"data": "07/11/2026", "trecho": "Paris > Milão", "tipo": "Aéreo"},
    {"data": "08/11/2026", "trecho": "Milão", "tipo": "Estadia"},
    {"data": "09/11/2026", "trecho": "Milão > Suíça", "tipo": "Passeio/Deslocamento"},
    {"data": "10/11/2026", "trecho": "Milão > Veneza", "tipo": "Trem"},
    {"data": "11/11/2026", "trecho": "Milão > Florença", "tipo": "Trem"},
    {"data": "12/11/2026", "trecho": "Florença > Pisa", "tipo": "Passeio"},
    {"data": "13/11/2026", "trecho": "Florença > Roma", "tipo": "Trem"},
    {"data": "14/11/2026", "trecho": "Roma", "tipo": "Estadia"},
    {"data": "15/11/2026", "trecho": "Roma", "tipo": "Estadia"},
    {"data": "16/11/2026", "trecho": "Roma > Madrid", "tipo": "Aéreo"},
    {"data": "17/11/2026", "trecho": "Madrid > Fortaleza", "tipo": "Aéreo"},
]

checklist_padrao = [
    {"item": "Passaporte válido", "status": False},
    {"item": "Seguro viagem emitido", "status": False},
    {"item": "Reservas salvas em PDF", "status": False},
    {"item": "Cartões habilitados para uso internacional", "status": False},
    {"item": "eSIM / internet configurado", "status": False},
    {"item": "Roteiro revisado", "status": False},
    {"item": "Bagagem organizada", "status": False},
]

colunas_gastos = [
    "data", "categoria", "descricao", "cidade", "valor", "moeda", "pago"
]

# =========================
# FUNÇÕES
# =========================
def inicializar_arquivos():
    if not ARQUIVO_GASTOS.exists():
        pd.DataFrame(columns=colunas_gastos).to_csv(ARQUIVO_GASTOS, index=False)

    if not ARQUIVO_ROTEIRO.exists():
        with open(ARQUIVO_ROTEIRO, "w", encoding="utf-8") as f:
            json.dump(roteiro_padrao, f, ensure_ascii=False, indent=2)

    if not ARQUIVO_PREPARACAO.exists():
        with open(ARQUIVO_PREPARACAO, "w", encoding="utf-8") as f:
            json.dump(checklist_padrao, f, ensure_ascii=False, indent=2)

def carregar_gastos():
    try:
        if ARQUIVO_GASTOS.exists():
            df = pd.read_csv(ARQUIVO_GASTOS)
            for coluna in colunas_gastos:
                if coluna not in df.columns:
                    df[coluna] = ""
            return df[colunas_gastos]
    except Exception:
        pass
    return pd.DataFrame(columns=colunas_gastos)

def salvar_gastos(df):
    df.to_csv(ARQUIVO_GASTOS, index=False)

def carregar_roteiro():
    try:
        with open(ARQUIVO_ROTEIRO, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return roteiro_padrao

def carregar_checklist():
    try:
        with open(ARQUIVO_PREPARACAO, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return checklist_padrao

def salvar_checklist(lista):
    with open(ARQUIVO_PREPARACAO, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

def dias_restantes():
    return (DATA_INICIO - date.today()).days

def duracao_viagem():
    return (DATA_FIM - DATA_INICIO).days + 1

def moeda_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_totais():
    df = carregar_gastos()

    if df.empty:
        return {
            "total_gasto": 0.0,
            "total_ja_pago": 0.0,
            "gasto_total_viagem": 0.0,
            "saldo_final": ORCAMENTO_TOTAL,
            "percentual": 0.0
        }

    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    def eh_pago(v):
        if isinstance(v, bool):
            return v
        if pd.isna(v):
            return False
        return str(v).strip().lower() in ["true", "1", "sim", "yes", "x"]

    df["pago_bool"] = df["pago"].apply(eh_pago)

    total_gasto = float(df["valor"].sum())
    total_ja_pago = float(df.loc[df["pago_bool"], "valor"].sum())
    gasto_total_viagem = total_gasto
    saldo_final = ORCAMENTO_TOTAL - gasto_total_viagem
    percentual = (gasto_total_viagem / ORCAMENTO_TOTAL * 100) if ORCAMENTO_TOTAL > 0 else 0.0

    return {
        "total_gasto": total_gasto,
        "total_ja_pago": total_ja_pago,
        "gasto_total_viagem": gasto_total_viagem,
        "saldo_final": saldo_final,
        "percentual": percentual
    }

def resumo_por_categoria(df):
    if df.empty:
        return pd.DataFrame(columns=["categoria", "valor"])
    base = df.copy()
    base["valor"] = pd.to_numeric(base["valor"], errors="coerce").fillna(0)
    return (
        base.groupby("categoria", as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
    )

def resumo_por_cidade(df):
    if df.empty:
        return pd.DataFrame(columns=["cidade", "valor"])
    base = df.copy()
    base["valor"] = pd.to_numeric(base["valor"], errors="coerce").fillna(0)
    return (
        base.groupby("cidade", as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
    )

# =========================
# INICIALIZAÇÃO
# =========================
inicializar_arquivos()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 💰 Orçamento")
    totais_sidebar = calcular_totais()

    st.metric("💵 Orçamento Total", moeda_brl(ORCAMENTO_TOTAL))
    st.write("**Progresso:**")
    st.progress(min(max(totais_sidebar["percentual"] / 100, 0), 1))

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Gasto", f"{totais_sidebar['percentual']:.1f}%")
    with c2:
        st.metric("Saldo", moeda_brl(totais_sidebar["saldo_final"]))

    st.divider()

    st.markdown("## ✅ Preparação")
    checklist_lateral = carregar_checklist()
    total_itens = len(checklist_lateral)
    concluidos = sum(1 for x in checklist_lateral if x.get("status", False))
    st.metric("Itens Prontos", f"{concluidos}/{total_itens}")
    progresso = (concluidos / total_itens) if total_itens > 0 else 0
    st.progress(progresso)

    st.divider()

    st.markdown("## 📋 Informações da Viagem")
    st.write("**Estilo:** Econômico")
    st.write("**Acompanhantes:** Casal")
    st.write("**Início:** 30/out (Fortaleza → Madrid)")
    st.write("**Término:** 17/nov (Madrid → Fortaleza)")
    st.markdown("**Passagens Int.:** ✅ Compradas")
    st.markdown("**Hospedagem:** ⏳ Em andamento")
    st.markdown("**Seguro:** ⏳ Pendente")

    st.divider()

    st.markdown("## 🗺️ Cidades")
    roteiro_sidebar = carregar_roteiro()
    for item in roteiro_sidebar:
        st.caption(f"• {item['data']}: {item['trecho']}")

# =========================
# CABEÇALHO
# =========================
st.title("✈️ VIAGEM EUROPA 2026")
st.caption("Controle de Gastos — Clébio & Esposa")
st.write("**30/out a 17/nov — 19 dias de viagem!**")

st.divider()

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Painel", "➕ Adicionar Gasto", "✈️ Transportes", "📈 Gráficos", "✅ Preparação"]
)

# =========================
# TAB 1
# =========================
with tab1:
    st.subheader("Resumo Geral")
    totais = calcular_totais()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("💰 Gasto Registrado", moeda_brl(totais["total_gasto"]))
    with c2:
        st.metric("💳 Já Pago", moeda_brl(totais["total_ja_pago"]))
    with c3:
        st.metric("🛫 Total", moeda_brl(totais["gasto_total_viagem"]))
    with c4:
        st.metric("💵 Saldo", moeda_brl(totais["saldo_final"]))

    st.markdown("### Progresso do Orçamento")
    st.progress(min(max(totais["percentual"] / 100, 0), 1))
    st.caption(f"{totais['percentual']:.1f}% do orçamento utilizado")

    df = carregar_gastos()

    st.markdown("### Gastos por Categoria")
    if df.empty:
        st.info("Nenhum gasto cadastrado ainda.")
    else:
        resumo_cat = resumo_por_categoria(df)
        st.dataframe(resumo_cat, use_container_width=True, hide_index=True)

# =========================
# TAB 2
# =========================
with tab2:
    st.subheader("Adicionar Gasto")

    with st.form("form_gasto"):
        c1, c2 = st.columns(2)

        with c1:
            data_gasto = st.date_input("Data", value=date.today())
            categoria = st.selectbox(
                "Categoria",
                ["Passagem", "Hospedagem", "Alimentação", "Transporte", "Passeio", "Seguro", "Compras", "Outros"]
            )
            descricao = st.text_input("Descrição")

        with c2:
            cidade = st.text_input("Cidade")
            valor = st.number_input("Valor", min_value=0.0, step=10.0, format="%.2f")
            moeda = st.selectbox("Moeda", ["BRL", "EUR"])
            pago = st.checkbox("Já foi pago?")

        salvar = st.form_submit_button("Salvar gasto")

        if salvar:
            novo = pd.DataFrame([{
                "data": data_gasto.strftime("%d/%m/%Y"),
                "categoria": categoria,
                "descricao": descricao,
                "cidade": cidade,
                "valor": valor,
                "moeda": moeda,
                "pago": pago
            }])

            base = carregar_gastos()
            base = pd.concat([base, novo], ignore_index=True)
            salvar_gastos(base)
            st.success("Gasto salvo com sucesso.")

# =========================
# TAB 3
# =========================
with tab3:
    st.subheader("Transportes")
    st.dataframe(pd.DataFrame(carregar_roteiro()), use_container_width=True, hide_index=True)

# =========================
# TAB 4
# =========================
with tab4:
    st.subheader("Gráficos")
    df = carregar_gastos()

    if df.empty:
        st.info("Cadastre gastos para visualizar os gráficos.")
    else:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Gastos por categoria")
            st.bar_chart(resumo_por_categoria(df).set_index("categoria"))

        with c2:
            st.markdown("#### Gastos por cidade")
            st.bar_chart(resumo_por_cidade(df).set_index("cidade"))

# =========================
# TAB 5
# =========================
with tab5:
    st.subheader("Preparação")

    checklist = carregar_checklist()
    atualizado = []

    for item in checklist:
        marcado = st.checkbox(item["item"], value=item.get("status", False), key=item["item"])
        atualizado.append({"item": item["item"], "status": marcado})

    if st.button("Salvar checklist"):
        salvar_checklist(atualizado)
        st.success("Checklist atualizado.")

    total_itens = len(atualizado)
    concluidos = sum(1 for i in atualizado if i["status"])
    percentual = (concluidos / total_itens * 100) if total_itens > 0 else 0

    st.progress(percentual / 100)
    st.write(f"{concluidos}/{total_itens} itens concluídos ({percentual:.1f}%)")
