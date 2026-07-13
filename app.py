import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# CSS para visual profissional
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
        # Busca o funcionário pelo CPF
        func_data = supabase.table("funcionarios").select("*").eq("cpf", cpf).execute().data
        
        if func_data:
            funcionario = func_data[0]
            st.success(f"Bem-vindo, {funcionario['nome']}!")
            
            # AQUI: Coloque abaixo a lógica de renderização do seu questionário
            st.info("O sistema identificou seu cadastro. Carregando questionário...")
            
        else:
            st.error("CPF não encontrado. Verifique o número.")

# --- LÓGICA DO GESTOR ---
else:
    st.title("Painel do Gestor")
    empresas_data = supabase.table("empresas").select("id, nome_empresa").execute().data
    
    if empresas_data:
        nomes_empresas = {e['nome_empresa']: e['id'] for e in empresas_data}
        empresa_selecionada = st.selectbox("Selecione a Empresa", list(nomes_empresas.keys()))

        if st.button("CARREGAR
