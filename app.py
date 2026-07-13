import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# CSS para garantir fontes pretas, tamanho 16px e leitura confortável
st.markdown("""
    <style>
    .stApp { font-family: sans-serif; font-size: 16px !important; color: #000000 !important; }
    h1, h2, h3, .stMarkdown, .stText { color: #000000 !important; }
    div[data-testid="stDataFrame"] { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

# Alternância de modo
menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

if menu == "Funcionário":
    st.title("Questionário do Funcionário")
    cpf = st.text_input("Digite seu CPF para iniciar:")
    if cpf:
        st.write(f"Bem-vindo. Por favor, responda às perguntas abaixo:")
        # Aqui entra o seu formulário de preenchimento
else:
    st.title("Painel do Gestor")
    
    empresas_data = supabase.table("empresas").select("id, nome_empresa").execute().data
    if empresas_data:
        nomes_empresas = {e['nome_empresa']: e['id'] for e in empresas_data}
        empresa_selecionada = st.selectbox("Selecione a Empresa", list(nomes_empresas.keys()))

        if st.button("CARREGAR DADOS"):
            res = supabase.table("respostas").select("resposta, perguntas(pergunta)").eq("empresa_id", nomes_empresas[empresa_selecionada]).execute()
            
            if res.data:
                df = pd.DataFrame(res.data)
                # Extraindo o texto da pergunta
                df['Pergunta'] = df['perguntas'].apply(lambda x: x.get('pergunta', ''))
                
                # Mapeamento para texto legível
                mapa_respostas = {1: "Discordo", 2: "Parcialmente", 3: "Concordo"}
                df['Status_Texto'] = df['resposta'].map(mapa_respostas)
                
                # Gráfico
                fig = px.bar(df.groupby(['Pergunta', 'Status_Texto']).size().reset_index(name='Contagem'), 
                             y="Pergunta", x="Contagem", color="Status_Texto", orientation='h',
                             color_discrete_map={"Discordo": "#C0504D", "Parcialmente": "#FFEB3B", "Concordo": "#4F81BD"})
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela organizada
                st.subheader("Detalhes das Respostas")
                st.dataframe(df[['Pergunta', 'Status_Texto']], use_container_width=True)
            else:
                st.warning("Nenhum dado para esta empresa.")
