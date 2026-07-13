import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# Mapeamento para o formulário e tabela de respostas
MAPA_TEXTO = {1: "Concordo", 2: "Parcialmente", 3: "Discordo"}
# Mapeamento para o gráfico (Legendas solicitadas)
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
                
                # Inversão de polaridade (mantendo 1,2,3 internamente para calcular)
                def aplicar_inversao(row):
                    if row['Pergunta'] in perguntas_de_risco:
                        return 4 - row['resposta']
                    return row['resposta']
                
                df['valor_calculado'] = df.apply(aplicar_inversao, axis=1)
                
                # Legendas para o gráfico
                df['Legenda_Grafico'] = df['valor_calculado'].map(MAPA_GRAFICO)
                # Legendas para a tabela (texto original)
                df['Resposta_Tabela'] = df['resposta'].map(MAPA_TEXTO)

                # Gráficos Separados por Categoria
                st.subheader("Análise por Categoria")
                cols = st.tabs(ORDEM_STATUS)
                for i, status in enumerate(ORDEM_STATUS):
                    with cols[i]:
                        df_s = df[df['Legenda_Grafico'] == status]
                        if not df_s.empty:
                            df_grouped = df_s.groupby(['Pergunta', 'Legenda_Grafico']).size().reset_index(name='Contagem')
                            fig = px.bar(df_grouped, y="Pergunta", x="Contagem", orientation='h', 
                                         color_discrete_sequence=[CORES_FINAIS[status]])
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info(f"Sem dados para {status}")

                # Tabela de Respostas Individuais
                st.subheader("Respostas Individuais")
                st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta_Tabela']], use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar CSV", csv, "relatorio.csv", "text/csv")
            else:
                st.warning("Nenhum dado encontrado.")

# --- LÓGICA FUNCIONÁRIO (Mantida) ---
else:
    # ... (seu código de salvamento do formulário aqui)
    pass
