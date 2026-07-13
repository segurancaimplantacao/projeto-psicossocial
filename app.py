import streamlit as st
from supabase import create_client
import pandas as pd

# Configuração
SUPABASE_URL = "https://auiyjfhumfvfdqhhyoch.supabase.co"
SUPABASE_KEY = "sb_publishable_u4mWfoCij_AnmwEw_H8H2w_OcPP_ToN"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="centered")

# --- MODO DE OPERAÇÃO ---
modo = st.sidebar.radio("Modo de Operação", ["Funcionário", "Gestor"])

try:
    # Carregamento Geral
    df_respostas = pd.DataFrame(supabase.table("respostas").select("*").execute().data)
    df_funcs = pd.DataFrame(supabase.table("funcionarios").select("*").execute().data)
    df_perguntas = pd.DataFrame(supabase.table("perguntas").select("*").execute().data)
    df_empresas = pd.DataFrame(supabase.table("empresas").select("*").execute().data)

    if modo == "Funcionário":
        st.title("👤 Área do Funcionário")
        cpf = st.text_input("Digite seu CPF:")
        if cpf:
            # Lógica de acesso via CPF
            st.write("Acesso liberado para o questionário...")
            
    elif modo == "Gestor":
        st.title("🩺 Relatório de Avaliação Individual")
        
        # Seletores de Empresa e Funcionário
        emp_map = dict(zip(df_empresas['nome_empresa'], df_empresas['id']))
        emp_selecionada = st.selectbox("Selecione uma empresa:", list(emp_map.keys()))
        
        funcs_emp = df_funcs[df_funcs['empresa_id'] == emp_map[emp_selecionada]]
        func_map = dict(zip(funcs_emp['nome'], funcs_emp['id']))
        func_selecionado = st.selectbox("Selecione o Funcionário:", list(func_map.keys()))

        if st.button("Gerar Análise"):
            func_id = func_map[func_selecionado]
            
            # FILTRO CRÍTICO
            df_f = df_respostas[df_respostas['funcionarios_id'] == func_id]
            
            if df_f.empty:
                st.error(f"ERRO: Nenhuma resposta encontrada no banco para ID {func_id}.")
                st.write("Colunas disponíveis em 'respostas':", df_respostas.columns.tolist())
            else:
                # Merge após garantir que existem dados
                df_final = df_f.merge(df_perguntas, left_on='pergunta_id', right_on='id')
                
                # Cálculo (Exemplo simplificado)
                st.success(f"Dados encontrados! Total de respostas: {len(df_final)}")
                st.dataframe(df_final.head())

except Exception as e:
    st.error(f"Erro no sistema: {e}")
