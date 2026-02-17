"""
Página Análise de Indicadores
Busca detalhada e visualização de séries temporais
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_time_series
from utils.styling import apply_custom_css, render_header
from utils.components import render_line_chart, render_status_badge, render_year_selector

# Configuração da página
st.set_page_config(
    page_title="Análise de Indicadores - RAPI",
    page_icon="📊",
    layout="wide"
)

# Aplicar CSS
apply_custom_css()

# Header
render_header("📊 Análise Detalhada de Indicadores", "Busca e Visualização de Séries Temporais")

try:
    # Carregar dados
    df = load_data()
    
    # Renderizar seletor de ano na sidebar
    selected_year = render_year_selector(df)
    
    # Painel de busca
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🔍 Buscar Indicador")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_text = st.text_input(
            "Digite o nome ou palavras-chave do indicador:",
            placeholder="Ex: água, energia, resíduos..."
        )
    
    with col2:
        dimension_filter = st.selectbox(
            "Dimensão:",
            options=['Todas', 'AMBIENTAL', 'URBANO', 'FISCAL']
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtrar indicadores
    df_unique = df.drop_duplicates(subset=['id']).copy()
    
    if dimension_filter != 'Todas':
        df_unique = df_unique[df_unique['dimensoes'] == dimension_filter]
    
    if search_text:
        mask = df_unique['indicador'].str.contains(search_text, case=False, na=False)
        df_unique = df_unique[mask]
    
    # Lista de resultados
    st.markdown("---")
    
    if df_unique.empty:
        st.warning("⚠️ Nenhum indicador encontrado com os critérios de busca.")
    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader(f"📋 Resultados ({len(df_unique)} indicadores encontrados)")
        
        # Criar lista de opções para seleção
        indicadores_options = {}
        for idx, row in df_unique.iterrows():
            label = f"{row['indicador'][:80]}... - ({row['dimensoes']} | {row['orgao_responsavel']})"
            indicadores_options[label] = row['id']
        
        selected_label = st.selectbox(
            "Selecione um indicador para visualizar:",
            options=list(indicadores_options.keys())
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Detalhes do indicador selecionado
        if selected_label:
            selected_id = indicadores_options[selected_label]
            
            # Obter dados do indicador
            df_indicator = df[df['id'] == selected_id].iloc[0]
            df_series = get_time_series(df, selected_id)
            
            st.markdown("---")
            
            # Informações do indicador
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📌 Informações do Indicador")
                st.markdown(f"**Nome:** {df_indicator['indicador']}")
                st.markdown(f"**Dimensão:** {df_indicator['dimensoes']}")
                st.markdown(f"**Pilar:** {df_indicator['pilar']}")
                st.markdown(f"**Tema:** {df_indicator['tema']}")
                st.markdown(f"**Órgão Responsável:** {df_indicator['orgao_responsavel']}")
            
            with col2:
                # Valor do ano selecionado
                valor_year = df[df['id'] == selected_id][df['ano'] == selected_year]['valor'].values
                status_year = df[df['id'] == selected_id][df['ano'] == selected_year]['status'].values
                trend_year = df[df['id'] == selected_id][df['ano'] == selected_year]['tendencia_icon'].values
                
                if len(valor_year) > 0:
                    st.metric(f"📊 Valor {selected_year}", f"{valor_year[0]:.2f}" if pd.notna(valor_year[0]) else "N/D")
                    
                    if len(status_year) > 0:
                        st.markdown(f"**Status:** {render_status_badge(status_year[0])}", unsafe_allow_html=True)
                    
                    if len(trend_year) > 0:
                        st.markdown(f"**Tendência:** {trend_year[0]}")
                else:
                    st.info(f"Sem dados para {selected_year}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Faixas de metas
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("🎯 Metas e Faixas de Avaliação")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                faixa_verde = df_indicator.get('faixa_1', 'N/D')
                st.markdown(f"""
                <div style="padding: 1rem; background: #D4EDDA; border-radius: 8px; border-left: 4px solid #28A745;">
                    <strong>🟢 Faixa Verde</strong><br>
                    <span style="color: #155724;">{faixa_verde}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                faixa_amarela = df_indicator.get('faixa_2', 'N/D')
                st.markdown(f"""
                <div style="padding: 1rem; background: #FFF3CD; border-radius: 8px; border-left: 4px solid #FFC107;">
                    <strong>🟡 Faixa Amarela</strong><br>
                    <span style="color: #856404;">{faixa_amarela}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                faixa_vermelha = df_indicator.get('faixa_3', 'N/D')
                st.markdown(f"""
                <div style="padding: 1rem; background: #F8D7DA; border-radius: 8px; border-left: 4px solid #DC3545;">
                    <strong>🔴 Faixa Vermelha</strong><br>
                    <span style="color: #721C24;">{faixa_vermelha}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Gráfico de série temporal
            st.markdown("---")
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("📈 Série Temporal")
            
            if df_series.empty or df_series['valor'].isna().all():
                st.warning("⚠️ Não há dados históricos disponíveis para este indicador.")
            else:
                render_line_chart(
                    df_series,
                    df_indicator['indicador'],
                    faixa_1=df_indicator.get('faixa_1'),
                    faixa_2=df_indicator.get('faixa_2')
                )
                
                # Tabela de dados
                with st.expander("📋 Ver Dados Tabulares"):
                    df_display = df_series.copy()
                    df_display['valor'] = df_display['valor'].apply(
                        lambda x: f"{x:.2f}" if pd.notna(x) else "N/D"
                    )
                    df_display.columns = ['Ano', 'Valor']
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Placeholder para análise qualitativa e ODS
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("📝 Análise Qualitativa")
                st.info("ℹ️ Análise qualitativa não disponível no dataset atual.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("🌍 Objetivos de Desenvolvimento Sustentável (ODS)")
                st.info("ℹ️ Metas ODS não disponíveis no dataset atual.")
                st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ **Erro ao carregar dados:** {str(e)}")
    st.exception(e)
