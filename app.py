import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# --- CONFIGURAÇÃO MASTER ---
st.set_page_config(page_title="EMBASSERRA | LOGÍSTICA", layout="wide", initial_sidebar_state="expanded")

# --- CSS PERSONALIZADO (VISUAL INDUSTRIAL REFINADO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp { background: #020617; color: #f1f5f9; font-family: 'Space Grotesk', sans-serif; }
    
    /* Esconder marcas da IA/Streamlit */
    #MainMenu, footer, header {visibility: hidden;}

    /* Sidebar Estilizada */
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 2px solid #1e293b; }
    .nav-brand { font-family: 'Syncopate', sans-serif; color: #3b82f6; font-size: 1.2rem; letter-spacing: 4px; margin-bottom: 0px; }
    .nav-version { font-size: 9px; color: #64748b; letter-spacing: 2px; margin-bottom: 30px; }

    /* Cards de Métricas (Brutalismo Elegante) */
    div[data-testid="stMetric"] {
        background: #0f172a;
        border: 1px solid #334155;
        border-left: 6px solid #3b82f6 !important;
        border-radius: 0px !important;
        padding: 25px !important;
        box-shadow: 10px 10px 0px #000;
    }
    
    /* Botões Operacionais */
    .stButton>button {
        width: 100%;
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 0px !important;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        padding: 20px;
        text-transform: uppercase;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2563eb !important; transform: scale(1.01); box-shadow: 0px 0px 20px rgba(59, 130, 246, 0.4); }

    /* Estilo de Tabelas */
    .stDataFrame { border: 1px solid #1e293b; border-radius: 0px; }
    
    /* Títulos de Seção */
    .section-title { font-family: 'Syncopate', sans-serif; font-size: 1.5rem; color: #fff; margin-bottom: 25px; border-bottom: 2px solid #3b82f6; display: inline-block; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE (BANCO DE DADOS) ---
def setup_db():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    if os.path.exists(v):
        df_v = pd.read_csv(v)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        # Criado com a coluna Placa
        df_v = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"])
    return df_p, df_v

def save_db(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = setup_db()

# --- SIDEBAR NAVEGAÇÃO ---
with st.sidebar:
    st.markdown('<p class="nav-brand">EMBASSERRA</p>', unsafe_allow_html=True)
    st.markdown('<p class="nav-version">CARGO SYSTEM v5.0</p>', unsafe_allow_html=True)
    menu = st.radio("SISTEMA CENTRAL", ["DASHBOARD", "ESTOQUE", "SAÍDA DE CARGA", "HISTÓRICO"])
    st.divider()
    if st.button("BLOQUEAR"):
        st.session_state.clear()
        st.rerun()

# --- DASHBOARD ---
if menu == "DASHBOARD":
    st.markdown('<p class="section-title">Monitoramento de Operações</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    faturamento = st.session_state.vendas['Total'].sum()
    lucro = st.session_state.vendas['Lucro'].sum()
    transacoes = len(st.session_state.vendas)
    
    c1.metric("FATURAMENTO BRUTO", f"R$ {faturamento:,.2f}")
    c2.metric("LUCRO LÍQUIDO", f"R$ {lucro:,.2f}")
    c3.metric("CARREGAMENTOS", transacoes)

    if not st.session_state.vendas.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        fig = px.bar(st.session_state.vendas, x='Data', y='Total', color='Produto', template="plotly_dark", title="Volume por Dia")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# --- ESTOQUE ---
elif menu == "ESTOQUE":
    st.markdown('<p class="section-title">Controle de Inventário</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    
    with st.expander("➕ CADASTRAR NOVO ITEM"):
        with st.form("add_p"):
            n = st.text_input("Nome do Produto")
            col1, col2, col3 = st.columns(3)
            c = col1.number_input("Custo Unitário", min_value=0.0, format="%.2f")
            v = col2.number_input("Preço de Venda", min_value=0.0, format="%.2f")
            e = col3.number_input("Estoque Inicial", min_value=0, step=1)
            if st.form_submit_button("SALVAR NO INVENTÁRIO"):
                new_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 100
                new_row = pd.DataFrame([{"ID": new_id, "Nome": n, "Custo": c, "Venda": v, "Estoque": e}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, new_row], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success("ITEM CADASTRADO")
                st.rerun()

# --- SAÍDA DE CARGA (PDV) ---
elif menu == "SAÍDA DE CARGA":
    st.markdown('<p class="section-title">Despacho de Mercadoria</p>', unsafe_allow_html=True)
    
    if st.session_state.produtos.empty:
        st.warning("Cadastre produtos antes de realizar uma saída.")
    else:
        with st.container():
            col_a, col_b = st.columns([2, 1])
            prod_nome = col_a.selectbox("Produto", st.session_state.produtos["Nome"])
            placa = col_b.text_input("Placa do Caminhão", placeholder="ABC-1234").upper()
            
            qtd = st.number_input("Quantidade de Volumes", min_value=1, step=1)
            
            item = st.session_state.produtos[st.session_state.produtos["Nome"] == prod_nome].iloc[0]
            total_venda = item['Venda'] * qtd
            
            st.markdown(f"<h2 style='color:#3b82f6;'>VALOR TOTAL: R$ {total_venda:,.2f}</h2>", unsafe_allow_html=True)
            
            if st.button("CONFIRMAR CARREGAMENTO"):
                if item["Estoque"] >= qtd:
                    # Lógica de venda
                    lucro_v = (item['Venda'] - item['Custo']) * qtd
                    nova_venda = pd.DataFrame([{
                        "Data": datetime.now(), 
                        "Produto": prod_nome, 
                        "Qtd": qtd, 
                        "Total": total_venda, 
                        "Lucro": lucro_v, 
                        "Placa": placa
                    }])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, nova_venda], ignore_index=True)
                    
                    # Baixa no estoque
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == prod_nome, "Estoque"] -= qtd
                    
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success(f"CARGA LIBERADA! Placa: {placa}")
                    st.rerun()
                else:
                    st.error("ESTOQUE INSUFICIENTE PARA ESTA CARGA")

# --- HISTÓRICO E PDF ---
elif menu == "HISTÓRICO":
    st.markdown('<p class="section-title">Arquivos e Romaneios</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
    
    if not st.session_state.vendas.empty:
        st.markdown("---")
        if st.button("GERAR ROMANEIO DA ÚLTIMA CARGA (PDF)"):
            u = st.session_state.vendas.tail(1).iloc[0]
            
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho
            pdf.set_font("Arial", 'B', 18)
            pdf.cell(190, 15, "EMBASSERRA EMBALAGENS", ln=True, align='C')
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(190, 10, "DOC. DE TRANSPORTE E ROMANEIO", ln=True, align='C')
            pdf.ln(10)
            
            # Dados
            pdf.set_font("Arial", size=11)
            pdf.cell(95, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M')}", border=1)
            pdf.cell(95, 10, f"PLACA: {u['Placa']}", border=1, ln=True)
            
            pdf.cell(130, 10, f"PRODUTO: {u['Produto']}", border=1)
            pdf.cell(60, 10, f"QTD: {u['Qtd']} UN", border=1, ln=True)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(190, 15, f"VALOR TOTAL DA CARGA: R$ {u['Total']:.2f}", border=1, ln=True, align='R')
            
            pdf.ln(30)
            pdf.cell(95, 10, "__________________________", ln=0, align='C')
            pdf.cell(95, 10, "__________________________", ln=1, align='C')
            pdf.set_font("Arial", size=8)
            pdf.cell(95, 5, "EXPEDIÇÃO EMBASSERRA", ln=0, align='C')
            pdf.cell(95, 5, "MOTORISTA / RECEBEDOR", ln=1, align='C')
            
            st.download_button(
                label="BAIXAR ROMANEIO EM PDF",
                data=bytes(pdf.output()),
                file_name=f"romaneio_{u['Placa']}_{datetime.now().strftime('%d%m%y')}.pdf",
                mime="application/pdf"
            )
