"""
Módulo de clasificación inteligente por objetivos V4.
Detecta el objetivo real de cada campaña/anuncio basándose en
las métricas disponibles y el comportamiento de los datos.
"""
import pandas as pd
import json
import os
from config import SCHEMA_DIR, PESOS_POR_OBJETIVO


def cargar_config_objetivos():
    """
    Carga la configuración de objetivos desde el archivo JSON.
    
    Returns:
        dict: Configuración de detección y análisis por objetivo
    """
    config_path = f"{SCHEMA_DIR}/objetivos.json"
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    print("  [AVISO] No se encontró schema/objetivos.json")
    return {}


def detectar_objetivo_anuncio(row, config):
    """
    Detecta el objetivo real de un anuncio basándose en sus métricas.
    
    La detección usa múltiples señales:
    1. Columna 'objective' si existe y es clara
    2. Presencia y valores de métricas específicas
    3. Proporción de métricas activas
    
    Args:
        row: Fila del DataFrame (un anuncio)
        config: Configuración de objetivos
        
    Returns:
        str: Objetivo detectado ('mensajes', 'trafico', etc.)
    """
    deteccion = config.get('deteccion', {})
    puntuaciones = {}
    
    # Revisar cada tipo de objetivo
    for objetivo, criterios in deteccion.items():
        if objetivo.startswith('_'):
            continue
            
        score = 0
        
        # Verificar columnas requeridas
        cols_req = criterios.get('columnas_requeridas', [])
        cols_con_valor = sum(1 for col in cols_req if row.get(col, 0) > 0)
        
        if cols_con_valor == len(cols_req) and len(cols_req) > 0:
            score += 50  # Bonus alto si tiene todas las columnas requeridas con valor
        elif cols_con_valor > 0:
            score += 20 * (cols_con_valor / max(len(cols_req), 1))
        
        # Verificar columnas opcionales
        cols_opt = criterios.get('columnas_opcionales', [])
        cols_opt_con_valor = sum(1 for col in cols_opt if row.get(col, 0) > 0)
        score += 5 * cols_opt_con_valor
        
        # Verificar palabras clave en el objetivo declarado
        objetivo_declarado = str(row.get('objective', '')).lower()
        palabras_clave = criterios.get('palabras_clave_objetivo', [])
        
        for palabra in palabras_clave:
            if palabra.lower() in objetivo_declarado:
                score += 30
                break
        
        puntuaciones[objetivo] = score
    
    # Seleccionar el objetivo con mayor puntuación
    if puntuaciones:
        mejor_objetivo = max(puntuaciones, key=puntuaciones.get)
        
        # Si la puntuación es muy baja, usar 'general'
        if puntuaciones[mejor_objetivo] < 10:
            return 'general'
        
        return mejor_objetivo
    
    return 'general'


def clasificar_objetivos_dataframe(df):
    """
    Clasifica todos los anuncios del DataFrame por su objetivo.
    
    Args:
        df: DataFrame con anuncios
        
    Returns:
        DataFrame con columna 'objetivo_detectado' añadida
    """
    config = cargar_config_objetivos()
    
    # Aplicar detección a cada fila
    df['objetivo_detectado'] = df.apply(
        lambda row: detectar_objetivo_anuncio(row, config), 
        axis=1
    )
    
    return df


def obtener_metricas_objetivo(objetivo):
    """
    Obtiene las métricas relevantes para un objetivo específico.
    
    Args:
        objetivo: Tipo de objetivo ('mensajes', 'trafico', etc.)
        
    Returns:
        dict: Pesos de métricas para ese objetivo
    """
    return PESOS_POR_OBJETIVO.get(objetivo, PESOS_POR_OBJETIVO['general'])


def generar_insights_objetivo(df, objetivo):
    """
    Genera insights específicos para anuncios de un objetivo.
    
    Args:
        df: DataFrame filtrado por objetivo
        objetivo: Tipo de objetivo
        
    Returns:
        list: Lista de insights detectados
    """
    config = cargar_config_objetivos()
    metricas_config = config.get('metricas_clave', {}).get(objetivo, {})
    alertas = metricas_config.get('alertas', {})
    
    insights = []
    
    # Análisis según objetivo
    if objetivo == 'mensajes':
        # Verificar frecuencia alta
        freq_alta = df[df.get('frequency', 0) > 3]
        if len(freq_alta) > 0:
            insights.append({
                'tipo': 'alerta',
                'mensaje': alertas.get('frecuencia_alta', 'Audiencia posiblemente saturada'),
                'anuncios_afectados': len(freq_alta)
            })
        
        # Verificar costo alto sin mensajes
        gasto_sin_msg = df[(df['spend'] > 1000) & (df['msg_init'] == 0)]
        if len(gasto_sin_msg) > 0:
            insights.append({
                'tipo': 'critico',
                'mensaje': alertas.get('costo_alto_sin_mensajes', 'Gasto sin conversaciones'),
                'anuncios_afectados': len(gasto_sin_msg)
            })
    
    elif objetivo == 'trafico':
        # Verificar CTR bajo
        ctr_bajo = df[df.get('ctr', 0) < 0.5]
        if len(ctr_bajo) > 0:
            insights.append({
                'tipo': 'alerta',
                'mensaje': alertas.get('ctr_bajo', 'CTR bajo detectado'),
                'anuncios_afectados': len(ctr_bajo)
            })
    
    elif objetivo == 'leads':
        # Verificar clicks sin leads
        clicks_sin_leads = df[(df['link_clicks'] > 50) & (df.get('leads', 0) == 0)]
        if len(clicks_sin_leads) > 0:
            insights.append({
                'tipo': 'alerta',
                'mensaje': alertas.get('clicks_sin_leads', 'Clics sin conversión a leads'),
                'anuncios_afectados': len(clicks_sin_leads)
            })
    
    return insights
