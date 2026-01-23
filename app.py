import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="EMBASSERRA | CARGO OS", layout="wide", initial_sidebar_state="expanded")

# --- DESIGN INDUSTRIAL REFINADO (SEM CARA DE IA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}

    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    .sidebar-brand { font-family: 'Syncopate', sans-serif; color: #58a6ff; font-size: 1.1rem; letter-spacing: 3px; padding: 10px 0px; }

    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-top: 4px solid #58a6ff !important;
        border-radius: 4px !important;
        padding: 20px !important;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        padding: 15px;
        text-transform: uppercase;
        transition: 0.3s;
    }

    .section-header {
        font-family: 'Syncopate', sans-serif;
        font-size: 1.3rem;
        color: #f0f6fc;
        border-left: 5px solid #58a6ff;
        padding-left: 15px;
        margin: 30px 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ---
def load_db():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    if os.path.exists(v):
        df_v = pd.read_csv(v)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        df_v = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"])
    return df_p, df_v

def save_db(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = load_db()

# --- SEGURANÇA ---
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align: center; font-family:Syncopate; color:#58a6ff;'>SISTEMA EMBASSERRA</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("gate"):
            pwd = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("AUTORIZAR"):
                if pwd == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<p class="sidebar-brand">EMBASSERRA OS</p>', unsafe_allow_html=True)
    menu = st.radio("MÓDULOS", ["DASHBOARD", "ESTOQUE / EDITAR", "SAÍDA / PLACA", "REGISTROS"])
    st.divider()
    if st.button("BLOQUEAR"):
        st.session_state.clear()
        st.rerun()

# --- DASHBOARD ---
if menu == "DASHBOARD":
    st.markdown('<p class="section-header">Fluxo de Operação</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("FATURAMENTO", f"R$ {st.session_state.vendas['Total'].sum():,.2f}")
    c2.metric("LUCRO", f"R$ {st.session_state.vendas['Lucro'].sum():,.2f}")
    c3.metric("CARGAS", len(st.session_state.vendas))

# --- ESTOQUE / EDITAR (O QUE VOCÊ PEDIU) ---
elif menu == "ESTOQUE / EDITAR":
    st.markdown('<p class="section-header">Gestão de Inventário</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["VER ESTOQUE", "ADICIONAR NOVO", "EDITAR / EXCLUIR"])
    
    with tab1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    
    with tab2:
        with st.form("new_p"):
            n = st.text_input("NOME")
            c1, c2, c3 = st.columns(3)
            pc = c1.number_input("CUSTO", format="%.2f")
            pv = c2.number_input("VENDA", format="%.2f")
            pq = c3.number_input("ESTOQUE", step=1)
            if st.form_submit_button("SALVAR"):
                nid = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 100
                new_row = pd.DataFrame([{"ID": nid, "Nome": n, "Custo": pc, "Venda": pv, "Estoque": pq}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, new_row], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success("ITEM CADASTRADO")
                st.rerun()

    with tab3:
        if not st.session_state.produtos.empty:
            st.write("Selecione um item para modificar os dados:")
            item_edit = st.selectbox("Escolher Item", st.session_state.produtos["Nome"])
            idx = st.session_state.produtos[st.session_state.produtos["Nome"] == item_edit].index[0]
            
            with st.form("edit_p"):
                new_nome = st.text_input("Nome", value=st.session_state.produtos.loc[idx, "Nome"])
                col1, col2, col3 = st.columns(3)
                new_custo = col1.number_input("Custo", value=float(st.session_state.produtos.loc[idx, "Custo"]))
                new_venda = col2.number_input("Venda", value=float(st.session_state.produtos.loc[idx, "Venda"]))
                new_estoque = col3.number_input("Estoque", value=int(st.session_state.produtos.loc[idx, "Estoque"]))
                
                c_btn, d_btn = st.columns(2)
                if c_btn.form_submit_button("ATUALIZAR DADOS"):
                    st.session_state.produtos.at[idx, "Nome"] = new_nome
                    st.session_state.produtos.at[idx, "Custo"] = new_custo
                    st.session_state.produtos.at[idx, "Venda"] = new_venda
                    st.session_state.produtos.at[idx, "Estoque"] = new_estoque
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success("DADOS ATUALIZADOS!")
                    st.rerun()
                
                if d_btn.form_submit_button("🚨 EXCLUIR ITEM"):
                    st.session_state.produtos = st.session_state.produtos.drop(idx)
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.warning("ITEM REMOVIDO!")
                    st.rerun()
        else:
            st.info("Nenhum item para editar.")

# --- SAÍDA ---
elif menu == "SAÍDA / PLACA":
    st.markdown('<p class="section-header">Despacho de Carga</p>', unsafe_allow_html=True)
    prods = st.session_state.produtos["Nome"].tolist()
    if prods:
        with st.container(border=True):
            p_sel = st.selectbox("Produto", prods)
            placa = st.text_input("Placa do Caminhão").upper()
            qtd = st.number_input("Quantidade", min_value=1)
            
            item = st.session_state.produtos[st.session_state.produtos["Nome"] == p_sel].iloc[0]
            total = item['Venda'] * qtd
            
            if st.button("PROCESSAR SAÍDA"):
                if item["Estoque"] >= qtd:
                    v_log = pd.DataFrame([{"Data": datetime.now(), "Produto": p_sel, "Qtd": qtd, "Total": total, "Lucro": (item['Venda']-item['Custo'])*qtd, "Placa": placa}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, v_log], ignore_index=True)
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == p_sel, "Estoque"] -= qtd
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success("VENDA REGISTRADA!")
                    st.rerun()
                else:
                    st.error("ESTOQUE BAIXO")
    else:
        st.warning("Estoque vazio.")

# --- REGISTROS ---
elif menu == "REGISTROS":
    st.markdown('<p class="section-header">Histórico de Saídas</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
