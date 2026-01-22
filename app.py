import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# --- CONFIGURAÇÃO DE ELITE ---
st.set_page_config(page_title="EMBASSERRA | CARGO", layout="wide", initial_sidebar_state="expanded")

# --- DESIGN PREMIUM (INDUSTRIAL NEON) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    /* Reset Geral */
    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    
    /* Esconder Lixo do Streamlit */
    #MainMenu, footer, header {visibility: hidden;}

    /* Sidebar Estilizada */
    [data-testid="stSidebar"] { 
        background-color: #0d1117 !important; 
        border-right: 1px solid #30363d; 
    }
    .sidebar-brand { 
        font-family: 'Syncopate', sans-serif; 
        color: #58a6ff; 
        font-size: 1.1rem; 
        letter-spacing: 3px;
        padding: 10px 0px;
    }

    /* Cards de Métricas (Visual de Monitor) */
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-top: 4px solid #58a6ff !important;
        border-radius: 4px !important;
        padding: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    /* Botões Pica */
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
        transition: 0.3s ease;
    }
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.5);
    }

    /* Input e Select */
    input, select { border-radius: 4px !important; }

    /* Titulos de Seção */
    .section-header {
        font-family: 'Syncopate', sans-serif;
        font-size: 1.3rem;
        color: #f0f6fc;
        border-left: 5px solid #58a6ff;
        padding-left: 15px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE LOGICA ---
def carregar_dados():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    if os.path.exists(v):
        df_v = pd.read_csv(v)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        df_v = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"])
    return df_p, df_v

def salvar_dados(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

# Inicializar Estado
if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = carregar_dados()

# --- SISTEMA DE LOGIN (BLOQUEIO) ---
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align: center; font-family:Syncopate; color:#58a6ff;'>TERMINAL EMBASSERRA</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login_form"):
            senha = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("AUTORIZAR"):
                if senha == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("ACESSO NEGADO")
    st.stop()

# --- SIDEBAR NAVEGAÇÃO ---
with st.sidebar:
    st.markdown('<p class="sidebar-brand">EMBASSERRA OS</p>', unsafe_allow_html=True)
    menu = st.radio("MÓDULOS", ["DASHBOARD", "ESTOQUE", "SAÍDA / PLACA", "REGISTROS"])
    st.divider()
    
    # CORREÇÃO DO BOTÃO BLOQUEAR
    if st.button("BLOQUEAR TERMINAL"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- CONTEÚDO ---
if menu == "DASHBOARD":
    st.markdown('<p class="section-header">Fluxo Financeiro e Carga</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    faturamento = st.session_state.vendas['Total'].sum()
    lucro = st.session_state.vendas['Lucro'].sum()
    transacoes = len(st.session_state.vendas)
    
    c1.metric("TOTAL FATURADO", f"R$ {faturamento:,.2f}")
    c2.metric("LUCRO LÍQUIDO", f"R$ {lucro:,.2f}")
    c3.metric("CARGAS DESPACHADAS", transacoes)

    if not st.session_state.vendas.empty:
        fig = px.line(st.session_state.vendas.sort_values('Data'), x='Data', y='Total', title="Evolução de Vendas", template="plotly_dark")
        fig.update_traces(line_color='#58a6ff')
        st.plotly_chart(fig, use_container_width=True)

elif menu == "ESTOQUE":
    st.markdown('<p class="section-header">Gerenciamento de Materiais</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    
    with st.expander("ADICIONAR NOVO ITEM"):
        with st.form("novo_p"):
            nome = st.text_input("NOME")
            col1, col2, col3 = st.columns(3)
            pc = col1.number_input("CUSTO", min_value=0.0)
            pv = col2.number_input("VENDA", min_value=0.0)
            pq = col3.number_input("ESTOQUE", min_value=0)
            if st.form_submit_button("CADASTRAR"):
                new_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 100
                novo = pd.DataFrame([{"ID": new_id, "Nome": nome, "Custo": pc, "Venda": pv, "Estoque": pq}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo], ignore_index=True)
                salvar_dados(st.session_state.produtos, st.session_state.vendas)
                st.success("ITEM SALVO")
                st.rerun()

elif menu == "SAÍDA / PLACA":
    st.markdown('<p class="section-header">Despacho Logístico</p>', unsafe_allow_html=True)
    if st.session_state.produtos.empty:
        st.warning("Cadastre produtos no estoque.")
    else:
        with st.container(border=True):
            p_nome = st.selectbox("PRODUTO", st.session_state.produtos["Nome"])
            placa = st.text_input("PLACA DO VEÍCULO", placeholder="Ex: ABC1D23").upper()
            qtd = st.number_input("QTD DE VOLUMES", min_value=1)
            
            item = st.session_state.produtos[st.session_state.produtos["Nome"] == p_nome].iloc[0]
            total = item['Venda'] * qtd
            
            st.markdown(f"### TOTAL CARGA: R$ {total:,.2f}")
            
            if st.button("FINALIZAR E GERAR ROMANEIO"):
                if item["Estoque"] >= qtd:
                    # Registrar
                    venda_df = pd.DataFrame([{"Data": datetime.now(), "Produto": p_nome, "Qtd": qtd, "Total": total, "Lucro": (item['Venda']-item['Custo'])*qtd, "Placa": placa}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, venda_df], ignore_index=True)
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == p_nome, "Estoque"] -= qtd
                    salvar_dados(st.session_state.produtos, st.session_state.vendas)
                    st.success(f"CARGA LIBERADA - VEÍCULO: {placa}")
                    st.rerun()
                else:
                    st.error("ESTOQUE INSUFICIENTE")

elif menu == "REGISTROS":
    st.markdown('<p class="section-header">Histórico de Saídas</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
    
    if not st.session_state.vendas.empty:
        if st.button("BAIXAR ÚLTIMO ROMANEIO (PDF)"):
            u = st.session_state.vendas.tail(1).iloc[0]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, "EMBASSERRA EMBALAGENS - ROMANEIO", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(190, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
            pdf.cell(190, 10, f"PLACA DO VEICULO: {u['Placa']}", ln=True)
            pdf.cell(190, 10, f"PRODUTO: {u['Produto']} | QTD: {u['Qtd']}", ln=True)
            pdf.cell(190, 10, f"VALOR DECLARADO: R$ {u['Total']:.2f}", ln=True)
            pdf.ln(20)
            pdf.cell(95, 10, "____________________", align='C')
            pdf.cell(95, 10, "____________________", ln=True, align='C')
            pdf.cell(95, 5, "EXPEDICAO", align='C')
            pdf.cell(95, 5, "MOTORISTA", ln=True, align='C')
            
            st.download_button("DOWNLOAD PDF", data=bytes(pdf.output()), file_name=f"romaneio_{u['Placa']}.pdf")
