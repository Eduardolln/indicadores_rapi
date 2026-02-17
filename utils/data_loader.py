"""
Módulo de ETL e processamento de dados para o Dashboard RAPI.
Responsável por carregar, limpar e transformar os dados do CSV.
"""

import pandas as pd
import streamlit as st
import re
from typing import Dict, List, Tuple, Optional


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Carrega e cacheia os dados do CSV bd_RAPI.csv.
    
    Returns:
        DataFrame com os dados do RAPI
    """
    df = pd.read_csv('bd_RAPI.csv')
    
    # Limpar e converter valores
    df = clean_valor(df)
    
    # Adicionar colunas computadas
    df = add_computed_columns(df)
    
    return df


def clean_valor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e converte a coluna 'valor' para numérico.
    Trata valores como 'ND', '-', strings vazias convertendo para NaN.
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame com coluna valor limpa
    """
    df = df.copy()
    
    # Substituir valores inválidos por NaN
    df['valor'] = df['valor'].replace(['ND', '-', '', ' '], pd.NA)
    
    # Converter para numérico (coerce força conversão de erros para NaN)
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    
    return df


def parse_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parseia strings de faixa como "> 90%–100%" ou "120–200" em tuplas (min, max).
    
    Args:
        range_str: String da faixa (ex: "> 90%–100%", "< 75%")
        
    Returns:
        Tupla (min, max) ou (None, None) se não parseável
    """
    if pd.isna(range_str) or not isinstance(range_str, str):
        return (None, None)
    
    # Remover espaços e substituir travessão por hífen
    range_str = range_str.strip().replace('–', '-').replace('%', '')
    
    # Casos especiais
    if '>' in range_str and '-' in range_str:
        # Ex: "> 90-100" ou ">90-100"
        match = re.search(r'>?\s*(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', range_str)
        if match:
            return (float(match.group(1)), float(match.group(2)))
    
    if '<' in range_str and '-' in range_str:
        # Ex: "< 80" ou "<80-120"
        match = re.search(r'<?\s*(\d+\.?\d*)\s*-?\s*(\d+\.?\d*)?', range_str)
        if match:
            min_val = float(match.group(1)) if match.group(1) else None
            max_val = float(match.group(2)) if match.group(2) else None
            return (None, min_val) if not max_val else (min_val, max_val)
    
    if '>' in range_str:
        # Ex: "> 20 h/dia"
        match = re.search(r'>\s*(\d+\.?\d*)', range_str)
        if match:
            return (float(match.group(1)), None)
    
    if '<' in range_str:
        # Ex: "< 75"
        match = re.search(r'<\s*(\d+\.?\d*)', range_str)
        if match:
            return (None, float(match.group(1)))
    
    # Faixa simples: "120-200"
    match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', range_str)
    if match:
        return (float(match.group(1)), float(match.group(2)))
    
    # Valor único
    match = re.search(r'(\d+\.?\d*)', range_str)
    if match:
        val = float(match.group(1))
        return (val, val)
    
    return (None, None)


def classify_status(row: pd.Series) -> str:
    """
    Classifica o status de um indicador baseado no valor de 2024 e nas faixas.
    
    Args:
        row: Linha do DataFrame com colunas faixa_1, faixa_2, faixa_3 e valor
        
    Returns:
        Status: 'Verde', 'Amarelo', 'Vermelho', ou 'Cinza'
    """
    valor = row.get('valor', None)
    
    # Se não há valor, retorna Cinza
    if pd.isna(valor):
        return 'Cinza'
    
    # Parsear as faixas
    verde_min, verde_max = parse_range(row.get('faixa_1', ''))
    amarelo_min, amarelo_max = parse_range(row.get('faixa_2', ''))
    vermelho_min, vermelho_max = parse_range(row.get('faixa_3', ''))
    
    # Verificar se está na faixa verde (faixa_1)
    if verde_min is not None and verde_max is not None:
        if verde_min <= valor <= verde_max:
            return 'Verde'
    elif verde_min is not None and verde_max is None:
        if valor >= verde_min:
            return 'Verde'
    elif verde_min is None and verde_max is not None:
        if valor <= verde_max:
            return 'Verde'
    
    # Verificar se está na faixa amarela (faixa_2)
    if amarelo_min is not None and amarelo_max is not None:
        if amarelo_min <= valor <= amarelo_max:
            return 'Amarelo'
    elif amarelo_min is not None and amarelo_max is None:
        if valor >= amarelo_min:
            return 'Amarelo'
    elif amarelo_min is None and amarelo_max is not None:
        if valor <= amarelo_max:
            return 'Amarelo'
    
    # Verificar se está na faixa vermelha (faixa_3)
    if vermelho_min is not None and vermelho_max is not None:
        if vermelho_min <= valor <= vermelho_max:
            return 'Vermelho'
    elif vermelho_min is not None and vermelho_max is None:
        if valor >= vermelho_min:
            return 'Vermelho'
    elif vermelho_min is None and vermelho_max is not None:
        if valor <= vermelho_max:
            return 'Vermelho'
    
    # Se não se encaixa em nenhuma faixa, retorna Cinza
    return 'Cinza'


def calculate_trend(df: pd.DataFrame, year: int = 2024) -> pd.DataFrame:
    """
    Calcula a tendência comparando o ano especificado vs ano anterior.
    
    Args:
        df: DataFrame com dados
        year: Ano de referência para calcular tendência (padrão: 2024)
        
    Returns:
        DataFrame com coluna tendencia_icon adicionada
    """
    df = df.copy()
    
    # Criar pivot para facilitar comparação ano a ano
    year_prev = year - 1
    df_current = df[df['ano'] == year][['id', 'valor']].rename(columns={'valor': f'valor_{year}'})
    df_previous = df[df['ano'] == year_prev][['id', 'valor']].rename(columns={'valor': f'valor_{year_prev}'})
    
    # Merge
    df_trend = df.merge(df_current, on='id', how='left')
    df_trend = df_trend.merge(df_previous, on='id', how='left')
    
    # Calcular tendência
    def get_trend_icon(row):
        v_current = row.get(f'valor_{year}')
        v_previous = row.get(f'valor_{year_prev}')
        
        if pd.isna(v_current) or pd.isna(v_previous):
            return '➡️'  # Sem dados suficientes
        
        if v_current > v_previous:
            return '⬆️'
        elif v_current < v_previous:
            return '⬇️'
        else:
            return '➡️'
    
    df_trend['tendencia_icon'] = df_trend.apply(get_trend_icon, axis=1)
    
    # Remover colunas auxiliares
    df_trend = df_trend.drop(columns=[f'valor_{year}', f'valor_{year_prev}'], errors='ignore')
    
    return df_trend


def add_computed_columns(df: pd.DataFrame, year: int = 2024) -> pd.DataFrame:
    """
    Adiciona colunas computadas (status, tendência) ao DataFrame.
    
    Args:
        df: DataFrame original
        year: Ano de referência para cálculo de tendência (padrão: 2024)
        
    Returns:
        DataFrame com colunas adicionadas
    """
    df = df.copy()
    
    # Adicionar status
    df['status'] = df.apply(classify_status, axis=1)
    
    # Adicionar tendência para o ano especificado
    df = calculate_trend(df, year=year)
    
    return df


def get_summary_stats(df: pd.DataFrame, year: int = 2024) -> Dict[str, any]:
    """
    Calcula estatísticas resumidas globais.
    
    Args:
        df: DataFrame completo
        year: Ano para calcular estatísticas (padrão: 2024)
        
    Returns:
        Dicionário com estatísticas
    """
    # Filtrar dados do ano especificado
    df_year = df[df['ano'] == year].copy()
    
    total_indicadores = df_year['id'].nunique()
    total_orgaos = df_year['orgao_responsavel'].nunique()
    
    # Contagem por status
    status_counts = df_year['status'].value_counts().to_dict()
    verde_count = status_counts.get('Verde', 0)
    
    pct_verde = (verde_count / total_indicadores * 100) if total_indicadores > 0 else 0
    
    return {
        'total_indicadores': total_indicadores,
        'total_orgaos': total_orgaos,
        'pct_verde': pct_verde,
        'status_counts': status_counts
    }


def filter_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """
    Filtra o DataFrame por dimensão.
    
    Args:
        df: DataFrame completo
        dimension: Nome da dimensão ('AMBIENTAL', 'URBANO', 'FISCAL')
        
    Returns:
        DataFrame filtrado
    """
    return df[df['dimensoes'] == dimension.upper()].copy()


def get_time_series(df: pd.DataFrame, indicator_id: int) -> pd.DataFrame:
    """
    Obtém série temporal de um indicador específico.
    
    Args:
        df: DataFrame completo
        indicator_id: ID do indicador
        
    Returns:
        DataFrame com série temporal (ano, valor)
    """
    return df[df['id'] == indicator_id][['ano', 'valor']].sort_values('ano')


def get_available_years(df: pd.DataFrame) -> List[int]:
    """
    Retorna lista de anos disponíveis no dataset em ordem decrescente.
    
    Args:
        df: DataFrame completo
        
    Returns:
        Lista de anos únicos ordenados do mais recente para o mais antigo
    """
    years = sorted(df['ano'].dropna().unique().tolist(), reverse=True)
    return [int(year) for year in years]


def get_available_filters(df: pd.DataFrame, dimension: str = None) -> Dict[str, List[str]]:
    """
    Retorna listas de valores únicos para filtros.
    
    Args:
        df: DataFrame
        dimension: Dimensão opcional para filtrar
        
    Returns:
        Dicionário com listas de pilares, temas, órgãos
    """
    if dimension:
        df = filter_by_dimension(df, dimension)
    
    return {
        'pilares': sorted(df['pilar'].dropna().unique().tolist()),
        'temas': sorted(df['tema'].dropna().unique().tolist()),
        'orgaos': sorted(df['orgao_responsavel'].dropna().unique().tolist())
    }


def get_yearly_evolution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula evolução de status por ano (2014-2024).
    
    Returns:
        DataFrame com colunas: ano, Verde, Amarelo, Vermelho, Cinza, pct_verde
    """
    evolution = []
    
    for year in sorted(df['ano'].unique()):
        df_year = df[df['ano'] == year]
        status_counts = df_year['status'].value_counts().to_dict()
        total = df_year['id'].nunique()
        
        evolution.append({
            'ano': year,
            'Verde': status_counts.get('Verde', 0),
            'Amarelo': status_counts.get('Amarelo', 0),
            'Vermelho': status_counts.get('Vermelho', 0),
            'Cinza': status_counts.get('Cinza', 0),
            'total': total,
            'pct_verde': (status_counts.get('Verde', 0) / total * 100) if total > 0 else 0
        })
    
    return pd.DataFrame(evolution)


