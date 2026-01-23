import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# 1. CONFIGURAÇÃO MASTER
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide")

# 2. CSS "TIRO DE CANHÃO" (PARA A FLECHA E O DESIGN)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    /* Fundo e Fonte Geral */
    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    
    /* --- A MALDITA FLECHA (FIX SUPREMO) --- */
    /* Isso aqui busca qualquer ícone de seta nos selects e força a cor */
    svg[viewBox="0 0 24 24"], svg path, [data-testid="stIconMaterial"] {
        fill: #58a6ff !important;
        color: #58a6ff !important;
        stroke: #58a6ff !important;
        display: block !important;
    }
    
    /* Forçando o container da seta a ser visível */
    div[data-baseweb="select"] [pointer-events="none"] {
        display: block !important;
        opacity: 1 !important;
    }

    /* Estilo do Campo */
    div[data-baseweb="select"] {
        border: 1px solid #30363d !important;
        background-color: #0d1117 !important;
    }

    /* Botão Estilizado */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
        color: white !important;
        font-family: 'Syncopate', sans-serif;
        border: none !important;
        padding: 10px;
        text-transform: uppercase;
    }

    h1, h2, h3 { font-family: 'Syncopate', sans-serif; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# 3. BANCO DE DADOS
def load_db():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    df_v = pd.read_csv(v) if os.path.exists(v) else pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"])
    return df_p, df_v

def save_db(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

st.session_state.produtos, st.session_state.vendas = load_db()

# 4. MENU LATERAL
with st.sidebar:
    st.markdown("### EMBASSERRA v2.0")
    menu = st.selectbox("NAVEGAÇÃO", ["DASHBOARD", "ESTOQUE", "VENDAS", "HISTÓRICO"])

# 5. DASHBOARD COMPLETO (VOLTOU TUDO)
if menu == "DASHBOARD":
    st.title("PERFORMANCE")
    v = st.session_state.vendas
    if not v.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("FATURAMENTO", f"R$ {v['Total'].sum():,.2f}")
        c2.metric("LUCRO", f"R$ {v['Lucro'].sum():,.2f}")
        c3.metric("CARGAS", len(v))
        
        col_a, col_b = st.columns(2)
        fig_pie = px.pie(v, names='Produto', values='Total', hole=0.4, template="plotly_dark", title="Mix de Saída")
        col_a.plotly_chart(fig_pie, use_container_width=True)
        
        fig_line = px.line(v, x='Data', y='Total', title="Evolução de Vendas", template="plotly_dark")
        col_b.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Sem dados para exibir.")

# 6. ESTOQUE (COM EDIÇÃO E EXCLUSÃO)
elif menu == "ESTOQUE":
    st.title("MATERIAIS")
    tab1, tab2 = st.tabs(["LISTA", "ADICIONAR/EDITAR"])
    
    with tab1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
        
    with tab2:
        with st.form("estoque_form"):
            nome = st.text_input("NOME DO PRODUTO")
            c1, c2, c3 = st.columns(3)
            custo = c1.number_input("CUSTO")
            venda = c2.number_input("VENDA")
            estoque = c3.number_input("QTD", step=1)
            
            if st.form_submit_button("SALVAR"):
                novo = pd.DataFrame([{"ID": len(st.session_state.produtos)+1, "Nome": nome, "Custo": custo, "Venda": venda, "Estoque": estoque}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.rerun()

# 7. VENDAS (FOCO NA FLECHA)
elif menu == "VENDAS":
    st.title("SAÍDA DE CARGA")
    if st.session_state.produtos.empty:
        st.error("Cadastre produtos no estoque!")
    else:
        # SELECTBOX COM A FLECHA FORÇADA PELO CSS ACIMA
        p_list = st.session_state.produtos["Nome"].tolist()
        escolha = st.selectbox("QUAL O MATERIAL?", p_list)
        
        placa = st.text_input("PLACA DO CAMINHÃO").upper()
        qtd_v = st.number_input("QUANTIDADE", min_value=1, step=1)
        
        item = st.session_state.produtos[st.session_state.produtos["Nome"] == escolha].iloc[0]
        total_v = item['Venda'] * qtd_v
        
        st.markdown(f"## TOTAL: R$ {total_v:,.2f}")
        
        if st.button("CONFIRMAR VENDA"):
            if item['Estoque'] >= qtd_v:
                lucro_v = (item['Venda'] - item['Custo']) * qtd_v
                nova_venda = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Produto": escolha, "Qtd": qtd_v, "Total": total_v, "Lucro": lucro_v, "Placa": placa}])
                st.session_state.vendas = pd.concat([st.session_state.vendas, nova_venda], ignore_index=True)
                st.session_state.produtos.loc[st.session_state.produtos["Nome"] == escolha, "Estoque"] -= qtd_v
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success("VENDA REALIZADA!")
                st.rerun()
            else:
                st.error("ESTOQUE INSUFICIENTE!")

# 8. HISTÓRICO
elif menu == "HISTÓRICO":
    st.title("LOG DE VENDAS")
    st.dataframe(st.session_state.vendas, use_container_width=True)
