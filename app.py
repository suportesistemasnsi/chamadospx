import os
import streamlit as st
import pandas as pd
from services.supabase import supabase
import time

# Ler a variável de ambiente PORT
port = int(os.environ.get("PORT", 8501))
# Configurar o Streamlit para usar a porta
#st.set_option('server.port', port)
# Configuração da página
st.set_page_config(
    layout="wide",
    page_title="Gestão de Chamados",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
# Configuração do gerenciador de cookies
cookies = EncryptedCookieManager(
    password="sua_senha_secreta_aqui",  # Substitua por uma senha segura
)
if not cookies.ready():
    st.stop()

# Função para autenticar o usuário
def autenticar_usuario(email, senha):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        if response.user:
            # Salvar access_token e refresh_token no cookie
            cookies["access_token"] = response.session.access_token
            cookies["refresh_token"] = response.session.refresh_token
            cookies.save()
            return response.user, None
        elif response.error:
            return None, response.error.message
        else:
            return None, "Erro desconhecido ao autenticar."
    except Exception as e:
        return None, f"Erro ao autenticar: {str(e)}"

# Função para exibir a tela de login
def tela_login():
    st.markdown("""
    <style>
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .login-box {
            background-color: #1e1e1e;
            padding: 2rem;
            border-radius: 10px;
            width: 400px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title("🔒 Login")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            
            if st.button("Entrar", key="login_btn"):
                if email and senha:
                    usuario, erro = autenticar_usuario(email, senha)
                    if usuario:
                        st.session_state["usuario"] = usuario
                        st.success("Login realizado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(erro or "Erro ao autenticar")
                else:
                    st.warning("Preencha todos os campos")

# Função principal de verificação de autenticação
def verificar_autenticacao():
    if "usuario" not in st.session_state:
        st.session_state["usuario"] = None
    
    # Verificar se há tokens no cookie
    access_token = cookies.get("access_token")
    refresh_token = cookies.get("refresh_token")
    
    if access_token and refresh_token and st.session_state["usuario"] is None:
        try:
            # Restaurar a sessão do Supabase com ambos os tokens
            response = supabase.auth.set_session(access_token, refresh_token)
            if response.user:
                st.session_state["usuario"] = response.user
        except Exception as e:
            st.error(f"Erro ao restaurar sessão: {str(e)}")
            cookies.pop("access_token", None)
            cookies.pop("refresh_token", None)
            cookies.save()
    
    if st.session_state["usuario"] is None:
        tela_login()
        st.stop()
    else:
        def logout():
            st.session_state["usuario"] = None
            cookies.pop("access_token", None)
            cookies.pop("refresh_token", None)
            cookies.save()
            st.rerun()
        
        st.sidebar.button("Sair", on_click=logout)

# Adicionar o CSS personalizado para o tema escuro
st.markdown("""
    <style>
        /* Fundo da página */
        .main {
            background-color: #121212;
            color: #ffffff;
        }

        /* Fundo da barra lateral */
        .sidebar .sidebar-content {
            background-color: #1e1e1e;
        }

        /* Títulos */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
        }

        /* Texto */
        p, label, span {
            color: #ffffff;
        }

        /* Botões */
        .stButton>button {
            background-color: #004aad;
            color: #ffffff;
            border: none;
            border-radius: 5px;
        }

        .stButton>button:hover {
            background-color: #005eff;
            color: #ffffff;
        }

        /* Caixa de entrada */
        .stTextInput, .stNumberInput, .stSelectbox, .stDateInput {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #333333;
        }

        /* Tabela */
        .stDataFrame {
            background-color: #1e1e1e;
            color: #ffffff;
        }

        /* Estilo do título */
        .main-title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            background-color: #333333;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5);
        }

        /* Contadores */
        .metric-container {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        .metric-box {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            width: 250px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
            border: 2px solid #333333;
        }
        .metric-label {
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
        }
        .metric-value {
            font-size: 24px;
            color: #00ff00;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)
# Estilo do título
st.markdown("""
    <style>
        .main-title { 
            text-align: center; 
            font-size: 36px; 
            font-weight: bold; 
            color: #004aad; 
            padding: 15px; 
            border-radius: 10px; 
            background-color: #333333; 
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); 
        }
        .sidebar .sidebar-content { 
            background-color: #f8f9fa; 
        }
    </style>
    <div class='main-title'>📊 Gestão de Chamados SH/Pixeon</div>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_chamados():
    try:
        response = supabase.table("Chamados").select("*").order("data_abertura", desc=False).order("id", desc=False).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df.rename(columns={
                "id": "ID",
                "chamados_sh": "Chamados SH",
                "chamados_px": "Chamados Pixeon",
                "titulo": "Título",
                "data_abertura": "Data",
                "pendencia_retorno": "Pendência",
                "usuario_resp": "Usuário Resp",
                "status": "Status",
                "observacao": "Observação",
            }, inplace=True)
            df["Chamados SH"] = pd.to_numeric(df["Chamados SH"], errors='coerce').fillna(0).astype(int)
            # df["Chamados Pixeon"] = pd.to_numeric(df["Chamados Pixeon"], errors='coerce').fillna(0).astype(int)
            df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
            
            df = df.sort_values(by=["Data", "ID"], ascending=[True, True])
            df["Data"] = df["Data"].dt.strftime("%Y-%m-%d")
            df["Data"] = pd.to_datetime(df["Data"], format="%Y-%m-%d", errors="coerce")
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar os chamados: {e}")
        return pd.DataFrame()

def exibir_contadores(df, df_completo):
    if df.empty and df_completo.empty:
        st.warning("Nenhum dado disponível para exibir os contadores.")
        return

    # Contadores baseados nos dados filtrados
    total_abertos = df[df["Status"] == "Aberto"].shape[0]
    total_pend_px = df[df["Pendência"] == "Pixeon"].shape[0]
    total_pend_sh = df[df["Pendência"] == "SH"].shape[0]
    
    # Contador de concluídos sempre mostra o total, independente dos filtros
    total_concluidos = df_completo[df_completo["Status"] == "Concluído"].shape[0]
    total_abertos = df_completo[df_completo["Status"] == "Aberto"].shape[0]

    st.markdown("""
    <style>
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    .metric-box {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        width: 250px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        border: 2px solid #004aad;
    }
    .metric-label {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
    }
    .metric-value {
        font-size: 24px;
        color: #004aad;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-box'>
            <div class='metric-label'>📋 Chamados Abertos</div>
            <div class='metric-value'>{total_abertos}</div>
        </div>
        <div class='metric-box'>
            <div class='metric-label'>✅ Chamados Concluídos</div>
            <div class='metric-value'>{total_concluidos}</div>
        </div>
        <div class='metric-box'>
            <div class='metric-label'>📍 Pendência Sta Helena</div>
            <div class='metric-value'>{total_pend_sh}</div>
        </div>
        <div class='metric-box'>
            <div class='metric-label'>📍 Pendência Pixeon</div>
            <div class='metric-value'>{total_pend_px}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():

    # Verificar autenticação antes de exibir o conteúdo
    verificar_autenticacao()
    st.sidebar.header("Navegação")
    pagina = st.sidebar.radio("Escolha uma página:", ["Principal", "Dashboard"])
    
    if pagina == "Principal":
        # Carregar dados completos (não filtrados)
        df_completo = carregar_chamados()
        
        # Filtros na sidebar
        st.sidebar.header("Filtros e Pesquisa")
        selected_status = st.sidebar.selectbox("Filtrar por Status", ["Todos", "Aberto", "Concluído"],index=1) # Define "Aberto" como o valor padrão 
        selected_pendencia = st.sidebar.selectbox("Filtrar por Pendência", ["Todos", "Pixeon", "SH"])
        search_term = st.sidebar.text_input("Pesquisar por Número ou Título")
        
        # Aplicar filtros (cria uma cópia filtrada)
        df_filtrado = df_completo.copy()
        if selected_status != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Status"] == selected_status]
        if selected_pendencia != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Pendência"] == selected_pendencia]
        if search_term:
            search_term = str(search_term).lower()
            df_filtrado = df_filtrado[
                df_filtrado["Chamados SH"].astype(str).str.lower().str.contains(search_term) |
                df_filtrado["Chamados Pixeon"].astype(str).str.lower().str.contains(search_term) |
                df_filtrado["Título"].str.lower().str.contains(search_term)
                | df_filtrado["Usuário Resp"].str.lower().str.contains(search_term)
            ]

        # Exibir contadores (passando ambos os DataFrames)
        st.header("Resumo dos Chamados")
        exibir_contadores(df_filtrado, df_completo)

        # FORMULÁRIO DE INSERÇÃO DE NOVOS CHAMADOS (ADICIONADO AQUI)
        with st.expander("➕ Inserir Novo Chamado", expanded=False):
            with st.form(key="add_chamado", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    chamado_sh = st.number_input("Chamado SH", min_value=0, step=1)
                    titulo = st.text_input("Título*", placeholder="Descrição do chamado")
                    data_abertura = st.date_input("Data de Abertura*")
                
                with col2:
                    chamado_px = st.text_input("Chamado Pixeon", value="")
                    pendencia = st.selectbox("Pendência*", ["Pixeon", "SH"])
                
                with col3:
                    usuario_resp = st.text_input("Usuário Responsável*")
                    status = st.selectbox("Status*", ["Aberto", "Concluído"])
                    observacao = st.text_area("Observações")

                if st.form_submit_button("Cadastrar Chamado"):
                    if not titulo or not data_abertura or not usuario_resp:
                        st.error("Preencha os campos obrigatórios (*)")
                    else:
                        novo_chamado = {
                            "chamados_sh": chamado_sh if chamado_sh else None,
                            "chamados_px": chamado_px if chamado_px else None,
                            "titulo": titulo,
                            "data_abertura": data_abertura.strftime("%Y-%m-%d"),
                            "pendencia_retorno": pendencia,
                            "usuario_resp": usuario_resp,
                            "status": status,
                            "observacao": observacao if observacao else None
                        }
                        
                        try:
                            response = supabase.table("Chamados").insert(novo_chamado).execute()
                            if response.data:
                                st.success("Chamado cadastrado com sucesso!")
                                st.cache_data.clear()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Erro ao cadastrar chamado. Verifique os dados.")
                        except Exception as e:
                            st.error(f"Erro ao cadastrar: {str(e)}")

        # Lista editável de chamados
        st.write("### Lista de Chamados")
        
        if not df_filtrado.empty:
            # Garantir ordenação por Data e ID
            df_filtrado = df_filtrado.sort_values(by=["Data", "ID"], ascending=[True, True])

            # Adicionar uma coluna de contador
            df_filtrado = df_filtrado.reset_index(drop=True)  # Redefinir o índice do DataFrame
            df_filtrado["Nº"] = df_filtrado.index + 1  # Criar a coluna de contador (1, 2, 3, ...)

            # Reorganizar as colunas para exibição no editor
            colunas_exibidas = ["Nº", "Chamados SH", "Chamados Pixeon", "Título", "Data", 
                                "Pendência", "Usuário Resp", "Status", "Observação"]
            df_exibido = df_filtrado[colunas_exibidas]  # Criar um DataFrame apenas com as colunas visíveis

            # Configuração das colunas para edição
            column_config = {
                "Nº": st.column_config.NumberColumn("Nº", disabled=True),  # Contador visível, não editável
                "Chamados SH": st.column_config.NumberColumn("Chamado SH", format="%d"),
                "Chamados Pixeon": st.column_config.TextColumn("Chamado Pixeon", width="medium"),
                "Título": st.column_config.TextColumn("Título", width="large"),
                "Data": st.column_config.DateColumn("Data", format="DD-MM-YYYY"),
                "Pendência": st.column_config.SelectboxColumn("Pendência", options=["Pixeon", "SH"]),
                "Usuário Resp": st.column_config.TextColumn("Responsável"),
                "Status": st.column_config.SelectboxColumn("Status", options=["Aberto", "Concluído"]),
                "Observação": st.column_config.TextColumn("Observação", width="large"),
            }

            # Altura dinâmica para o editor de dados
            altura_por_linha = 35  # Altura aproximada de cada linha em pixels
            altura_maxima = 1000    # Altura máxima do editor em pixels
            altura_minima = 600    # Altura mínima do editor em pixels

            # Calcular a altura com base no número de linhas
            altura_calculada = min(max(len(df_exibido) * altura_por_linha, altura_minima), altura_maxima)

            # Editor de dados com altura automática
            edited_df = st.data_editor(
                df_exibido,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                key="data_editor",
                height=altura_calculada
            )

            # Botão para salvar alterações
            if st.button("💾 Salvar Alterações"):
                try:
                    changes = []
                    for index, row in edited_df.iterrows():
                        # Recuperar o ID correspondente ao índice
                        original_row = df_filtrado.loc[index]
                        if not row.equals(original_row):
                            # Tratar valores nulos na coluna "Data"
                            data_abertura = row["Data"]
                            if pd.isnull(data_abertura):  # Verificar se a data é nula
                                data_abertura = None  # Substituir por None
                            else:
                                data_abertura = data_abertura.strftime("%Y-%m-%d")  # Formatar a data

                            changes.append({
                                "id": original_row["ID"],  # Usar o ID original para identificar o registro
                                "data": {
                                    "chamados_sh": row["Chamados SH"],
                                    "chamados_px": row["Chamados Pixeon"],
                                    "titulo": row["Título"],
                                    "data_abertura": data_abertura,  # Data tratada
                                    "pendencia_retorno": row["Pendência"],
                                    "usuario_resp": row["Usuário Resp"],
                                    "status": row["Status"],
                                    "observacao": row["Observação"]
                                }
                            })

                    if changes:
                        for change in changes:
                            supabase.table("Chamados").update(change["data"]).eq("id", change["id"]).execute()

                        st.success(f"{len(changes)} alteração(ões) salva(s) com sucesso!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.info("Nenhuma alteração detectada para salvar.")
                except Exception as e:
                    st.error(f"Erro ao salvar alterações: {str(e)}")
        else:
            st.warning("Nenhum chamado encontrado com os filtros atuais.")
    
    elif pagina == "Dashboard":
        from streamlit_dashboard_extra import dashboard
        dashboard()


if __name__ == "__main__":
    main()
