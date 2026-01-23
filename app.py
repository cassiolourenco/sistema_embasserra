import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# 1. CONFIGURAÇÃO DO APP
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide", initial_sidebar_state="expanded")

# 2. CSS SUPREMO (FLECHA + DESIGN + BOTÃO SAIR)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');
    
    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }

    /* --- FIX DEFINITIVO DA FLECHA AZUL --- */
    [data-testid="stSelectbox"] svg {
        fill: #58a6ff !important;
        color: #58a6ff !important;
        width: 1.8rem !important;
        height: 1.8rem !important;
        display: inline-block !important;
    }
    div[data-baseweb="select"] {
        border: 1px solid #30363d !important;
        background-color: #0d1117 !important;
    }

    /* CARDS DE MÉTRICA */
    div[data-testid="stMetric"] {
        background: #0d1117;
        border: 1px solid #30363d;
        border-left: 5px solid #58a6ff !important;
        padding: 15px !important;
    }

    /* BOTÕES GERAIS */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
        color: white !important;
        font-family: 'Syncopate', sans-serif;
        border: none !important;
        text-transform: uppercase;
    }

    /* BOTÃO SAIR (VERMELHO) */
    .stButton>button[kind="secondary"] {
        background: linear-gradient(90deg, #da3633, #f85149) !important;
        margin-top: 40px !important;
        color: white !important;
        border: none !important;
    }

    h1, h2, h3 { font-family: 'Syncopate', sans-serif; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE DE DADOS (DATABASE)
def load_db():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    df_v = pd.read_csv(v) if os.path.exists(v) else pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"])
    if not df_v.empty: 
        df_v['Data'] = pd.to_datetime(df_v['Data'], errors='coerce')
    return df_p, df_v

def save_db(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = load_db()

# 4. SIDEBAR COM MENU E SAIR
with st.sidebar:
    st.markdown("### 📦 EMBASSERRA LOG")
    menu = st.radio("NAVEGAÇÃO", ["DASHBOARD", "ESTOQUE", "VENDAS", "HISTÓRICO"])
    
    st.divider()
    # Botão de Sair com estilo secundário para ativar o CSS vermelho
    if st.button("SAIR DO SISTEMA", kind="secondary"):
        st.session_state.clear()
        st.rerun()

# 5. DASHBOARD (COM TODOS OS GRÁFICOS)
if menu == "DASHBOARD":
    st.title("📊 PERFORMANCE")
    v = st.session_state.vendas
    if not v.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("FATURAMENTO", f"R$ {v['Total'].sum():,.2f}")
        c2.metric("LUCRO", f"R$ {v['Lucro'].sum():,.2f}")
        c3.metric("TRANSAÇÕES", len(v))
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(px.pie(v, names='Produto', values='Total', hole=0.5, template="plotly_dark", title="Mix de Saída"), use_container_width=True)
        with col_b:
            v_day = v.groupby(v['Data'].dt.date)['Total'].sum().reset_index()
            st.plotly_chart(px.line(v_day, x='Data', y='Total', title="Evolução Financeira", template="plotly_dark"), use_container_width=True)
    else:
        st.info("Aguardando primeiras vendas...")

# 6. ESTOQUE (COM EDITAR E EXCLUIR)
elif menu == "ESTOQUE":
    st.title("📦 GESTÃO DE MATERIAIS")
    t1, t2, t3 = st.tabs(["LISTA ATUAL", "NOVO MATERIAL", "EDITAR / EXCLUIR"])
    
    with t1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    
    with t2:
        with st.form("add"):
            n = st.text_input("NOME DO MATERIAL")
            c, v = st.columns(2)
            custo = c.number_input("CUSTO UNITÁRIO")
            venda = v.number_input("PREÇO DE VENDA")
            qtd = st.number_input("ESTOQUE INICIAL", step=1)
            if st.form_submit_button("CADASTRAR"):
                novo = pd.DataFrame([{"ID": len(st.session_state.produtos)+1, "Nome": n, "Custo": custo, "Venda": venda, "Estoque": qtd}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.rerun()

    with t3:
        if not st.session_state.produtos.empty:
            sel = st.selectbox("QUAL ITEM DESEJA ALTERAR?", st.session_state.produtos["Nome"])
            idx = st.session_state.produtos[st.session_state.produtos["Nome"] == sel].index[0]
            with st.form("edit"):
                en = st.text_input("Nome", st.session_state.produtos.loc[idx, "Nome"])
                ev = st.number_input("Venda", value=float(st.session_state.produtos.loc[idx, "Venda"]))
                ee = st.number_input("Estoque", value=int(st.session_state.produtos.loc[idx, "Estoque"]))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("SALVAR"):
                    st.session_state.produtos.loc[idx, ["Nome", "Venda", "Estoque"]] = [en, ev, ee]
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.rerun()
                if b2.form_submit_button("EXCLUIR"):
                    st.session_state.produtos = st.session_state.produtos.drop(idx)
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.rerun()

# 7. VENDAS (FOCO NA OPERAÇÃO)
elif menu == "VENDAS":
    st.title("🚛 TERMINAL DE SAÍDA")
    if not st.session_state.produtos.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            prod = st.selectbox("SELECIONAR MATERIAL", st.session_state.produtos["Nome"])
        with col2:
            placa = st.text_input("PLACA DO VEÍCULO").upper()
        
        qtd_v = st.number_input("QUANTIDADE", min_value=1, step=1)
        
        item = st.session_state.produtos[st.session_state.produtos["Nome"] == prod].iloc[0]
        total = item['Venda'] * qtd_v
        st.markdown(f"<h1 style='text-align: center;'>TOTAL: R$ {total:,.2f}</h1>", unsafe_allow_html=True)
        
        if st.button("CONFIRMAR DESPACHO"):
            if item['Estoque'] >= qtd_v:
                luc = (item['Venda'] - item['Custo']) * qtd_v
                nv = pd.DataFrame([{"Data": datetime.now(), "Produto": prod, "Qtd": qtd_v, "Total": total, "Lucro": luc, "Placa": placa}])
                st.session_state.vendas = pd.concat([st.session_state.vendas, nv], ignore_index=True)
                st.session_state.produtos.loc[st.session_state.produtos["Nome"] == prod, "Estoque"] -= qtd_v
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success("REGISTRADO!")
                st.rerun()
            else: st.error("SEM ESTOQUE!")

# 8. HISTÓRICO
elif menu == "HISTÓRICO":
    st.title("📜 REGISTROS")
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True)
