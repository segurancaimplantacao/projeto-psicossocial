import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# CSS: Forçando preto absoluto (#000000) e negrito pesado
st.markdown("""
    <style>
    .stApp { font-family: sans-serif; }
    h1, h2, h3, .stMarkdown { color: #000000 !important; font-weight: 900 !important; }
    .js-plotly-plot .plotly .main-svg { background: transparent !important; }
    /* Estilizando as labels do eixo Y do Plotly */
    .xtick text, .ytick text { fill: #000000 !important; font-weight: bold !important; }
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

                # Agrupamento para o gráfico: conta quantos funcionários deram cada resposta por pergunta
                df_grouped = df.groupby(['Pergunta', 'Resposta']).size().reset_index(name='Contagem')

                # Criando abas
                tab1, tab2 = st.tabs(["📊 Visão Completa", "📑 Análise Individual por Status"])

                with tab1:
                    st.subheader("Gráfico Geral (Barras Agrupadas)")
                    # barmode='group' separa as barras (o que você queria)
                    fig_geral = px.bar(df_grouped, y="Pergunta", x="Contagem", color="Resposta", 
                                       orientation='h', barmode='group',
                                       color_discrete_map={"Discordo": "#B22222", "Parcialmente": "#DAA520", "Concordo": "#00008B"})
                    
                    fig_geral.update_layout(
                        font=dict(color="black", size=14, weight="bold"),
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig_geral, use_container_width=True)

                with tab2:
                    st.subheader("Gráficos Individuais")
                    cols = st.columns(3)
                    status_map = {"Discordo": "#B22222", "Parcialmente": "#DAA520", "Concordo": "#00008B"}
                    for i, (status, cor) in enumerate(status_map.items()):
                        with cols[i]:
                            df_s = df_grouped[df_grouped['Resposta'] == status]
                            fig_ind = px.bar(df_s, y="Pergunta", x="Contagem", title=status, 
                                             color_discrete_sequence=[cor], orientation='h')
                            fig_ind.update_layout(showlegend=False, font=dict(color="black", weight="bold"))
                            st.plotly_chart(fig_ind, use_container_width=True)

                st.subheader("Detalhes das Respostas")
                st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta']], use_container_width=True)
