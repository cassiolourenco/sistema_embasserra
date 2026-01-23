import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# 1. CONFIGURAÇÃO DE ALTA PERFORMANCE
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide", initial_sidebar_state="expanded")

# 2. CSS INDUSTRIAL SUPREMO (A FLECHA AZUL ESTÁ AQUI)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    
    /* FIX DA FLECHA AZUL - ALVO DIRETO NO SVG DO STREAMLIT */
    div[data-baseweb="select"] svg {
        fill: #58a6ff !important;
        color: #58a6ff !important;
        width: 1.8rem !important;
        height: 1.8rem !important;
        display: block !important;
        visibility: visible !important;
    }

    /* ESTILO DOS CARDS DE MÉTRICA */
    div[data-testid="stMetric"] {
        background: #0d1117;
        border: 1px solid #30363d;
        border-left: 5px solid #58a6ff !important;
        padding: 15px !important;
        border-radius: 5px;
    }

    /* BOTÕES PREMIUM */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
        color: white !important;
        font-family: 'Syncopate', sans-serif;
        border: none !important;
        border-radius: 4px;
        padding: 12px;
        font-size: 12px;
        letter-spacing: 2px;
    }

    h1, h2, h3 { font-family: 'Syncopate', sans-serif; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# 3. MOTOR DE DADOS (DATABASE LOCAL)
def load_db():
    p_file, v_file = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p_file) if os.path.exists(p_file) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    df_v = pd.read_csv(v_file) if os.path.exists(v_file) else pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"])
    if not df_v.empty: df_v['Data'] = pd.to_datetime(df_v['Data'])
    return df_p, df_v

