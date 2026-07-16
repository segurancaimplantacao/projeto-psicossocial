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
                df['Funcionario'] = df['funcionarios'].apply(lambda
