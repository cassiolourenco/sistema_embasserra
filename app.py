import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# 1. CONFIGURAÇÃO MASTER
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide")

# 2. CSS INDUSTRIAL COM FIX DA SETA (FORCE BLUE)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    
    /* --- FIX DA SETA DO SELECTBOX (CATÁLOGO) --- */
    div[data-baseweb="select"] svg {
        fill: #58a6ff !important; 
        display: block !important;
        visibility: visible !important;
        width: 25px !important;
        height: 25px !important;
    }
    div[data-baseweb="select"] {
        border: 1px solid #30363d !important;
        background-color: #0d1117 !important;
    }
    /* ------------------------------------------- */

    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-top: 4px solid #58a6ff !important;
        border-radius: 4px !important;
        padding: 20px !important;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
        color: white !important;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        border: none !important;
        padding: 15px;
    }
    
    h1, h2, h3 { font-family: 'Syncopate', sans-serif; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE DE DADOS
def load_data():
    if not os.path.exists("produtos.csv"):
        pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"]).to_csv("produtos.csv", index=False)
    if not os.path.exists("vendas.csv"):
        pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"]).to_csv("vendas.csv", index=False)
    return pd.read_csv("produtos.csv"), pd.read_csv("vendas.csv")

def save_data(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

st.session_state.produtos, st.session_state.vendas = load_data()

# 4. SIDEBAR
with st.sidebar:
    st.markdown("<h2 style='font-size:15px;'>EMBASSERRA OS</h2>", unsafe_allow_html=True)
    menu = st.radio("MENU", ["DASHBOARD", "ESTOQUE", "VENDAS"])

# 5. DASHBOARD
if menu == "DASHBOARD":
    st.title("PERFORMANCE")
    col1, col2, col3 = st.columns(3)
    
    vendas_df = st.session_state.vendas
    faturamento = vendas_df['Total'].sum() if not vendas_df.empty else 0
    lucro = vendas_df['Lucro'].sum() if not vendas_df.empty else 0
    
    col1.metric("FATURAMENTO", f"R$ {faturamento:,.2f}")
    col2.metric("LUCRO LÍQUIDO", f"R$ {lucro:,.2f}")
    col3.metric("TRANSAÇÕES", len(vendas_df))

    if not vendas_df.empty:
        fig = px.pie(vendas_df, names='Produto', values='Total', hole=0.4, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# 6. ESTOQUE
elif menu == "ESTOQUE":
    st.title("GESTÃO DE ITENS")
    with st.form("add_item"):
        n = st.text_input("NOME")
        c, v = st.columns(2)
        custo = c.number_input("CUSTO")
        venda = v.number_input("VENDA")
        qtd = st.number_input("ESTOQUE", step=1)
        if st.form_submit_button("CADASTRAR"):
            novo = pd.DataFrame([{"ID": 1, "Nome": n, "Custo": custo, "Venda": venda, "Estoque": qtd}])
            st.session_state.produtos = pd.concat([st.session_state.produtos, novo], ignore_index=True)
            save_data(st.session_state.produtos, st.session_state.vendas)
            st.rerun()
    st.dataframe(st.session_state.produtos, use_container_width=True)

# 7. VENDAS (ONDE A FLECHA APARECE)
elif menu == "VENDAS":
    st.title("SAÍDA DE CARGA")
    if st.session_state.produtos.empty:
        st.error("Cadastre produtos primeiro!")
    else:
        # AQUI É ONDE A SETA TINHA SUMIDO
        lista_prods = st.session_state.produtos["Nome"].tolist()
        prod_sel = st.selectbox("SELECIONE O PRODUTO NO CATÁLOGO", lista_prods)
        
        placa = st.text_input("PLACA DO CAMINHÃO").upper()
        qtd_venda = st.number_input("QUANTIDADE", min_value=1, step=1)
        
        item = st.session_state.produtos[st.session_state.produtos["Nome"] == prod_sel].iloc[0]
        total = item['Venda'] * qtd_venda
        
        st.subheader(f"TOTAL: R$ {total:,.2f}")
        
        if st.button("FINALIZAR VENDA"):
            if item['Estoque'] >= qtd_venda:
                lucro_v = (item['Venda'] - item['Custo']) * qtd_venda
                nova_venda = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Produto": prod_sel, "Qtd": qtd_venda, "Total": total, "Lucro": lucro_v, "Placa": placa
                }])
                st.session_state.vendas = pd.concat([st.session_state.vendas, nova_venda], ignore_index=True)
                st.session_state.produtos.loc[st.session_state.produtos["Nome"] == prod_sel, "Estoque"] -= qtd_venda
                save_data(st.session_state.produtos, st.session_state.vendas)
                st.success("VENDA REGISTRADA!")
                st.rerun()
            else:
                st.error("SEM ESTOQUE!")import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# 1. CONFIGURAÇÃO MASTER
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide")

