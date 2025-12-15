"""
Módulo de exportación JSON V4.
Genera el archivo JSON estructurado para consumir desde web/dashboard.
"""
from datetime import datetime
import math
# --- NUEVA IMPORTACIÓN ---
try:
    # Intenta importar la nueva función de análisis de managers
    from analyzer import analizar_rendimiento_managers
except ImportError:
    # Fallback si el archivo analyzer.py no está actualizado aún
    analizar_rendimiento_managers = lambda df: {}
# -------------------------


def safe_number(value, default=0):
    """
    Convierte cualquier NaN, None o valor inválido en un valor seguro.
    Evita errores de serialización JSON.
    """
    if value is None:
        return default
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return default
    return value


def limpiar_lista(lista):
    """
    Limpia listas de dicts, reemplazando NaN en cualquier campo.
    """
    lista_limpia = []
    for item in lista:
        nuevo = {}
        for k, v in item.items():
            if isinstance(v, (float, int)):
                nuevo[k] = safe_number(v)
            elif isinstance(v, list):
                # Limpieza recursiva para listas anidadas
                nuevo[k] = [safe_number(x) if isinstance(x, (float, int)) else x for x in v]
            elif isinstance(v, dict):
                # Limpieza en diccionarios anidados (como sub-diccionarios de resumen)
                nuevo[k] = {k_sub: safe_number(v_sub) if isinstance(v_sub, (float, int)) else v_sub 
                           for k_sub, v_sub in v.items()}
            else:
                nuevo[k] = v
        lista_limpia.append(nuevo)
    return lista_limpia


def generar_json(cliente, resumen, rankings, candidatos_duplicar,
                 acciones_urgentes, anomalias, historico, analisis_objetivo,
                 df, mediana_cpa):
    """
    Genera el JSON completo para el dashboard web.
    
    Returns:
        dict estructurado listo para serializar a JSON
    """
    fecha = datetime.now().strftime("%Y-%m-%d")
    
    # --- NUEVA LÓGICA: CALCULAR COMPARATIVA AQUÍ ---
    # La función debe devolver un diccionario (ej: {"Ian": {...}, "General": {...}})
    comparativa_managers = analizar_rendimiento_managers(df)
    # -----------------------------------------------

    # Limpiar estructuras complejas
    limpio_rankings = {k: limpiar_lista(v) for k, v in rankings.items()}
    limpio_duplicar = limpiar_lista(candidatos_duplicar)
    limpio_urgentes = limpiar_lista(acciones_urgentes)
    limpio_anomalias = limpiar_lista(anomalias)
    limpio_historico = limpiar_lista(historico)
    
    # Asegurar que los anuncios se limpien
    anuncios_limpios = df.to_dict('records')
    anuncios_limpios = [
        {k: safe_number(v) if isinstance(v, (float, int)) else v for k, v in row.items()}
        for row in anuncios_limpios
    ]

    # Metadatos del glosario (asumiendo que está aquí)
    glosario = {
        "score": {
            "nombre": "Score (Conversiones Ponderadas)",
            "descripcion": "Valor TOTAL de las conversiones generadas. Mensajes 1.0, Clicks 0.15, etc.",
            "interpretacion": "Mayor score = más resultados generados"
        },
        "score_100": {
            "nombre": "Score Normalizado (0-100)",
            "descripcion": "Rendimiento relativo comparado con otros anuncios",
            "categorias": {
                "90-100": "Anuncio Héroe - Escalar",
                "70-89": "Anuncio Sano - Mantener",
                "40-69": "En Alerta - Revisar",
                "0-39": "Para Pausar - Eliminar"
            }
        },
        "cpa": {
            "nombre": "CPA (Costo Por Adquisición)",
            "descripcion": "Gasto ÷ Score = cuánto pagas por cada resultado",
            "interpretacion": "Menor CPA = más eficiente"
        },
        "tendencia": {
            "nombre": "Tendencia (7d vs 30d)",
            "categorias": {
                "EN_ASCENSO": "Rendimiento mejorando (+20%)",
                "ESTABLE": "Rendimiento constante (±20%)",
                "EN_CAIDA": "Rendimiento bajando (-20%)",
                "CRITICO": "Caída severa (-50%)"
            }
        },
        "clasificacion": {
            "nombre": "Clasificación de Anuncio",
            "categorias": {
                "HEROE": "Alto score, eficiente, activo → Escalar",
                "SANO": "Buen rendimiento general → Mantener",
                "ALERTA": "Problemas detectados → Revisar",
                "MUERTO": "Sin rendimiento → Pausar"
            }
        }
    }


    data = {
        "meta": {
            "cliente": cliente,
            "fecha_generacion": fecha,
            "total_anuncios": len(df),
        },
        "mediana_cpa": safe_number(mediana_cpa),
        "resumen": resumen,
        "rankings": limpio_rankings,
        "anuncios": anuncios_limpios,
        "duplicar": limpio_duplicar,
        "acciones_urgentes": limpio_urgentes,
        "anomalias": limpio_anomalias,
        "historico": limpio_historico,
        "analisis_objetivo": analisis_objetivo,
        "glosario": glosario,
        # --- NUEVO CAMPO AGREGADO ---
        "comparativa_managers": comparativa_managers 
        # ----------------------------
    }
    
    # Limpiar números dentro del resumen
    for k, v in data['resumen'].items():
        if isinstance(v, (float, int)):
             data['resumen'][k] = safe_number(v)
        elif isinstance(v, dict):
            for k_sub, v_sub in v.items():
                data['resumen'][k][k_sub] = safe_number(v_sub)

    return data