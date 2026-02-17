"""
Componentes reutilizáveis de UI para o Dashboard RAPI.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional


def render_kpi_card(title: str, value: any, delta: str = None, icon: str = None):
    """
    Renderiza um cartão KPI.
    
    Args:
        title: Título do KPI
        value: Valor a exibir
        delta: Valor de variação (opcional)
        icon: Emoji de ícone (opcional)
    """
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if icon:
            st.markdown(f"<div style='font-size: 3rem;'>{icon}</div>", unsafe_allow_html=True)
    
    with col2:
        st.metric(label=title, value=value, delta=delta)


def render_status_badge(status: str) -> str:
    """
    Retorna HTML de um badge de status colorido.
    
    Args:
        status: Status ('Verde', 'Amarelo', 'Vermelho', 'Cinza')
        
    Returns:
        HTML do badge
    """
    status_lower = status.lower()
    
    icons = {
        'verde': '🟢',
        'amarelo': '🟡',
        'vermelho': '🔴',
        'cinza': '⚫'
    }
    
    icon = icons.get(status_lower, '⚪')
    
    return f'<span class="status-badge status-{status_lower}">{icon} {status}</span>'


def render_filter_panel(df: pd.DataFrame, dimension: str = None) -> dict:
    """
    Renderiza painel de filtros e retorna os valores selecionados.
    
    Args:
        df: DataFrame para extrair opções de filtro
        dimension: Dimensão opcional para pré-filtrar
        
    Returns:
        Dicionário com filtros selecionados
    """
    from utils.data_loader import get_available_filters
    
    filters = get_available_filters(df, dimension)
    
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.subheader("🔍 Filtros")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_pilares = st.multiselect(
            "Pilar",
            options=filters['pilares'],
            default=None,
            key=f"filter_pilar_{dimension}"
        )
    
    with col2:
        # Filtrar temas baseado em pilares selecionados
        if selected_pilares:
            df_filtered = df[df['pilar'].isin(selected_pilares)]
            temas_options = sorted(df_filtered['tema'].dropna().unique().tolist())
        else:
            temas_options = filters['temas']
        
        selected_temas = st.multiselect(
            "Tema",
            options=temas_options,
            default=None,
            key=f"filter_tema_{dimension}"
        )
    
    with col3:
        selected_orgaos = st.multiselect(
            "Órgão Responsável",
            options=filters['orgaos'],
            default=None,
            key=f"filter_orgao_{dimension}"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return {
        'pilares': selected_pilares,
        'temas': selected_temas,
        'orgaos': selected_orgaos
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Aplica filtros ao DataFrame.
    
    Args:
        df: DataFrame original
        filters: Dicionário com filtros
        
    Returns:
        DataFrame filtrado
    """
    df_filtered = df.copy()
    
    if filters['pilares']:
        df_filtered = df_filtered[df_filtered['pilar'].isin(filters['pilares'])]
    
    if filters['temas']:
        df_filtered = df_filtered[df_filtered['tema'].isin(filters['temas'])]
    
    if filters['orgaos']:
        df_filtered = df_filtered[df_filtered['orgao_responsavel'].isin(filters['orgaos'])]
    
    return df_filtered


def render_hierarchical_table(df: pd.DataFrame, year: int = 2024):
    """
    Renderiza tabela hierárquica com Pilar > Tema > Indicador.
    
    Args:
        df: DataFrame filtrado
        year: Ano para exibir valores (padrão: 2024)
    """
    df_year = df[df['ano'] == year].copy()
    
    if df_year.empty:
        st.warning(f"Não há dados disponíveis para o ano {year}")
        return
    
    # Preparar dados para exibição
    display_df = df_year[[
        'pilar', 'tema', 'indicador', 'valor', 'status', 'tendencia_icon'
    ]].copy()
    
    display_df.columns = ['Pilar', 'Tema', 'Indicador', f'Valor {year}', 'Status', 'Tendência']
    
    # Formatar valor
    display_df[f'Valor {year}'] = display_df[f'Valor {year}'].apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else "N/D"
    )
    
    # Renderizar tabela
    st.dataframe(
        display_df,
        use_container_width=True,
        height=600,
        hide_index=True
    )


