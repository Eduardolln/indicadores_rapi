"""
Página Início - Dashboard Executivo
KPIs globais e visão geral do RAPI com visualizações profissionais
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_data, get_summary_stats, filter_by_dimension,
    get_yearly_evolution, calculate_year_over_year,
    get_top_bottom_indicators, get_dimension_performance_matrix,
    generate_insights, get_sparkline_data
)
from utils.styling import apply_custom_css, render_header
from utils.components import (
    render_donut_chart, render_summary_cards, render_year_selector,
    render_kpi_with_sparkline, render_evolution_chart,
    render_heatmap, render_top_bottom_cards, render_radar_chart,
    render_insight_box
)

# Configuração da página
st.set_page_config(
    page_title="Início - RAPI",
    page_icon="🏠",
    layout="wide"
)

# Aplicar CSS
apply_custom_css()

#Header
render_header("🏠 Dashboard Executivo", "Visão Geral dos Indicadores RAPI")

# Carregar dados
try:
    df = load_data()
    
    # Renderizar seletor de ano na sidebar
    selected_year = render_year_selector(df)
    
    stats = get_summary_stats(df, year=selected_year)
    yoy = calculate_year_over_year(df, selected_year)
    
    # ==================================================
    # SEÇÃO 1: INSIGHTS AUTOMÁTICOS
    # ==================================================
    insights = generate_insights(df, selected_year)
    render_insight_box(insights)
    
    st.markdown("---")
    
    # ==================================================
    # SEÇÃO 2: KPIs PRINCIPAIS COM SPARKLINES
    # ==================================================
    st.subheader(f"📊 Indicadores-Chave de Performance ({selected_year})")
    
    col1, col2, col3 = st.columns(3)
    
    # Obter dados de sparkline para últimos 5 anos
    sparkline_verde = get_sparkline_data(df, metric='pct_verde', last_n_years=5)
    sparkline_total = get_sparkline_data(df, metric='verde', last_n_years=5)
    
    with col1:
        render_kpi_with_sparkline(
            title="📋 Total de Indicadores",
            value=stats['total_indicadores'],
            sparkline_data=sparkline_total,
            delta=None
        )
    
    with col2:
        render_kpi_with_sparkline(
            title="🟢 Performance Verde",
            value=f"{stats['pct_verde']:.1f}%",
            sparkline_data=sparkline_verde,
            delta=yoy['variation'] if yoy['variation'] != 0 else None
        )
    
    with col3:
        st.metric(
            label="🏛️ Órgãos Monitorados",
            value=stats['total_orgaos'],
            help="Número de órgãos responsáveis pelos indicadores"
        )
    
    st.markdown("---")
    
    # ==================================================
    # SEÇÃO 3: EVOLUÇÃO TEMPORAL
    # ==================================================
    st.subheader("📈 Evolução Histórica dos Indicadores")
    
    evolution_df = get_yearly_evolution(df)
    render_evolution_chart(evolution_df)
    
    st.markdown("---")
    
   # ==================================================
    # SEÇÃO 4: ANÁLISE POR DIMENSÃO
    # ==================================================
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🗺️ Mapa de Calor: Performance por Dimensão")
        matrix_data = get_dimension_performance_matrix(df)
        render_heatmap(matrix_data)
    
    with col2:
        st.subheader("🎯 Comparação entre Dimensões")
        # Preparar dados para radar chart
        df_year = df[df['ano'] == selected_year]
        radar_data = {}
        for dim in df_year['dimensoes'].unique():
            df_dim = df_year[df_year['dimensoes'] == dim]
            total = df_dim['id'].nunique()
            verde = (df_dim['status'] == 'Verde').sum()
            pct = (verde / total * 100) if total > 0 else 0
            radar_data[dim] = pct
        
        render_radar_chart(radar_data)
    
    st.markdown("---")
    
    # ==================================================
    # SEÇÃO 5: TOP/BOTTOM PERFORMERS
    # ==================================================
    st.subheader(f"🏅 Destaques e Oportunidades de Melhoria ({selected_year})")
    
    top_indicators, bottom_indicators = get_top_bottom_indicators(df, selected_year, n=5)
    render_top_bottom_cards(top_indicators, bottom_indicators)
    
    st.markdown("---")
    
    # ==================================================
    # SEÇÃO 6: RESUMO POR DIMENSÃO (COMPACTO)
    # ==================================================
    st.subheader("🌍 Resumo Rápido por Dimensão")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🌳 Ambiental")
        df_amb = filter_by_dimension(df, 'AMBIENTAL')
        render_summary_cards(df_amb, year=selected_year)
        total_amb = df_amb[df_amb['ano'] == selected_year]['id'].nunique()
        st.info(f"**Total:** {total_amb} indicadores")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🏙️ Urbana")
        df_urb = filter_by_dimension(df, 'URBANO')
        render_summary_cards(df_urb, year=selected_year)
        total_urb = df_urb[df_urb['ano'] == selected_year]['id'].nunique()
        st.info(f"**Total:** {total_urb} indicadores")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Fiscal")
        df_fisc = filter_by_dimension(df, 'FISCAL')
        render_summary_cards(df_fisc, year=selected_year)
        total_fisc = df_fisc[df_fisc['ano'] == selected_year]['id'].nunique()
        st.info(f"**Total:** {total_fisc} indicadores")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Informações adicionais
    st.markdown("---")
    st.info("""
    💡 **Dica:** Utilize o menu lateral para explorar os indicadores de cada dimensão 
    ou buscar por indicadores específicos na página de Análise de Indicadores.
    """)

except FileNotFoundError:
    st.error("""
    ❌ **Erro:** Arquivo `bd_RAPI.csv` não encontrado.
    
    Por favor, certifique-se de que o arquivo está no diretório raiz do projeto.
    """)
except Exception as e:
    st.error(f"❌ **Erro ao carregar dados:** {str(e)}")
    st.exception(e)
