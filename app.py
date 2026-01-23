import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# 1. CONFIGURAÇÃO DE ALTO NÍVEL
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide", initial_sidebar_state="expanded")

# 2. DESIGN INDUSTRIAL PREMIUM (FIX DA SETA + VISUAL CLEAN)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}

    /* Sidebar Estilizada */
    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    .sidebar-brand { font-family: 'Syncopate', sans-serif; color: #58a6ff; font-size: 1.1rem; letter-spacing: 3px; padding: 10px 0px; text-align: center; }

    /* Cards de Métricas */
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-top: 4px solid #58a6ff !important;
        border-radius: 4px !important;
        padding: 20px !important;
    }

    /* FIX DA SETA DO CATÁLOGO (O QUE TINHA SUMIDO) */
    div[data-baseweb="select"] svg {
        fill: #58a6ff !important;
        display: block !important;
        width: 25px !important;
        height: 25px !important;
    }
    
    /* Botão de Comando */
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
        transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 0 20px rgba(88, 166, 255, 0.4); }

    .section-header {
        font-family: 'Syncopate', sans-serif;
        font-size: 1.2rem;
        color: #f0f6fc;
        border-left: 5px solid #58a6ff;
        padding-left: 15px;
        margin: 25px 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ENGINE DE DADOS
def load_db():
    p, v = "produtos.csv", "vendas.csv"
    df_p = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["ID", "Nome", "Custo", "Venda", "Estoque"])
    if os.path.exists(v):
        df_v = pd.read_csv(v)
        df_v['Data'] = pd.to_datetime(df_v['Data'])
    else:
        df_v = pd.DataFrame(columns=["Data", "Produto", "Qtd", "Total", "Lucro", "Placa"])
    return df_p, df_v

def save_db(p, v):
    p.to_csv("produtos.csv", index=False)
    v.to_csv("vendas.csv", index=False)

if 'produtos' not in st.session_state:
    st.session_state.produtos, st.session_state.vendas = load_db()

# 4. SISTEMA DE LOGIN (SEGURANÇA)
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align: center; font-family:Syncopate; color:#58a6ff;'>TERMINAL EMBASSERRA</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login_gate"):
            pwd = st.text_input("SENHA DE ACESSO", type="password")
            if st.form_submit_button("DESBLOQUEAR"):
                if pwd == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
    st.stop()

