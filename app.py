import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# Configuração
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .stApp { font-family: sans-serif; font-size: 16px !important; color: #000000 !important; }
    h1, h2, h3, .stMarkdown { color: #000000 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

if menu == "Funcionário":
    st.title("Questionário")
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
                df['Resposta'] = df['resposta'].map({1: "Discordo", 2: "Parcialmente", 3: "Concordo"})

                # Criando as abas
                tab1, tab2 = st.tabs(["📊 Visão Completa", "📑 Análise Individual por Status"])

                with tab1:
                    st.subheader("Gráfico Geral")
                    fig_geral = px.bar(df.groupby(['Pergunta', 'Resposta']).size().reset_index(name='Contagem'), 
                                       y="Pergunta", x="Contagem", color="Resposta", orientation='h',
                                       color_discrete_map={"Discordo": "#B22222", "Parcialmente": "#DAA520", "Concordo": "#00008B"})
                    st.plotly_chart(fig_geral, use_container_width=True)

                with tab2:
                    st.subheader("Gráficos Individuais")
                    cols = st.columns(3)
                    status_list = ["Discordo", "Parcialmente", "Concordo"]
                    cores = {"Discordo": "#B22222", "Parcialmente": "#DAA520", "Concordo": "#00008B"}
                    
                    for i, status in enumerate(status_list):
                        with cols[i]:
                            df_s = df[df['Resposta'] == status].groupby('Pergunta').size().reset_index(name='Contagem')
                            fig_ind = px.bar(df_s, y="Pergunta", x="Contagem", title=status, 
                                             color_discrete_sequence=[cores[status]], orientation='h')
                            fig_ind.update_layout(showlegend=False)
                            st.plotly_chart(fig_ind, use_container_width=True)

                st.subheader("Detalhes das Respostas")
                st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta']], use_container_width=True)
