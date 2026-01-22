import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Embasserra Embalagens - ERP", layout="wide", page_icon="📦")

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
    
    if os.path.exists("produtos.csv"):
        df_p = pd.read_csv("produtos.csv")
    else:
        df_p = pd.DataFrame(columns=cols_p)
        
    if os.path.exists("vendas.csv"):
        df_v = pd.read_csv("vendas.csv")
        df_v['Data'] = pd.to_datetime(df_v['Data'], errors='coerce')
    else:
        df_v = pd.DataFrame(columns=cols_v)
        
    return df_p, df_v

def salvar(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

# Inicializa os dados
if 'produtos' not in st.session_state or 'vendas' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = carregar_dados()

# --- FUNÇÃO DO PDF (ROMANEIO) ---
def gerar_pdf_romaneio(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="EMBASSERRA EMBALAGENS", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="ROMANEIO DE CARGA", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 10, "Produto", border=1)
    pdf.cell(40, 10, "Qtd", border=1)
    pdf.cell(50, 10, "Total (R$)", border=1, ln=True)
    
    pdf.set_font("Arial", size=11)
    for _, row in dados.iterrows():
        pdf.cell(100, 10, str(row['Produto']), border=1)
        pdf.cell(40, 10, str(row['Qtd']), border=1)
        pdf.cell(50, 10, f"{row['Total']:.2f}", border=1, ln=True)
    
    pdf.ln(20)
    pdf.cell(200, 10, txt="_______________________________________", ln=True, align='C')
    pdf.cell(200, 10, txt="Assinatura do Recebedor", ln=True, align='C')
    return pdf.output()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("EMBASSERRA")
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    st.divider()
    menu = st.radio("Módulos", ["📈 Painel", "📦 Estoque", "🛒 Vendas", "📑 Relatórios"])
    if st.button("Sair"):
        del st.session_state.autenticado
        st.rerun()

# --- LÓGICA DOS MÓDULOS ---
if menu == "📈 Painel":
    st.title("Resumo")
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento", f"R$ {st.session_state.vendas['Total'].sum():,.2f}")
    c2.metric("Estoque Total", int(st.session_state.produtos['Estoque'].sum()))
    c3.metric("Vendas Hoje", len(st.session_state.vendas))

elif menu == "📦 Estoque":
    st.title("Estoque")
    st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    with st.expander("Novo Produto"):
        n = st.text_input("Nome")
        c, v, e = st.columns(3)
        custo = c.number_input("Custo", 0.0)
        venda = v.number_input("Venda", 0.0)
        qtd = e.number_input("Qtd", 0)
        if st.button("Cadastrar"):
            novo_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 1001
            item = pd.DataFrame([{"ID": novo_id, "Nome": n, "Custo": custo, "Venda": venda, "Estoque": qtd}])
            st.session_state.produtos = pd.concat([st.session_state.produtos, item], ignore_index=True)
            salvar(st.session_state.produtos, st.session_state.vendas)
            st.rerun()

elif menu == "🛒 Vendas":
    st.title("PDV")
    if st.session_state.produtos.empty:
        st.info("Cadastre produtos no estoque.")
    else:
        p_nome = st.selectbox("Produto", st.session_state.produtos["Nome"])
        p_qtd = st.number_input("Qtd", 1)
        p_dados = st.session_state.produtos[st.session_state.produtos["Nome"] == p_nome].iloc[0]
        if st.button("Finalizar Venda"):
            if p_dados["Estoque"] >= p_qtd:
                venda = pd.DataFrame([{"Data": datetime.now(), "Produto": p_nome, "Qtd": p_qtd, "Total": p_dados['Venda']*p_qtd, "Lucro": (p_dados['Venda']-p_dados['Custo'])*p_qtd}])
                st.session_state.vendas = pd.concat([st.session_state.vendas, venda], ignore_index=True)
                st.session_state.produtos.loc[st.session_state.produtos["Nome"] == p_nome, "Estoque"] -= p_qtd
                salvar(st.session_state.produtos, st.session_state.vendas)
                st.success("Venda ok!")
                st.rerun()

elif menu == "📑 Relatórios":
    st.title("Relatórios")
    st.dataframe(st.session_state.vendas, use_container_width=True)
    if not st.session_state.vendas.empty:
        if st.button("📦 Gerar PDF da Última Carga"):
            pdf_out = gerar_pdf_romaneio(st.session_state.vendas.tail(1))
            st.download_button("📥 Baixar Romaneio", pdf_out, "romaneio.pdf", "application/pdf")