# 5. SIDEBAR NAVEGAÇÃO
with st.sidebar:
    st.markdown('<p class="sidebar-brand">EMBASSERRA OS</p>', unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO", ["📊 DASHBOARD", "📦 ESTOQUE / EDITAR", "🚛 VENDA / SAÍDA", "📜 REGISTROS"])
    st.divider()
    if st.button("🔒 BLOQUEAR SISTEMA"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 6. MÓDULO: DASHBOARD
if menu == "📊 DASHBOARD":
    st.markdown('<p class="section-header">Monitoramento de Performance</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    fatur = st.session_state.vendas['Total'].sum()
    lucro = st.session_state.vendas['Lucro'].sum()
    c1.metric("FATURAMENTO TOTAL", f"R$ {fatur:,.2f}")
    c2.metric("LUCRO ESTIMADO", f"R$ {lucro:,.2f}")
    c3.metric("TOTAL DE CARGAS", len(st.session_state.vendas))

    if not st.session_state.vendas.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            fig1 = px.area(st.session_state.vendas.sort_values('Data'), x='Data', y='Total', title="Fluxo de Caixa", template="plotly_dark")
            fig1.update_traces(line_color='#58a6ff')
            st.plotly_chart(fig1, use_container_width=True)
        with col_b:
            fig2 = px.pie(st.session_state.vendas, names='Produto', values='Total', hole=0.4, title="Mix de Produtos", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

# 7. MÓDULO: ESTOQUE / EDITAR
elif menu == "📦 ESTOQUE / EDITAR":
    st.markdown('<p class="section-header">Gestão de Materiais</p>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["ESTOQUE ATUAL", "CADASTRAR NOVO", "EDITAR / EXCLUIR"])
    
    with t1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    
    with t2:
        with st.form("form_add"):
            n = st.text_input("NOME DO MATERIAL")
            c_a, c_b, c_c = st.columns(3)
            pc = c_a.number_input("CUSTO UNITÁRIO", format="%.2f")
            pv = c_b.number_input("PREÇO DE VENDA", format="%.2f")
            pq = c_c.number_input("ESTOQUE INICIAL", step=1)
            if st.form_submit_button("SALVAR ITEM"):
                nid = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 100
                new_row = pd.DataFrame([{"ID": nid, "Nome": n, "Custo": pc, "Venda": pv, "Estoque": pq}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, new_row], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.success("ITEM CADASTRADO!")
                st.rerun()

    with t3:
        if not st.session_state.produtos.empty:
            sel_prod = st.selectbox("Selecione para Alterar", st.session_state.produtos["Nome"])
            idx = st.session_state.produtos[st.session_state.produtos["Nome"] == sel_prod].index[0]
            with st.form("form_edit"):
                en = st.text_input("Editar Nome", value=st.session_state.produtos.loc[idx, "Nome"])
                ec1, ec2, ec3 = st.columns(3)
                ec = ec1.number_input("Custo", value=float(st.session_state.produtos.loc[idx, "Custo"]))
                ev = ec2.number_input("Venda", value=float(st.session_state.produtos.loc[idx, "Venda"]))
                ee = ec3.number_input("Estoque", value=int(st.session_state.produtos.loc[idx, "Estoque"]))
                b_up, b_rm = st.columns(2)
                if b_up.form_submit_button("ATUALIZAR"):
                    st.session_state.produtos.loc[idx, ["Nome", "Custo", "Venda", "Estoque"]] = [en, ec, ev, ee]
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success("DADOS ATUALIZADOS!")
                    st.rerun()
                if b_rm.form_submit_button("EXCLUIR PERMANENTEMENTE"):
                    st.session_state.produtos = st.session_state.produtos.drop(idx)
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.warning("ITEM REMOVIDO!")
                    st.rerun()

# 8. MÓDULO: VENDA / SAÍDA (PDV + PLACA)
elif menu == "🚛 VENDA / SAÍDA":
    st.markdown('<p class="section-header">Terminal de Despacho</p>', unsafe_allow_html=True)
    if st.session_state.produtos.empty:
        st.warning("Não há produtos cadastrados no sistema.")
    else:
        with st.container():
            col_sel, col_placa = st.columns([2, 1])
            p_venda = col_sel.selectbox("PRODUTO NO CATÁLOGO", st.session_state.produtos["Nome"])
            placa = col_placa.text_input("PLACA DO VEÍCULO").upper()
            
            qtd = st.number_input("QUANTIDADE (VOLUMES)", min_value=1, step=1)
            
            item_v = st.session_state.produtos[st.session_state.produtos["Nome"] == p_venda].iloc[0]
            total_v = item_v['Venda'] * qtd
            
            st.divider()
            st.markdown(f"<h1 style='color:#58a6ff; font-family:Syncopate; margin:0;'>TOTAL: R$ {total_v:,.2f}</h1>", unsafe_allow_html=True)
            st.write(f"Estoque disponível após saída: {int(item_v['Estoque'] - qtd)}")
            
            if st.button("CONFIRMAR SAÍDA E BAIXAR ESTOQUE"):
                if item_v['Estoque'] >= qtd:
                    # Registrar Venda
                    lucro_v = (item_v['Venda'] - item_v['Custo']) * qtd
                    venda_df = pd.DataFrame([{"Data": datetime.now(), "Produto": p_venda, "Qtd": qtd, "Total": total_v, "Lucro": lucro_v, "Placa": placa}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, venda_df], ignore_index=True)
                    
                    # Atualizar Estoque
                    st.session_state.produtos.loc[st.session_state.produtos["Nome"] == p_venda, "Estoque"] -= qtd
                    
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success(f"CARGA REGISTRADA - PLACA: {placa}")
                    st.rerun()
                else:
                    st.error("ERRO: ESTOQUE INSUFICIENTE!")

# 9. MÓDULO: REGISTROS
elif menu == "📜 REGISTROS":
    st.markdown('<p class="section-header">Log de Operações</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
    
    if not st.session_state.vendas.empty:
        if st.button("GERAR PDF DA ÚLTIMA CARGA"):
            u = st.session_state.vendas.tail(1).iloc[0]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, "EMBASSERRA - ROMANEIO", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(190, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
            pdf.cell(190, 10, f"PLACA: {u['Placa']}", ln=True)
            pdf.cell(190, 10, f"MATERIAL: {u['Produto']}", ln=True)
            pdf.cell(190, 10, f"QUANTIDADE: {u['Qtd']} UN", ln=True)
            pdf.cell(190, 10, f"VALOR DECLARADO: R$ {u['Total']:.2f}", ln=True)
            pdf.ln(20)
            pdf.cell(190, 10, "ASSINATURA RESPONSAVEL: __________________________", ln=True)
            st.download_button("BAIXAR ROMANEIO", data=bytes(pdf.output()), file_name=f"romaneio_{u['Placa']}.pdf")
