import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# Mapeamentos
MAPA_TEXTO = {1: "Concordo", 2: "Parcialmente", 3: "Discordo"}
MAPA_GRAFICO = {1: "Sem Evidências", 2: "Parcialmente Evidenciado", 3: "Evidências Claras"}
CORES_FINAIS = {"Sem Evidências": "#2A6FB9", "Parcialmente Evidenciado": "#F4D03F", "Evidências Claras": "#D32F2F"}
ORDEM_STATUS = ["Sem Evidências", "Parcialmente Evidenciado", "Evidências Claras"]

perguntas_de_risco = [
    "São observadas atitudes de assédio, ironia ou desrespeito?",
    "O trabalho exige ritmo acelerado sem pausas adequadas?",
    "Existem queixas sobre falta de recursos ou pessoal insuficiente?",
    "Existem conflitos interpessoais ou isolamento de pessoas?",
    "A equipe demonstra sinais de fadiga, estresse ou irritabilidade constante?",
    "Há relatos de sobrecarga de tarefas ou prazos excessivos?",
    "Há rigidez excessiva em procedimentos, sem margem de flexibilidade?",
    "Há queixas sobre tratamento desigual ou injustiça?",
    "Há interrupções frequentes que prejudicam a concentração e a produtividade?"
]

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

# --- LÓGICA DO FUNCIONÁRIO ---
if menu == "Funcionário":
    st.title("👤 Área do Funcionário")
    cpf = st.text_input("Digite seu CPF:")
    
    if cpf:
        func_data = supabase.table("funcionarios").select("*").eq("cpf", cpf).execute().data
        if func_data:
            funcionario = func_data[0]
            st.success(f"Bem-vindo, {funcionario['nome']}!")
            perguntas_data = supabase.table("perguntas").select("*").execute().data
            if perguntas_data:
                with st.form("form_questionario"):
                    respostas = {}
                    for p in perguntas_data:
                        respostas[p['id']] = st.radio(
                            p['pergunta'], [1, 2, 3], format_func=lambda x: MAPA_TEXTO[x], key=f"p_{p['id']}"
                        )
                    if st.form_submit_button("Enviar Respostas"):
                        for p_id, val in respostas.items():
                            supabase.table("respostas").insert({
                                "funcionarios_id": funcionario['id'], "pergunta_id": p_id,
                                "resposta": val, "empresa_id": funcionario['empresa_id']
                            }).execute()
                        st.success("Respostas enviadas!")

# --- LÓGICA DO GESTOR ---
else:
    st.title("📊 Painel do Gestor")
    empresas_data = supabase.table("empresas").select("id, nome_empresa").execute().data
    
    if empresas_data:
        nomes_empresas = {e['nome_empresa']: e['id'] for e in empresas_data}
        empresa_selecionada = st.selectbox("Selecione a Empresa", list(nomes_empresas.keys()))
