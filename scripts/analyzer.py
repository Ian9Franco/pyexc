"""
Módulo de análisis V4.
Genera rankings, estadísticas, análisis comparativos y detección de anomalías.
"""
import pandas as pd
from config import UMBRALES, ANOMALIAS
from metrics import calcular_score_basico # Se añade esta importación si no existía para la función historico

def generar_rankings(df):
    """
    Genera los diferentes rankings de anuncios.
    
    Rankings:
        - impacto: Mayor score (más conversiones ponderadas)
        - volumen: Mayor gasto (más inversión)
        - eficiencia: Menor CPA (más eficiente)
        - heroes: Score 0-100 más alto (rendimiento integral)
        - tendencia: Mayor crecimiento 7d vs 30d
    
    Returns:
        dict con rankings por diferentes criterios
    """
    rankings = {}
    
    # TOP por Impacto (mayor score)
    rankings['impacto'] = df.nlargest(5, 'score')[
        ['ad_name', 'score', 'cpa', 'spend', 'actividad', 'clasificacion']
    ].to_dict('records')
    
    # TOP por Volumen (mayor gasto)
    rankings['volumen'] = df.nlargest(5, 'spend')[
        ['ad_name', 'spend', 'cpa', 'score', 'eficiencia']
    ].to_dict('records')
    
    # TOP por Eficiencia (menor CPA con conversiones)
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
    
    # TOP por Score 0-100 (rendimiento integral)
    if 'score_100' in df.columns:
        rankings['heroes'] = df.nlargest(5, 'score_100')[
            ['ad_name', 'score_100', 'score', 'cpa', 'clasificacion', 'tendencia']
        ].to_dict('records')
    else:
        rankings['heroes'] = []
    
    # TOP por Tendencia (mayor crecimiento)
    if 'ratio_tendencia' in df.columns:
        df_tendencia = df[df['ratio_tendencia'] > 0]
        if not df_tendencia.empty:
            rankings['tendencia'] = df_tendencia.nlargest(5, 'ratio_tendencia')[
                ['ad_name', 'ratio_tendencia', 'tendencia', 'score_7d', 'score']
            ].to_dict('records')
        else:
            rankings['tendencia'] = []
    else:
        rankings['tendencia'] = []
    
    return rankings


