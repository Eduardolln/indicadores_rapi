"""
Componentes reutilizáveis de UI para o Dashboard RAPI.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional, Dict



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


def render_kpi_with_sparkline(title: str, value: any, sparkline_data: List[float], delta: float = None):
    """
    Renderiza um KPI card com mini-gráfico de tendência (sparkline).
    
    Args:
        title: Título do KPI
        value: Valor principal a exibir
        sparkline_data: Lista de valores para o mini-gráfico
        delta: Variação percentual opcional
    """
    import plotly.graph_objects as go
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.metric(
            label=title,
            value=value,
            delta=f"{delta:+.1f}%" if delta is not None else None
        )
    
    with col2:
        # Criar sparkline
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=sparkline_data,
            mode='lines',
            line=dict(color='#2E8B57', width=2),
            fill='tozeroy',
            fillcolor='rgba(46, 139, 87, 0.1)'
        ))
        
        fig.update_layout(
            height=80,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"sparkline_{title}")


def render_evolution_chart(df_evolution: pd.DataFrame):
    """
    Gráfico combo de evolução anual com barras e linhas.
    
    Args:
        df_evolution: DataFrame com colunas ano, Verde, Amarelo, Vermelho, pct_verde
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Barras empilhadas
    fig.add_trace(
        go.Bar(name='Verde', x=df_evolution['ano'], y=df_evolution['Verde'],
               marker_color='#059669'),
        secondary_y=False
    )
    fig.add_trace(
        go.Bar(name='Amarelo', x=df_evolution['ano'], y=df_evolution['Amarelo'],
               marker_color='#F59E0B'),
        secondary_y=False
    )
    fig.add_trace(
        go.Bar(name='Vermelho', x=df_evolution['ano'], y=df_evolution['Vermelho'],
               marker_color='#DC2626'),
        secondary_y=False
    )
    
    # Linha de % verde
    fig.add_trace(
        go.Scatter(name='% Verde', x=df_evolution['ano'], y=df_evolution['pct_verde'],
                   mode='lines+markers', line=dict(color='#1E3A8A', width=3),
                   marker=dict(size=8)),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Evolução dos Indicadores ao Longo dos Anos',
        barmode='stack',
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(title_text="Ano")
    fig.update_yaxes(title_text="Quantidade de Indicadores", secondary_y=False)
    fig.update_yaxes(title_text="Percentual Verde (%)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)


def render_heatmap(matrix_data: pd.DataFrame):
    """
    Renderiza heatmap de performance (Dimensões x Anos).
    
    Args:
        matrix_data: DataFrame com Dimensão como primeira coluna e anos como demais colunas
    """
    import plotly.graph_objects as go
    
    # Preparar dados
    dimensions = matrix_data['Dimensão'].tolist()
    years = [col for col in matrix_data.columns if col != 'Dimensão']
    values = matrix_data[years].values
    
    fig = go.Figure(data=go.Heatmap(
        z=values,
        x=years,
        y=dimensions,
        colorscale=[
            [0, '#DC2626'],      # Vermelho para baixa performance  
            [0.5, '#F59E0B'],    # Amarelo para média
            [1, '#059669']       # Verde para alta performance
        ],
        text=[[f'{val:.1f}%' for val in row] for row in values],
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="% Verde")
    ))
    
    fig.update_layout(
        title='Mapa de Calor: Performance por Dimensão e Ano',
        xaxis_title='Ano',
        yaxis_title='Dimensão',
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_top_bottom_cards(top_data: pd.DataFrame, bottom_data: pd.DataFrame):
    """
    Renderiza cards de melhores e piores performers.
    
    Args:
        top_data: DataFrame com top indicadores
        bottom_data: DataFrame com bottom indicadores
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top 5 Melhores Indicadores")
        for idx, row in top_data.iterrows():
            status_emoji = {'Verde': '🟢', 'Amarelo': '🟡', 'Vermelho': '🔴', 'Cinza': '⚫'}
            emoji = status_emoji.get(row['status'], '')
            
            st.markdown(f"""
            <div style="padding: 0.8rem; margin: 0.5rem 0; background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%); 
                        border-radius: 8px; border-left: 4px solid #28A745;">
                <strong>{emoji} {row['indicador'][:60]}...</strong><br>
                <span style="color: #155724; font-size: 0.9rem;">
                    {row['dimensoes']} | {row['orgao_responsavel'][:30]}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ⚠️ Top 5 Que Necessitam Atenção")
        for idx, row in bottom_data.iterrows():
            status_emoji = {'Verde': '🟢', 'Amarelo': '🟡', 'Vermelho': '🔴', 'Cinza': '⚫'}
            emoji = status_emoji.get(row['status'], '')
            
            st.markdown(f"""
            <div style="padding: 0.8rem; margin: 0.5rem 0; background: linear-gradient(135deg, #F8D7DA 0%, #F5C6CB 100%); 
                        border-radius: 8px; border-left: 4px solid #DC3545;">
                <strong>{emoji} {row['indicador'][:60]}...</strong><br>
                <span style="color: #721C24; font-size: 0.9rem;">
                    {row['dimensoes']} | {row['orgao_responsavel'][:30]}
                </span>
            </div>
            """, unsafe_allow_html=True)


def render_radar_chart(dimensions_data: Dict[str, float]):
    """
    Renderiza radar chart para comparação entre dimensões.
    
    Args:
        dimensions_data: Dict com {dimensão: % performance}
    """
    import plotly.graph_objects as go
    
    categories = list(dimensions_data.keys())
    values = list(dimensions_data.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(46, 139, 87, 0.2)',
        line=dict(color='#2E8B57', width=2),
        marker=dict(size=8, color='#2E8B57')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title='Comparação entre Dimensões (% Verde)',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_insight_box(insights: List[str]):
    """
    Renderiza box destacado com insights automáticos.
    
    Args:
        insights: Lista de strings com insights
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); 
                padding: 1.5rem; border-radius: 12px; color: white; margin: 1rem 0;">
        <h3 style="margin-top: 0; color: white;">💡 Insights Automáticos</h3>
    """, unsafe_allow_html=True)
    
    for insight in insights:
        st.markdown(f"- {insight}")
    
    st.markdown("</div>", unsafe_allow_html=True)
