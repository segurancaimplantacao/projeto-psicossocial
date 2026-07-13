import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# Mapeamento Solicitado
# 1=Sem Evidências (Azul), 2=Parcialmente (Amarelo), 3=Evidências Claras (Vermelho)
MAPA_ROTULOS = {1: "Sem Evidências", 2: "Parcialmente Evidenciado", 3: "Evidências Claras"}
CORES_FINAIS = {"Sem Evidências": "#2A6FB9", "Parcialmente Evidenciado": "#F4D03F", "Evidências Claras": "#D32F2F"}
ORDEM_STATUS = ["Sem Evidências", "Parcialmente Evidenciado", "Evidências Claras"]

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

# --- LÓGICA DO GESTOR ---
if menu == "Gestor":
    st.title("📊 Painel do Gestor")
    
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
                df['Resposta'] = df['resposta'].map(MAPA_ROTULOS)

                # 1. Filtro de Perguntas
                todas_perguntas = df['Pergunta'].unique().tolist()
                perguntas_selecionadas = st.multiselect("Filtrar Perguntas para o Gráfico", todas_perguntas, default=todas_perguntas)
                df_filtrado = df[df['Pergunta'].isin(perguntas_selecionadas)]

                # 2. Gráfico
                df_grouped = df_filtrado.groupby(['Pergunta', 'Resposta']).size().reset_index(name='Contagem')
                fig = px.bar(df_grouped, y="Pergunta", x="Contagem", color="Resposta", 
                             orientation='h', barmode='group',
                             color_discrete_map=CORES_FINAIS,
                             category_orders={"Resposta": ORDEM_STATUS})
                st.plotly_chart(fig, use_container_width=True)

                # 3. Tabela de Dados e Download
                st.subheader("Respostas Individuais")
                st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta']], use_container_width=True)
                
                # Botão de Download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar Dados (CSV)",
                    data=csv,
                    file_name='relatorio_respostas.csv',
                    mime='text/csv',
                )
            else:
                st.warning("Nenhum dado encontrado.")

# --- LÓGICA DO FUNCIONÁRIO (Mant
