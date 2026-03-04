import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ==============================
# Configuração da página
# ==============================
st.set_page_config(page_title="Banco Digital Finance", layout="wide")

# ==============================
# Estilo Dark Fintech
# ==============================
st.markdown("""
<style>
body {background-color: #0E1117; color: white;}
.block-container {padding-top: 2rem;}
div[data-testid="metric-container"] {
    background-color: #1C1F26;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏦 Banco Digital Finance")

# ==============================
# Sessão inicial
# ==============================
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "Tipo", "Descricao", "Valor", "Data", "Recorrencia"
    ])

# ==============================
# Sidebar - Cadastro
# ==============================
st.sidebar.header("➕ Nova Transação")

tipo = st.sidebar.selectbox("Tipo", ["Receita", "Despesa"])
descricao = st.sidebar.text_input("Descrição")
valor = st.sidebar.number_input("Valor", min_value=0.0, step=0.01)
data = st.sidebar.date_input("Data", datetime.today())
recorrencia = st.sidebar.selectbox("Recorrência", ["Única vez", "Mensal"])

if st.sidebar.button("Adicionar"):
    nova = pd.DataFrame([{
        "Tipo": tipo,
        "Descricao": descricao,
        "Valor": valor,
        "Data": pd.to_datetime(data),
        "Recorrencia": recorrencia
    }])
    st.session_state.dados = pd.concat([st.session_state.dados, nova], ignore_index=True)
    st.sidebar.success("Transação adicionada!")

# ==============================
# Upload CSV
# ==============================
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Importar CSV")
arquivo = st.sidebar.file_uploader("Envie um CSV", type=["csv"])
if arquivo:
    df_upload = pd.read_csv(arquivo)
    st.session_state.dados = pd.concat([st.session_state.dados, df_upload], ignore_index=True)
    st.sidebar.success("Arquivo importado!")

# ==============================
# Função para gerar recorrências
# ==============================
def gerar_recorrencias(df, meses=12):
    todas_transacoes = []
    for idx, row in df.iterrows():
        data = row["Data"]
        for m in range(meses):
            if row["Recorrencia"] == "Mensal":
                transacao = row.copy()
                transacao["Data"] = data + relativedelta(months=m)
                todas_transacoes.append(transacao)
            else:
                todas_transacoes.append(row)
    return pd.DataFrame(todas_transacoes)

# ==============================
# Processamento dos dados
# ==============================
meses_proj = st.sidebar.slider("Projetar quantos meses?", 1, 120, 12)

if not st.session_state.dados.empty:
    df = st.session_state.dados.copy()
    df_expandido = gerar_recorrencias(df, meses_proj)
    df_expandido["Mes"] = df_expandido["Data"].dt.to_period("M").astype(str)
    resumo_mensal = df_expandido.groupby(["Mes","Tipo"])["Valor"].sum().unstack().fillna(0)
    resumo_mensal["Saldo"] = resumo_mensal.get("Receita",0) - resumo_mensal.get("Despesa",0)

# ==============================
# Dashboard
# ==============================
st.markdown("## 📊 Dashboard Mensal")
if not st.session_state.dados.empty:
    receitas = df_expandido[df_expandido["Tipo"]=="Receita"]["Valor"].sum()
    despesas = df_expandido[df_expandido["Tipo"]=="Despesa"]["Valor"].sum()
    saldo_total = receitas - despesas

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Receitas", f"R$ {receitas:,.2f}")
    col2.metric("💸 Despesas", f"R$ {despesas:,.2f}")
    col3.metric("📈 Saldo Total", f"R$ {saldo_total:,.2f}")

    fig = px.bar(resumo_mensal.reset_index(), x="Mes", y=["Receita","Despesa"], barmode="group",
                 color_discrete_sequence=["#00C896","#FF4B4B"])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 💹 Saldo Mensal")
    fig2 = px.line(resumo_mensal.reset_index(), x="Mes", y="Saldo", color_discrete_sequence=["#00C896"])
    st.plotly_chart(fig2, use_container_width=True)

# ==============================
# Metas Financeiras
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
# Reserva de Emergência
# ==============================
st.markdown("---")
st.header("🛟 Reserva de Emergência")
meses_reserva = st.slider("Meses de segurança", 3, 12, 6)
if not st.session_state.dados.empty:
    despesas_mensais = resumo_mensal["Despesa"].mean()
    reserva_ideal = despesas_mensais * meses_reserva
    st.info(f"Sua reserva ideal é R$ {reserva_ideal:,.2f}")

# ==============================
# Projeção CDI
# ==============================
st.markdown("---")
st.header("📈 Projeção de Patrimônio com CDI")
if not st.session_state.dados.empty:
    saldo_mensal = resumo_mensal["Saldo"].mean()
    patrimonio = 0
    historico = []
    for i in range(meses_proj):
        patrimonio = (patrimonio + saldo_mensal) * (1 + taxa_mensal)
        historico.append(patrimonio)
    df_proj = pd.DataFrame({"Mês": range(1, meses_proj+1), "Patrimônio": historico})
    fig3 = px.line(df_proj, x="Mês", y="Patrimônio", color_discrete_sequence=["#00C896"])
    st.plotly_chart(fig3, use_container_width=True)

# ==============================
# Simulação de Financiamento
# ==============================
st.markdown("---")
st.header("🏦 Simulação de Financiamento (Tabela Price)")
valor_financiado = st.number_input("Valor financiado (R$)", min_value=0.0)
juros_anual = st.number_input("Taxa anual (%)", value=10.0)
parcelas = st.number_input("Número de parcelas", min_value=1, value=60)

if valor_financiado > 0:
    juros_mensal = juros_anual/100/12
    parcela = (valor_financiado*juros_mensal)/(1-(1+juros_mensal)**-parcelas)
    total_pago = parcela*parcelas
    juros_total = total_pago-valor_financiado
    col1, col2, col3 = st.columns(3)
    col1.metric("💳 Parcela", f"R$ {parcela:,.2f}")
    col2.metric("📊 Total Pago", f"R$ {total_pago:,.2f}")
    col3.metric("🏦 Juros Totais", f"R$ {juros_total:,.2f}")

    # Tabela detalhada
    saldo_devedor = valor_financiado
    tabela = []
    for i in range(1, parcelas+1):
        juros = saldo_devedor*juros_mensal
        amortizacao = parcela-juros
        saldo_devedor -= amortizacao
        tabela.append([i, parcela, juros, amortizacao, max(saldo_devedor,0)])
    df_tabela = pd.DataFrame(tabela, columns=["Parcela","Valor Parcela","Juros","Amortização","Saldo Devedor"])
    st.dataframe(df_tabela)

st.markdown("---")
st.caption("Banco Digital Finance • Desenvolvido com Streamlit")
