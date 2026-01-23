import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide", initial_sidebar_state="expanded")

# 2. CSS (MANTENDO A FLECHA AZUL E O DESIGN)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');
    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    
    /* FIX DA FLECHA AZUL */
    div[data-baseweb="select"] svg {
        fill: #58a6ff !important;
        color: #58a6ff !important;
        width: 1.8rem !important;
        height: 1.8rem !important;
        display: block !important;
        visibility: visible !important;
    }

    div[data-testid="stMetric"] {
        background: #0d1117;
        border: 1px solid #30363d;
        border-left: 5px solid #58a6ff !important;
        padding: 15px !important;
        border-radius: 5px;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
        color: white !important;
        font-family: 'Syncopate', sans-serif;
        border: none !important;
        padding: 12px;
    }

    /* ESTILO DO BOTÃO DE SAIR (VERMELHO) */
    .btn-sair>div>button {
        background: linear-gradient(90deg, #da3633, #f85149) !important;
        margin-top: 50px;
    }

    h1, h2, h3 { font-family: 'Syncopate', sans-serif; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# 3. MOTOR DE DADOS
def load_db():
    p_file, v_file = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p_file) if os.path.exists(p_file) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    df_v = pd.read_csv(v_file) if os.path.exists(v_file) else pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"])
    if not df_v.empty: df_v['Data'] = pd.to_datetime(df_v['Data'])
    return df_p, df_v

def save_db(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = load_db()

# 4. MENU LATERAL COM BOTÃO DE SAIR
with st.sidebar:
    st.markdown("### 📦 EMBASSERRA LOG")
    menu = st.radio("SISTEMA", ["DASHBOARD", "ESTOQUE PROFISSIONAL", "TERMINAL DE VENDAS", "HISTÓRICO COMPLETO"])
    
    st.markdown('<div class="btn-sair">', unsafe_allow_html=True)
    if st.button("SAIR DO SISTEMA"):
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 5. DASHBOARD
if menu == "DASHBOARD":
    st.title("📊 PERFORMANCE")
    v = st.session_state.vendas
    if not v.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("FATURAMENTO", f"R$ {v['Total'].sum():,.2f}")
        c2.metric("LUCRO", f"R$ {v['Lucro'].sum():,.2f}")
        c3.metric("CARGAS", len(v))
        col_left, col_right = st.columns(2)
        with col_left:
            st.plotly_chart(px.pie(v, names='Produto', values='Total', hole=0.5, template="plotly_dark", title="Mix de Produtos"), use_container_width=True)
        with col_right:
            v_agrupada = v.groupby(v['Data'].dt.date)['Total'].sum().reset_index()
            st.plotly_chart(px.line(v_agrupada, x='Data', y='Total', title="Evolução", template="plotly_dark"), use_container_width=True)
    else: st.warning("Sem vendas.")

# 6. ESTOQUE
elif menu == "ESTOQUE PROFISSIONAL":
    st.title("📦 GESTÃO")
    tab1, tab2, tab3 = st.tabs(["ESTOQUE ATUAL", "NOVO MATERIAL", "EDITAR / EXCLUIR"])
    with tab1: st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    with tab2:
        with st.form("add_form"):
            n, c, v, q = st.text_input("NOME"), st.number_input("CUSTO"), st.number_input("VENDA"), st.number_input("ESTOQUE", step=1)
            if st.form_submit_button("CADASTRAR"):
                novo = pd.DataFrame([{"ID": len(st.session_state.produtos)+1, "Nome": n, "Custo": c, "Venda": v, "Estoque": q}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.rerun()
    with tab3:
        if not st.session_state.produtos.empty:
            sel_edit = st.selectbox("ITEM PARA ALTERAR", st.session_state.produtos["Nome"])
            idx = st.session_state.produtos[st.session_state.produtos["Nome"] == sel_edit].index[0]
            with st.form("edit_form"):
                en = st.text_input("Novo Nome", st.session_state.produtos.loc[idx, "Nome"])
                ev = st.number_input("Nova Venda", value=float(st.session_state.produtos.loc[idx, "Venda"]))
                ee = st.number_input("Novo Estoque", value=int(st.session_state.produtos.loc[idx, "Estoque"]))
                if st.form_submit_button("SALVAR ALTERAÇÕES"):
                    st.session_state.produtos.loc[idx, ["Nome", "Venda", "Estoque"]] = [en, ev, ee]
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.rerun()

# 7. VENDAS
elif menu == "TERMINAL DE VENDAS":
    st.title("🚛 SAÍDA")
    if not st.session_state.produtos.empty:
        col_v1, col_v2 = st.columns([2, 1])
        escolha = col_v1.selectbox("PRODUTO EM CATÁLOGO", st.session_state.produtos["Nome"])
        placa = col_v2.text_input("PLACA").upper()
        qtd_venda = st.number_input("QUANTIDADE", min_value=1, step=1)
        item_v = st.session_state.produtos[st.session_state.produtos["Nome"] == escolha].iloc[0]
        total_v = item_v['Venda'] * qtd_venda
        st.markdown(f"<h1 style='text-align: center; color: #58a6ff;'>TOTAL: R$ {total_v:,.2f}</h1>", unsafe_allow_html=True)
        if st.button("CONFIRMAR DESPACHO"):
            if item_v['Estoque'] >= qtd_venda:
                luc_v = (item_v['Venda'] - item_v['Custo']) * qtd_venda
                nova_v = pd.DataFrame([{"Data": datetime.now(), "Produto": escolha, "Qtd": qtd_venda, "Total": total_v, "Lucro": luc_v, "Placa": placa}])
                st.session_state.vendas = pd.concat([st.session_state.vendas, nova_v], ignore_index=True)
                st.session_state.produtos.loc[st.session_state.produtos["Nome"] == escolha, "Estoque"] -= qtd_venda
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.rerun()
            else: st.error("SEM ESTOQUE!")

# 8. HISTÓRICO
elif menu == "HISTÓRICO COMPLETO":
    st.title("📜 REGISTROS")
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
