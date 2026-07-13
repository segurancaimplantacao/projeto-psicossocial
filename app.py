import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# Mapeamentos Exatos
MAPA_TEXTO = {1: "Concordo", 2: "Parcialmente", 3: "Discordo"}
# Mapeamento do Gráfico exatamente como você pediu
MAPA_GRAFICO = {1: "Sem Evidências", 2: "Parcialmente Evidenciado", 3: "Evidências Claras"}
CORES_FINAIS = {"Sem Evidências": "#2A6FB9", "Parcialmente Evidenciado": "#F4D03F", "Evidências Claras": "#D32F2F"}
ORDEM_STATUS = ["Sem Evidências", "Parcialmente Evidenciado", "Evidências Claras"]

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

# --- LÓGICA DO FUNCIONÁRIO ---
if menu == "Funcionário":
    st.title("👤 Área do Funcionário")
    cpf = st.text_input("Digite seu CPF:")
    if cpf:
        func_data = supabase.table("funcionarios").select("*").eq("cpf", cpf).execute().data
        if func_data:
            funcionario = func_data[0]
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

# --- LÓGICA DO GESTOR (CARREGAMENTO DIRETO) ---
else:
    st.title("📊 Painel do Gestor")
    
    # 1. Busca de empresas sem interrupções
    empresas_response = supabase.table("empresas").select("id, nome_empresa").execute()
    empresas_data = empresas_response.data
    
    if empresas_data:
        nomes_empresas = {e['nome_empresa']: e['id'] for e in empresas_data}
        empresa_selecionada = st.selectbox("Selecione a Empresa", list(nomes_empresas.keys()))

        # 2. Botão de Carregar sempre presente
        if st.button("CARREGAR DADOS"):
            res = supabase.table("respostas").select("resposta, perguntas(pergunta), funcionarios(nome)").eq("empresa_id", nomes_empresas[empresa_selecionada]).execute()
            
            if res.data:
                df = pd.DataFrame(res.data)
                df['Pergunta'] = df['perguntas'].apply(lambda x: x.get('pergunta', ''))
                df['Funcionario'] = df['funcionarios'].apply(lambda x: x.get('nome', 'N/A') if x else 'N/A')
                
                # CÁLCULO EXATO: Sem inversão. 1 é sempre 1, 3 é sempre 3.
                df['Legenda_Grafico'] = df['resposta'].map(MAPA_GRAFICO)
                df['Resposta_Tabela'] = df['resposta'].map(MAPA_TEXTO)

                # Seletor de categorias
                categorias_selecionadas = st.multiselect(
                    "Selecione quais níveis exibir no gráfico:",
                    options=ORDEM_STATUS, default=ORDEM_STATUS
                )

                # Filtragem aplicada APENAS ao gráfico
                df_grafico = df[df['Legenda_Grafico'].isin(categorias_selecionadas)]
                
                if not df_grafico.empty:
                    df_grouped = df_grafico.groupby(['Pergunta', 'Legenda_Grafico']).size().reset_index(name='Contagem')
                    
                    fig = px.bar(df_grouped, y="Pergunta", x="Contagem", color="Legenda_Grafico", 
                                 orientation='h', barmode='group',
                                 color_discrete_map=CORES_FINAIS,
                                 category_orders={"Legenda_Grafico": ORDEM_STATUS})
                    
                    # Estilo final solicitado
                    fig.update_layout(yaxis=dict(tickfont=dict(color="black", size=13)))
                    st.plotly_chart(fig, use_container_width=True)

                # Tabela de dados (Fiel ao banco)
                st.subheader("Respostas Individuais")
                st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta_Tabela']], use_container_width=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar CSV", csv, "relatorio_final.csv", "text/csv")
            else:
                st.warning("Nenhum dado encontrado para esta empresa.")
    else:
        st.error("Erro ao carregar lista de empresas do Supabase.")
