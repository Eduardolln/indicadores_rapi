"""
Página Órgãos Responsáveis
Visão por órgão gestor dos indicadores
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.styling import apply_custom_css, render_header
from utils.components import render_status_badge, render_year_selector

# Configuração da página
st.set_page_config(
    page_title="Órgãos Responsáveis - RAPI",
    page_icon="🏛️",
    layout="wide"
)

# Aplicar CSS
apply_custom_css()

# Header
render_header("🏛️ Órgãos Responsáveis", "Visão por Órgão Gestor dos Indicadores")

try:
    # Carregar dados
    df = load_data()
    
    # Renderizar seletor de ano na sidebar
    selected_year = render_year_selector(df)
    
    df_year = df[df['ano'] == selected_year].copy()
    
    # Seletor de órgão
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🔍 Filtrar por Órgão")
    
    orgaos_lista = sorted(df_year['orgao_responsavel'].dropna().unique().tolist())
    selected_orgao = st.selectbox(
        "Selecione um órgão para ver detalhes:",
        options=['Todos'] + orgaos_lista,
        index=0
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Se um órgão específico foi selecionado
    if selected_orgao != 'Todos':
        df_orgao = df_year[df_year['orgao_responsavel'] == selected_orgao]
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader(f"📊 {selected_orgao}")
        
        # Estatísticas do órgão
        total_indicadores = df_orgao['id'].nunique()
        status_counts = df_orgao['status'].value_counts().to_dict()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total de Indicadores", total_indicadores)
        
        with col2:
            verde = status_counts.get('Verde', 0)
            st.metric("🟢 Verde", verde)
        
        with col3:
            amarelo = status_counts.get('Amarelo', 0)
            st.metric("🟡 Amarelo", amarelo)
        
        with col4:
            vermelho = status_counts.get('Vermelho', 0)
            st.metric("🔴 Vermelho", vermelho)
        
        st.markdown("---")
        
        # Lista de indicadores
        st.subheader("📋 Indicadores do Órgão")
        
        display_df = df_orgao[[
            'dimensoes', 'pilar', 'tema', 'indicador', 'valor', 'status', 'tendencia_icon'
        ]].copy()
        
        display_df.columns = ['Dimensão', 'Pilar', 'Tema', 'Indicador', f'Valor {selected_year}', 'Status', 'Tendência']
        
        display_df[f'Valor {selected_year}'] = display_df[f'Valor {selected_year}'].apply(
            lambda x: f"{x:.2f}" if pd.notna(x) else "N/D"
        )
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Visão geral de todos os órgãos
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📊 Resumo de Todos os Órgãos")
        
        # Agrupar por órgão
        orgaos_stats = []
        
        for orgao in orgaos_lista:
            df_org = df_year[df_year['orgao_responsavel'] == orgao]
            total = df_org['id'].nunique()
            status_counts = df_org['status'].value_counts().to_dict()
            
            orgaos_stats.append({
                'Órgão': orgao,
                'Total Indicadores': total,
                '🟢 Verde': status_counts.get('Verde', 0),
                '🟡 Amarelo': status_counts.get('Amarelo', 0),
                '🔴 Vermelho': status_counts.get('Vermelho', 0),
                '⚫ Sem Dados': status_counts.get('Cinza', 0)
            })
        
        df_orgaos = pd.DataFrame(orgaos_stats)
        df_orgaos = df_orgaos.sort_values('Total Indicadores', ascending=False)
        
        st.dataframe(
            df_orgaos,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Top órgãos
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("🏆 Órgãos com Mais Indicadores")
            top_5 = df_orgaos.nlargest(5, 'Total Indicadores')
            
            for idx, row in top_5.iterrows():
                st.markdown(f"""
                <div style="padding: 0.8rem; margin: 0.5rem 0; background: #F8F9FA; border-radius: 8px; border-left: 4px solid #2E8B57;">
                    <strong>{row['Órgão']}</strong><br>
                    <span style="color: #6C757D;">Total: {row['Total Indicadores']} indicadores</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("🌟 Órgãos com Mais Indicadores Verdes")
            top_verde = df_orgaos.nlargest(5, '🟢 Verde')
            
            for idx, row in top_verde.iterrows():
                pct_verde = (row['🟢 Verde'] / row['Total Indicadores'] * 100) if row['Total Indicadores'] > 0 else 0
                st.markdown(f"""
                <div style="padding: 0.8rem; margin: 0.5rem 0; background: #D4EDDA; border-radius: 8px; border-left: 4px solid #28A745;">
                    <strong>{row['Órgão']}</strong><br>
                    <span style="color: #155724;">🟢 {row['🟢 Verde']} verdes ({pct_verde:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Informações
    st.markdown("---")
    st.info("""
    💡 **Dica:** Selecione um órgão específico acima para ver a lista completa de indicadores 
    sob sua responsabilidade.
    """)

except Exception as e:
    st.error(f"❌ **Erro ao carregar dados:** {str(e)}")
    st.exception(e)
