import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Gestor 2026", layout="wide")
st.header("PAINEL GESTOR - DADOS EM TEMPO REAL")

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

# --- MODO FUNCIONÁRIO ---
if menu == "Funcionário":
    st.title("Acesso ao Questionário")
    cpf_input = st.text_input("Digite seu CPF (ex: 450.367.848-55):")
    
    if cpf_input:
        st.info(f"Buscando CPF: {cpf_input}")
        func = supabase.table("funcionarios").select("id, nome, empresa_id").eq("cpf", cpf_input).execute().data
        
        if func:
            f = func[0]
            st.success(f"Bem-vindo, {f['nome']}!")
            perguntas = supabase.table("perguntas").select("id, pergunta").eq("ativa", True).execute().data
            
            if perguntas:
                with st.form("form_resp"):
                    respostas = {
                        p['id']: st.radio(
                            p['pergunta'], [1, 2, 3], 
                            format_func=lambda x: {1:"Discordo", 2:"Parcial", 3:"Concordo"}[x], 
                            horizontal=True
                        ) for p in perguntas
                    }
                    if st.form_submit_button("Enviar Respostas"):
                        dados = [
                            {
                                "funcionarios_id": f['id'], 
                                "empresa_id": f['empresa_id'], 
                                "pergunta_id": p_id, 
                                "resposta": nota, 
                                "ano": 2026
                            } for p_id, nota in respostas.items()
                        ]
                        supabase.table("respostas").insert(dados).execute()
                        st.success("Respostas enviadas com sucesso!")
        else:
            st.error("CPF não encontrado. Certifique-se de digitar com pontos e traços exatamente como no cadastro.")

# --- MODO GESTOR ---
elif menu == "Gestor":
    st.title("Painel do Gestor")
    
    filtro_status = st.sidebar.multiselect("Filtrar Status:", 
                                           options=["Sem evidência de risco", "Parcial", "Evidências de risco"], 
                                           default=["Sem evidência de risco", "Parcial", "Evidências de risco"])
    
    empresas = supabase.table("empresas").select("id, nome_empresa").execute().data
    if empresas:
        nomes = {e['nome_empresa']: e['id'] for e in empresas}
        sel = st.selectbox("Selecione a Empresa", list(nomes.keys()))

        if st.button("CARREGAR DADOS ATUALIZADOS"):
            res = supabase.table("respostas").select("resposta, perguntas(pergunta, Tipo), funcionarios(nome)").eq("empresa_id", nomes[sel]).execute()
            
            if res.data:
                df = pd.DataFrame(res.data)
                df['Pergunta'] = df['perguntas'].apply(lambda x: x['pergunta'])
                df['Funcionario'] = df['funcionarios'].apply(lambda x: x['nome'])
                
                def classificar(row):
                    r = int(row['resposta'])
                    t = str(row['perguntas'].get('Tipo', '')).strip()
                    if r == 2: return "Parcial"
                    if t == "Negativa": return "Evidências de risco" if r == 3 else "Sem evidência de risco"
                    else: return "Sem evidência de risco" if r == 3 else "Evidências de risco"

                df['Status'] = df.apply(classificar, axis=1)
                df['Resposta_Texto'] = df['resposta'].map({1: "Discordo", 2: "Parcial", 3: "Concordo"})
                
                # Gráfico
                df_plot = df[df['Status'].isin(filtro_status)]
                
                fig = px.histogram(df_plot, y="Pergunta", color="Status", 
                                   color_discrete_map={
                                       "Parcial": "#FFEB3B", 
                                       "Evidências de risco": "#C0504D", 
                                       "Sem evidência de risco": "#4F81BD"
                                   }, orientation='h', barmode='group')
                
                fig.update_layout(
                    showlegend=False, 
                    plot_bgcolor='white', 
                    yaxis={'categoryorder': 'total descending', 'tickfont': {'color': '#000000', 'size': 14}},
                    xaxis={'tickfont': {'color': '#000000', 'size': 12}}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # --- LEGENDA COMPACTA ABAIXO DO GRÁFICO ---
                st.markdown("""
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; padding: 10px; border-top: 1px solid #ddd; color: #555;">
                    <span>🔵 Sem evidência de risco</span>
                    <span>🟡 Parcial</span>
                    <span>🔴 Evidências de risco</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.subheader("Respostas Individuais")
                st.dataframe(df[['Funcionario', 'Pergunta', 'Resposta_Texto']], use_container_width=True, height=400)
                csv = df[['Funcionario', 'Pergunta', 'Resposta_Texto']].to_csv(index=False).encode('utf-8')
                st.download_button("Baixar Tabela em CSV", data=csv, file_name="respostas.csv", mime="text/csv")
            else:
                st.error("Nenhum dado encontrado para esta empresa.")
