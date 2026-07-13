import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# Mapeamento Global
MAPA_ROTULOS = {1: "Concordo", 2: "Parcialmente", 3: "Discordo"}
CORES_FINAIS = {"Concordo": "#2A6FB9", "Parcialmente": "#F4D03F", "Discordo": "#D32F2F"}
ORDEM_STATUS = ["Concordo", "Parcialmente", "Discordo"]

# Lista de perguntas onde a resposta "Concordo" é um ponto de ATENÇÃO (Risco)
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
        if func
