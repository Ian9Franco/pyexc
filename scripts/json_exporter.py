"""
Módulo de exportación JSON V4.
Genera el archivo JSON estructurado para consumir desde web/dashboard.
"""
from datetime import datetime
import math


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
                nuevo[k] = [safe_number(x) if isinstance(x, (float, int)) else x for x in v]
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
    hora = datetime.now().strftime("%H:%M")

    # Convertir DataFrame a lista de anuncios
    anuncios = []
    for _, r in df.iterrows():
        anuncios.append({
            "nombre": r["ad_name"],
            "score": safe_number(round(r["score"], 2)),
            "score_100": safe_number(round(r.get("score_100", 0), 1)),
            "cpa": safe_number(round(safe_number(r.get("cpa")), 2)),
            "gasto": safe_number(round(r["spend"], 2)),
            "eficiencia": r["eficiencia"],
            "actividad": r["actividad"],
            "tendencia": r.get("tendencia", "SIN_DATOS"),
            "clasificacion": r.get("clasificacion", "SIN_DATOS"),
            "score_7d": safe_number(round(r.get("score_7d", 0), 2)),
            "gasto_7d": safe_number(round(r.get("gasto_7d", 0), 2)),
            "objetivo": r.get("objetivo_detectado", "general"),
            "ratio_tendencia": safe_number(round(r.get("ratio_tendencia", 1.0), 2))
        })

    return {
        "meta": {
            "cliente": cliente,
            "fecha": fecha,
            "hora": hora,
            "version": "4.0",
            "total_anuncios": len(df)
        },
        
        "resumen": {
            "gasto_total": safe_number(resumen['gasto_total']),
            "score_total": safe_number(resumen['score_total']),
            "cpa_global": safe_number(resumen['cpa_global']),
            "mediana_cpa": safe_number(round(mediana_cpa, 2)),
            "score_100_promedio": safe_number(resumen.get('score_100_promedio', 0)),
            "total_anuncios": resumen['total_anuncios'],
            "con_conversiones": resumen['con_conversiones'],
            "actividad": resumen['actividad'],
            "eficiencia": resumen['eficiencia'],
            "clasificacion": resumen.get('clasificacion', {}),
            "tendencia": resumen.get('tendencia', {})
        },

        "rankings": {
            "impacto": limpiar_lista(rankings.get('impacto', [])),
            "volumen": limpiar_lista(rankings.get('volumen', [])),
            "eficiencia": limpiar_lista(rankings.get('eficiencia', [])),
            "heroes": limpiar_lista(rankings.get('heroes', [])),
            "tendencia": limpiar_lista(rankings.get('tendencia', []))
        },

        "duplicar": limpiar_lista(candidatos_duplicar),

        "acciones_urgentes": [
            {
                "tipo": a["tipo"],
                "prioridad": a.get("prioridad", "MEDIA"),
                "nombre": a["nombre"],
                "razon": a["razon"],
                "accion": a["accion"]
            }
            for a in acciones_urgentes
        ],

        "anomalias": [
            {
                "tipo": a["tipo"],
                "severidad": a["severidad"],
                "anuncio": a["anuncio"],
                "valor": safe_number(a["valor"]),
                "mensaje": a["mensaje"],
                "accion": a["accion"]
            }
            for a in anomalias
        ],

        "anuncios": sorted(anuncios, key=lambda x: x["score_100"], reverse=True),

        "historico": limpiar_lista(historico),

        "analisis_por_objetivo": analisis_objetivo,

        "glosario": {
            "score": {
                "nombre": "Score (Conversiones Ponderadas)",
                "descripcion": "Valor total de acciones ponderadas según importancia",
                "interpretacion": "Mayor score = mejor rendimiento absoluto"
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
                "descripcion": "Gasto ÷ Score = cuánto pagas por cada conversión",
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
    }
