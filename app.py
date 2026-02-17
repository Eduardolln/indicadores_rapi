"""
Dashboard RAPI - Relatório Anual de Progresso dos Indicadores
Florianópolis - SC

Aplicação principal Streamlit
"""

import streamlit as st
from utils.styling import apply_custom_css, render_header
from utils.data_loader import load_data, get_available_years

# Configuração da página
st.set_page_config(
    page_title="RAPI Florianópolis",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados
df = load_data()

# Sidebar - Seletor de Ano
st.sidebar.markdown("### 📅 Seleção de Ano")

# Inicializar session_state
if 'selected_year' not in st.session_state:
    st.session_state['selected_year'] = 2024

# Obter anos disponíveis
available_years = get_available_years(df)

# Seletor de ano
selected_year = st.sidebar.selectbox(
    "Selecione o ano de referência:",
    options=available_years,
    index=available_years.index(st.session_state['selected_year']) if st.session_state['selected_year'] in available_years else 0,
    key='year_selector'
)

# Atualizar session_state
st.session_state['selected_year'] = selected_year

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Ano selecionado:** {selected_year}")
st.sidebar.markdown(f"*Dados disponíveis: {min(available_years)} - {max(available_years)}*")

# Aplicar CSS customizado
apply_custom_css()


# Header principal
render_header(
    "Relatório Anual de Progresso dos Indicadores (RAPI)",
    "Florianópolis - Santa Catarina"
)

# Conteúdo principal
st.markdown("## 👋 Bem-vindo ao Dashboard RAPI")

st.markdown("""
Este dashboard interativo apresenta os indicadores de progresso de Florianópolis
organizados em três dimensões principais: **Ambiental**, **Urbana** e **Fiscal**.
""")

st.markdown("### 📊 Navegação")
st.markdown("Utilize o menu lateral para navegar entre as páginas:")

st.markdown("""
- **🏠 Início** - Visão executiva com KPIs globais
- **🌳 Dimensão Ambiental** - Indicadores ambientais detalhados
- **🏙️ Dimensão Urbana** - Indicadores urbanos detalhados
- **💰 Dimensão Fiscal** - Indicadores fiscais detalhados
- **🏛️ Órgãos Responsáveis** - Visão por órgão gestor
- **📊 Análise de Indicadores** - Busca e análise detalhada com séries temporais
""")

# Informações adicionais
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="section-card">
        <h3 style="color: #2E8B57;">🎯 Objetivo</h3>
        <p style="color: #5F6368;">
            Monitorar e avaliar o progresso dos indicadores municipais
            para subsidiar a tomada de decisão e políticas públicas.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="section-card">
        <h3 style="color: #2E8B57;">📈 Classificação</h3>
        <p style="color: #5F6368;">
            <strong>🟢 Verde:</strong> Meta atingida<br>
            <strong>🟡 Amarelo:</strong> Atenção necessária<br>
            <strong>🔴 Vermelho:</strong> Abaixo da meta<br>
            <strong>⚫ Cinza:</strong> Sem dados
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="section-card">
        <h3 style="color: #2E8B57;">📅 Período</h3>
        <p style="color: #5F6368;">
            Dados disponíveis de <strong>{min(available_years)} a {max(available_years)}</strong>.
            Use o seletor na barra lateral para escolher o ano de visualização.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6C757D; padding: 1rem;">
    <p>Dashboard RAPI - Florianópolis | Desenvolvido com Streamlit 🌳</p>
</div>
""", unsafe_allow_html=True)

