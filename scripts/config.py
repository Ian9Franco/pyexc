"""
Configuración central del pipeline de Meta Ads V4.
Todos los umbrales y parámetros ajustables están aquí.
Comentarios en español para mejor comprensión.
"""
import os

# Obtener el directorio donde está este archivo (scripts/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Obtener el directorio raíz del proyecto (un nivel arriba)
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# ==============================================
# DIRECTORIOS DEL SISTEMA
# Estructura de carpetas para organizar datos
# ==============================================
CRUDA_DIR = os.path.join(ROOT_DIR, 'crudo')           # Archivos Excel originales de Meta Ads
LIMPIOS_DIR = os.path.join(ROOT_DIR, 'limpios')       # Datos procesados y normalizados
INFORMES_DIR = os.path.join(ROOT_DIR, 'informes')     # PDFs y reportes generados
SCHEMA_DIR = os.path.join(ROOT_DIR, 'schema')         # Archivos JSON de configuración
WEB_DIR = os.path.join(ROOT_DIR, 'web')               # Dashboard web

# Crear directorios si no existen
for directorio in [LIMPIOS_DIR, INFORMES_DIR, SCHEMA_DIR, WEB_DIR]:
    os.makedirs(directorio, exist_ok=True)


# ==============================================
# PESOS DE CONVERSIONES POR TIPO DE ACCIÓN
# Ajusta según el valor real de cada acción para tu negocio
# ==============================================
PESOS_CONVERSIONES = {
    'results': 1.0,          # Resultado directo de Meta = valor completo
    'msg_init': 1.0,         # Mensaje iniciado = alto valor (contacto directo)
    'msg_contacts': 1.0,     # Contacto de mensaje = alto valor
    'link_clicks': 0.15,     # Clic en enlace = bajo valor (solo interés)
    'ig_profile': 0.3,       # Visita a perfil IG = valor medio-bajo
    'leads': 1.0,            # Lead generado = alto valor
    'purchases': 2.0,        # Compra = máximo valor
    'interactions': 0.1,     # Interacción general = bajo valor
    'video_views': 0.05,     # Reproducciones de video = muy bajo valor
    'thruplay': 0.1,         # Video visto completo = bajo valor
}


# ==============================================
# PESOS POR OBJETIVO DE CAMPAÑA
# Define qué métricas son importantes para cada objetivo
# ==============================================
PESOS_POR_OBJETIVO = {
    'mensajes': {
        'msg_init': 0.35,
        'msg_contacts': 0.35,
        'results': 0.20,
        'link_clicks': 0.05,
        'ig_profile': 0.05,
    },
    'trafico': {
        'link_clicks': 0.40,
        'ctr': 0.25,
        'cpc': 0.20,  # Invertido: menor es mejor
        'ig_profile': 0.10,
        'results': 0.05,
    },
    'interaccion': {
        'interactions': 0.35,
        'video_views': 0.20,
        'thruplay': 0.15,
        'ig_profile': 0.15,
        'results': 0.15,
    },
    'leads': {
        'leads': 0.50,
        'results': 0.30,
        'link_clicks': 0.10,
        'cpl': 0.10,  # Invertido: menor es mejor
    },
    'ventas': {
        'purchases': 0.40,
        'roas': 0.30,
        'results': 0.20,
        'conversion_value': 0.10,
    },
    'general': {
        'results': 0.30,
        'msg_init': 0.25,
        'msg_contacts': 0.25,
        'link_clicks': 0.10,
        'ig_profile': 0.10,
    }
}


