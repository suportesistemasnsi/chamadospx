import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.supabase import carregar_chamados
from plotly.subplots import make_subplots
import plotly.io as pio

def dashboard():
    st.title("Dashboard de Chamados")

    # Carregar os dados reais
    df = carregar_chamados()

    if df.empty:
        st.warning("Nenhum dado disponível para exibir no dashboard.")
        return

    # Gráfico de distribuição por status
    chamados_por_status = df["Status"].value_counts().reset_index()
    chamados_por_status.columns = ["Status", "Quantidade"]
    fig_status = px.pie(chamados_por_status, values='Quantidade', names='Status', title="Distribuição de Chamados")

    chamados_por_usuario = df["Usuário Resp"].value_counts().reset_index()
    chamados_por_usuario.columns = ["Usuário Resp", "Quantidade"]
    fig_usuario = px.bar(chamados_por_usuario, x='Usuário Resp', y='Quantidade', title="Chamados por Usuário", text_auto=True)

    # Gráfico de pendências
    chamados_por_pendencia = df["Pendência"].value_counts().reset_index()
    chamados_por_pendencia.columns = ["Pendência", "Quantidade"]
    fig_pendencia = px.bar(chamados_por_pendencia, x='Pendência', y='Quantidade', title="Chamados por Pendência", text_auto=True)

    # Exibir os gráficos
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_status, use_container_width=True)
    col2.plotly_chart(fig_pendencia, use_container_width=True)
    st.plotly_chart(fig_usuario, use_container_width=True)

if __name__ == "__main__":
    dashboard()