def render_donut_chart(status_counts: dict, title: str = "Distribuição de Status"):
    """
    Renderiza gráfico de rosca (donut) com distribuição de status.
    
    Args:
        status_counts: Dicionário com contagens por status
        title: Título do gráfico
    """
    # Cores customizadas
    colors = {
        'Verde': '#28A745',
        'Amarelo': '#FFC107',
        'Vermelho': '#DC3545',
        'Cinza': '#6C757D'
    }
    
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    color_list = [colors.get(label, '#CCCCCC') for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=color_list),
        textinfo='label+percent',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{label}</b><br>Contagem: %{value}<br>Percentual: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20, color='#2E8B57')),
        showlegend=True,
        height=400,
        margin=dict(t=80, b=40, l=40, r=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_line_chart(df_series: pd.DataFrame, indicator_name: str, 
                      faixa_1: str = None, faixa_2: str = None):
    """
    Renderiza gráfico de linha com série temporal.
    
    Args:
        df_series: DataFrame com colunas 'ano' e 'valor'
        indicator_name: Nome do indicador
        faixa_1: String da faixa verde (opcional)
        faixa_2: String da faixa amarela (opcional)
    """
    fig = go.Figure()
    
    # Linha principal
    fig.add_trace(go.Scatter(
        x=df_series['ano'],
        y=df_series['valor'],
        mode='lines+markers',
        name='Valor',
        line=dict(color='#2E8B57', width=3),
        marker=dict(size=10, color='#2E8B57')
    ))
    
    # Linhas de referência (se disponíveis)
    if faixa_1:
        from utils.data_loader import parse_range
        verde_min, verde_max = parse_range(faixa_1)
        
        if verde_min is not None:
            fig.add_hline(
                y=verde_min, 
                line_dash="dash", 
                line_color="green",
                annotation_text="Meta Verde (Min)",
                annotation_position="right"
            )
    
    fig.update_layout(
        title=dict(text=indicator_name, font=dict(size=18, color='#2E8B57')),
        xaxis_title="Ano",
        yaxis_title="Valor",
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_dimension_header(dimension_name: str, icon: str = ""):
    """
    Renderiza cabeçalho de uma dimensão.
    
    Args:
        dimension_name: Nome da dimensão
        icon: Emoji/ícone
    """
    st.markdown(f"""
    <div class="section-header">
        {icon} {dimension_name}
    </div>
    """, unsafe_allow_html=True)


def render_summary_cards(df: pd.DataFrame, year: int = 2024):
    """
    Renderiza cartões resumidos de status.
    
    Args:
        df: DataFrame da dimensão
        year: Ano de referência
    """
    df_year = df[df['ano'] == year]
    
    status_counts = df_year['status'].value_counts().to_dict()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        verde_count = status_counts.get('Verde', 0)
        st.metric("🟢 Verde", verde_count)
    
    with col2:
        amarelo_count = status_counts.get('Amarelo', 0)
        st.metric("🟡 Amarelo", amarelo_count)
    
    with col3:
        vermelho_count = status_counts.get('Vermelho', 0)
        st.metric("🔴 Vermelho", vermelho_count)
    
    with col4:
        cinza_count = status_counts.get('Cinza', 0)
        st.metric("⚫ Sem Dados", cinza_count)


def render_year_selector(df):
    """
    Renderiza seletor de ano na sidebar e retorna o ano selecionado.
    
    Args:
        df: DataFrame completo com dados
        
    Returns:
        Ano selecionado pelo usuário
    """
    from utils.data_loader import get_available_years
    
    # Inicializar session_state se necessário
    if 'selected_year' not in st.session_state:
        st.session_state['selected_year'] = 2024
    
    # Obter anos disponíveis
    available_years = get_available_years(df)
    
    # Seletor de ano na sidebar
    
    selected_year = st.sidebar.selectbox(
        "Selecione o ano de referência:",
        options=available_years,
        index=available_years.index(st.session_state['selected_year']) if st.session_state['selected_year'] in available_years else 0,
        key='year_selector_widget'
    )
    
    # Atualizar session_state
    st.session_state['selected_year'] = selected_year
    
    # Informações adicionais
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Ano selecionado:** {selected_year}")
    st.sidebar.markdown(f"*Dados disponíveis: {min(available_years)} - {max(available_years)}*")
    
    return selected_year
