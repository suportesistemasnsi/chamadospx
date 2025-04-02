import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.supabase import carregar_chamados
from plotly.subplots import make_subplots
import plotly.io as pio

# Função para carregar dados com cache
@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_dados_dashboard():
    return carregar_chamados()

# Função para criar gráfico de pizza
@st.cache_data
def create_pie_chart(data, values_col, names_col, title=""):
    return px.pie(data, 
                values=values_col, 
                names=names_col,
                title=title,
                template='plotly_dark')

# Função para criar gráfico de barras
@st.cache_data
def create_bar_chart(data, x_col, y_col, title="", color_col=None):
    fig = px.bar(data, 
                x=x_col, 
                y=y_col,
                title=title,
                text_auto=True,
                template='plotly_dark')
    if color_col:
        fig.update_traces(marker_color=px.colors.qualitative.Plotly)
    return fig

def dashboard():
    # CSS customizado modificado
    st.markdown("""
    <style>
        /* Estilo para o container do título */
        .dashboard-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        
        /* Estilo apenas para o texto do título */
        .dashboard-title {
            color: #f0f2f6;
            font-size: 2.2rem;
            display: inline;
            vertical-align: middle;
        }
        
        /* Estilo específico para o ícone - sem efeitos de cor */
        .dashboard-icon {
            font-size: 2.2rem;
            display: inline;
            vertical-align: middle;
            margin-right: 10px;
            color: inherit !important;
            background: none !important;
            -webkit-text-fill-color: initial !important;
            text-shadow: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Título modificado com classes separadas
    st.markdown("""
    <div class="dashboard-header">
        <span class="dashboard-icon">📊</span>
        <span class="dashboard-title">Dashboard de Chamados</span>
    </div>
    """, unsafe_allow_html=True)

    # Restante do código do dashboard permanece igual
    [...]

    # Carregar dados com feedback visual
    with st.spinner('Carregando dados...'):
        df = carregar_dados_dashboard()
        
        if df.empty or not isinstance(df, pd.DataFrame):
            st.warning("Nenhum dado disponível para exibir no dashboard.")
            return

        # Verificar colunas necessárias
        required_columns = {'Status', 'Pendência', 'Usuário Resp'}
        if not required_columns.issubset(df.columns):
            st.error("Estrutura de dados inválida. Faltam colunas necessárias.")
            st.stop()

        # Preparar dados
        status_counts = df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'count']
        
        pendencia_counts = df['Pendência'].value_counts().reset_index()
        pendencia_counts.columns = ['Pendência', 'count']
        
        usuario_counts = df['Usuário Resp'].value_counts().reset_index()
        usuario_counts.columns = ['Usuário', 'count']

        # Layout com abas
        tab1, tab2 = st.tabs(["Visão Geral", "Detalhes"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    create_pie_chart(status_counts, 'count', 'Status', "Distribuição por Status"),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    create_bar_chart(pendencia_counts, 'Pendência', 'count', "Chamados por Pendência"),
                    use_container_width=True
                )

        with tab2:
            st.plotly_chart(
                create_bar_chart(usuario_counts, 'Usuário', 'count', "Chamados por Usuário", "Usuário"),
                use_container_width=True
            )

if __name__ == "__main__":
    dashboard()
