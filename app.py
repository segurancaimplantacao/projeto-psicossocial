import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")
st.title("Painel do Gestor - Versão Atualizada")

# Usando checkboxes fixos para evitar erros de cache do filtro lateral
st.sidebar.subheader("Filtrar Status:")
c1 = st.sidebar.checkbox("Sem evidência de risco", value=True)
c2 = st.sidebar.checkbox("Parcial", value=True)
c3 = st.sidebar.checkbox("Evidências de risco", value=True)

# Lógica do filtro
status_selecionados = []
if c1: status_selecionados.append("Sem evidência de risco")
if c2: status_selecionados.append("Parcial")
if c3: status_selecionados.append("Evidências de risco")

empresas_data = supabase.table("empresas").select("id, nome_empresa").execute().data
nomes_empresas = {e['nome_empresa']: e['id'] for e in empresas_data}
empresa_selecionada = st.selectbox("Selecione a Empresa", list(nomes_empresas.keys()))

if st.button("CARREGAR DADOS"):
    res = supabase.table("respostas").select("resposta, perguntas(pergunta)").eq("empresa_id", nomes_empresas[empresa_selecionada]).execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
        df['Pergunta'] = df['perguntas'].apply(lambda x: x['pergunta'])
        
        def status_map(r):
            if r == 1: return "Sem evidência de risco"
            if r == 2: return "Parcial"
            return "Evidências de risco"
        
        df['Status'] = df['resposta'].apply(status_map)
        
        # Filtra o DataFrame
        df_plot = df[df['Status'].isin(status_selecionados)]
        
        # Gráfico
        fig = px.bar(df_plot.groupby(['Pergunta', 'Status']).size().reset_index(name='Contagem'), 
                     y="Pergunta", x="Contagem", color="Status", 
                     orientation='h',
                     color_discrete_map={
                         "Parcial": "#FFEB3B", 
                         "Sem evidência de risco": "#4F81BD", 
                         "Evidências de risco": "#C0504D"
                     }, barmode='group')
        
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df)
    else:
        st.error("Nenhum dado encontrado para esta empresa.")
