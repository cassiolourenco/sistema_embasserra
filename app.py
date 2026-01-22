import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Embasserra ERP", layout="wide", page_icon="📦")

# --- DESIGN PREMIUM (CSS CUSTOMIZADO) ---
st.markdown("""
    <style>
    /* Fundo e Fonte Geral */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Barra Lateral Estilizada */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Cartões de Indicadores (Métricas) */
    div[data-testid="stMetric"] {
        background-color: #1c2128;
        border: 1px solid #30363d;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    /* Títulos e Textos de Métricas */
    div[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 14px !important; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #58a6ff !important; font-size: 28px !important; }

    /* Botões Modernos */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #238636;
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2ea043; border: none; color: white; }

    /* Estilo de Tabelas */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    
    /* Títulos de Seção */
    h1, h2, h3 { color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN PRIVADO ---
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("login"):
            senha = st.text_input("Chave de Segurança", type="password")
            if st.form_submit_button("Entrar no Sistema"):
                if senha == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta")
    st.stop()

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    cols_p = ["ID", "Nome", "Custo", "Venda", "Estoque"]
    cols_v = ["Data", "Produto", "Qtd", "Total", "Lucro"]
    df_p = pd.read_csv("produtos.csv") if os.path.exists("produtos.csv") else pd.DataFrame(columns=cols_p)
    if os.path.exists("vendas.csv"):
        df_v = pd.read_csv("vendas.csv")
        df_v['Data'] = pd.to_datetime(df_v['Data'], errors='coerce')
    else:
        df_v = pd.DataFrame(columns=cols_v)
    return df_p, df_v

def salvar(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state or 'vendas' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = carregar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #58a6ff;'>EMBASSERRA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 12px;'>Controle de Embalagens v2.0</p>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("Navegação", ["📈 Painel de Controle", "📦 Estoque Geral", "🛒 Nova Venda (PDV)", "📑 Relatórios & Romaneio"])
    st.divider()
    if st.button("Sair"):
        del st.session_state.autenticado
        st.rerun()

# --- PAINEL DE CONTROLE ---
if menu == "📈 Painel de Controle":
    st.title("📊 Resumo Operacional")
    st.markdown("Visão geral do desempenho da Embasserra.")
    
    # Linha de métricas
    m1, m2, m3, m4 = st.columns(4)
    vendas_hoje = st.session_state.vendas[st.session_state.vendas['Data'].dt.date == datetime.now().date()] if not st.session_state.vendas.empty else pd.DataFrame()
    
    m1.metric("Faturamento Total", f"R$ {st.session_state.vendas['Total'].sum():,.2f}")
    m2.metric("Vendas Hoje", len(vendas_hoje))
    m3.metric("Estoque Disponível", int(st.session_state.produtos['Estoque'].sum()) if not st.session_state.produtos.empty else 0)
    m4.metric("Lucro Acumulado", f"R$ {st.session_state.vendas['Lucro'].sum():,.2f}")

    st.divider()
    st.subheader("Últimas Atividades")
    st.dataframe(st.session_state.vendas.tail(5), width=2000, hide_index=True)

# --- ESTOQUE GERAL ---
elif menu == "📦 Estoque Geral":
    st.title("📦 Gestão de Inventário")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Produtos Cadastrados")
        st.dataframe(st.session_state.produtos, width=2000, hide_index=True)
    
    with col2:
        st.subheader("Novo Item")
        with st.form("cad_estoque", clear_on_submit=True):
            n = st.text_input("Nome da Embalagem")
            custo = st.number_input("Preço Custo", 0.0)
            venda = st.number_input("Preço Venda", 0.0)
            qtd = st.number_input("Quantidade Inicial", 0)
            if st.form_submit_button("Adicionar ao Estoque"):
                novo_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 1001
                item = pd.DataFrame([{"ID": novo_id, "Nome": n, "Custo": custo, "Venda": venda, "Estoque": qtd}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, item], ignore_index=True)
                salvar(st.session_state.produtos, st.session_state.vendas)
                st.success("✅ Produto cadastrado!")
                st.rerun()

# --- PDV ---
elif menu == "🛒 Nova Venda (PDV)":
    st.title("🛒 Frente de Caixa")
    if st.session_state.produtos.empty:
        st.warning("⚠️ Primeiro cadastre produtos no Estoque.")
    else:
        with st.container(border=True):
            p_nome = st.selectbox("Selecione o Produto", st.session_state.produtos["Nome"])
            p_qtd = st.number_input("Quantidade para Saída", 1, step=1)
            
            p_dados = st.session_state.produtos[st.session_state.produtos["Nome"] == p_nome].iloc[0]
            total = p_dados['Venda'] * p_qtd
            lucro = (p_dados['Venda'] - p_dados['Custo']) * p_qtd
            
            st.markdown(f"### Valor Total: :blue[R$ {total:,.2f}]")
            
            if st.button("Finalizar Pedido"):
                if p_dados["Estoque"] >= p_qtd:
                    venda_log = pd.DataFrame([{"Data": datetime.now(), "Produto": p_nome, "Qtd": p_qtd, "Total": total, "Lucro": lucro}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, venda_log], ignore_index=True)
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == p_nome, "Estoque"] -= p_qtd
                    salvar(st.session_state.produtos, st.session_state.vendas)
                    st.success("✨ Venda registrada com sucesso!")
                else:
                    st.error("❌ Estoque insuficiente!")

# --- RELATÓRIOS ---
elif menu == "📑 Relatórios & Romaneio":
    st.title("📑 Documentos e Histórico")
    
    tab1, tab2 = st.tabs(["Histórico de Vendas", "Gerar Romaneio"])
    
    with tab1:
        st.dataframe(st.session_state.vendas, width=2000, hide_index=True)
    
    with tab2:
        if not st.session_state.vendas.empty:
            st.info("O Romaneio será gerado com base na **última venda** registrada.")
            if st.button("📥 Gerar PDF para o Caminhão"):
                # Função do PDF aqui dentro ou chamada externa
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(190, 10, txt="EMBASSERRA EMBALAGENS - ROMANEIO", ln=True, align='C')
                pdf.set_font("Arial", size=11)
                pdf.ln(10)
                pdf.cell(190, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
                
                ultima = st.session_state.vendas.tail(1).iloc[0]
                pdf.ln(5)
                pdf.cell(100, 10, f"Produto: {ultima['Produto']}", border=1)
                pdf.cell(40, 10, f"Qtd: {ultima['Qtd']}", border=1)
                pdf.cell(50, 10, f"Total: R$ {ultima['Total']:.2f}", border=1, ln=True)
                
                pdf.ln(20)
                pdf.cell(190, 10, txt="_______________________________________", ln=True, align='C')
                pdf.cell(190, 10, txt="Assinatura do Responsável", ln=True, align='C')
                
                pdf_bytes = pdf.output()
                st.download_button("Clique aqui para Baixar", pdf_bytes, "romaneio.pdf", "application/pdf")
        else:
            st.warning("Não há vendas registradas para gerar documentos.")
