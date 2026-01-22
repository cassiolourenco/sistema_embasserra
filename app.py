import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px # Adiciona gráficos profissionais

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="EMBASSERRA | Intelligence ERP", layout="wide", page_icon="💎")

# --- DESIGN TOTALMENTE FODA (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0b0e14; color: #e6edf3; }
    
    /* Sidebar Futurista */
    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #30363d;
        padding-top: 2rem;
    }
    
    /* Cards de Métricas Neon */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        padding: 25px !important;
        border-radius: 16px;
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #58a6ff;
        transform: translateY(-5px);
    }
    
    /* Botões Pica */
    .stButton>button {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        border: none;
        color: white;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.5s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(46, 160, 67, 0.4);
        transform: scale(1.02);
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: white !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE DADOS (BLINDADO) ---
def load_data():
    p_file, v_file = "produtos.csv", "vendas.csv"
    p_cols = ["ID", "Nome", "Custo", "Venda", "Estoque"]
    v_cols = ["Data", "Produto", "Qtd", "Total", "Lucro"]
    
    df_p = pd.read_csv(p_file) if os.path.exists(p_file) else pd.DataFrame(columns=p_cols)
    if os.path.exists(v_file):
        df_v = pd.read_csv(v_file)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        df_v = pd.DataFrame(columns=v_cols)
    return df_p, df_v

def save_data(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = load_data()

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align: center; color: #58a6ff;'>💎 EMBASSERRA OS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("auth"):
            key = st.text_input("Security Key", type="password")
            if st.form_submit_button("UNLOCK SYSTEM"):
                if key == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Acesso Negado")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #58a6ff;'>COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.write(f"Operador: Admin | {datetime.now().strftime('%H:%M')}")
    st.divider()
    menu = st.radio("SISTEMA", ["🚀 Dashboard", "📦 Inventário", "💳 Checkout PDV", "📜 Logs & Romaneio"])
    st.divider()
    if st.button("LOCK SYSTEM"):
        del st.session_state.autenticado
        st.rerun()

# --- LÓGICA DO DASHBOARD ---
if menu == "🚀 Dashboard":
    st.title("🚀 Business Intelligence")
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    total_vendas = st.session_state.vendas['Total'].sum()
    total_lucro = st.session_state.vendas['Lucro'].sum()
    item_mais_vendido = st.session_state.vendas['Produto'].mode()[0] if not st.session_state.vendas.empty else "N/A"
    
    k1.metric("Faturamento Global", f"R$ {total_vendas:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
    k2.metric("Net Profit (Lucro)", f"R$ {total_lucro:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
    k3.metric("Volume de Saída", f"{st.session_state.vendas['Qtd'].sum()} un")
    k4.metric("Top Product", item_mais_vendido)
    
    st.divider()
    
    # Gráfico de Vendas Profissional
    if not st.session_state.vendas.empty:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📈 Curva de Faturamento")
            fig = px.area(st.session_state.vendas, x='Data', y='Total', color_discrete_sequence=['#58a6ff'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("📊 Mix de Produtos")
            fig2 = px.pie(st.session_state.vendas, names='Produto', values='Total', hole=.4, color_discrete_sequence=px.colors.sequential.Blues_r)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

# --- INVENTÁRIO ---
elif menu == "📦 Inventário":
    st.title("📦 Gestão de Ativos")
    tab_list, tab_cad = st.tabs(["📋 Estoque Ativo", "➕ Cadastrar Embalagem"])
    
    with tab_list:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
        
    with tab_cad:
        with st.container(border=True):
            n = st.text_input("Nome da Embalagem")
            c1, c2, c3 = st.columns(3)
            custo = c1.number_input("Custo Unitário (R$)", step=0.01, format="%.2f")
            venda = c2.number_input("Venda Unitária (R$)", step=0.01, format="%.2f")
            qtd = c3.number_input("Qtd Inicial", 0)
            if st.button("EFETIVAR CADASTRO"):
                new_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 1001
                new_row = pd.DataFrame([{"ID": new_id, "Nome": n, "Custo": custo, "Venda": venda, "Estoque": qtd}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, new_row], ignore_index=True)
                save_data(st.session_state.produtos, st.session_state.vendas)
                st.success("Produto Integrado ao Sistema!")
                st.rerun()

# --- PDV ---
elif menu == "💳 Checkout PDV":
    st.title("💳 Terminal de Vendas")
    if st.session_state.produtos.empty:
        st.warning("Estoque Vazio. Cadastre produtos primeiro.")
    else:
        col_v, col_r = st.columns([1, 1])
        with col_v:
            with st.container(border=True):
                p_nome = st.selectbox("Selecionar Item", st.session_state.produtos["Nome"])
                p_qtd = st.number_input("Quantidade de Saída", 1)
                
                p_info = st.session_state.produtos[st.session_state.produtos["Nome"] == p_nome].iloc[0]
                total = p_info['Venda'] * p_qtd
                lucro = (p_info['Venda'] - p_info['Custo']) * p_qtd
                
                st.markdown(f"<h2 style='color:#58a6ff'>TOTAL: R$ {total:,.2f}</h2>", unsafe_allow_html=True)
                
                if st.button("CONFIRMAR SAÍDA DE CARGA"):
                    if p_info["Estoque"] >= p_qtd:
                        venda_log = pd.DataFrame([{"Data": datetime.now(), "Produto": p_nome, "Qtd": p_qtd, "Total": total, "Lucro": lucro}])
                        st.session_state.vendas = pd.concat([st.session_state.vendas, venda_log], ignore_index=True)
                        st.session_state.produtos.loc[st.session_state.produtos["Nome"] == p_nome, "Estoque"] -= p_qtd
                        save_data(st.session_state.produtos, st.session_state.vendas)
                        st.balloons()
                        st.success("Transação Concluída!")
                    else: st.error("ESTOQUE INSUFICIENTE")

# --- RELATÓRIOS ---
elif menu == "📜 Logs & Romaneio":
    st.title("📜 Documentação")
    t_v, t_r = st.tabs(["📜 Histórico de Transações", "🚚 Emissão de Romaneio"])
    
    with t_v:
        st.dataframe(st.session_state.vendas.sort_values(by='Data', ascending=False), use_container_width=True)
        
    with t_r:
        if not st.session_state.vendas.empty:
            st.info("O sistema gera o romaneio baseado no último carregamento realizado.")
            if st.button("💎 GERAR DOCUMENTO DE CARGA"):
                ultima = st.session_state.vendas.tail(1).iloc[0]
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", 'B', 18)
                pdf.set_text_color(40, 40, 40)
                pdf.cell(190, 15, "EMBASSERRA EMBALAGENS - ROMANEIO", ln=True, align='C')
                pdf.set_font("Helvetica", size=12)
                pdf.cell(190, 10, f"ID de Transação: {datetime.now().strftime('%Y%m%d%H%M')}", ln=True, align='C')
                pdf.ln(10)
                
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(100, 10, "PRODUTO", 1, 0, 'C', True)
                pdf.cell(40, 10, "QUANTIDADE", 1, 0, 'C', True)
                pdf.cell(50, 10, "TOTAL", 1, 1, 'C', True)
                
                pdf.cell(100, 10, str(ultima['Produto']), 1)
                pdf.cell(40, 10, str(ultima['Qtd']), 1, 0, 'C')
                pdf.cell(50, 10, f"R$ {ultima['Total']:.2f}", 1, 1, 'C')
                
                pdf.ln(20)
                pdf.cell(190, 10, "ASSINATURA DO RESPONSÁVEL: ___________________________", ln=True)
                
                pdf_bytes = pdf.output()
                st.download_button("📥 DOWNLOAD ROMANEIO PDF", bytes(pdf_bytes), "romaneio_embasserra.pdf", "application/pdf")
