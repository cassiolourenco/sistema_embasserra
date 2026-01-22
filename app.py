import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# --- SETUP DE ELITE ---
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide")

# --- DESIGN "TOTALMENTE FODA" (CSS CUSTOM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap');

    /* Fundo com Gradiente Dinâmico */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f8fafc;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Sidebar Estilo Industrial */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 2px solid #334155;
    }

    /* Títulos em Neon */
    h1, h2, h3 {
        font-family: 'Syncopate', sans-serif;
        text-transform: uppercase;
        letter-spacing: 4px;
        background: linear-gradient(90deg, #fff, #64748b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Cards Neo-Brutalistas */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5);
        border: 2px solid #334155;
        border-radius: 0px !important; /* Estilo quadrado industrial */
        padding: 30px !important;
        box-shadow: 10px 10px 0px #000; /* Sombra brutalista */
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translate(-5px, -5px);
        box-shadow: 15px 15px 0px #3b82f6;
        border-color: #3b82f6;
    }

    /* Inputs Estilizados */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #0f172a !important;
        border: 2px solid #334155 !important;
        border-radius: 0px !important;
        color: #3b82f6 !important;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: bold;
    }

    /* Botão de Ação "Impacto" */
    .stButton>button {
        width: 100%;
        background-color: #f8fafc !important;
        color: #000 !important;
        border: none !important;
        border-radius: 0px !important;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        padding: 20px;
        transition: 0.4s;
        border: 2px solid #fff !important;
    }
    .stButton>button:hover {
        background-color: #000 !important;
        color: #fff !important;
        box-shadow: 8px 8px 0px #3b82f6;
    }

    /* Esconder elementos inúteis */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE ---
def load():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    if os.path.exists(v):
        df_v = pd.read_csv(v)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        df_v = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro"])
    return df_p, df_v

def save(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = load()

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align: center;'>SYSTEM ACCESS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("auth"):
            key = st.text_input("KEY", type="password")
            if st.form_submit_button("ENTER"):
                if key == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1>EMBASSERRA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='letter-spacing:2px; font-size:10px;'>CORE OPERATIONAL SYSTEM</p>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("SELECT MODULE", ["DASHBOARD", "INVENTORY", "TERMINAL", "LOGS"])
    st.divider()
    if st.button("LOGOUT"):
        del st.session_state.autenticado
        st.rerun()

# --- DASHBOARD ---
if menu == "DASHBOARD":
    st.markdown("<h3>Operations Intelligence</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    rev = st.session_state.vendas['Total'].sum()
    pro = st.session_state.vendas['Lucro'].sum()
    
    c1.metric("REVENUE", f"R$ {rev:,.2f}")
    c2.metric("PROFIT", f"R$ {pro:,.2f}")
    c3.metric("TRANSACTIONS", len(st.session_state.vendas))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.vendas.empty:
        fig = px.area(st.session_state.vendas.sort_values('Data'), x='Data', y='Total', title="PERFORMANCE LINE")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', title_font_family="Syncopate")
        fig.update_traces(line_color='#3b82f6', fillcolor='rgba(59, 130, 246, 0.2)')
        st.plotly_chart(fig, use_container_width=True)

# --- INVENTORY ---
elif menu == "INVENTORY":
    st.markdown("<h3>Stock Control</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["LIST", "ADD NEW"])
    with t1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    with t2:
        with st.form("add"):
            n = st.text_input("PRODUCT NAME")
            c, v, q = st.columns(3)
            custo = c.number_input("COST", format="%.2f")
            venda = v.number_input("PRICE", format="%.2f")
            qtd = q.number_input("QTY", 0)
            if st.form_submit_button("CONFIRM REGISTRATION"):
                new_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 1001
                new_p = pd.DataFrame([{"ID": new_id, "Nome": n, "Custo": custo, "Venda": venda, "Estoque": qtd}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, new_p], ignore_index=True)
                save(st.session_state.produtos, st.session_state.vendas)
                st.rerun()

# --- TERMINAL ---
elif menu == "TERMINAL":
    st.markdown("<h3>Point of Sale</h3>", unsafe_allow_html=True)
    if not st.session_state.produtos.empty:
        with st.container():
            p_sel = st.selectbox("PRODUCT", st.session_state.produtos["Nome"])
            q_sel = st.number_input("QUANTITY", 1)
            p_data = st.session_state.produtos[st.session_state.produtos["Nome"] == p_sel].iloc[0]
            total = p_data['Venda'] * q_sel
            
            st.markdown(f"<h1 style='-webkit-text-fill-color: #3b82f6;'>TOTAL: R$ {total:,.2f}</h1>", unsafe_allow_html=True)
            
            if st.button("EXECUTE SALE"):
                if p_data["Estoque"] >= q_sel:
                    log = pd.DataFrame([{"Data": datetime.now(), "Produto": p_sel, "Qtd": q_sel, "Total": total, "Lucro": (p_data['Venda']-p_data['Custo'])*q_sel}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, log], ignore_index=True)
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == p_sel, "Estoque"] -= q_sel
                    save(st.session_state.produtos, st.session_state.vendas)
                    st.success("SUCCESSFUL TRANSACTION")
                    st.rerun()

# --- LOGS ---
elif menu == "LOGS":
    st.markdown("<h3>Archives</h3>", unsafe_allow_html=True)
    st.dataframe(st.session_state.vendas, use_container_width=True, hide_index=True)
    if not st.session_state.vendas.empty:
        if st.button("GENERATE ROMANEIO PDF"):
            u = st.session_state.vendas.tail(1).iloc[0]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 16)
            pdf.cell(190, 10, "EMBASSERRA ROMANEIO", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Helvetica", size=12)
            pdf.cell(190, 10, f"PRODUTO: {u['Produto']} | QTD: {u['Qtd']} | TOTAL: R$ {u['Total']:.2f}", ln=True)
            st.download_button("DOWNLOAD PDF", bytes(pdf.output()), "romaneio.pdf", "application/pdf")
