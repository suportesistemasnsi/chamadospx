from supabase import create_client, Client
import pandas as pd
import streamlit as st

# URL e chave do Supabase
SUPABASE_URL = "https://skttsevdyxjkscfpqfmh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNrdHRzZXZkeXhqa3NjZnBxZm1oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM0NTY3NzYsImV4cCI6MjA1OTAzMjc3Nn0.z_jL9clPWRAx0dv2Icev4ttrjog9NcseEJiNC6sy-Ag"

# Criar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.cache_data
def carregar_chamados():
    """Função para carregar os chamados do banco de dados"""
    try:
        response = supabase.table("Chamados").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df.rename(columns={
                "chamados_sh": "Chamados SH",
                "chamados_px": "Chamados Pixeon",
                "titulo": "Título",
                "data_abertura": "Data",
                "pendencia_retorno": "Pendência",
                "usuario_resp": "Usuário Resp",
                "status": "Status",
                "observacao": "Observação",
            }, inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar os chamados: {e}")
        return pd.DataFrame()

