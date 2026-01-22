import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# --- SETUP DE ELITE ---
st.set_page_config(page_title="EMBASSERRA | ERP", layout="wide")

# --- DESIGN BRUTALISTA (PORTUGUÊS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f8fafc;
        font-family: 'Space Grotesk', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 2px solid #334155;
    }

    h1, h2, h3 {
        font-family: 'Syncopate', sans-serif;
        text-transform: uppercase;
        letter-spacing: 4px;
        background: linear-gradient(90deg, #fff, #64748b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5);
        border: 2px solid #334155;
        border-radius: 0px !important;
        padding: 30px !important;
        box-shadow: 10px 10px 0px #000;
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translate(-5px, -5px);
        box-shadow: 15px 15px 0px #3b82f6;
        border-color: #3b82f6;
    }

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
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
def carregar_dados():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    if os.path.exists(v):
        df_v = pd.read_csv(v)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        df_v = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro"])
    return df_p, df_v

def salvar_dados(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = carregar_dados()

# --- ACESSO ---
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align: center;'>ACESSO AO SISTEMA</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("auth"):
            key = st.text_input("CHAVE DE SEGURANÇA", type="password")
            if st.form_submit_button("ENTRAR"):
                if key == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("<h1>EMBASSERRA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='letter-spacing:2px; font-size:10px;'>SISTEMA OPERACIONAL CENTRAL</p>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("SELECIONE O MÓDULO", ["PAINEL GERAL", "ESTOQUE", "VENDAS PDV", "RELATÓRIOS"])
    st.divider()
    if st.button("ENCERRAR SESSÃO"):
        del st.session_state.autenticado
        st.rerun()

# --- PAINEL GERAL ---
if menu == "PAINEL GERAL":
    st.markdown("<h3>Inteligência de Negócio</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    faturamento = st.session_state.vendas['Total'].sum()
    lucro = st.session_state.vendas['Lucro'].sum()
    
    c1.metric("FATURAMENTO TOTAL", f"R$ {faturamento:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    c2.metric("LUCRO LÍQUIDO", f"R$ {lucro:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    c3.metric("TOTAL DE VENDAS", len(st.session_state.vendas))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.vendas.empty:
        fig = px.area(st.session_state.vendas.sort_values('Data'), x='Data', y='Total', title="LINHA DE PERFORMANCE")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', title_font_family="Syncopate")
        fig.update_traces(line_color='#3b82f6', fillcolor='rgba(59, 130, 246, 0.2)')
        st.plotly_chart(fig, use_container_width=True)

# --- ESTOQUE ---
elif menu == "ESTOQUE":
    st.markdown("<h3>Controle de Ativos</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["LISTA DE ITENS", "ADICIONAR NOVO"])
    with t1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    with t2:
        with st.form("add"):
            n = st.text_input("NOME DO PRODUTO")
            c, v, q = st.columns(3)
            custo = c.number_input("CUSTO (R$)", format="%.2f", step=0.01)
            venda = v.number_input("VENDA (R$)", format="%.2f", step=0.01)
            qtd = q.number_input("QUANTIDADE", 0)
            if st.form_submit_button("EFETUAR CADASTRO"):
                novo_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 1001
                novo_p = pd.DataFrame([{"ID": novo_id, "Nome": n, "Custo": custo, "Venda": venda, "Estoque": qtd}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo_p], ignore_index=True)
                salvar_dados(st.session_state.produtos, st.session_state.vendas)
                st.success("PRODUTO REGISTRADO!")
                st.rerun()

# --- VENDAS ---
elif menu == "VENDAS PDV":
    st.markdown("<h3>Terminal de Saída</h3>", unsafe_allow_html=True)
    if not st.session_state.produtos.empty:
        with st.container():
            p_sel = st.selectbox("SELECIONE O PRODUTO", st.session_state.produtos["Nome"])
            q_sel = st.number_input("QUANTIDADE", 1)
            p_dados = st.session_state.produtos[st.session_state.produtos["Nome"] == p_sel].iloc[0]
            total = p_dados['Venda'] * q_sel
            
            st.markdown(f"<h1 style='-webkit-text-fill-color: #3b82f6;'>TOTAL: R$ {total:,.2f}</h1>", unsafe_allow_html=True)
            
            if st.button("FINALIZAR TRANSAÇÃO"):
                if p_dados["Estoque"] >= q_sel:
                    lucro_venda = (p_dados['Venda'] - p_dados['Custo']) * q_sel
                    log = pd.DataFrame([{"Data": datetime.now(), "Produto": p_sel, "Qtd": q_sel, "Total": total, "Lucro": lucro_venda}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, log], ignore_index=True)
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == p_sel, "Estoque"] -= q_sel
                    salvar_dados(st.session_state.produtos, st.session_state.vendas)
                    st.success("VENDA CONCLUÍDA COM SUCESSO!")
                    st.rerun()
                else: st.error("SALDO DE ESTOQUE INSUFICIENTE!")

# --- RELATÓRIOS ---
elif menu == "RELATÓRIOS":
    st.markdown("<h3>Arquivos e Registros</h3>", unsafe_allow_html=True)
    t_hist, t_pdf = st.tabs(["HISTÓRICO", "EMISSÃO DE ROMANEIO"])
    
    with t_hist:
        st.dataframe(st.session_state.vendas, use_container_width=True, hide_index=True)
        
    with t_pdf:
        if not st.session_state.vendas.empty:
            st.write("Gerar romaneio baseado no último carregamento:")
            if st.button("GERAR DOCUMENTO PDF"):
                u = st.session_state.vendas.tail(1).iloc[0]
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", 'B', 16)
                pdf.cell(190, 10, "EMBASSERRA EMBALAGENS - ROMANEIO", ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("Helvetica", size=12)
                pdf.cell(190, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
                pdf.cell(190, 10, f"PRODUTO: {u['Produto']}", ln=True)
                pdf.cell(190, 10, f"QTD: {u['Qtd']}", ln=True)
                pdf.cell(190, 10, f"VALOR TOTAL: R$ {u['Total']:.2f}", ln=True)
                pdf.ln(20)
                pdf.cell(190, 10, "ASSINATURA RESPONSAVEL: ___________________________", ln=True)
                
                st.download_button("BAIXAR ROMANEIO", bytes(pdf.output()), "romaneio_embasserra.pdf", "application/pdf")
