import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# CSS: Fonte preta, legível, 16px
st.markdown("""
    <style>
    .stApp { font-family: sans-serif; font-size: 16px !important; color: #000000 !important; }
    h1, h2, h3, .stMarkdown { color: #000000 !important; font-weight: bold !important; }
    div[data-testid="stDataFrame"] { font-size: 15px !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

if menu == "Funcionário":
    st.title("Questionário")
    st.info("Formulário ativo.")
else:
    st.title("Painel do Gestor")
    
    empresas_data = supabase.table("empresas").select("id, nome_empresa").execute().data
    if empresas_data:
        nomes_empresas = {e['nome_empresa']: e['id'] for e in empresas_data}
        empresa_selecionada = st.selectbox("Selecione a Empresa", list(nomes_empresas.keys()))

        if st.button("CARREGAR DADOS"):
            # Ajuste: buscando 'nome' na tabela 'funcionarios' relacionada
            res = supabase.table("respostas").select("resposta, perguntas(pergunta), funcionarios(nome)").eq("empresa_id", nomes_empresas[empresa_selecionada]).execute()
            
            if res.data:
                df = pd.DataFrame(res.data)
                df['Pergunta'] = df['perguntas'].apply(lambda x: x.get('pergunta', ''))
                df['Funcionario'] = df['funcionarios'].apply(lambda x: x.get('nome', 'N/A') if x else 'N/A')
                
                mapa_res = {1: "Discordo", 2: "Parcialmente", 3: "Concordo"}
                df['Resposta'] = df['resposta'].map(mapa_res)
                
                # Gráfico
                fig = px.bar(df.groupby(['Pergunta', 'Resposta']).size().reset_index(name='Contagem'), 
                             y="Pergunta", x="Contagem", color="Resposta", orientation='h',
                             color_discrete_map={"Discordo": "#B22222", "Parcialmente": "#DAA520", "Concordo": "#00008B"},
                             barmode='stack')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela organizada sem CPF
                st.subheader("Detalhes das Respostas")
                st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta']], use_container_width=True)
