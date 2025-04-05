import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from services.supabase import supabase
import time
from streamlit_cookies_manager import EncryptedCookieManager

@st.cache_data(ttl=300)
def carregar_chamados_fc():
    try:
        response = supabase.table("Chamados_fc").select(
            "id, chamado_sd, chamado_facil, titulo, data_abertura, pendencia_retorno, usuario_resp, status, observacao"
        ).order("data_abertura", desc=False).order("id", desc=False).execute()
        
        # # Logs de depuração
        # st.write("Resposta bruta do Supabase:", response.data)
        # st.write("Tamanho da resposta:", len(response.data) if response.data else 0)
        
        if response.data:
            df = pd.DataFrame(response.data)
            df.rename(columns={
                "id": "ID",
                "chamado_sd": "Chamados SH",
                "chamado_facil": "Chamados Fácil",
                "titulo": "Título",
                "data_abertura": "Data",
                "pendencia_retorno": "Pendência",
                "usuario_resp": "Usuário Resp",
                "status": "Status",
                "observacao": "Observação",
            }, inplace=True)
            df["Chamados SH"] = pd.to_numeric(df["Chamados SH"], errors='coerce').fillna(0).astype(int)
            df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
            df = df.sort_values(by=["Data", "ID"], ascending=[True, True])
            df["Data"] = df["Data"].dt.strftime("%Y-%m-%d")
            df["Data"] = pd.to_datetime(df["Data"], format="%Y-%m-%d", errors="coerce")
            return df
        else:
            st.warning("Nenhum dado retornado pelo Supabase para a tabela 'Chamados_fc'.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar os chamados: {str(e)}")
        return pd.DataFrame()

def exibir_contadores(df, df_completo_fc):
    if df.empty and df_completo_fc.empty:
        st.warning("Nenhum dado disponível para exibir os contadores.")
        return

    total_abertos = df_completo_fc[df_completo_fc["Status"] == "Aberto"].shape[0]
    total_concluidos = df_completo_fc[df_completo_fc["Status"] == "Concluído"].shape[0]
    total_pend_sh = df_completo_fc[df_completo_fc["Pendência"] == "Nordeste"].shape[0]
    total_pend_fc = df_completo_fc[df_completo_fc["Pendência"] == "Fácil"].shape[0]

    st.markdown("""
    <style>
    .metric-container { display: flex; justify-content: space-around; margin: 25px 0; gap: 20px; }
    .metric-box { background: rgba(26, 43, 60, 0.8); backdrop-filter: blur(5px); padding: 25px; border-radius: 12px; text-align: center; width: 100%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border: 1px solid rgba(109, 213, 237, 0.3); transition: all 0.3s ease; }
    .metric-box:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.2); border: 1px solid rgba(109, 213, 237, 0.6); }
    .metric-label { font-size: 1.1rem; font-weight: 500; color: #a3c4d8; margin-bottom: 10px; }
    .metric-value { font-size: 2rem; font-weight: 700; background: linear-gradient(90deg, #6dd5ed 0%, #2193b0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-box'><div class='metric-label'>📋 Chamados Abertos</div><div class='metric-value'>{total_abertos}</div></div>
        <div class='metric-box'><div class='metric-label'>✅ Chamados Concluídos</div><div class='metric-value'>{total_concluidos}</div></div>
        <div class='metric-box'><div class='metric-label'>📍 Pendência Nordeste</div><div class='metric-value'>{total_pend_sh}</div></div>
        <div class='metric-box'><div class='metric-label'>📍 Pendência Fácil</div><div class='metric-value'>{total_pend_fc}</div></div>
    </div>
    """, unsafe_allow_html=True)

