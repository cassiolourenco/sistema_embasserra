import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# 1. CONFIGURAÇÃO DE ALTO NÍVEL
st.set_page_config(
    page_title="EMBASSERRA | ENTERPRISE OS",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. DESIGN SISTEMA BRUTALISTA (CSS CUSTOMIZADO)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap');

    /* Variáveis e Fundo */
    :root {
        --primary: #3b82f6;
        --bg: #020617;
    }

    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f8fafc;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Títulos Impactantes */
    h1, h2, h3 {
        font-family: 'Syncopate', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        background: linear-gradient(90deg, #ffffff, #64748b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Sidebar Industrial */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(12px);
        border-right: 2px solid #334155;
    }

    /* Cards Brutalistas (Responsivos via Flexbox) */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.4);
        border: 2px solid #334155;
        border-radius: 0px !important;
        padding: 25px !important;
        box-shadow: 10px 10px 0px #000000;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translate(-5px, -5px);
        box-shadow: 15px 15px 0px var(--primary);
        border-color: var(--primary);
    }

    /* Botão de Comando */
    .stButton>button {
        width: 100%;
        background-color: #f8fafc !important;
        color: #000000 !important;
        border: 2px solid #ffffff !important;
        border-radius: 0px !important;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        padding: 20px;
        text-transform: uppercase;
        transition: 0.4s;
    }

    .stButton>button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
        box-shadow: 8px 8px 0px var(--primary);
        border-color: var(--primary) !important;
    }

    /* Tabelas e Inputs */
    .stDataFrame { border: 2px solid #334155; border-radius: 0px; }
    input { border-radius: 0px !important; background-color: #0f172a !important; border: 1px solid #334155 !important; }

    /* Ajuste Mobile */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. NÚCLEO DE PROCESSAMENTO DE DADOS
def engine_dados():
    path_p, path_v = "produtos.csv", "vendas.csv"
    
    # Carregar ou Criar Produtos
    if os.path.exists(path_p):
        df_p = pd.read_csv(path_p)
    else:
        df_p = pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
        
    # Carregar ou Criar Vendas
    if os.path.exists(path_v):
        df_v = pd.read_csv(path_v)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        df_v = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro"])
        
    return df_p, df_v

def salvar_estado(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

# Inicialização da Sessão
if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = engine_dados()

# 4. SISTEMA DE SEGURANÇA (LOGIN)
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align: center;'>SYSTEM_LOCK</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.form("gate"):
            key = st.text_input("CHAVE DE ACESSO CRIPTOGRAFADA", type="password")
            if st.form_submit_button("DESBLOQUEAR TERMINAL"):
                if key == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("ACESSO NEGADO: CHAVE INCORRETA")
    st.stop()

# 5. NAVEGAÇÃO LATERAL
with st.sidebar:
    st.markdown("<h1>EMBASSERRA</h1>")
    st.markdown("<p style='font-size: 10px; letter-spacing: 2px;'>OPERATIONAL INTELLIGENCE v4.0</p>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("MÓDULOS DE COMANDO", ["PAINEL DE PERFORMANCE", "INVENTÁRIO DE ATIVOS", "TERMINAL PDV", "RELATÓRIOS E PDF"])
    st.divider()
    if st.button("LOGOUT / LOCK"):
        del st.session_state.autenticado
        st.rerun()

# 6. MÓDULO: PAINEL DE PERFORMANCE (DASHBOARD)
if menu == "PAINEL DE PERFORMANCE":
    st.markdown("<h3>Análise de Fluxo</h3>", unsafe_allow_html=True)
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    faturamento_total = st.session_state.vendas['Total'].sum()
    lucro_total = st.session_state.vendas['Lucro'].sum()
    volume_itens = st.session_state.vendas['Qtd'].sum()
    
    c1.metric("FATURAMENTO ACUMULADO", f"R$ {faturamento_total:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
    c2.metric("LUCRO LÍQUIDO", f"R$ {lucro_total:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
    c3.metric("VOLUME DE CARGA", f"{int(volume_itens)} un")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.vendas.empty:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.write("Linha de Performance Temporal")
            fig = px.area(st.session_state.vendas.sort_values('Data'), x='Data', y='Total', template="plotly_dark")
            fig.update_traces(line_color='#3b82f6', fillcolor='rgba(59, 130, 246, 0.1)')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            st.write("Mix de Saída")
            fig2 = px.pie(st.session_state.vendas, names='Produto', values='Total', hole=0.5, template="plotly_dark")
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

# 7. MÓDULO: INVENTÁRIO DE ATIVOS
elif menu == "INVENTÁRIO DE ATIVOS":
    st.markdown("<h3>Gestão de Estoque</h3>", unsafe_allow_html=True)
    tab_list, tab_add = st.tabs(["ESTOQUE ATIVO", "CADASTRAR NOVA CARGA"])
    
    with tab_list:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
        
    with tab_add:
        with st.container(border=True):
            nome_p = st.text_input("NOME DO PRODUTO / EMBALAGEM")
            cc1, cc2, cc3 = st.columns(3)
            custo_p = cc1.number_input("CUSTO UNITÁRIO (R$)", format="%.2f", step=0.01)
            venda_p = cc2.number_input("VALOR DE VENDA (R$)", format="%.2f", step=0.01)
            estoque_p = cc3.number_input("QUANTIDADE INICIAL", step=1)
            
            if st.button("REGISTRAR NO SISTEMA"):
                if nome_p:
                    novo_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 1000
                    nova_linha = pd.DataFrame([{"ID": novo_id, "Nome": nome_p, "Custo": custo_p, "Venda": venda_p, "Estoque": estoque_p}])
                    st.session_state.produtos = pd.concat([st.session_state.produtos, nova_linha], ignore_index=True)
                    salvar_estado(st.session_state.produtos, st.session_state.vendas)
                    st.success(f"PRODUTO {nome_p} CADASTRADO COM SUCESSO.")
                    st.rerun()
                else:
                    st.error("NOME DO PRODUTO É OBRIGATÓRIO.")

# 8. MÓDULO: TERMINAL PDV
elif menu == "TERMINAL PDV":
    st.markdown("<h3>Ponto de Saída de Mercadoria</h3>", unsafe_allow_html=True)
    
    lista_produtos = st.session_state.produtos["Nome"].tolist()
    
    if not lista_produtos:
        st.warning("NENHUM PRODUTO DISPONÍVEL NO INVENTÁRIO.")
    else:
        with st.container(border=True):
            col_v1, col_v2 = st.columns([2, 1])
            prod_venda = col_v1.selectbox("SELECIONAR ITEM PARA SAÍDA", options=lista_produtos)
            qtd_venda = col_v2.number_input("QUANTIDADE", min_value=1, step=1)
            
            # Busca Dados do Item
            idx = st.session_state.produtos[st.session_state.produtos["Nome"] == prod_venda].index[0]
            item_info = st.session_state.produtos.loc[idx]
            
            valor_final = item_info['Venda'] * qtd_venda
            lucro_final = (item_info['Venda'] - item_info['Custo']) * qtd_venda
            
            st.markdown(f"<h1 style='color: #3b82f6; text-align: left;'>VALOR: R$ {valor_final:,.2f}</h1>", unsafe_allow_html=True)
            st.write(f"Estoque Disponível: {item_info['Estoque']} un")
            
            if st.button("CONFIRMAR E GERAR TRANSAÇÃO"):
                if item_info["Estoque"] >= qtd_venda:
                    # Registra Venda
                    venda_data = pd.DataFrame([{"Data": datetime.now(), "Produto": prod_venda, "Qtd": qtd_venda, "Total": valor_final, "Lucro": lucro_final}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, venda_data], ignore_index=True)
                    
                    # Baixa Estoque
                    st.session_state.produtos.at[idx, "Estoque"] -= qtd_venda
                    
                    salvar_estado(st.session_state.produtos, st.session_state.vendas)
                    st.success("TRANSAÇÃO CONCLUÍDA COM SUCESSO.")
                    st.rerun()
                else:
                    st.error("ESTOQUE INSUFICIENTE PARA ESTA OPERAÇÃO.")

# 9. MÓDULO: RELATÓRIOS E PDF
elif menu == "RELATÓRIOS E PDF":
    st.markdown("<h3>Documentação e Logs</h3>", unsafe_allow_html=True)
    t_logs, t_pdf = st.tabs(["LOG DE OPERAÇÕES", "ROMANEIO DE CARGA"])
    
    with t_logs:
        st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
        
    with t_pdf:
        if st.session_state.vendas.empty:
            st.info("REALIZE UMA VENDA PARA GERAR DOCUMENTAÇÃO.")
        else:
            st.write("Emissão de Romaneio da última carga processada:")
            u_venda = st.session_state.vendas.tail(1).iloc[0]
            
            with st.container(border=True):
                st.write(f"**Item:** {u_venda['Produto']}")
                st.write(f"**Qtd:** {u_venda['Qtd']}")
                st.write(f"**Total:** R$ {u_venda['Total']:.2f}")
                
                if st.button("GERAR ARQUIVO PDF"):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 20)
                    pdf.cell(190, 15, "EMBASSERRA EMBALAGENS", ln=True, align='C')
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(190, 10, "ROMANEIO DE CARGA E SAIDA", ln=True, align='C')
                    pdf.ln(10)
                    
                    pdf.set_font("Arial", size=12)
                    pdf.cell(190, 10, f"DATA DA EMISSAO: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
                    pdf.cell(190, 10, f"DESCRICAO DO ITEM: {u_venda['Produto']}", ln=True)
                    pdf.cell(190, 10, f"QUANTIDADE TOTAL: {u_venda['Qtd']}", ln=True)
                    pdf.cell(190, 10, f"VALOR DECLARADO: R$ {u_venda['Total']:.2f}", ln=True)
                    
                    pdf.ln(30)
                    pdf.cell(190, 10, "________________________________________________", ln=True, align='C')
                    pdf.cell(190, 10, "ASSINATURA DO RESPONSAVEL", ln=True, align='C')
                    
                    pdf_bytes = pdf.output()
                    st.download_button(
                        label="BAIXAR PDF AGORA",
                        data=bytes(pdf_bytes),
                        file_name=f"romaneio_{datetime.now().strftime('%d%m%y')}.pdf",
                        mime="application/pdf"
                    )
