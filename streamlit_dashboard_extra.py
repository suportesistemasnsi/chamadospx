import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.supabase import carregar_chamados
from plotly.subplots import make_subplots
import plotly.io as pio

# Configuração de cache
@st.cache_data(ttl=300)
def carregar_dados_dashboard():
    return carregar_chamados()

# Funções para gráficos
@st.cache_data
def create_pie_chart(data, values_col, names_col, title=""):
    return px.pie(data, 
                values=values_col, 
                names=names_col,
                title=title,
                template='plotly_dark',
                hole=0.3,  # Donut chart
                color_discrete_sequence=px.colors.sequential.Blues_r)

@st.cache_data
def create_bar_chart(data, x_col, y_col, title="", color_col=None,  horizontal=False):
    if horizontal:
        fig = px.bar(data,
                    y=x_col,
                    x=y_col,
                    title=title,
                    text_auto=True,
                    template='plotly_dark',
                    orientation='h',
                    color=y_col,
                    color_continuous_scale=px.colors.sequential.Blues_r)
    else:
        fig = px.bar(data,
                    x=x_col,
                    y=y_col,
                    title=title,
                    text_auto=True,
                    template='plotly_dark',
                    color=y_col,
                    color_continuous_scale=px.colors.sequential.Blues_r)
    return fig

def dashboard():
    # CSS customizado
    st.markdown("""
    <style>
        .dashboard-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .dashboard-title {
            color: #f0f2f6;
            font-size: 2.2rem;
            display: inline;
            vertical-align: middle;
        }
        .dashboard-icon {
            font-size: 2.2rem;
            display: inline;
            vertical-align: middle;
            margin-right: 10px;
        }
        .stPlotlyChart {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="dashboard-header">
        <span class="dashboard-icon">📊</span>
        <span class="dashboard-title">Dashboard de Chamados</span>
    </div>
    """, unsafe_allow_html=True)

    # Carregamento de dados
    with st.spinner('Carregando dados...'):
        df = carregar_dados_dashboard()
        
        if df.empty or not isinstance(df, pd.DataFrame):
            st.warning("Nenhum dado disponível para exibir no dashboard.")
            return

        # Processamento de dados
        status_counts = df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'count']
        
        pendencia_counts = df['Pendência'].value_counts().reset_index()
        pendencia_counts.columns = ['Pendência', 'count']
        
        usuario_counts = df['Usuário Resp'].value_counts().reset_index()
        usuario_counts.columns = ['Usuário', 'count']
        usuario_counts = usuario_counts.sort_values('count', ascending=True)  # Ordenação

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
            fig = create_bar_chart(usuario_counts, 'Usuário', 'count', 
                                 "Chamados por Usuário (Ordenados)", 
                                 horizontal=True)
            fig.update_layout(
                yaxis_title=None,
                xaxis_title="Número de Chamados",
                showlegend=False,
                margin=dict(l=100, r=20, t=40, b=20),
                coloraxis_showscale=False
            )
            fig.update_traces(
                textposition='outside' if len(usuario_counts) < 15 else 'inside',
                marker_line_color='rgba(0,0,0,0.3)'
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    dashboard()
