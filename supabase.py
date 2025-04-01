import os
from supabase import create_client

# Obter as variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Verificar se as variáveis estão configuradas
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não estão configuradas.")

# Criar o cliente do Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

