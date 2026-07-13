import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# CSS Profissional
st.markdown("""
    <style>
    .stApp { font-family: sans-serif; }
    h1, h2, h3, .stMarkdown { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

CORES_FINAIS = {"Sem Evidências": "#2A6FB9", "Parcialmente Evidenciado": "#F4D03F", "Evidências Claras": "#D32F2F"}
ORDEM_STATUS = ["Sem Evidências", "Parcialmente Evidenciado", "Evidências Claras"]

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

# --- LÓGICA DO FUNCIONÁRIO ---
if menu == "Funcionário":
    st.title("👤 Área do Funcionário")
    cpf = st.text_input("Digite seu CPF:")
    
    if cpf:
        # Busca no Supabase
        func_data = supabase.table("funcionarios").select("*").eq("cpf", cpf).execute().data
        
        if func_data:
            funcionario = func_data[0]
            st.success(f"Bem-vindo, {funcionario['nome']}!")
            st.info("O sistema identificou seu cadastro. Carregando questionário...")
            # INSIRA AQUI O SEU CÓDIGO DE QUESTIONÁRIO ORIGINAL
        else:
            st.error("CPF não encontrado.")

# --- LÓGICA DO GESTOR ---
else:
    st.title("Painel do Gestor")
    empresas_data = supabase.table("empresas").select("id, nome_empresa").execute().data
    
    if empresas_data:
        nomes_empresas = {e['nome_empresa']: e['id'] for e in empresas_data}
        empresa_selecionada = st.selectbox("Selecione a Empresa", list(nomes_empresas.keys()))

        if st.button("CARREGAR DADOS"):
            res = supabase.table("respostas").select("resposta, perguntas(pergunta), funcionarios(nome)").eq("empresa_id", nomes_empresas[empresa_selecionada]).execute()
            
            if res.data:
                df = pd.DataFrame(res.data)
                df['Pergunta'] = df['perguntas'].apply(lambda x: x.get('pergunta', ''))
                df['Funcionario'] = df['funcionarios'].apply(lambda x: x.get('nome', 'N/A') if x else 'N/A')
                
                mapa_res = {1: "Evidências Claras", 2: "Parcialmente Evidenciado", 3: "Sem Evidências"}
                df['Resposta'] = df['resposta'].map(mapa_res)

                df_grouped = df.groupby(['Pergunta', 'Resposta']).size().reset_index(name='Contagem')

                tab1, tab2 = st.tabs(["📊 Visão Completa", "📑 Análise Individual por Status"])

                with tab1:
                    fig_geral = px.bar(df_grouped, y="Pergunta", x="Contagem", color="Resposta", 
                                       orientation='h', barmode='group',
                                       color_discrete_map=CORES_FINAIS,
                                       category_orders={"Resposta": ORDEM_STATUS})
                    st.plotly_chart(fig_geral, use_container_width=True)

                with tab2:
                    cols = st.columns(3)
                    for i, status in enumerate(ORDEM_STATUS):
                        with cols[i]:
                            df_s = df_grouped[df_grouped['Resposta'] == status]
                            fig_ind = px.bar(df_s, y="Pergunta", x="Contagem", title=status, 
                                             color_discrete_sequence=[CORES_FINAIS[status]], orientation='h')
                            st.plotly_chart(fig_ind, use_container_width=True)

                st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta']], use_container_width=True)
            else:
                st.warning("Nenhum dado encontrado.")
