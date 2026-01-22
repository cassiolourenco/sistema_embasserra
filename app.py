import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# --- SETUP DO SISTEMA ---
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide")

# --- DESIGN BRUTALISTA RESPONSIVO (O JEITÃO QUE VOCÊ CURTIU) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f8fafc;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Sidebar Estilo Industrial */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(10px);
        border-right: 2px solid #334155;
    }

    /* Títulos em Neon Dinâmico */
    h1 { font-family: 'Syncopate', sans-serif; text-transform: uppercase; letter-spacing: 4px; background: linear-gradient(90deg, #fff, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: clamp(1.5rem, 5vw, 2.5rem) !important; }
    h3 { font-family: 'Syncopate', sans-serif; color: #fff; text-transform: uppercase; font-size: clamp(1rem, 3vw, 1.3rem) !important; }

    /* Cards Brutalistas que se ajustam (PC vs Mobile) */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5);
        border: 2px solid #334155;
        border-radius: 0px !important;
        padding: 20px !important;
        box-shadow: 8px 8px 0px #000;
        margin-bottom: 15px;
    }

    /* Forçar colunas a empilharem no Mobile */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }

    /* Botões de Alto Impacto */
    .stButton>button {
        width: 100%;
        background-color: #f8fafc !important;
        color: #000 !important;
        border: 2px solid #fff !important;
        border-radius: 0px !important;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        padding: 18px;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3b82f6 !important;
        color: #fff !important;
        box-shadow: 6px 6px 0px #000;
        transform: translate(-2px, -2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CORE ENGINE ---
def load_engine():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    if os.path.exists(v):
        df_v = pd.read_csv(v)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        df_v = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro"])
    return df_p, df_v

def save_engine(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = load_engine()

# --- SEGURANÇA ---
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align: center;'>ACESSO RESTRITO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.form("login"):
            key = st.text_input("CHAVE MESTRA", type="password")
            if st.form_submit_button("DESBLOQUEAR"):
                if key == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("CHAVE INVÁLIDA")
    st.stop()

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("<h1>EMBASSERRA</h1>")
    st.write("SISTEMA OPERACIONAL")
    st.divider()
    menu = st.radio("MÓDULOS", ["PAINEL GERAL", "INVENTÁRIO", "TERMINAL VENDAS", "ARQUIVOS"])
    st.divider()
    if st.button("TERMINAR SESSÃO"):
        del st.session_state.autenticado
        st.rerun()

# --- PAINEL GERAL ---
if menu == "PAINEL GERAL":
    st.markdown("<h3>Performance do Negócio</h3>", unsafe_allow_html=True)
    faturamento = st.session_state.vendas['Total'].sum()
    lucro = st.session_state.vendas['Lucro'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("FATURAMENTO", f"R$ {faturamento:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
    c2.metric("LUCRO LÍQUIDO", f"R$ {lucro:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
    c3.metric("TRANSAÇÕES", len(st.session_state.vendas))
    
    if not st.session_state.vendas.empty:
        st.markdown("---")
        fig = px.area(st.session_state.vendas.sort_values('Data'), x='Data', y='Total', title="FLUXO DE CAIXA")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', height=400)
        fig.update_traces(line_color='#3b82f6', fillcolor='rgba(59, 130, 246, 0.1)')
        st.plotly_chart(fig, use_container_width=True)

# --- INVENTÁRIO ---
elif menu == "INVENTÁRIO":
    st.markdown("<h3>Gestão de Ativos</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["ESTOQUE ATUAL", "NOVA ENTRADA"])
    with t1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    with t2:
        with st.form("cad"):
            nome = st.text_input("NOME DO ITEM")
            col1, col2 = st.columns(2)
            pc = col1.number_input("CUSTO (R$)", format="%.2f", step=0.01)
            pv = col2.number_input("VENDA (R$)", format="%.2f", step=0.01)
            pq = st.number_input("QUANTIDADE INICIAL", 0)
            if st.form_submit_button("EFETIVAR CADASTRO"):
                nid = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 1001
                novo_p = pd.DataFrame([{"ID": nid, "Nome": nome, "Custo": pc, "Venda": pv, "Estoque": pq}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo_p], ignore_index=True)
                save_engine(st.session_state.produtos, st.session_state.vendas)
                st.success("ITEM INTEGRADO AO SISTEMA!")
                st.rerun()

# --- TERMINAL VENDAS ---
elif menu == "TERMINAL VENDAS":
    st.markdown("<h3>Ponto de Saída</h3>", unsafe_allow_html=True)
    # Proteção contra erro de selectbox vazio
    opcoes = st.session_state.produtos["Nome"].tolist() if not st.session_state.produtos.empty else []
    
    if opcoes:
        with st.container():
            psel = st.selectbox("SELECIONAR PRODUTO", options=opcoes)
            qsel = st.number_input("QUANTIDADE", min_value=1, step=1)
            item = st.session_state.produtos[st.session_state.produtos["Nome"] == psel].iloc[0]
            total = item['Venda'] * qsel
            
            st.markdown(f"<h1 style='color: #3b82f6; text-shadow: 2px 2px 0px #000;'>TOTAL: R$ {total:,.2f}</h1>", unsafe_allow_html=True)
            
            if st.button("PROCESSAR VENDA"):
                if item["Estoque"] >= qsel:
                    lucro_v = (item['Venda'] - item['Custo']) * qsel
                    log_v = pd.DataFrame([{"Data": datetime.now(), "Produto": psel, "Qtd": qsel, "Total": total, "Lucro": lucro_v}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, log_v], ignore_index=True)
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == psel, "Estoque"] -= qsel
                    save_engine(st.session_state.produtos, st.session_state.vendas)
                    st.success("TRANSAÇÃO CONCLUÍDA!")
                    st.rerun()
                else:
                    st.error("ERRO: ESTOQUE INSUFICIENTE")
    else:
        st.warning("CADASTRE PRODUTOS NO INVENTÁRIO ANTES DE VENDER.")

# --- ARQUIVOS ---
elif menu == "ARQUIVOS":
    st.markdown("<h3>Registros de Carga</h3>", unsafe_allow_html=True)
    t_h, t_p = st.tabs(["HISTÓRICO", "ROMANEIO PDF"])
    with t_h:
        st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
    with t_p:
        if not st.session_state.vendas.empty:
            st.write("Gerar documento para o último carregamento:")
            if st.button("GERAR DOCUMENTO AGORA"):
                u = st.session_state.vendas.tail(1).iloc[0]
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(190, 15, "EMBASSERRA EMBALAGENS - ROMANEIO", ln=True, align='C')
                pdf.set_font("Arial", size=12)
                pdf.ln(10)
                pdf.cell(190, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
                pdf.cell(190, 10, f"CARGA: {u['Produto']}", ln=True)
                pdf.cell(190, 10, f"QUANTIDADE: {u['Qtd']}", ln=True)
                pdf.cell(190, 10, f"VALOR TOTAL: R$ {u['Total']:.2f}", ln=True)
                pdf.ln(20)
                pdf.cell(190, 10, "ASSINATURA RESPONSAVEL: ___________________________", ln=True)
                st.download_button("BAIXAR ROMANEIO PDF", bytes(pdf.output()), "romaneio_embasserra.pdf", "application/pdf")
