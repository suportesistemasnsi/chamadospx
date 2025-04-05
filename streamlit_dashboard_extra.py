import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.supabase import carregar_chamados, carregar_chamados_fc
from plotly.subplots import make_subplots
import plotly.io as pio

# Configuração de cache
@st.cache_data(ttl=300)
def carregar_dados_dashboard():
    return carregar_chamados()

@st.cache_data(ttl=300)
def carregar_dados_dashboard_facil():
    return carregar_chamados_fc()

# Funções para gráficos
@st.cache_data
def create_pie_chart(data, values_col, names_col, title=""):
    return px.pie(data, 
                values=values_col, 
                names=names_col,
                title=title,
                template='plotly_dark',
                hole=0.3,
                color_discrete_sequence=px.colors.sequential.Blues_r)

@st.cache_data
def create_bar_chart(data, x_col, y_col, title="", color_col=None, horizontal=False):
    if horizontal:
        fig = px.bar(data,
                    y=x_col,
                    x=y_col,
                    title=title,
                    text_auto=True,
                    template='plotly_dark',
                    orientation='h',
                    color=y_col,
                    color_continuous_scale=px.colors.sequential.Blues)
    else:
        fig = px.bar(data,
                    x=x_col,
                    y=y_col,
                    title=title,
                    text_auto=True,
                    template='plotly_dark',
                    color=y_col,
                    color_continuous_scale=px.colors.sequential.Blues)
    return fig

# Função padronizada para o gráfico de usuários
def create_user_chart(data, title=""):
    fig = px.bar(data,
                y='Usuário',
                x='count',
                title=title,
                text_auto=True,
                template='plotly_dark',
                orientation='h',
                color='count',
                color_continuous_scale=px.colors.sequential.Blues)
    
    fig.update_layout(
        yaxis_title=None,
        xaxis_title="Número de Chamados",
        showlegend=False,
        margin=dict(l=100, r=20, t=40, b=20),
        coloraxis_showscale=False,
        height=max(400, 30 * len(data)))  # Altura dinâmica baseada no número de usuários
    
    fig.update_traces(
        textposition='outside',
        marker_line_color='rgba(0,0,0,0.3)',
        textfont_size=12
    )
    
    return fig

def dashboard():
    # CSS customizado
    st.markdown("""
    <style>
        .dashboard-header { text-align: center; margin-bottom: 1.5rem; }
        .dashboard-title { color: #f0f2f6; font-size: 2.2rem; display: inline; vertical-align: middle; font-weight: bold; }
        .dashboard-icon { font-size: 2.2rem; display: inline; vertical-align: middle; margin-right: 10px; }
        .stPlotlyChart { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
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
        df_facil = carregar_dados_dashboard_facil()

        # Processamento de dados Pixeon
        if isinstance(df, pd.DataFrame) and not df.empty:
            status_counts = df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'count']
            pendencia_counts = df['Pendência'].value_counts().reset_index()
            pendencia_counts.columns = ['Pendência', 'count']
            usuario_counts = df['Usuário Resp'].value_counts().reset_index()
            usuario_counts.columns = ['Usuário', 'count']
            usuario_counts = usuario_counts.sort_values('count', ascending=True)
        else:
            df = pd.DataFrame()
            status_counts = pd.DataFrame(columns=['Status', 'count'])
            pendencia_counts = pd.DataFrame(columns=['Pendência', 'count'])
            usuario_counts = pd.DataFrame(columns=['Usuário', 'count'])

        # Processamento de dados Fácil
        if isinstance(df_facil, pd.DataFrame) and not df_facil.empty:
            status_counts_fc = df_facil['Status'].value_counts().reset_index()
            status_counts_fc.columns = ['Status', 'count']
            pendencia_counts_fc = df_facil['Pendência'].value_counts().reset_index()
            pendencia_counts_fc.columns = ['Pendência', 'count']
            usuario_counts_fc = df_facil['Usuário Resp'].value_counts().reset_index()
            usuario_counts_fc.columns = ['Usuário', 'count']
            usuario_counts_fc = usuario_counts_fc.sort_values('count', ascending=True)
        else:
            df_facil = pd.DataFrame()
            status_counts_fc = pd.DataFrame(columns=['Status', 'count'])
            pendencia_counts_fc = pd.DataFrame(columns=['Pendência', 'count'])
            usuario_counts_fc = pd.DataFrame(columns=['Usuário', 'count'])

    # Layout com abas
    tab1, tab2 = st.tabs(["Chamados Pixeon", "Chamados Fácil"])

    with tab1:
        if not df.empty:
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
            st.plotly_chart(
            create_user_chart(usuario_counts, "Chamados por Usuário"),
            use_container_width=True
        )
        else:
            st.warning("Nenhum dado disponível para Chamados Pixeon")

    with tab2:
        if not df_facil.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    create_pie_chart(status_counts_fc, 'count', 'Status', "Distribuição por Status"),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    create_bar_chart(pendencia_counts_fc, 'Pendência', 'count', "Chamados por Pendência"),
                    use_container_width=True
                )
            st.plotly_chart(
            create_user_chart(usuario_counts_fc, "Chamados por Usuário"),
            use_container_width=True
        )
        else:
            st.warning("Nenhum dado disponível para Chamados Fácil")

if __name__ == "__main__":
    dashboard()