# 2. CSS INDUSTRIAL COM FIX DA SETA (FORCE BLUE)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    
    /* --- FIX DA SETA DO SELECTBOX (CATÁLOGO) --- */
    div[data-baseweb="select"] svg {
        fill: #58a6ff !important; 
        display: block !important;
        visibility: visible !important;
        width: 25px !important;
        height: 25px !important;
    }
    div[data-baseweb="select"] {
        border: 1px solid #30363d !important;
        background-color: #0d1117 !important;
    }
    /* ------------------------------------------- */

    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-top: 4px solid #58a6ff !important;
        border-radius: 4px !important;
        padding: 20px !important;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
        color: white !important;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        border: none !important;
        padding: 15px;
    }
    
    h1, h2, h3 { font-family: 'Syncopate', sans-serif; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE DE DADOS
def load_data():
    if not os.path.exists("produtos.csv"):
        pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"]).to_csv("produtos.csv", index=False)
    if not os.path.exists("vendas.csv"):
        pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"]).to_csv("vendas.csv", index=False)
    return pd.read_csv("produtos.csv"), pd.read_csv("vendas.csv")

def save_data(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

st.session_state.produtos, st.session_state.vendas = load_data()

# 4. SIDEBAR
with st.sidebar:
    st.markdown("<h2 style='font-size:15px;'>EMBASSERRA OS</h2>", unsafe_allow_html=True)
    menu = st.radio("MENU", ["DASHBOARD", "ESTOQUE", "VENDAS"])

# 5. DASHBOARD
if menu == "DASHBOARD":
    st.title("PERFORMANCE")
    col1, col2, col3 = st.columns(3)
    
    vendas_df = st.session_state.vendas
    faturamento = vendas_df['Total'].sum() if not vendas_df.empty else 0
    lucro = vendas_df['Lucro'].sum() if not vendas_df.empty else 0
    
    col1.metric("FATURAMENTO", f"R$ {faturamento:,.2f}")
    col2.metric("LUCRO LÍQUIDO", f"R$ {lucro:,.2f}")
    col3.metric("TRANSAÇÕES", len(vendas_df))

    if not vendas_df.empty:
        fig = px.pie(vendas_df, names='Produto', values='Total', hole=0.4, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# 6. ESTOQUE
elif menu == "ESTOQUE":
    st.title("GESTÃO DE ITENS")
    with st.form("add_item"):
        n = st.text_input("NOME")
        c, v = st.columns(2)
        custo = c.number_input("CUSTO")
        venda = v.number_input("VENDA")
        qtd = st.number_input("ESTOQUE", step=1)
        if st.form_submit_button("CADASTRAR"):
            novo = pd.DataFrame([{"ID": 1, "Nome": n, "Custo": custo, "Venda": venda, "Estoque": qtd}])
            st.session_state.produtos = pd.concat([st.session_state.produtos, novo], ignore_index=True)
            save_data(st.session_state.produtos, st.session_state.vendas)
            st.rerun()
    st.dataframe(st.session_state.produtos, use_container_width=True)

# 7. VENDAS (ONDE A FLECHA APARECE)
elif menu == "VENDAS":
    st.title("SAÍDA DE CARGA")
    if st.session_state.produtos.empty:
        st.error("Cadastre produtos primeiro!")
    else:
        # AQUI É ONDE A SETA TINHA SUMIDO
        lista_prods = st.session_state.produtos["Nome"].tolist()
        prod_sel = st.selectbox("SELECIONE O PRODUTO NO CATÁLOGO", lista_prods)
        
        placa = st.text_input("PLACA DO CAMINHÃO").upper()
        qtd_venda = st.number_input("QUANTIDADE", min_value=1, step=1)
        
        item = st.session_state.produtos[st.session_state.produtos["Nome"] == prod_sel].iloc[0]
        total = item['Venda'] * qtd_venda
        
        st.subheader(f"TOTAL: R$ {total:,.2f}")
        
        if st.button("FINALIZAR VENDA"):
            if item['Estoque'] >= qtd_venda:
                lucro_v = (item['Venda'] - item['Custo']) * qtd_venda
                nova_venda = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Produto": prod_sel, "Qtd": qtd_venda, "Total": total, "Lucro": lucro_v, "Placa": placa
                }])
                st.session_state.vendas = pd.concat([st.session_state.vendas, nova_venda], ignore_index=True)
                st.session_state.produtos.loc[st.session_state.produtos["Nome"] == prod_sel, "Estoque"] -= qtd_venda
                save_data(st.session_state.produtos, st.session_state.vendas)
                st.success("VENDA REGISTRADA!")
                st.rerun()
            else:
                st.error("SEM ESTOQUE!")
