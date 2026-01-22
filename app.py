import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Embasserra Embalagens - ERP", layout="wide", page_icon="📦")

# CSS Ajustado
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    div[data-testid="stMetricValue"] { color: #58a6ff !important; font-weight: 700; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN PRIVADO ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    senha = col.text_input("Chave de Segurança", type="password")
    if col.button("Acessar Sistema"):
        if senha == "admin123":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# --- GESTÃO DE DADOS ---
def carregar_dados():
    cols_p = ["ID", "Nome", "Custo", "Venda", "Estoque"]
    cols_v = ["Data", "Produto", "Qtd", "Total", "Lucro"]
    
    df_p = pd.read_csv("produtos.csv") if os.path.exists("produtos.csv") else pd.DataFrame(columns=cols_p)
    if os.path.exists("vendas.csv"):
        df_v = pd.read_csv("vendas.csv")
        df_v['Data'] = pd.to_datetime(df_v['Data'], errors='coerce')
    else:
        df_v = pd.DataFrame(columns=cols_v)
    return df_p, df_v

def salvar(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state or 'vendas' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = carregar_dados()

# --- FUNÇÃO DO PDF ---
def gerar_pdf_romaneio(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt="EMBASSERRA EMBALAGENS", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, txt="ROMANEIO DE CARGA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.cell(190, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(90, 10, "Produto", border=1)
    pdf.cell(40, 10, "Qtd", border=1)
    pdf.cell(60, 10, "Total (R$)", border=1, ln=True)
    pdf.set_font("Arial", size=11)
    for _, row in dados.iterrows():
        pdf.cell(90, 10, str(row['Produto']), border=1)
        pdf.cell(40, 10, str(row['Qtd']), border=1)
        pdf.cell(60, 10, f"{row['Total']:.2f}", border=1, ln=True)
    pdf.ln(20)
    pdf.cell(190, 10, txt="_______________________________________", ln=True, align='C')
    pdf.cell(190, 10, txt="Assinatura do Recebedor", ln=True, align='C')
    return pdf.output()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("EMBASSERRA")
    menu = st.radio("Módulos", ["📈 Painel", "📦 Estoque", "🛒 Vendas", "📑 Relatórios"])

# --- LÓGICA ---
if menu == "📈 Painel":
    st.title("Resumo Operacional")
    c1, c2 = st.columns(2)
    c1.metric("Faturamento", f"R$ {st.session_state.vendas['Total'].sum():,.2f}")
    c2.metric("Vendas Hoje", len(st.session_state.vendas))

elif menu == "📦 Estoque":
    st.title("Estoque")
    st.dataframe(st.session_state.produtos, width=2000) # Ajustado conforme logs [cite: 132]
    with st.expander("Cadastrar"):
        n = st.text_input("Nome")
        c_val = st.number_input("Custo", 0.0)
        v_val = st.number_input("Venda", 0.0)
        e_val = st.number_input("Qtd", 0)
        if st.button("Salvar"):
            novo = pd.DataFrame([{"ID": 1, "Nome": n, "Custo": c_val, "Venda": v_val, "Estoque": e_val}])
            st.session_state.produtos = pd.concat([st.session_state.produtos, novo], ignore_index=True)
            salvar(st.session_state.produtos, st.session_state.vendas)
            st.rerun()

elif menu == "🛒 Vendas":
    st.title("PDV")
    if not st.session_state.produtos.empty:
        p_sel = st.selectbox("Produto", st.session_state.produtos["Nome"])
        q_sel = st.number_input("Qtd", 1)
        if st.button("Vender"):
            venda = pd.DataFrame([{"Data": datetime.now(), "Produto": p_sel, "Qtd": q_sel, "Total": 0, "Lucro": 0}])
            st.session_state.vendas = pd.concat([st.session_state.vendas, venda], ignore_index=True)
            salvar(st.session_state.produtos, st.session_state.vendas)
            st.success("Venda registrada!")

elif menu == "📑 Relatórios":
    st.title("Relatórios")
    st.dataframe(st.session_state.vendas, width=2000)
    if not st.session_state.vendas.empty:
        if st.button("📦 Gerar PDF da Última Carga"):
            pdf_data = gerar_pdf_romaneio(st.session_state.vendas.tail(1))
            st.download_button("📥 Baixar Romaneio", pdf_data, "romaneio.pdf", "application/pdf")