def pagina_facil():
    df_completo_fc = carregar_chamados_fc()
    if df_completo_fc.empty:
        st.warning("Nenhum dado foi carregado da tabela Chamados_fc. Você pode adicionar novos chamados abaixo.")

    st.sidebar.header("Filtros e Pesquisa", divider="blue")
    selected_status = st.sidebar.selectbox("Filtrar por Status", ["Todos", "Aberto", "Concluído"], index=1)
    selected_pendencia = st.sidebar.selectbox("Filtrar por Pendência", ["Todos", "Fácil", "Nordeste"])
    search_term = st.sidebar.text_input("Pesquisar por Número, Título ou Responsável", placeholder="Digite o termo de pesquisa")  # Ajustado para "search_term"

    df_filtrado_fc = df_completo_fc.copy()
    if not df_filtrado_fc.empty:
        if selected_status != "Todos":
            df_filtrado_fc = df_filtrado_fc[df_filtrado_fc["Status"] == selected_status]
        if selected_pendencia != "Todos":
            df_filtrado_fc = df_filtrado_fc[df_filtrado_fc["Pendência"] == selected_pendencia]
        if search_term:
            search_term = str(search_term).lower()
            # # Log de depuração
            # st.write("Colunas disponíveis em df_filtrado_fc:", df_filtrado_fc.columns.tolist())
            # st.write("Primeiras 5 linhas antes do filtro de pesquisa:", df_filtrado_fc.head())
            try:
                df_filtrado_fc = df_filtrado_fc[
                    df_filtrado_fc["Chamados SH"].astype(str).str.lower().str.contains(search_term, na=False) |
                    df_filtrado_fc["Chamados Fácil"].astype(str).str.lower().str.contains(search_term, na=False) |
                    df_filtrado_fc["Título"].str.lower().str.contains(search_term, na=False) |
                    df_filtrado_fc["Usuário Resp"].str.lower().str.contains(search_term, na=False) |
                    df_filtrado_fc["Observação"].str.lower().str.contains(search_term, na=False)
                ]
                # st.write("Primeiras 5 linhas após o filtro de pesquisa:", df_filtrado_fc.head())
            except Exception as e:
                st.error(f"Erro ao aplicar filtro de pesquisa: {str(e)}")

    st.header("Resumo dos Chamados", divider="blue")
    exibir_contadores(df_filtrado_fc, df_completo_fc)

    with st.expander("➕ Inserir Novo Chamado", expanded=False):
        with st.form(key="add_chamado_fc", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                chamado_sh = st.number_input("Chamado SH", min_value=0, step=1)
                titulo = st.text_input("Título*", placeholder="Descrição do chamado")
                data_abertura = st.date_input("Data de Abertura*")
            with col2:
                chamado_fc = st.text_input("Chamado Fácil", value="")
                pendencia = st.selectbox("Pendência*", ["Fácil", "Nordeste"])
            with col3:
                usuario_resp = st.text_input("Usuário Responsável*")
                status = st.selectbox("Status*", ["Aberto", "Concluído"])
                observacao = st.text_area("Observações")

            if st.form_submit_button("Cadastrar Chamado"):
                if not titulo or not data_abertura or not usuario_resp:
                    st.error("Preencha os campos obrigatórios (*)")
                else:
                    novo_chamado = {
                        "chamado_sd": chamado_sh if chamado_sh else None,
                        "chamado_facil": chamado_fc if chamado_fc else None,
                        "titulo": titulo,
                        "data_abertura": data_abertura.strftime("%Y-%m-%d"),
                        "pendencia_retorno": pendencia,
                        "usuario_resp": usuario_resp,
                        "status": status,
                        "observacao": observacao if observacao else None
                    }
                    try:
                        response = supabase.table("Chamados_fc").insert(novo_chamado).execute()
                        if response.data:
                            st.success("Chamado cadastrado com sucesso!")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erro ao cadastrar chamado. Verifique os dados.")
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {str(e)}")

    if not df_filtrado_fc.empty:
        st.write("### Lista de Chamados")
        df_filtrado_fc = df_filtrado_fc.sort_values(by=["Data", "ID"], ascending=[True, True])
        df_filtrado_fc = df_filtrado_fc.reset_index(drop=True)
        df_filtrado_fc["Nº"] = df_filtrado_fc.index + 1
        colunas_exibidas = ["Nº", "Chamados SH", "Chamados Fácil", "Título", "Data", "Pendência", "Usuário Resp", "Status", "Observação"]
        df_exibido = df_filtrado_fc[colunas_exibidas]

        column_config = {
            "Nº": st.column_config.NumberColumn("Nº", width=None, disabled=True),
            "Chamados SH": st.column_config.NumberColumn("Chamado Nordeste", format="%d", width=None),
            "Chamados Fácil": st.column_config.TextColumn("Chamado Fácil", width=None),
            "Título": st.column_config.TextColumn("Título", width="large"),
            "Data": st.column_config.DateColumn("Data", format="DD-MM-YYYY"),
            "Pendência": st.column_config.SelectboxColumn("Pendência", options=["Fácil", "Nordeste"]),
            "Usuário Resp": st.column_config.TextColumn("Responsável"),
            "Status": st.column_config.SelectboxColumn("Status", options=["Aberto", "Concluído"]),
            "Observação": st.column_config.TextColumn("Observação", width="large"),
        }

        altura_calculada = min(max(len(df_exibido) * 35, 600), 1000)
        edited_df = st.data_editor(
            df_exibido, column_config=column_config, use_container_width=True, hide_index=True,
            num_rows="fixed", key="data_editor_fc", height=altura_calculada
        )

        if st.button("💾 Salvar Alterações"):
            try:
                changes = []
                for index, row in edited_df.iterrows():
                    original_row = df_filtrado_fc.loc[index]
                    if not row.equals(original_row):
                        data_abertura = row["Data"]
                        if pd.isnull(data_abertura):
                            data_abertura = None
                        else:
                            data_abertura = data_abertura.strftime("%Y-%m-%d")
                        changes.append({
                            "id": original_row["ID"],
                            "data": {
                                "chamado_sd": row["Chamados Nordeste"],
                                "chamado_facil": row["Chamados Fácil"],
                                "titulo": row["Título"],
                                "data_abertura": data_abertura,
                                "pendencia_retorno": row["Pendência"],
                                "usuario_resp": row["Usuário Resp"],
                                "status": row["Status"],
                                "observacao": row["Observação"]
                            }
                        })

                if changes:
                    for change in changes:
                        supabase.table("Chamados_fc").update(change["data"]).eq("id", change["id"]).execute()
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

def main():
    st.sidebar.header("Navegação", divider="blue")
    pagina = st.sidebar.radio("Escolha uma página:", ["Chamados Pixeon", "Chamados Fácil", "Dashboard"])
    
    if pagina == "Chamados Fácil":
        pagina_facil()
    elif pagina == "Dashboard":
        from streamlit_dashboard_extra import dashboard
        dashboard()

if __name__ == "__main__":
    app = pagina_facil()
    app.mainloop()