# ==============================================
# UMBRALES DE DECISIÓN PARA RECOMENDACIONES
# ==============================================
UMBRALES = {
    # Para recomendar DUPLICAR un anuncio
    'DUPLICAR_SCORE_MIN': 10,           # Score mínimo para considerar duplicar
    'DUPLICAR_CPA_RATIO_MAX': 1.2,      # CPA máximo como ratio de mediana (120%)
    
    # Para recomendar PAUSAR un anuncio
    'PAUSAR_GASTO_MIN': 4000,           # Gasto mínimo sin conversiones para alertar
    'PAUSAR_CPA_RATIO': 2.0,            # Si CPA > 2x mediana, alertar
    
    # Categorías de eficiencia (ratio del CPA vs mediana)
    'EFICIENCIA_MUY_BUENA': 0.7,        # CPA < 70% de mediana = excelente
    'EFICIENCIA_BUENA': 1.0,            # CPA < 100% de mediana = bueno
    'EFICIENCIA_NORMAL': 1.5,           # CPA < 150% de mediana = aceptable
    # > 1.5 = CARO
    
    # Mínimos para rankings
    'MIN_CONV_EFICIENCIA': 1.0,         # Conversiones mínimas para ranking
    
    # Umbrales de tendencia (comparación 7d vs 30d)
    'TENDENCIA_SUBIDA': 1.2,            # +20% = en ascenso
    'TENDENCIA_CAIDA': 0.8,             # -20% = en caída
    'TENDENCIA_CRITICA': 0.5,           # -50% = caída crítica
    
    # Score normalizado 0-100
    'SCORE_HEROE': 90,                  # >= 90 = anuncio héroe
    'SCORE_SANO': 70,                   # >= 70 = anuncio sano
    'SCORE_ALERTA': 40,                 # >= 40 = en alerta
    # < 40 = para pausar/eliminar
}


# ==============================================
# DETECCIÓN DE ANOMALÍAS
# Parámetros para identificar comportamientos anómalos
# ==============================================
ANOMALIAS = {
    # Frecuencia alta = audiencia saturada
    'FRECUENCIA_ALTA': 3.0,
    'FRECUENCIA_MUY_ALTA': 5.0,
    
    # CTR bajo = mala segmentación o creatividad
    'CTR_BAJO': 0.5,  # Porcentaje
    'CTR_MUY_BAJO': 0.2,
    
    # Fake clicks: muchos clics pero pocas visitas
    'RATIO_CLICKS_VISITAS_SOSPECHOSO': 5.0,
}


# ==============================================
# MAPEO DE COLUMNAS META ADS -> INTERNAS
# Nombres estándar para normalización
# ==============================================
META_COLS = {
    'Nombre del anuncio': 'ad_name',
    'Importe gastado (ARS)': 'spend',
    'Resultados': 'results',
    'Conversaciones con mensajes iniciadas': 'msg_init',
    'Contactos de mensajes': 'msg_contacts',
    'Clics en el enlace': 'link_clicks',
    'Visitas al perfil de Instagram': 'ig_profile',
    'Objetivo': 'objective',
    'Ubicación de la conversión': 'placement',
    'Inicio del informe': 'date_start',
    'Fin del informe': 'date_end',
    'Alcance': 'reach',
    'Impresiones': 'impressions',
    'Frecuencia': 'frequency',
    'CTR (tasa de clics en el enlace)': 'ctr',
    'CPC (costo por clic en el enlace)': 'cpc',
    'CPM (costo por 1.000 impresiones)': 'cpm',
    'Clientes potenciales': 'leads',
    'Costo por cliente potencial': 'cpl',
    'Compras': 'purchases',
    'ROAS (retorno del gasto en anuncios)': 'roas',
    'Valor de conversión de compras': 'conversion_value',
    'Interacciones con la publicación': 'interactions',
    'Reproducciones de video': 'video_views',
    'ThruPlays': 'thruplay',
}


# Listas derivadas para validación
COLUMNAS_CLAVE = list(META_COLS.keys())
COLUMNAS_NORMALIZADAS = list(META_COLS.values())
COLUMNAS_NUMERICAS = [
    'spend', 'results', 'msg_init', 'msg_contacts', 'ig_profile', 
    'link_clicks', 'reach', 'impressions', 'frequency', 'ctr', 'cpc', 
    'cpm', 'leads', 'cpl', 'purchases', 'roas', 'conversion_value',
    'interactions', 'video_views', 'thruplay'
]


# ==============================================
# CONFIGURACIÓN DE INFORMES PDF
# ==============================================
PDF_CONFIG = {
    'titulo_fuente': 'Helvetica-Bold',
    'cuerpo_fuente': 'Helvetica',
    'color_primario': (0.2, 0.4, 0.8),      # Azul corporativo
    'color_exito': (0.2, 0.7, 0.3),          # Verde
    'color_alerta': (0.9, 0.6, 0.1),         # Naranja
    'color_peligro': (0.8, 0.2, 0.2),        # Rojo
    'margen': 50,
    'ancho_pagina': 595,                      # A4
    'alto_pagina': 842,
}
