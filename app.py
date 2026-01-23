# --- CSS REFINADO (COM CORREÇÃO DA SETA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Space+Grotesk:wght@300;500;700&display=swap');

    .stApp { background: #010409; color: #e6edf3; font-family: 'Space Grotesk', sans-serif; }
    
    /* Esconder o que não presta */
    #MainMenu, footer, header {visibility: hidden;}

    /* Sidebar pica */
    [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d; }
    .sidebar-brand { font-family: 'Syncopate', sans-serif; color: #58a6ff; font-size: 1.1rem; letter-spacing: 3px; padding: 10px 0px; }

    /* Cards de Performance (Estilo os que você tem no print) */
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-top: 4px solid #58a6ff !important;
        border-radius: 4px !important;
        padding: 20px !important;
    }

    /* FIX DA SETA DO CATÁLOGO: Garante que o ícone do selectbox apareça */
    div[data-baseweb="select"] svg {
        fill: #58a6ff !important;
        display: block !important;
    }
    
    .stSelectbox label, .stTextInput label {
        font-family: 'Syncopate', sans-serif;
        font-size: 10px !important;
        color: #8b949e !important;
        letter-spacing: 1px;
    }

    /* Botão Industrial */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1f6feb, #58a6ff) !important;
        color: white !important;
        border: none !important;
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        padding: 15px;
        text-transform: uppercase;
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MÓDULO DE VENDA (VERIFIQUE SE ESTÁ ASSIM) ---
if menu == "🚛 VENDA / SAÍDA":
    st.markdown('<p class="section-header">PONTO DE SAÍDA</p>', unsafe_allow_html=True)
    
    if st.session_state.produtos.empty:
        st.warning("Estoque vazio. Cadastre materiais primeiro.")
    else:
        # Colocamos um container para organizar o visual
        with st.container():
            prods = st.session_state.produtos["Nome"].tolist()
            
            c1, c2 = st.columns([2, 1])
            with c1:
                # Onde a flecha tinha sumido
                p_venda = st.selectbox("SELECIONAR PRODUTO", prods, key="cat_venda")
            with c2:
                placa = st.text_input("PLACA DO CAMINHÃO", placeholder="OPCIONAL").upper()
            
            qtd = st.number_input("QUANTIDADE", min_value=1, step=1, value=1)
            
            # Buscando dados do item selecionado
            item = st.session_state.produtos[st.session_state.produtos["Nome"] == p_venda].iloc[0]
            total_v = item['Venda'] * qtd
            
            st.markdown(f"<h1 style='color:#f0f6fc; font-family:Syncopate;'>TOTAL: R$ {total_v:,.2f}</h1>", unsafe_allow_html=True)
            
            if st.button("PROCESSAR VENDA"):
                if item['Estoque'] >= qtd:
                    # Lógica de salvar e baixar estoque
                    lucro_v = (item['Venda'] - item['Custo']) * qtd
                    venda_data = pd.DataFrame([{
                        "Data": datetime.now(), "Produto": p_venda, 
                        "Qtd": qtd, "Total": total_v, "Lucro": lucro_v, "Placa": placa
                    }])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, venda_data], ignore_index=True)
                    
                    # Baixa
                    idx = st.session_state.produtos[st.session_state.produtos["Nome"] == p_venda].index[0]
                    st.session_state.produtos.at[idx, "Estoque"] -= qtd
                    
                    save_db(st.session_state.produtos, st.session_state.vendas)
                    st.success(f"CARGA REGISTRADA: {p_venda}")
                    st.rerun()
                else:
                    st.error("ESTOQUE INSUFICIENTE")
