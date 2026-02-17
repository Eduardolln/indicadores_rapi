"""
Página Início - Dashboard Executivo
KPIs globais e visão geral do RAPI
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_summary_stats, filter_by_dimension
from utils.styling import apply_custom_css, render_header
from utils.components import render_donut_chart, render_summary_cards, render_year_selector

# Configuração da página
st.set_page_config(
    page_title="Início - RAPI",
    page_icon="🏠",
    layout="wide"
)

# Aplicar CSS
apply_custom_css()

# Header
render_header("🏠 Dashboard Executivo", "Visão Geral dos Indicadores RAPI")

# Carregar dados
try:
    df = load_data()
    
    # Renderizar seletor de ano na sidebar
    selected_year = render_year_selector(df)
    
    stats = get_summary_stats(df, year=selected_year)
    
    # KPIs Globais
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"📊 Principais Indicadores ({selected_year})")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📋 Total de Indicadores",
            value=stats['total_indicadores'],
            help="Número total de indicadores monitorados"
        )
    
    with col2:
        st.metric(
            label="🟢 Indicadores Verdes",
            value=f"{stats['pct_verde']:.1f}%",
            help=f"Percentual de indicadores que atingiram a meta verde em {selected_year}"
        )
    
    with col3:
        st.metric(
            label="🏛️ Órgãos Monitorados",
            value=stats['total_orgaos'],
            help="Número de órgãos responsáveis pelos indicadores"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico de distribuição de status
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_donut_chart(
            stats['status_counts'],
            title=f"Distribuição de Status dos Indicadores ({selected_year})"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📈 Resumo por Status")
        
        for status, count in sorted(stats['status_counts'].items(), 
                                    key=lambda x: x[1], reverse=True):
            pct = (count / stats['total_indicadores'] * 100) if stats['total_indicadores'] > 0 else 0
            
            status_icons = {
                'Verde': '🟢',
                'Amarelo': '🟡',
                'Vermelho': '🔴',
                'Cinza': '⚫'
            }
            
            icon = status_icons.get(status, '⚪')
            
            st.markdown(f"""
            <div style="padding: 0.5rem; margin: 0.5rem 0; background: #F8F9FA; border-radius: 8px;">
                <strong>{icon} {status}:</strong> {count} ({pct:.1f}%)
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Resumo por Dimensão
    st.markdown("---")
    st.subheader("🌍 Resumo por Dimensão")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🌳 Dimensão Ambiental")
        df_amb = filter_by_dimension(df, 'AMBIENTAL')
        render_summary_cards(df_amb, year=selected_year)
        total_amb = df_amb[df_amb['ano'] == selected_year]['id'].nunique()
        st.info(f"**Total:** {total_amb} indicadores")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🏙️ Dimensão Urbana")
        df_urb = filter_by_dimension(df, 'URBANA')
        render_summary_cards(df_urb, year=selected_year)
        total_urb = df_urb[df_urb['ano'] == selected_year]['id'].nunique()
        st.info(f"**Total:** {total_urb} indicadores")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Dimensão Fiscal")
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
