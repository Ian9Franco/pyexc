"""
Configuración central del pipeline de Meta Ads.
Todos los umbrales y parámetros ajustables están aquí.
"""
import os

# ==============================================
# DIRECTORIOS
# ==============================================
CRUDA_DIR = 'crudo'
LIMPIOS_DIR = 'limpios'
INFORMES_DIR = 'informes'

os.makedirs(LIMPIOS_DIR, exist_ok=True)
os.makedirs(INFORMES_DIR, exist_ok=True)

# ==============================================
# PESOS DE CONVERSIONES
# Ajusta estos valores según el valor real de cada acción para tu negocio
# ==============================================
PESOS_CONVERSIONES = {
    'results': 1.0,          # Resultado directo de Meta = valor completo
    'msg_init': 1.0,         # Mensaje iniciado = alto valor (contacto directo)
    'msg_contacts': 1.0,     # Contacto de mensaje = alto valor
    'link_clicks': 0.15,     # Clic en enlace = bajo valor (solo interés)
    'ig_profile': 0.3,       # Visita a perfil IG = valor medio-bajo
}

# ==============================================
# UMBRALES DE DECISIÓN
# ==============================================
UMBRALES = {
    # Para recomendar DUPLICAR un anuncio
    'DUPLICAR_SCORE_MIN': 10,           # Score mínimo para considerar duplicar
    'DUPLICAR_CPA_RATIO_MAX': 1.2,      # CPA máximo como ratio de mediana (1.2 = 120% de mediana)
    
    # Para recomendar PAUSAR un anuncio
    'PAUSAR_GASTO_MIN': 4000,           # Gasto mínimo sin conversiones para alertar
    'PAUSAR_CPA_RATIO': 2.0,            # Si CPA > 2x mediana, alertar
    
    # Categorías de eficiencia (como ratio del CPA vs mediana)
    'EFICIENCIA_MUY_BUENA': 0.7,        # CPA < 70% de mediana
    'EFICIENCIA_BUENA': 1.0,            # CPA < 100% de mediana
    'EFICIENCIA_NORMAL': 1.5,           # CPA < 150% de mediana
    # > 1.5 = CARO
    
    # Mínimos para rankings
    'MIN_CONV_EFICIENCIA': 1.0,         # Conversiones mínimas para ranking de eficiencia
}

# ==============================================
# MAPEO DE COLUMNAS META ADS -> INTERNAS
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
    'Fin del informe': 'date_end'
}

# Listas derivadas para validación
COLUMNAS_CLAVE = list(META_COLS.keys())
COLUMNAS_NORMALIZADAS = list(META_COLS.values())
COLUMNAS_NUMERICAS = ['spend', 'results', 'msg_init', 'msg_contacts', 'ig_profile', 'link_clicks']
