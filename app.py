import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide", initial_sidebar_state="expanded")

# --- DESIGN INDUSTRIAL REFINADO ---
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

# --- DASHBOARD (COM GRÁFICOS) ---
if menu == "DASHBOARD":
    st.markdown('<p class="section-header">Análise de Performance</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    faturamento = st.session_state.vendas['Total'].sum()
    lucro = st.session_state.vendas['Lucro'].sum()
    transacoes = len(st.session_state.vendas)
    
    c1.metric("FATURAMENTO TOTAL", f"R$ {faturamento:,.2f}")
    c2.metric("LUCRO LÍQUIDO", f"R$ {lucro:,.2f}")
    c3.metric("TRANSAÇÕES", transacoes)

    if not st.session_state.vendas.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.write("Evolução Financeira")
            fig_evolucao = px.area(st.session_state.vendas.sort_values('Data'), x='Data', y='Total', template="plotly_dark")
            fig_evolucao.update_traces(line_color='#58a6ff', fillcolor='rgba(88, 166, 255, 0.2)')
            fig_evolucao.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_evolucao, use_container_width=True)
            
        with col_graf2:
            st.write("Saída por Produto")
            fig_pizza = px.pie(st.session_state.vendas, names='Produto', values='Total', hole=0.4, template="plotly_dark")
            fig_pizza.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pizza, use_container_width=True)

# --- ESTOQUE / EDITAR ---
elif menu == "ESTOQUE / EDITAR":
    st.markdown('<p class="section-header">Gestão de Inventário</p>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["ESTOQUE ATUAL", "NOVO ITEM", "EDITAR / EXCLUIR"])
    
    with tab1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    
    with tab2:
        with st.form("new_p"):
            n = st.text_input("NOME")
            col_a, col_b, col_c = st.columns(3)
            pc = col_a.number_input("CUSTO (R$)", format="%.2f")
            pv = col_b.number_input("VENDA (R$)", format="%.2f")
            pq = col_c.number_input("QTD INICIAL", step=1)
            if st.form_submit_button("REGISTRAR"):
                nid = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 100
                new_row = pd.DataFrame([{"ID": nid, "Nome": n, "Custo": pc, "Venda": pv, "Estoque": pq}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, new_row], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success("ITEM CADASTRADO!")
                st.rerun()

    with tab3:
        if not st.session_state.produtos.empty:
            sel_edit = st.selectbox("Escolher para Editar", st.session_state.produtos["Nome"])
            idx = st.session_state.produtos[st.session_state.produtos["Nome"] == sel_edit].index[0]
            with st.form("edit_form"):
                enome = st.text_input("Nome", value=st.session_state.produtos.loc[idx, "Nome"])
                ec1, ec2, ec3 = st.columns(3)
                ecusto = ec1.number_input("Custo", value=float(st.session_state.produtos.loc[idx, "Custo"]))
                evenda = ec2.number_input("Venda", value=float(st.session_state.produtos.loc[idx, "Venda"]))
                eestoque = ec3.number_input("Estoque", value=int(st.session_state.produtos.loc[idx, "Estoque"]))
                
                b_att, b_del = st.columns(2)
                if b_att.form_submit_button("ATUALIZAR"):
                    st.session_state.produtos.at[idx, "Nome"] = enome
                    st.session_state.produtos.at[idx, "Custo"] = ecusto
                    st.session_state.produtos.at[idx, "Venda"] = evenda
                    st.session_state.produtos.at[idx, "Estoque"] = eestoque
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success("ATUALIZADO!")
                    st.rerun()
                if b_del.form_submit_button("EXCLUIR"):
                    st.session_state.produtos = st.session_state.produtos.drop(idx)
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.warning("REMOVIDO!")
                    st.rerun()

# --- SAÍDA ---
elif menu == "SAÍDA / PLACA":
    st.markdown('<p class="section-header">Despacho de Carga</p>', unsafe_allow_html=True)
    prods = st.session_state.produtos["Nome"].tolist()
    if prods:
        with st.container(border=True):
            psel = st.selectbox("Produto", prods)
            placa = st.text_input("Placa do Caminhão").upper()
            qsel = st.number_input("Qtd", min_value=1)
            item = st.session_state.produtos[st.session_state.produtos["Nome"] == psel].iloc[0]
            if st.button("CONFIRMAR SAÍDA"):
                if item["Estoque"] >= qsel:
                    val_t = item['Venda'] * qsel
                    v_df = pd.DataFrame([{"Data": datetime.now(), "Produto": psel, "Qtd": qsel, "Total": val_t, "Lucro": (item['Venda']-item['Custo'])*qsel, "Placa": placa}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, v_df], ignore_index=True)
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == psel, "Estoque"] -= qsel
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success("CARGA DESPACHADA!")
                    st.rerun()
                else: st.error("SEM ESTOQUE")

# --- REGISTROS ---
elif menu == "REGISTROS":
    st.markdown('<p class="section-header">Histórico Operacional</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
