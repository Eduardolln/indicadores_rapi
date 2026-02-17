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
        dimension: Nome da dimensão ('AMBIENTAL', 'URBANA', 'FISCAL')
        
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
