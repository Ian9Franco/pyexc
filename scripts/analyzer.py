"""
Módulo de análisis.
Genera rankings, estadísticas y análisis comparativos.
"""
import pandas as pd
from config import UMBRALES


def generar_rankings(df):
    """
    Genera los diferentes rankings de anuncios.
    
    Returns:
        dict con rankings por diferentes criterios
    """
    rankings = {}
    
    # TOP por Impacto (mayor score)
    rankings['impacto'] = df.nlargest(5, 'score')[
        ['ad_name', 'score', 'cpa', 'spend', 'actividad']
    ].to_dict('records')
    
    # TOP por Volumen (mayor gasto)
    rankings['volumen'] = df.nlargest(5, 'spend')[
        ['ad_name', 'spend', 'cpa', 'score']
    ].to_dict('records')
    
    # TOP por Eficiencia (menor CPA con conversiones suficientes)
    df_con_conv = df[
        (df['cpa'].notna()) & 
        (df['cpa'] > 0) & 
        (df['score'] >= UMBRALES['MIN_CONV_EFICIENCIA'])
    ]
    
    if not df_con_conv.empty:
        rankings['eficiencia'] = df_con_conv.nsmallest(5, 'cpa')[
            ['ad_name', 'cpa', 'score', 'spend', 'eficiencia']
        ].to_dict('records')
    else:
        rankings['eficiencia'] = []
    
    return rankings


def generar_resumen(df, mediana_cpa):
    """
    Genera métricas de resumen de la cuenta.
    
    Returns:
        dict con estadísticas generales
    """
    gasto_total = df['spend'].sum()
    score_total = df['score'].sum()
    cpa_global = gasto_total / score_total if score_total > 0 else 0
    
    # Conteo por estado de actividad
    activos = len(df[df['actividad'] == 'ACTIVO'])
    gastando = len(df[df['actividad'] == 'GASTANDO'])
    inactivos = len(df[df['actividad'] == 'INACTIVO'])
    sin_datos = len(df[df['actividad'] == 'SIN_DATOS_7D'])
    
    # Conteo por eficiencia
    muy_eficientes = len(df[df['eficiencia'] == 'MUY_EFICIENTE'])
    eficientes = len(df[df['eficiencia'] == 'EFICIENTE'])
    normales = len(df[df['eficiencia'] == 'NORMAL'])
    caros = len(df[df['eficiencia'] == 'CARO'])
    
    return {
        'gasto_total': round(gasto_total, 2),
        'score_total': round(score_total, 2),
        'cpa_global': round(cpa_global, 2),
        'mediana_cpa': round(mediana_cpa, 2),
        'total_anuncios': len(df),
        'con_conversiones': len(df[df['cpa'].notna()]),
        'actividad': {
            'activos': activos,
            'gastando': gastando,
            'inactivos': inactivos,
            'sin_datos_7d': sin_datos
        },
        'eficiencia': {
            'muy_eficientes': muy_eficientes,
            'eficientes': eficientes,
            'normales': normales,
            'caros': caros
        }
    }


def generar_historico(df_hist):
    """
    Genera resumen histórico por período.
    
    Returns:
        list de dicts con score por período
    """
    if df_hist.empty:
        return []
    
    from metrics import calcular_score
    df_hist = calcular_score(df_hist)
    
    resumen = df_hist.groupby('periodo')['score'].sum()
    
    return [
        {'periodo': periodo, 'score': round(valor, 2)}
        for periodo, valor in resumen.items()
    ]
