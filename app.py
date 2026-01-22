import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Embasserra Embalagens - ERP", layout="wide", page_icon="📦")

# CSS para deixar com cara de software de alto padrão
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    div[data-testid="stMetricValue"] { color: #58a6ff !important; font-weight: 700; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN PRIVADO ---
if "autenticado" not in st.session_state:
    st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    senha = col.text_input("Chave de Segurança", type="password")
    if col.button("Acessar Sistema"):
        if senha == "admin123":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# --- GESTÃO DE DADOS (BLINDAGEM CONTRA ERROS) ---
def carregar_dados():
    # Estrutura profissional de colunas
    cols_p = ["ID", "Nome", "Custo", "Venda", "Estoque"]
    cols_v = ["Data", "Produto", "Qtd", "Total", "Lucro"]
    
    # Carrega ou cria Produtos
    if os.path.exists("produtos.csv"):
        df_p = pd.read_csv("produtos.csv")
        for c in cols_p: 
            if c not in df_p.columns: df_p[c] = 0
    else:
        df_p = pd.DataFrame(columns=cols_p)
        
    # Carrega ou cria Vendas
    if os.path.exists("vendas.csv"):
        df_v = pd.read_csv("vendas.csv")
        for c in cols_v:
            if c not in df_v.columns: df_v[c] = 0
        df_v['Data'] = pd.to_datetime(df_v['Data'], errors='coerce')
        df_v = df_v.dropna(subset=['Data'])
    else:
        df_v = pd.DataFrame(columns=cols_v)
        
    return df_p, df_v

def salvar(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

st.session_state.produtos, st.session_state.vendas = carregar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=220)
    else:
        st.title("EMBASSERRA")
    
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    st.divider()
    menu = st.radio("Módulos de Gestão", ["📈 Painel Geral", "📦 Inventário", "🛒 PDV (Vendas)", "📑 Relatórios"])
    st.divider()
    if st.button("Sair do Sistema"):
        del st.session_state.autenticado
        st.rerun()

# --- MÓDULO 1: PAINEL GERAL ---
if menu == "📈 Painel Geral":
    st.title("Resumo Operacional")
    
    c1, c2, c3, c4 = st.columns(4)
    vendas_df = st.session_state.vendas
    
    receita = vendas_df["Total"].sum() if not vendas_df.empty else 0
    lucro = vendas_df["Lucro"].sum() if not vendas_df.empty else 0
    estoque_qtd = st.session_state.produtos["Estoque"].sum() if not st.session_state.produtos.empty else 0
    
    c1.metric("Faturamento", f"R$ {receita:,.2f}")
    c2.metric("Lucro Líquido", f"R$ {lucro:,.2f}")
    c3.metric("Estoque Total", int(estoque_qtd))
    c4.metric("Vendas Hoje", len(vendas_df))

    st.divider()
    if not vendas_df.empty:
        st.subheader("Análise de Faturamento")
        graf = vendas_df.groupby(vendas_df['Data'].dt.date)['Total'].sum()
        st.area_chart(graf, color="#58a6ff")

# --- MÓDULO 2: INVENTÁRIO ---
elif menu == "📦 Inventário":
    st.title("Controle de Estoque")
    tab_ver, tab_add = st.tabs(["Produtos Ativos", "Cadastrar Novo"])
    
    with tab_ver:
        if not st.session_state.produtos.empty:
            st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
            st.divider()
            st.subheader("Ações Rápidas")
            id_edit = st.selectbox("Escolha o ID do Produto", st.session_state.produtos["ID"])
            if st.button("Excluir Item Selecionado", type="primary"):
                st.session_state.produtos = st.session_state.produtos[st.session_state.produtos["ID"] != id_edit]
                salvar(st.session_state.produtos, st.session_state.vendas)
                st.rerun()
        else:
            st.info("Nenhum produto cadastrado.")

    with tab_add:
        with st.form("novo_p", clear_on_submit=True):
            n = st.text_input("Nome da Embalagem")
            col_a, col_b, col_c = st.columns(3)
            custo = col_a.number_input("Preço de Custo", min_value=0.0)
            venda = col_b.number_input("Preço de Venda", min_value=0.0)
            est = col_c.number_input("Qtd Inicial", min_value=0)
            if st.form_submit_button("Confirmar Cadastro"):
                novo_id = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 1001
                novo_item = pd.DataFrame([{"ID": novo_id, "Nome": n, "Custo": custo, "Venda": venda, "Estoque": est}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo_item], ignore_index=True)
                salvar(st.session_state.produtos, st.session_state.vendas)
                st.success("Produto Ativado!")
                st.rerun()

# --- MÓDULO 3: PDV ---
elif menu == "🛒 PDV (Vendas)":
    st.title("Frente de Caixa")
    if st.session_state.produtos.empty:
        st.warning("Adicione produtos no inventário primeiro.")
    else:
        with st.container(border=True):
            p_nome = st.selectbox("Produto", st.session_state.produtos["Nome"])
            p_qtd = st.number_input("Quantidade", min_value=1, value=1)
            
            p_dados = st.session_state.produtos[st.session_state.produtos["Nome"] == p_nome].iloc[0]
            total_venda = p_dados["Venda"] * p_qtd
            lucro_venda = (p_dados["Venda"] - p_dados["Custo"]) * p_qtd
            
            st.subheader(f"Total: R$ {total_venda:,.2f}")
            
            if st.button("Finalizar Venda"):
                if p_dados["Estoque"] >= p_qtd:
                    venda_log = pd.DataFrame([{"Data": datetime.now(), "Produto": p_nome, "Qtd": p_qtd, "Total": total_venda, "Lucro": lucro_venda}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, venda_log], ignore_index=True)
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == p_nome, "Estoque"] -= p_qtd
                    salvar(st.session_state.produtos, st.session_state.vendas)
                    st.toast("Venda registrada com sucesso!")
                    st.rerun()
                else:
                    st.error("Estoque insuficiente!")

# --- MÓDULO 4: RELATÓRIOS ---
elif menu == "📑 Relatórios":
    st.title("Histórico de Operações")
    st.dataframe(st.session_state.vendas, use_container_width=True)
    csv = st.session_state.vendas.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Planilha Excel", csv, "vendas_embasserra.csv", "text/csv")