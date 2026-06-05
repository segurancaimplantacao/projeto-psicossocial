import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN" 

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Avaliação Psicossocial 2026", layout="wide")

menu = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

# --- MODO FUNCIONÁRIO ---
if menu == "Funcionário":
    st.title("Acesso ao Questionário")
    cpf = st.text_input("Digite seu CPF:")
    if cpf:
        try:
            func = supabase.table("funcionarios").select("id, nome, empresa_id").eq("cpf", cpf).execute().data
            if func:
                f = func[0]
                st.success(f"Bem-vindo, {f['nome']}!") 
                perguntas = supabase.table("perguntas").select("id, pergunta").execute().data
                with st.form("form_resp"):
                    respostas = {p['id']: st.radio(p['pergunta'], [1, 2, 3], format_func=lambda x: {1:"Discordo", 2:"Parcialmente", 3:"Concordo"}[x], horizontal=True) for p in perguntas}
                    if st.form_submit_button("Enviar Respostas"):
                        dados = [{"funcionarios_id": f['id'], "empresa_id": f['empresa_id'], "pergunta_id": p_id, "resposta": nota, "ano": 2026} for p_id, nota in respostas.items()]
                        supabase.table("respostas").insert(dados).execute()
                        st.success("Respostas enviadas!")
        except Exception as e: st.error(f"Erro: {e}")

# --- MODO GESTOR ---
elif menu == "Gestor":
    st.title("Painel do Gestor")
    
    # Filtro lateral para escolher o que visualizar
    filtro_exibicao = st.sidebar.multiselect(
        "Filtrar Status no Gráfico:", 
        ["Sem evidência de risco", "Evidências de risco"], 
        default=["Sem evidência de risco", "Evidências de risco"]
    )
    
    empresas = supabase.table("empresas").select("id, nome_empresa").execute().data
    if empresas:
        nomes = {e['nome_empresa']: e['id'] for e in empresas}
        sel = st.selectbox("Selecione a Empresa", list(nomes.keys()))
        if st.button("Carregar Dados"):
            res = supabase.table("respostas").select("resposta, perguntas(pergunta), funcionarios(nome)").eq("empresa_id", nomes[sel]).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df['Pergunta'] = df['perguntas'].apply(lambda x: x['pergunta'])
                df['Funcionario'] = df['funcionarios'].apply(lambda x: x['nome'])
                df['Resposta_Texto'] = df['resposta'].map({1: "Discordo", 2: "Parcialmente", 3: "Concordo"})
                
                termos_risco = ["assédio", "fadiga", "estresse", "irritabilidade", "rigidez", "conflitos", "sobrecarga", "desigual", "injustiça", "frequentes", "recursos", "pessoal insuficiente", "ritmo acelerado", "pausas adequadas"]
                
                def categorizar(row):
                    pergunta = row['Pergunta'].lower()
                    resp = row['resposta']
                    if resp == 2: return "Evidências de risco"
                    is_risco = any(termo in pergunta for termo in termos_risco)
                    return "Sem evidência de risco" if (is_risco and resp == 1) or (not is_risco and resp == 3) else "Evidências de risco"
                
                df['Status'] = df.apply(categorizar, axis=1)
                
                # Aplica o filtro selecionado na sidebar
                df_filtrado = df[df['Status'].isin(filtro_exibicao)]
                
                st.subheader("Análise de Riscos Psicossociais")
                
                fig = px.histogram(df_filtrado, y="Pergunta", color="Status", 
                                   color_discrete_map={"Evidências de risco": "#C0504D", "Sem evidência de risco": "#4F81BD"},
                                   orientation='h', barmode='group')
                
                fig.update_layout(
                    yaxis={'categoryorder': 'total descending', 'tickfont': {'color': 'black', 'size': 14}},
                    xaxis={'tickfont': {'color': 'black'}},
                    legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5, font={'color': 'black'}),
                    plot_bgcolor='white', font={'color': 'black', 'family': 'Arial'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Respostas Individuais")
                st.dataframe(df_filtrado[['Funcionario', 'Pergunta', 'Resposta_Texto']], use_container_width=True)
            else:
                st.warning("Nenhum dado encontrado.")