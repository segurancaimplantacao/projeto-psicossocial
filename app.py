import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# CSS para garantir fontes pretas, legibilidade e coluna à esquerda
st.markdown("""
    <style>
    .stApp { font-family: sans-serif; }
    h1, h2, h3, .stMarkdown { color: #000000 !important; }
    .js-plotly-plot .plotly .ytick text { fill: #000000 !important; font-weight: normal !important; font-size: 13px !important; }
    </style>
    """, unsafe_allow_html=True)

# Cores ajustadas: Azul (Puro), Amarelo (Gema Intensa), Vermelho (Mantido)
CORES_FINAIS = {
    "Sem Evidências": "#1E90FF",         # Azul Dodgger (puro, nada de roxo)
    "Parcialmente Evidenciado": "#FFD700", # Dourado/Gema frita (intenso)
    "Evidências Claras": "#B22222"        # Vermelho (mantido)
}

# Ordem desejada para a legenda e organização
ORDEM_STATUS = ["Sem Evidências", "Parcialmente Evidenciado", "Evidências Claras"]

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

if menu == "Gestor":
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
                
                # Mapeamento
                mapa_res = {1: "Evidências Claras", 2: "Parcialmente Evidenciado", 3: "Sem Evidências"}
                df['Resposta'] = df['resposta'].map(mapa_res)

                df_grouped = df.groupby(['Pergunta', 'Resposta']).size().reset_index(name='Contagem')

                tab1, tab2 = st.tabs(["📊 Visão Completa", "📑 Análise Individual por Status"])

                with tab1:
                    fig_geral = px.bar(df_grouped, y="Pergunta", x="Contagem", color="Resposta", 
                                       orientation='h', barmode='group',
                                       color_discrete_map=CORES_FINAIS,
                                       category_orders={"Resposta": ORDEM_STATUS})
                    
                    fig_geral.update_layout(
                        plot_bgcolor='white',
                        font=dict(color="black", size=14),
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig_geral, use_container_width=True)

                with tab2:
                    cols = st.columns(3)
                    for i, status in enumerate(ORDEM_STATUS):
                        with cols[i]:
                            df_s = df_grouped[df_grouped['Resposta'] == status]
                            cor = CORES_FINAIS[status]
                            fig_ind = px.bar(df_s, y="Pergunta", x="Contagem", title=status, 
                                             color_discrete_sequence=[cor], orientation='h')
                            fig_ind.update_layout(showlegend=False, font=dict(color="black"), plot_bgcolor='white')
                            st.plotly_chart(fig_ind, use_container_width=True)

                st.subheader("Detalhes das Respostas")
                st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta']], use_container_width=True)
