import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# --- CONFIGURAÇÃO DE ALTO NÍVEL ---
st.set_page_config(page_title="EMBASSERRA | OS", layout="wide", initial_sidebar_state="expanded")

# --- DESIGN INDUSTRIAL PREMIUM (SEM CARA DE IA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}

    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    .sidebar-brand { font-family: 'Syncopate', sans-serif; color: #58a6ff; font-size: 1.1rem; letter-spacing: 3px; padding: 10px 0px; }

    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-top: 4px solid #58a6ff !important;
        border-radius: 4px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
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
        font-size: 1.3rem;
        color: #f0f6fc;
        border-left: 5px solid #58a6ff;
        padding-left: 15px;
        margin: 30px 0px;
    }
    
    .sale-card {
        background: #0d1117;
        padding: 20px;
        border: 1px solid #30363d;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NÚCLEO DE DADOS ---
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

# --- SEGURANÇA (LOGIN) ---
if "autenticado" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align: center; font-family:Syncopate; color:#58a6ff;'>TERMINAL EMBASSERRA</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("gate"):
            pwd = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("AUTORIZAR"):
                if pwd == "admin123":
                    st.session_state.autenticado = True
                    st.rerun()
    st.stop()

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.markdown('<p class="sidebar-brand">EMBASSERRA OS</p>', unsafe_allow_html=True)
    menu = st.radio("MÓDULOS", ["📊 DASHBOARD", "📦 ESTOQUE / EDITAR", "🚛 VENDA / SAÍDA", "📜 REGISTROS"])
    st.divider()
    if st.button("🔒 BLOQUEAR TERMINAL"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- DASHBOARD (GRÁFICOS MANTIDOS) ---
if menu == "📊 DASHBOARD":
    st.markdown('<p class="section-header">Performance Financeira</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("FATURAMENTO", f"R$ {st.session_state.vendas['Total'].sum():,.2f}")
    c2.metric("LUCRO LÍQUIDO", f"R$ {st.session_state.vendas['Lucro'].sum():,.2f}")
    c3.metric("TRANSAÇÕES", len(st.session_state.vendas))

    if not st.session_state.vendas.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig1 = px.area(st.session_state.vendas.sort_values('Data'), x='Data', y='Total', title="Fluxo de Caixa", template="plotly_dark")
            fig1.update_traces(line_color='#58a6ff')
            st.plotly_chart(fig1, use_container_width=True)
        with col_g2:
            fig2 = px.pie(st.session_state.vendas, names='Produto', values='Total', hole=0.4, title="Mix de Saída", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

# --- ESTOQUE / EDITAR (MANTIDO) ---
elif menu == "📦 ESTOQUE / EDITAR":
    st.markdown('<p class="section-header">Gestão de Inventário</p>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["ESTOQUE ATUAL", "NOVO ITEM", "EDITAR / EXCLUIR"])
    
    with t1:
        st.dataframe(st.session_state.produtos, use_container_width=True, hide_index=True)
    
    with t2:
        with st.form("new_p"):
            n = st.text_input("NOME")
            ca, cb, cc = st.columns(3)
            pc = ca.number_input("CUSTO", format="%.2f")
            pv = cb.number_input("VENDA", format="%.2f")
            pq = cc.number_input("QTD INICIAL", step=1)
            if st.form_submit_button("CADASTRAR"):
                nid = int(st.session_state.produtos["ID"].max() + 1) if not st.session_state.produtos.empty else 100
                new_row = pd.DataFrame([{"ID": nid, "Nome": n, "Custo": pc, "Venda": pv, "Estoque": pq}])
                st.session_state.produtos = pd.concat([st.session_state.produtos, new_row], ignore_index=True)
                save_db(st.session_state.produtos, st.session_state.vendas)
                st.rerun()

    with t3:
        if not st.session_state.produtos.empty:
            sel = st.selectbox("Escolher para Modificar", st.session_state.produtos["Nome"])
            idx = st.session_state.produtos[st.session_state.produtos["Nome"] == sel].index[0]
            with st.form("edit_form"):
                en = st.text_input("Nome", value=st.session_state.produtos.loc[idx, "Nome"])
                e1, e2, e3 = st.columns(3)
                ec = e1.number_input("Custo", value=float(st.session_state.produtos.loc[idx, "Custo"]))
                ev = e2.number_input("Venda", value=float(st.session_state.produtos.loc[idx, "Venda"]))
                ee = e3.number_input("Estoque", value=int(st.session_state.produtos.loc[idx, "Estoque"]))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("ATUALIZAR"):
                    st.session_state.produtos.loc[idx, ["Nome", "Custo", "Venda", "Estoque"]] = [en, ec, ev, ee]
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success("Atualizado!")
                    st.rerun()
                if b2.form_submit_button("EXCLUIR"):
                    st.session_state.produtos = st.session_state.produtos.drop(idx)
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.rerun()

# --- VENDA / SAÍDA (RESTAURADO E COMPLETO) ---
elif menu == "🚛 VENDA / SAÍDA":
    st.markdown('<p class="section-header">Terminal de Venda e Carga</p>', unsafe_allow_html=True)
    
    if st.session_state.produtos.empty:
        st.warning("Cadastre produtos no inventário primeiro.")
    else:
        with st.container():
            st.markdown('<div class="sale-card">', unsafe_allow_html=True)
            prods = st.session_state.produtos["Nome"].tolist()
            
            c_v1, c_v2 = st.columns([2, 1])
            p_venda = c_v1.selectbox("PRODUTO", prods)
            placa = c_v2.text_input("PLACA DO CAMINHÃO").upper()
            
            q_venda = st.number_input("QUANTIDADE (UNIDADES/VOLUMES)", min_value=1, step=1)
            
            # Cálculo em tempo real
            item = st.session_state.produtos[st.session_state.produtos["Nome"] == p_venda].iloc[0]
            total_v = item['Venda'] * q_venda
            lucro_v = (item['Venda'] - item['Custo']) * q_venda
            estoque_atual = item['Estoque']
            
            st.divider()
            st.markdown(f"<h1 style='color:#58a6ff; margin:0;'>TOTAL: R$ {total_v:,.2f}</h1>", unsafe_allow_html=True)
            st.write(f"Estoque após venda: {int(estoque_atual - q_venda)}")
            
            if st.button("PROCESSAR VENDA E BAIXAR ESTOQUE"):
                if estoque_atual >= q_venda:
                    # Registra a venda
                    nova_venda = pd.DataFrame([{
                        "Data": datetime.now(), 
                        "Produto": p_venda, 
                        "Qtd": q_venda, 
                        "Total": total_v, 
                        "Lucro": lucro_v, 
                        "Placa": placa
                    }])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, nova_venda], ignore_index=True)
                    
                    # Baixa estoque
                    idx_p = st.session_state.produtos[st.session_state.produtos["Nome"] == p_venda].index[0]
                    st.session_state.produtos.at[idx_p, "Estoque"] -= q_venda
                    
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success(f"VENDA REALIZADA! Romaneio gerado para placa {placa}")
                    st.rerun()
                else:
                    st.error("ERRO: ESTOQUE INSUFICIENTE PARA ESTA QUANTIDADE.")
            st.markdown('</div>', unsafe_allow_html=True)

# --- REGISTROS ---
elif menu == "📜 REGISTROS":
    st.markdown('<p class="section-header">Histórico Operacional</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.vendas.sort_values('Data', ascending=False), use_container_width=True, hide_index=True)
    
    if not st.session_state.vendas.empty:
        if st.button("GERAR PDF DA ÚLTIMA SAÍDA"):
            u = st.session_state.vendas.tail(1).iloc[0]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, "EMBASSERRA - ROMANEIO DE CARGA", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(190, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
            pdf.cell(190, 10, f"PLACA: {u['Placa']}", ln=True)
            pdf.cell(190, 10, f"PRODUTO: {u['Produto']} | QTD: {u['Qtd']}", ln=True)
            pdf.cell(190, 10, f"TOTAL: R$ {u['Total']:.2f}", ln=True)
            pdf.ln(20)
            pdf.cell(190, 10, "ASSINATURA: _________________________________", ln=True)
            st.download_button("BAIXAR PDF", data=bytes(pdf.output()), file_name="romaneio.pdf")
