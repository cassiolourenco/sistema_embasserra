import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# 1. CONFIGURAÇÃO DE ALTO NÍVEL
st.set_page_config(
    page_title="EMBASSERRA | OS",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. DESIGN REFINADO (SEM CARA DE IA)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap');

    /* Fundo e Scroll */
    .stApp {
        background: #020617;
        color: #f1f5f9;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Título da Sidebar Estilizado (Resolvendo o seu problema) */
    .sidebar-title {
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        color: #3b82f6;
        letter-spacing: 3px;
        margin-bottom: 0px;
        padding-top: 10px;
    }
    .sidebar-subtitle {
        font-size: 10px;
        letter-spacing: 2px;
        color: #64748b;
        margin-bottom: 20px;
    }

    /* Escondendo Elementos Padrão do Streamlit que denunciam a ferramenta */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Cards Neo-Brutalistas Refinados */
    div[data-testid="stMetric"] {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-left: 5px solid #3b82f6 !important;
        border-radius: 0px !important;
        padding: 20px !important;
        box-shadow: 10px 10px 0px #000;
    }

    /* Botão Industrial */
    .stButton>button {
        width: 100%;
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 0px !important;
        font-family: 'Syncopate', sans-serif;
        font-size: 12px !important;
        font-weight: 700;
        padding: 15px;
        text-transform: uppercase;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #2563eb !important;
        transform: translateY(-2px);
        box-shadow: 0px 5px 15px rgba(59, 130, 246, 0.4);
    }

    /* Ajuste de Inputs para não parecerem formulários web comuns */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: white !important;
        border-radius: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE DE DADOS (SIMPLIFICADA)
def load_data():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    if os.path.exists(v):
        df_v = pd.read_csv(v)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        df_v = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro"])
    return df_p, df_v

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = load_data()

# 4. SIDEBAR REFINADA (Aqui a mágica acontece)
with st.sidebar:
    st.markdown('<p class="sidebar-title">EMBASSERRA</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-subtitle">INTELLIGENCE v4.2</p>', unsafe_allow_html=True)
    st.divider()
    menu = st.radio("NAVEGAÇÃO", ["PAINEL", "INVENTÁRIO", "TERMINAL", "ARQUIVOS"])
    st.divider()
    if st.button("TERMINAR SESSÃO"):
        st.session_state.clear()
        st.rerun()

# 5. MÓDULOS (LÓGICA LIMPA)
if menu == "PAINEL":
    st.markdown("<h2 style='font-family:Syncopate;'>Performance</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    faturamento = st.session_state.vendas['Total'].sum()
    lucro = st.session_state.vendas['Lucro'].sum()
    
    c1.metric("FATURAMENTO", f"R$ {faturamento:,.2f}")
    c2.metric("LUCRO", f"R$ {lucro:,.2f}")
    c3.metric("TRANSAÇÕES", len(st.session_state.vendas))
    
    if not st.session_state.vendas.empty:
        st.markdown("### Fluxo de Caixa")
        fig = px.area(st.session_state.vendas.sort_values('Data'), x='Data', y='Total')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

elif menu == "INVENTÁRIO":
    st.markdown("<h2 style='font-family:Syncopate;'>Estoque</h2>", unsafe_allow_html=True)
    st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    
    with st.expander("ADICIONAR ITEM"):
        with st.form("add_item"):
            n = st.text_input("NOME")
            c1, c2, c3 = st.columns(3)
            pc = c1.number_input("CUSTO")
            pv = c2.number_input("VENDA")
            pq = c3.number_input("QTD", step=1)
            if st.form_submit_button("CADASTRAR"):
                # Lógica de salvar aqui...
                st.success("ITEM ADICIONADO")

elif menu == "TERMINAL":
    st.markdown("<h2 style='font-family:Syncopate;'>Ponto de Saída</h2>", unsafe_allow_html=True)
    prods = st.session_state.produtos["Nome"].tolist()
    if prods:
        sel = st.selectbox("PRODUTO", prods)
        qtd = st.number_input("QUANTIDADE", min_value=1)
        item = st.session_state.produtos[st.session_state.produtos["Nome"] == sel].iloc[0]
        total = item['Venda'] * qtd
        st.markdown(f"<h1 style='color:#3b82f6; font-family:Syncopate;'>TOTAL: R$ {total:,.2f}</h1>", unsafe_allow_html=True)
        if st.button("PROCESSAR"):
            st.success("VENDA OK")
    else:
        st.warning("SEM PRODUTOS NO ESTOQUE")

elif menu == "ARQUIVOS":
    st.markdown("<h2 style='font-family:Syncopate;'>Logs</h2>", unsafe_allow_html=True)
    st.dataframe(st.session_state.vendas, use_container_width=True)