def calculate_year_over_year(df: pd.DataFrame, year: int) -> Dict:
    """
    Calcula variação percentual ano a ano.
    
    Returns:
        Dict com métricas de variação
    """
    if year <= 2014:
        return {'variation': 0, 'previous_year': None}
    
    current = df[df['ano'] == year]
    previous = df[df['ano'] == year - 1]
    
    current_verde = (current['status'] == 'Verde').sum()
    previous_verde = (previous['status'] == 'Verde').sum()
    
    current_total = current['id'].nunique()
    previous_total = previous['id'].nunique()
    
    current_pct = (current_verde / current_total * 100) if current_total > 0 else 0
    previous_pct = (previous_verde / previous_total * 100) if previous_total > 0 else 0
    
    variation = current_pct - previous_pct
    
    return {
        'variation': variation,
        'previous_year': year - 1,
        'current_pct': current_pct,
        'previous_pct': previous_pct,
        'current_verde': current_verde,
        'previous_verde': previous_verde
    }


def get_top_bottom_indicators(df: pd.DataFrame, year: int, n: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retorna os top N melhores e piores indicadores.
    
    Args:
        df: DataFrame completo
        year: Ano para análise
        n: Número de indicadores a retornar
        
    Returns:
        Tuple com (top_indicators, bottom_indicators)
    """
    df_year = df[df['ano'] == year].copy()
    
    # Ranking por status (Verde=3, Amarelo=2, Vermelho=1, Cinza=0)
    status_rank = {'Verde': 3, 'Amarelo': 2, 'Vermelho': 1, 'Cinza': 0}
    df_year['rank'] = df_year['status'].map(status_rank)
    
    # Top performers (status verde + maior valor)
    top = df_year.nlargest(n, 'rank')[['indicador', 'valor', 'status', 'orgao_responsavel', 'dimensoes']]
    
    # Bottom performers (status vermelho/cinza + menor valor)
    bottom = df_year.nsmallest(n, 'rank')[['indicador', 'valor', 'status', 'orgao_responsavel', 'dimensoes']]
    
    return top, bottom


def get_dimension_performance_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria matriz de performance para heatmap (Dimensões x Anos).
    
    Returns:
        DataFrame com índice=dimensões, colunas=anos, valores=% verde
    """
    dimensions = df['dimensoes'].unique()
    years = sorted(df['ano'].unique())
    
    matrix = []
    
    for dim in dimensions:
        row = {'Dimensão': dim}
        df_dim = df[df['dimensoes'] == dim]
        
        for year in years:
            df_year = df_dim[df_dim['ano'] == year]
            total = df_year['id'].nunique()
            verde = (df_year['status'] == 'Verde').sum()
            pct = (verde / total * 100) if total > 0 else 0
            row[str(year)] = pct
        
        matrix.append(row)
    
    return pd.DataFrame(matrix)


def generate_insights(df: pd.DataFrame, year: int) -> List[str]:
    """
    Gera insights automáticos textuais baseados nos dados.
    
    Returns:
        Lista de strings com insights
    """
    insights = []
    
    df_year = df[df['ano'] == year]
    total = df_year['id'].nunique()
    status_counts = df_year['status'].value_counts().to_dict()
    
    verde_count = status_counts.get('Verde', 0)
    pct_verde = (verde_count / total * 100) if total > 0 else 0
    
    # Insight de performance geral
    if pct_verde >= 70:
        insights.append(f"✅ **Excelente desempenho**: {pct_verde:.1f}% dos indicadores atingiram meta verde em {year}")
    elif pct_verde >= 50:
        insights.append(f"🟡 **Bom desempenho**: {pct_verde:.1f}% dos indicadores em verde, mas há espaço para melhoria")
    else:
        insights.append(f"🔴 **Atenção necessária**: Apenas {pct_verde:.1f}% dos indicadores em verde em {year}")
    
    # Comparação com ano anterior
    if year > 2014:
        yoy = calculate_year_over_year(df, year)
        if yoy['variation'] > 5:
            insights.append(f"📈 **Tendência positiva**: +{yoy['variation']:.1f}% de melhora vs {year-1}")
        elif yoy['variation'] < -5:
            insights.append(f"📉 **Alerta de queda**: -{abs(yoy['variation']):.1f}% de piora vs {year-1}")
    
    # Melhor dimensão
    dim_performance = {}
    for dim in df_year['dimensoes'].unique():
        df_dim = df_year[df_year['dimensoes'] == dim]
        total_dim = df_dim['id'].nunique()
        verde_dim = (df_dim['status'] == 'Verde').sum()
        dim_performance[dim] = (verde_dim / total_dim * 100) if total_dim > 0 else 0
    
    best_dim = max(dim_performance, key=dim_performance.get)
    insights.append(f"🏆 **Destaque**: Dimensão {best_dim} lidera com {dim_performance[best_dim]:.1f}% de performance")
    
    return insights


def get_sparkline_data(df: pd.DataFrame, metric: str = 'pct_verde', last_n_years: int = 5) -> List[float]:
    """
    Retorna dados para sparkline (mini-gráfico de tendência).
    
    Args:
        df: DataFrame completo
        metric: Métrica a calcular ('pct_verde', 'total', etc)
        last_n_years: Número de anos a incluir
        
    Returns:
        Lista de valores para o sparkline
    """
    evolution = get_yearly_evolution(df)
    recent = evolution.tail(last_n_years)
    
    if metric == 'pct_verde':
        return recent['pct_verde'].tolist()
    elif metric == 'verde':
        return recent['Verde'].tolist()
    elif metric == 'total':
        return recent['total'].tolist()
    else:
        return recent['pct_verde'].tolist()
