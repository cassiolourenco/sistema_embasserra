import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# 1. CONFIGURAÇÃO MASTER
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide", initial_sidebar_state="expanded")

# 2. CSS INDUSTRIAL SUPREMO (FLECHA AZUL + DESIGN DARK)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}

    /* --- FIX DA FLECHA AZUL (O QUE VOCÊ PEDIU) --- */
    div[data-baseweb="select"] svg {
        fill: #58a6ff !important; 
        color: #58a6ff !important;
        display: block !important;
        visibility: visible !important;
        width: 1.5rem !important;
        height: 1.5rem !important;
    }
    div[data-baseweb="select"] {
        border: 1px solid #30363d !important;
        background-color: #0d1117 !important;
        border-radius: 4px !important;
    }
    /* ------------------------------------------- */

    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-top: 4px solid #58a6ff !important;
        border-radius: 4px !important;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
        color: white !important;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        border: none !important;
        padding: 15px;
        text-transform: uppercase;
    }

    .section-header {
        font-family: 'Syncopate', sans-serif;
        font-size: 1.2rem;
        color: #58a6ff;
        border-left: 5px solid #58a6ff;
        padding-left: 15px;
        margin: 20px 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE DE DADOS
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

# 4. SIDEBAR NAVEGAÇÃO
with st.sidebar:
    st.markdown('<p style="font-family:Syncopate; color:#58a6ff; font-size:20px;">EMBASSERRA</p>', unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO", ["📊 DASHBOARD", "📦 ESTOQUE / EDITAR", "🚛 VENDA / SAÍDA", "📜 REGISTROS"])
    st.divider()
    if st.button("🔒 BLOQUEAR"):
        st.session_state.clear()
        st.rerun()

# 5. MÓDULO: DASHBOARD
if menu == "📊 DASHBOARD":
    st.markdown('<p class="section-header">Performance de Vendas</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    fatur = st.session_state.vendas['Total'].sum()
    lucro = st.session_state.vendas['Lucro'].sum()
    c1.metric("FATURAMENTO", f"R$ {fatur:,.2f}")
    c2.metric("LUCRO", f"R$ {lucro:,.2f}")
    c3.metric("CARGAS", len(st.session_state.vendas))

    if not st.session_state.vendas.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            fig1 = px.area(st.session_state.vendas.sort_values('Data'), x='Data', y='Total', title="Fluxo de Caixa", template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)
        with col_b:
            fig2 = px.pie(st.session_state.vendas, names='Produto', values='Total', hole=0.4, title="Mix de Saída", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

# 6. MÓDULO: ESTOQUE / EDITAR
elif menu == "📦 ESTOQUE / EDITAR":
    st.markdown('<p class="section-header">Gestão de Materiais</p>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["ESTOQUE ATUAL", "NOVO ITEM", "EDITAR / EXCLUIR"])
    
    with t1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    
    with t2:
        with st.form("form_add"):
            n = st.text_input("NOME")
            pc = st.number_input("CUSTO")
            pv = st.number_input("VENDA")
            pq = st.number_input("ESTOQUE", step=1)
            if st.form_submit_button("CADASTRAR"):
                novo = pd.DataFrame([{"ID": len(st.session_state.produtos)+100, "Nome": n, "Custo": pc, "Venda": pv, "Estoque": pq}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success("ITEM SALVO")
                st.rerun()

    with t3:
        if not st.session_state.produtos.empty:
            sel_p = st.selectbox("Selecione para alterar", st.session_state.produtos["Nome"])
            idx = st.session_state.produtos[st.session_state.produtos["Nome"] == sel_p].index[0]
            with st.form("form_edit"):
                en = st.text_input("Nome", st.session_state.produtos.loc[idx, "Nome"])
                ec = st.number_input("Custo", value=float(st.session_state.produtos.loc[idx, "Custo"]))
                ev = st.number_input("Venda", value=float(st.session_state.produtos.loc[idx, "Venda"]))
                ee = st.number_input("Estoque", value=int(st.session_state.produtos.loc[idx, "Estoque"]))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("ATUALIZAR"):
                    st.session_state.produtos.loc[idx, ["Nome", "Custo", "Venda", "Estoque"]] = [en, ec, ev, ee]
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success("OK")
                    st.rerun()
                if b2.form_submit_button("EXCLUIR"):
                    st.session_state.produtos = st.session_state.produtos.drop(idx)
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.rerun()

# 7. MÓDULO: VENDA / SAÍDA (COM A FLECHA!)
elif menu == "🚛 VENDA / SAÍDA":
    st.markdown('<p class="section-header">Terminal de Despacho</p>', unsafe_allow_html=True)
    if st.session_state.produtos.empty:
        st.warning("Estoque vazio")
    else:
        col_a, col_b = st.columns([2, 1])
        prod_v = col_a.selectbox("PRODUTO NO CATÁLOGO", st.session_state.produtos["Nome"])
        placa = col_b.text_input("PLACA").upper()
        qtd = st.number_input("QUANTIDADE", min_value=1, step=1)
        
        item = st.session_state.produtos[st.session_state.produtos["Nome"] == prod_v].iloc[0]
        total = item['Venda'] * qtd
        st.markdown(f"<h1 style='color:#58a6ff;'>TOTAL: R$ {total:,.2f}</h1>", unsafe_allow_html=True)
        
        if st.button("PROCESSAR SAÍDA"):
            if item['Estoque'] >= qtd:
                lucro_v = (item['Venda'] - item['Custo']) * qtd
                nova_v = pd.DataFrame([{"Data": datetime.now(), "Produto": prod_v, "Qtd": qtd, "Total": total, "Lucro": lucro_v, "Placa": placa}])
                st.session_state.vendas = pd.concat([st.session_state.vendas, nova_v], ignore_index=True)
                st.session_state.produtos.loc[st.session_state.produtos["Nome"] == prod_v, "Estoque"] -= qtd
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success("CARGA REGISTRADA!")
                st.rerun()

# 8. MÓDULO: REGISTROS + PDF
elif menu == "📜 REGISTROS":
    st.markdown('<p class="section-header">Histórico de Movimentação</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True)
    
    if not st.session_state.vendas.empty:
        if st.button("GERAR ROMANEIO (PDF)"):
            u = st.session_state.vendas.tail(1).iloc[0]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, "EMBASSERRA - ROMANEIO DE CARGA", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, f"DATA: {u['Data']}", ln=True)
            pdf.cell(200, 10, f"PLACA: {u['Placa']}", ln=True)
            pdf.cell(200, 10, f"MATERIAL: {u['Produto']}", ln=True)
            pdf.cell(200, 10, f"QUANTIDADE: {u['Qtd']}", ln=True)
            st.download_button("BAIXAR PDF", pdf.output(dest='S').encode('latin-1'), "romaneio.pdf")
