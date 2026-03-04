import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(page_title="Banco Digital Finance", layout="wide")

# ==============================
# ESTILO DARK FINTECH
# ==============================
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
.block-container {
    padding-top: 2rem;
}
div[data-testid="metric-container"] {
    background-color: #1C1F26;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏦 Banco Digital Finance")

# ==============================
# SESSION STATE
# ==============================
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "Tipo", "Descricao", "Valor", "Data"
    ])

# ==============================
# SIDEBAR - NOVA TRANSAÇÃO
# ==============================
st.sidebar.header("➕ Nova Transação")

tipo = st.sidebar.selectbox("Tipo", ["Receita", "Despesa"])
descricao = st.sidebar.text_input("Descrição")
valor = st.sidebar.number_input("Valor", min_value=0.0, step=0.01)
data = st.sidebar.date_input("Data", datetime.today())

if st.sidebar.button("Adicionar"):
    nova = pd.DataFrame([{
        "Tipo": tipo,
        "Descricao": descricao,
        "Valor": valor,
        "Data": pd.to_datetime(data)
    }])
    st.session_state.dados = pd.concat([st.session_state.dados, nova], ignore_index=True)
    st.sidebar.success("Transação adicionada!")

# ==============================
# IMPORTAÇÃO CSV
# ==============================
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Importar CSV")

arquivo = st.sidebar.file_uploader("Envie um CSV", type=["csv"])

if arquivo:
    df_upload = pd.read_csv(arquivo)
    st.session_state.dados = pd.concat([st.session_state.dados, df_upload], ignore_index=True)
    st.sidebar.success("Arquivo importado com sucesso!")

# ==============================
# DASHBOARD PRINCIPAL
# ==============================
st.markdown("## 📊 Dashboard")

if not st.session_state.dados.empty:

    df = st.session_state.dados.copy()

    receitas = df[df["Tipo"] == "Receita"]["Valor"].sum()
    despesas = df[df["Tipo"] == "Despesa"]["Valor"].sum()
    saldo = receitas - despesas

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Receitas", f"R$ {receitas:,.2f}")
    col2.metric("💸 Despesas", f"R$ {despesas:,.2f}")
    col3.metric("📈 Saldo", f"R$ {saldo:,.2f}")

    fig = px.pie(df, names="Tipo", values="Valor", hole=0.6,
                 color_discrete_sequence=["#00C896", "#FF4B4B"])
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Adicione transações para visualizar o dashboard.")

# ==============================
# 🎯 METAS FINANCEIRAS
# ==============================
st.markdown("---")
st.header("🎯 Metas Financeiras")

meta_valor = st.number_input("Valor da Meta (R$)", min_value=0.0)
meta_prazo = st.number_input("Prazo (meses)", min_value=1, value=12)
cdi_anual = st.number_input("CDI anual (%)", value=13.15)

if meta_valor > 0:

    taxa_mensal = (1 + cdi_anual/100)**(1/12) - 1

    if taxa_mensal > 0:
        aporte_necessario = meta_valor * taxa_mensal / ((1 + taxa_mensal)**meta_prazo - 1)
    else:
        aporte_necessario = meta_valor / meta_prazo

    st.success(f"Você precisa investir aproximadamente R$ {aporte_necessario:,.2f} por mês.")

# ==============================
# 🛟 RESERVA DE EMERGÊNCIA
# ==============================
st.markdown("---")
st.header("🛟 Reserva de Emergência")

meses_reserva = st.slider("Meses de segurança", 3, 12, 6)

if not st.session_state.dados.empty:
    despesas = st.session_state.dados[
        st.session_state.dados["Tipo"] == "Despesa"
    ]["Valor"].sum()

    reserva_ideal = despesas * meses_reserva

    st.info(f"Sua reserva ideal é R$ {reserva_ideal:,.2f}")

# ==============================
# 📈 PROJEÇÃO COM CDI
# ==============================
st.markdown("---")
st.header("📈 Projeção de Patrimônio")

meses_proj = st.slider("Projetar por quantos meses?", 1, 120, 24)

if not st.session_state.dados.empty and saldo > 0:

    taxa_mensal = (1 + cdi_anual/100)**(1/12) - 1
    patrimonio = 0
    historico = []

    for i in range(meses_proj):
        patrimonio = (patrimonio + saldo) * (1 + taxa_mensal)
        historico.append(patrimonio)

    df_proj = pd.DataFrame({
        "Mês": range(1, meses_proj + 1),
        "Patrimônio": historico
    })

    fig2 = px.line(df_proj, x="Mês", y="Patrimônio",
                   color_discrete_sequence=["#00C896"])
    st.plotly_chart(fig2, use_container_width=True)

# ==============================
# 🏦 SIMULAÇÃO DE FINANCIAMENTO
# ==============================
st.markdown("---")
st.header("🏦 Simulação de Financiamento (Tabela Price)")

valor_financiado = st.number_input("Valor financiado (R$)", min_value=0.0)
juros_anual = st.number_input("Taxa anual (%)", value=10.0)
parcelas = st.number_input("Número de parcelas", min_value=1, value=60)

if valor_financiado > 0:

    juros_mensal = juros_anual / 100 / 12

    parcela = (valor_financiado * juros_mensal) / (1 - (1 + juros_mensal) ** -parcelas)

    total_pago = parcela * parcelas
    juros_total = total_pago - valor_financiado

    col1, col2, col3 = st.columns(3)
    col1.metric("💳 Parcela", f"R$ {parcela:,.2f}")
    col2.metric("📊 Total Pago", f"R$ {total_pago:,.2f}")
    col3.metric("🏦 Juros Totais", f"R$ {juros_total:,.2f}")

    # Tabela detalhada
    saldo_devedor = valor_financiado
    tabela = []

    for i in range(1, parcelas + 1):
        juros = saldo_devedor * juros_mensal
        amortizacao = parcela - juros
        saldo_devedor -= amortizacao

        tabela.append([i, parcela, juros, amortizacao, max(saldo_devedor, 0)])

    df_tabela = pd.DataFrame(tabela,
        columns=["Parcela", "Valor Parcela", "Juros", "Amortização", "Saldo Devedor"])

    st.dataframe(df_tabela)

st.markdown("---")
st.caption("Banco Digital Finance • Desenvolvido com Streamlit")