def generar_resumen(df, mediana_cpa):
    """
    Genera métricas de resumen de la cuenta.
    
    Returns:
        dict con estadísticas generales de la cuenta
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
    
    # Conteo por clasificación
    heroes = len(df[df.get('clasificacion', '') == 'HEROE'])
    sanos = len(df[df.get('clasificacion', '') == 'SANO'])
    alertas = len(df[df.get('clasificacion', '') == 'ALERTA'])
    muertos = len(df[df.get('clasificacion', '') == 'MUERTO'])
    
    # Conteo por tendencia
    en_ascenso = len(df[df.get('tendencia', '') == 'EN_ASCENSO'])
    estables = len(df[df.get('tendencia', '') == 'ESTABLE'])
    en_caida = len(df[df.get('tendencia', '') == 'EN_CAIDA'])
    criticos = len(df[df.get('tendencia', '') == 'CRITICO'])
    
    # Score promedio 0-100
    score_100_promedio = df['score_100'].mean() if 'score_100' in df.columns else 0
    
    return {
        'gasto_total': round(gasto_total, 2),
        'score_total': round(score_total, 2),
        'cpa_global': round(cpa_global, 2),
        'mediana_cpa': round(mediana_cpa, 2),
        'score_100_promedio': round(score_100_promedio, 1),
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
        },
        'clasificacion': {
            'heroes': heroes,
            'sanos': sanos,
            'alertas': alertas,
            'muertos': muertos
        },
        'tendencia': {
            'en_ascenso': en_ascenso,
            'estables': estables,
            'en_caida': en_caida,
            'criticos': criticos
        }
    }


def detectar_anomalias(df):
    """
    Detecta anomalías y problemas en los anuncios.
    
    Anomalías detectadas:
        - Frecuencia muy alta (audiencia saturada)
        - CTR muy bajo (creatividad/segmentación pobre)
        - Fake clicks (muchos clics, pocas visitas)
        - Gasto sin resultados
        - Tendencia crítica
    
    Returns:
        list de anomalías detectadas
    """
    anomalias = []
    
    # Frecuencia muy alta
    if 'frequency' in df.columns:
        freq_alta = df[df['frequency'] > ANOMALIAS['FRECUENCIA_MUY_ALTA']]
        for _, row in freq_alta.iterrows():
            anomalias.append({
                'tipo': 'FRECUENCIA_ALTA',
                'severidad': 'MEDIA',
                'anuncio': row['ad_name'],
                'valor': round(row['frequency'], 1),
                'mensaje': f"Frecuencia de {row['frequency']:.1f} - audiencia posiblemente saturada",
                'accion': "Ampliar audiencia o pausar para evitar fatiga"
            })
    
    # CTR muy bajo
    if 'ctr' in df.columns:
        ctr_bajo = df[(df['ctr'] > 0) & (df['ctr'] < ANOMALIAS['CTR_MUY_BAJO']) & (df['impressions'] > 1000)]
        for _, row in ctr_bajo.iterrows():
            anomalias.append({
                'tipo': 'CTR_MUY_BAJO',
                'severidad': 'MEDIA',
                'anuncio': row['ad_name'],
                'valor': round(row['ctr'], 2),
                'mensaje': f"CTR de {row['ctr']:.2f}% con {row['impressions']:.0f} impresiones",
                'accion': "Revisar creatividad y segmentación"
            })
    
    # Gasto alto sin conversiones
    gasto_sin_conv = df[(df['score'] == 0) & (df['spend'] > UMBRALES['PAUSAR_GASTO_MIN'])]
    for _, row in gasto_sin_conv.iterrows():
        anomalias.append({
            'tipo': 'GASTO_SIN_RESULTADOS',
            'severidad': 'ALTA',
            'anuncio': row['ad_name'],
            'valor': round(row['spend'], 0),
            'mensaje': f"Gastó ${row['spend']:,.0f} sin ninguna conversión",
            'accion': "Pausar inmediatamente y revisar configuración"
        })
    
    # Tendencia crítica
    if 'tendencia' in df.columns:
        criticos = df[df['tendencia'] == 'CRITICO']
        for _, row in criticos.iterrows():
            anomalias.append({
                'tipo': 'TENDENCIA_CRITICA',
                'severidad': 'ALTA',
                'anuncio': row['ad_name'],
                'valor': round(row.get('ratio_tendencia', 0), 2),
                'mensaje': f"Caída crítica: rendimiento 7d es {row.get('ratio_tendencia', 0)*100:.0f}% del promedio",
                'accion': "Evaluar si pausar o renovar creatividad"
            })
    
    return anomalias


def generar_historico(df_hist):
    """
    Genera resumen histórico por período con análisis de tendencia.
    
    Returns:
        list de dicts con score y métricas por período
    """
    if df_hist.empty:
        return []
    
    # from metrics import calcular_score_basico # Se asume importada arriba o en main
    df_hist = calcular_score_basico(df_hist)
    
    # Agrupar por período
    resumen = df_hist.groupby('periodo').agg({
        'score': 'sum',
        'spend': 'sum',
        'ad_name': 'count'
    }).reset_index()
    
    resumen.columns = ['periodo', 'score', 'gasto', 'anuncios']
    
    # Calcular CPA por período
    resumen['cpa'] = resumen.apply(
        lambda r: r['gasto'] / r['score'] if r['score'] > 0 else 0, 
        axis=1
    )
    
    return [
        {
            'periodo': row['periodo'],
            'score': round(row['score'], 2),
            'gasto': round(row['gasto'], 2),
            'cpa': round(row['cpa'], 2),
            'anuncios': int(row['anuncios'])
        }
        for _, row in resumen.iterrows()
    ]


def analizar_por_objetivo(df):
    """
    Genera análisis separado por objetivo de campaña.
    
    Returns:
        dict con análisis por cada objetivo detectado
    """
    if 'objetivo_detectado' not in df.columns:
        return {}
    
    analisis = {}
    
    for objetivo in df['objetivo_detectado'].unique():
        df_obj = df[df['objetivo_detectado'] == objetivo]
        
        analisis[objetivo] = {
            'total_anuncios': len(df_obj),
            'gasto_total': round(df_obj['spend'].sum(), 2),
            'score_total': round(df_obj['score'].sum(), 2),
            'cpa_promedio': round(df_obj['cpa'].mean(), 2) if df_obj['cpa'].notna().any() else 0,
            'score_100_promedio': round(df_obj['score_100'].mean(), 1) if 'score_100' in df_obj.columns else 0,
            'heroes': len(df_obj[df_obj.get('clasificacion', '') == 'HEROE']),
            'muertos': len(df_obj[df_obj.get('clasificacion', '') == 'MUERTO']),
            'mejores': df_obj.nlargest(3, 'score')[['ad_name', 'score', 'cpa']].to_dict('records')
        }
    
    return analisis


def analizar_rendimiento_managers(df):
    """
    Compara el rendimiento de las campañas de 'Ian' vs 'General'.
    
    Returns:
        dict con métricas comparativas o None si solo hay un manager.
    """
    if 'manager' not in df.columns or len(df['manager'].unique()) < 2:
        return None
        
    # Agrupar métricas clave por manager
    comparativa = df.groupby('manager').agg({
        'spend': 'sum',
        'score': 'sum',
        'ad_name': 'count',
        'cpa': 'mean', # Promedio simple para referencia
        'score_100': 'mean' # Calidad promedio de anuncios
    }).reset_index()
    
    resultado = {}
    
    for _, row in comparativa.iterrows():
        # Recalcular CPA real (Gasto Total / Score Total)
        score = row.get('score', 0)
        spend = row.get('spend', 0)
        cpa_real = spend / score if score > 0 else 0
        
        resultado[row['manager']] = {
            'gasto': spend,
            'conversiones': score,
            'cpa_real': cpa_real,
            'calidad_promedio': row.get('score_100', 0),
            'cant_anuncios': row['ad_name']
        }
        
    return resultado