"""
Página Dimensão Fiscal
Indicadores fiscais com filtros e visualização hierárquica
"""

import streamlit as st
from utils.data_loader import load_data, filter_by_dimension
from utils.styling import apply_custom_css, render_header
from utils.components import (
    render_filter_panel, apply_filters, render_hierarchical_table,
    render_summary_cards, render_dimension_header, render_year_selector
)

# Configuração da página
st.set_page_config(
    page_title="Dimensão Fiscal - RAPI",
    page_icon="💰",
    layout="wide"
)

# Aplicar CSS
apply_custom_css()

# Header
render_header("💰 Dimensão Fiscal", "Indicadores de Gestão Fiscal e Orçamentária")

try:
    # Carregar dados
    df = load_data()
    
    # Renderizar seletor de ano na sidebar
    selected_year = render_year_selector(df)
    
    df_fisc = filter_by_dimension(df, 'FISCAL')
    
    # Resumo de status
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"📊 Resumo Geral ({selected_year})")
    render_summary_cards(df_fisc, year=selected_year)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Painel de filtros
    filters = render_filter_panel(df_fisc, dimension='FISCAL')
    
    # Aplicar filtros
    df_filtered = apply_filters(df_fisc, filters)
    
    # Informação sobre filtros
    total_filtrado = df_filtered[df_filtered['ano'] == selected_year]['id'].nunique()
    total_original = df_fisc[df_fisc['ano'] == selected_year]['id'].nunique()
    
    if any([filters['pilares'], filters['temas'], filters['orgaos']]):
        st.info(f"📌 Mostrando **{total_filtrado}** de **{total_original}** indicadores")
    
    # Tabela hierárquica
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"📋 Indicadores Fiscais - {selected_year}")
    
    if df_filtered.empty:
        st.warning("⚠️ Nenhum indicador encontrado com os filtros selecionados.")
    else:
        render_hierarchical_table(df_filtered, year=selected_year)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Informações adicionais
    st.markdown("---")
    st.info("""
    💡 **Sobre os Indicadores Fiscais:**
    
    Esta dimensão abrange indicadores relacionados a:
    - 💵 Receitas e despesas públicas
    - 📊 Endividamento municipal
    - 💼 Gestão orçamentária
    - 🏦 Transparência fiscal
    - 📈 Eficiência dos gastos públicos
    
    Use a página **Análise de Indicadores** para visualizar séries temporais detalhadas.
    """)

except Exception as e:
    st.error(f"❌ **Erro ao carregar dados:** {str(e)}")
    st.exception(e)
