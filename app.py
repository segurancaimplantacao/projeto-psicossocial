import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

MAPA_ROTULOS = {1: "Concordo", 2: "Parcialmente", 3: "Discordo"}
CORES_FINAIS = {"Concordo": "#2A6FB9", "Parcialmente": "#F4D03F", "Discordo": "#D32F2F"}
ORDEM_STATUS = ["Concordo", "Parcialmente", "Discordo"]

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
        # O erro estava aqui - certifique-se de que o if termina com ":"
        if func_data:
            funcionario = func_data[0]
            st.success(f"Bem-vindo, {funcionario['nome']}!")
            
            perguntas_data = supabase.table("perguntas").select("*").execute().data
            if perguntas_data:
                with st.form("form_questionario"):
                    respostas = {}
                    for p in perguntas_data:
                        respostas[p['id']] = st.radio(
                            p['pergunta'], [1, 2, 3], format_func=lambda x: MAPA_ROTULOS[x], key=f"p_{p['id']}"
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
                
                def ajustar(row):
                    if row['Pergunta'] in perguntas_de_risco:
                        return 4 - row['resposta']
                    return row['resposta']

                df['resposta_ajustada'] = df.apply(ajustar, axis=1)
                df['Resposta'] = df['resposta_ajustada'].map(MAPA_ROTULOS)
                
                df_grouped = df.groupby(['Pergunta', 'Resposta']).size().reset_index(name='Contagem')
                fig = px.bar(df_grouped, y="Pergunta", x="Contagem", color="Resposta", 
                             orientation='h', barmode='group', color_discrete_map=CORES_FINAIS)
                st.plotly_chart(fig, use_container_width=True)
