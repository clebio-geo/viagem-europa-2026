import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, date

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

ORCAMENTO_TOTAL = 20000.0
DATA_INICIO = date(2026, 10, 30)
DATA_FIM = date(2026, 11, 17)

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
.block-container {
    padding-top: 1.5rem;
}
.kpi-card {
    padding: 18px;
    border-radius: 16px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}
.small-muted {
    font-size: 0.9rem;
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)

# =========================
# DADOS INICIAIS
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
# FUNÇÕES DE ARQUIVO
# =========================
def inicializar_arquivos():
    if not ARQUIVO_GASTOS.exists():
        df = pd.DataFrame(columns=colunas_gastos)
        df.to_csv(ARQUIVO_GASTOS, index=False)

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
        return pd.DataFrame(columns=colunas_gastos)
    except Exception:
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

# =========================
# FUNÇÕES DE NEGÓCIO
# =========================
def dias_restantes():
    hoje = date.today()
    return (DATA_INICIO - hoje).days

def duracao_viagem():
    return (DATA_FIM - DATA_INICIO).days + 1

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
    st.title("✈️ Menu")
    st.markdown("### Viagem Europa 2026")
    st.write("Casal | Econômica | 18 dias")
    st.metric("Orçamento total", f"R$ {ORCAMENTO_TOTAL:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.metric("Dias restantes", dias_restantes())
    st.metric("Duração", f"{duracao_viagem()} dias")

# =========================
# CABEÇALHO
# =========================
st.title("✈️ VIAGEM EUROPA 2026")
st.caption("Controle de Gastos — Clébio & Esposa")

colA, colB = st.columns([4, 1])
with colA:
    st.subheader(f"🗓️ Faltam {dias_restantes()} dias para a Viagem!")
    st.write(f"**Início:** {DATA_INICIO.strftime('%d/%m/%Y')} | **Duração:** {duracao_viagem()} dias")
with colB:
    st.metric("Dias restantes", dias_restantes())

st.divider()

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Painel", "➕ Adicionar Gasto", "✈️ Transportes", "📈 Gráficos", "✅ Preparação"]
)

# =========================
# TAB 1 - PAINEL
# =========================
with tab1:
    st.subheader("Resumo Geral")

    totais = calcular_totais()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Gasto registrado", f"R$ {totais['total_gasto']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with c2:
        st.metric("Já pago", f"R$ {totais['total_ja_pago']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with c3:
        st.metric("Orçamento", f"R$ {ORCAMENTO_TOTAL:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with c4:
        st.metric("Saldo", f"R$ {totais['saldo_final']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.progress(min(max(totais["percentual"] / 100, 0), 1))
    st.caption(f"Uso do orçamento: {totais['percentual']:.1f}%")

    df_gastos = carregar_gastos()

    st.markdown("### Últimos gastos")
    if df_gastos.empty:
        st.info("Nenhum gasto registrado ainda.")
    else:
        df_view = df_gastos.copy()
        df_view["valor"] = pd.to_numeric(df_view["valor"], errors="coerce").fillna(0)
        st.dataframe(
            df_view.sort_index(ascending=False),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("### Cidades do roteiro")
    roteiro = carregar_roteiro()
    st.dataframe(pd.DataFrame(roteiro), use_container_width=True, hide_index=True)

# =========================
# TAB 2 - ADICIONAR GASTO
# =========================
with tab2:
    st.subheader("Adicionar novo gasto")

    with st.form("form_gasto"):
        col1, col2 = st.columns(2)

        with col1:
            data_gasto = st.date_input("Data", value=date.today())
            categoria = st.selectbox(
                "Categoria",
                ["Passagem", "Hospedagem", "Alimentação", "Transporte", "Passeio", "Seguro", "Compras", "Outros"]
            )
            descricao = st.text_input("Descrição")

        with col2:
            cidade = st.text_input("Cidade")
            valor = st.number_input("Valor", min_value=0.0, step=10.0, format="%.2f")
            moeda = st.selectbox("Moeda", ["BRL", "EUR"])
            pago = st.checkbox("Já foi pago?")

        enviar = st.form_submit_button("Salvar gasto")

        if enviar:
            novo = pd.DataFrame([{
                "data": data_gasto.strftime("%d/%m/%Y"),
                "categoria": categoria,
                "descricao": descricao,
                "cidade": cidade,
                "valor": valor,
                "moeda": moeda,
                "pago": pago
            }])

            df_atual = carregar_gastos()
            df_atual = pd.concat([df_atual, novo], ignore_index=True)
            salvar_gastos(df_atual)
            st.success("Gasto salvo com sucesso.")

# =========================
# TAB 3 - TRANSPORTES
# =========================
with tab3:
    st.subheader("Planejamento de transportes")
    roteiro = carregar_roteiro()
    df_roteiro = pd.DataFrame(roteiro)

    if df_roteiro.empty:
        st.info("Nenhum transporte cadastrado.")
    else:
        st.dataframe(df_roteiro, use_container_width=True, hide_index=True)

# =========================
# TAB 4 - GRÁFICOS
# =========================
with tab4:
    st.subheader("Visualização dos gastos")
    df = carregar_gastos()

    if df.empty:
        st.info("Cadastre gastos para visualizar os gráficos.")
    else:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

        cat = resumo_por_categoria(df)
        cid = resumo_por_cidade(df)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Gastos por categoria")
            if not cat.empty:
                st.bar_chart(cat.set_index("categoria"))
            else:
                st.info("Sem dados por categoria.")

        with col2:
            st.markdown("#### Gastos por cidade")
            if not cid.empty:
                st.bar_chart(cid.set_index("cidade"))
            else:
                st.info("Sem dados por cidade.")

# =========================
# TAB 5 - PREPARAÇÃO
# =========================
with tab5:
    st.subheader("Checklist de preparação")

    checklist = carregar_checklist()
    checklist_atualizado = []

    for item in checklist:
        marcado = st.checkbox(item["item"], value=item.get("status", False), key=item["item"])
        checklist_atualizado.append({"item": item["item"], "status": marcado})

    if st.button("Salvar checklist"):
        salvar_checklist(checklist_atualizado)
        st.success("Checklist atualizado com sucesso.")

    total_itens = len(checklist_atualizado)
    concluidos = sum(1 for x in checklist_atualizado if x["status"])
    percentual = (concluidos / total_itens * 100) if total_itens > 0 else 0

    st.markdown("### Progresso")
    st.progress(percentual / 100)
    st.write(f"{concluidos}/{total_itens} itens concluídos ({percentual:.1f}%)")
