"""
Módulo de estilização customizada para o Dashboard RAPI.
Define CSS com tema verde conforme identidade visual.
"""

import streamlit as st


def apply_custom_css():
    """
    Aplica CSS customizado ao dashboard com tema verde.
    """
    st.markdown("""
    <style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Reset e configurações globais */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar estilizada */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2E8B57 0%, #3CB371 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg, 
    [data-testid="stSidebar"] .css-17eq0hr,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    /* Botões da sidebar */
    [data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Cartões KPI */
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #2E8B57;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-4px);
    }
    
    .kpi-title {
        color: #5F6368;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        color: #2E8B57;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .kpi-delta {
        color: #5F6368;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Badges de status */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        text-align: center;
    }
    
    .status-verde {
        background-color: #D4EDDA;
        color: #155724;
    }
    
    .status-amarelo {
        background-color: #FFF3CD;
        color: #856404;
    }
    
    .status-vermelho {
        background-color: #F8D7DA;
        color: #721C24;
    }
    
    .status-cinza {
        background-color: #E2E3E5;
        color: #383D41;
    }
    
    /* Tabelas */
    .dataframe {
        border: none !important;
    }
    
    .dataframe thead tr th {
        background-color: #2E8B57 !important;
        color: white !important;
        font-weight: 600;
        padding: 12px;
        border: none !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #F0F8F5;
        cursor: pointer;
    }
    
    /* Filtros */
    .filter-panel {
        background: #F8F9FA;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #E9ECEF;
    }
    
    /* Botões primários */
    .stButton > button {
        background-color: #2E8B57;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #246B43;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* Selectbox e Multiselect */
    .stSelectbox, .stMultiSelect {
        border-radius: 8px;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #F0F8F5;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Cards de seção */
    .section-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }
    
    .section-header {
        color: #2E8B57;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        border-bottom: 3px solid #2E8B57;
        padding-bottom: 0.5rem;
    }
    
    /* Ícones de tendência */
    .trend-icon {
        font-size: 1.5rem;
        margin-left: 0.5rem;
    }
    
    /* Métricas do Streamlit */
    [data-testid="stMetricValue"] {
        color: #2E8B57;
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #5F6368;
        font-weight: 500;
    }
    
    /* Container principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Animações suaves */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animated-enter {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Scrollbar customizada */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F1F1F1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2E8B57;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #246B43;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        
        .kpi-value {
            font-size: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = None):
    """
    Renderiza o cabeçalho principal da página.
    
    Args:
        title: Título principal
        subtitle: Subtítulo opcional
    """
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    
    st.markdown(f"""
    <div class="main-header animated-enter">
        <h1>{title}</h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)