def save_db(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = load_db()

# 4. MENU LATERAL TURBINADO
with st.sidebar:
    st.markdown("### 📦 EMBASSERRA LOG")
    menu = st.radio("SISTEMA", ["DASHBOARD", "ESTOQUE PROFISSIONAL", "TERMINAL DE VENDAS", "HISTÓRICO COMPLETO"])
    st.divider()
    st.info(f"Último login: {datetime.now().strftime('%H:%M')}")

# 5. DASHBOARD COM MIX DE SAÍDA E EVOLUÇÃO
if menu == "DASHBOARD":
    st.title("📊 PERFORMANCE")
    v = st.session_state.vendas
    if not v.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("FATURAMENTO ACUMULADO", f"R$ {v['Total'].sum():,.2f}")
        c2.metric("LUCRO LÍQUIDO", f"R$ {v['Lucro'].sum():,.2f}")
        c3.metric("MÉDIA POR CARGA", f"R$ {(v['Total'].mean()):,.2f}")

        col_left, col_right = st.columns(2)
        with col_left:
            fig_pizza = px.pie(v, names='Produto', values='Total', hole=0.5, template="plotly_dark", title="Mix de Produtos")
            st.plotly_chart(fig_pizza, use_container_width=True)
        with col_right:
            v_agrupada = v.groupby(v['Data'].dt.date)['Total'].sum().reset_index()
            fig_linha = px.line(v_agrupada, x='Data', y='Total', title="Evolução Financeira", template="plotly_dark")
            fig_linha.update_traces(line_color='#58a6ff')
            st.plotly_chart(fig_linha, use_container_width=True)
    else:
        st.warning("Nenhuma venda registrada até o momento.")

# 6. ESTOQUE COMPLETO (EDITAR / EXCLUIR / CADASTRAR)
elif menu == "ESTOQUE PROFISSIONAL":
    st.title("📦 GESTÃO DE MATERIAIS")
    tab1, tab2, tab3 = st.tabs(["ESTOQUE ATUAL", "NOVO MATERIAL", "EDITAR / EXCLUIR"])
    
    with tab1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
        
    with tab2:
        with st.form("add_form"):
            n_prod = st.text_input("NOME DO MATERIAL")
            c_prod = st.number_input("CUSTO UNITÁRIO")
            v_prod = st.number_input("PREÇO DE VENDA")
            q_prod = st.number_input("QUANTIDADE EM ESTOQUE", step=1)
            if st.form_submit_button("CADASTRAR ITEM"):
                novo = pd.DataFrame([{"ID": len(st.session_state.produtos)+1, "Nome": n_prod, "Custo": c_prod, "Venda": v_prod, "Estoque": q_prod}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, novo], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success("Produto cadastrado!")
                st.rerun()

    with tab3:
        if not st.session_state.produtos.empty:
            sel_edit = st.selectbox("SELECIONE O ITEM PARA ALTERAR", st.session_state.produtos["Nome"])
            idx = st.session_state.produtos[st.session_state.produtos["Nome"] == sel_edit].index[0]
            with st.form("edit_form"):
                en = st.text_input("Novo Nome", st.session_state.produtos.loc[idx, "Nome"])
                ec = st.number_input("Novo Custo", value=float(st.session_state.produtos.loc[idx, "Custo"]))
                ev = st.number_input("Nova Venda", value=float(st.session_state.produtos.loc[idx, "Venda"]))
                ee = st.number_input("Novo Estoque", value=int(st.session_state.produtos.loc[idx, "Estoque"]))
                col_b1, col_b2 = st.columns(2)
                if col_b1.form_submit_button("SALVAR ALTERAÇÕES"):
                    st.session_state.produtos.loc[idx, ["Nome", "Custo", "Venda", "Estoque"]] = [en, ec, ev, ee]
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success("Atualizado!")
                    st.rerun()
                if col_b2.form_submit_button("EXCLUIR PRODUTO"):
                    st.session_state.produtos = st.session_state.produtos.drop(idx)
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.rerun()

# 7. TERMINAL DE VENDAS (FOCO NA FLECHA E OPERAÇÃO)
elif menu == "TERMINAL DE VENDAS":
    st.title("🚛 SAÍDA DE CARGA")
    if st.session_state.produtos.empty:
        st.error("Adicione produtos no estoque primeiro!")
    else:
        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            escolha = st.selectbox("PRODUTO EM CATÁLOGO", st.session_state.produtos["Nome"]) # A FLECHA TA AQUI!
        with col_v2:
            placa = st.text_input("PLACA DO VEÍCULO").upper()
        
        qtd_venda = st.number_input("QUANTIDADE (UN)", min_value=1, step=1)
        
        item_v = st.session_state.produtos[st.session_state.produtos["Nome"] == escolha].iloc[0]
        total_v = item_v['Venda'] * qtd_venda
        
        st.markdown(f"<h1 style='text-align: center; color: #58a6ff;'>VALOR TOTAL: R$ {total_v:,.2f}</h1>", unsafe_allow_html=True)
        
        if st.button("CONFIRMAR DESPACHO"):
            if item_v['Estoque'] >= qtd_venda:
                luc_v = (item_v['Venda'] - item_v['Custo']) * qtd_venda
                nova_v = pd.DataFrame([{"Data": datetime.now(), "Produto": escolha, "Qtd": qtd_venda, "Total": total_v, "Lucro": luc_v, "Placa": placa}])
                st.session_state.vendas = pd.concat([st.session_state.vendas, nova_v], ignore_index=True)
                st.session_state.produtos.loc[st.session_state.produtos["Nome"] == escolha, "Estoque"] -= qtd_venda
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success(f"Venda de {escolha} registrada!")
                st.rerun()
            else:
                st.error("QUANTIDADE INSUFICIENTE EM ESTOQUE!")

# 8. HISTÓRICO COMPLETO
elif menu == "HISTÓRICO COMPLETO":
    st.title("📜 REGISTROS")
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
    if st.button("LIMPAR TODO HISTÓRICO (CUIDADO)"):
        st.session_state.vendas = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"])
        save_db(st.session_state.produtos, st.session_state.vendas)
        st.rerun()
