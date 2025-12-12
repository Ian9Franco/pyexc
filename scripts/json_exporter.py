"""
Módulo de exportación JSON.
Genera el archivo JSON estructurado para consumir desde web.
"""
from datetime import datetime
import math


def safe_number(value, default=0):
    """
    Convierte cualquier NaN, None o valor inválido en 0.
    """
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default
    return value


def limpiar_rank(lista):
    """
    Limpia listas de rankings, reemplazando NaN en cualquier campo por 0.
    """
    lista_limpia = []
    for item in lista:
        nuevo = {}
        for k, v in item.items():
            nuevo[k] = safe_number(v) if isinstance(v, (float, int)) else v
        lista_limpia.append(nuevo)
    return lista_limpia


def generar_json(cliente, resumen, rankings, candidatos_duplicar,
                 acciones_urgentes, historico, df, mediana_cpa):

    fecha = datetime.now().strftime("%Y-%m-%d")

    # Convertir DataFrame a lista de anuncios
    anuncios = []
    for _, r in df.iterrows():
        anuncios.append({
            "nombre": r["ad_name"],
            "score": safe_number(round(r["score"], 2)),
            "cpa": safe_number(round(safe_number(r.get("cpa")), 2)),
            "gasto": safe_number(round(r["spend"], 2)),
            "eficiencia": r["eficiencia"],
            "actividad": r["actividad"],
            "score_7d": safe_number(round(r.get("score_7d", 0), 2)),
            "gasto_7d": safe_number(round(r.get("gasto_7d", 0), 2))
        })

    return {
        "meta": {
            "cliente": cliente,
            "fecha": fecha,
            "version": "2.0"
        },
        "resumen": resumen,
        "mediana_cpa": safe_number(round(mediana_cpa, 2)),

        # LIMPIEZA DE RANKINGS AQUÍ (Fix definitivo)
        "rankings": {
            "impacto": limpiar_rank(rankings['impacto']),
            "volumen": limpiar_rank(rankings['volumen']),
            "eficiencia": limpiar_rank(rankings['eficiencia'])
        },

        "duplicar": candidatos_duplicar,

        "acciones_urgentes": [
            {
                "tipo": a["tipo"],
                "nombre": a["nombre"],
                "razon": a["razon"],
                "accion": a["accion"]
            }
            for a in acciones_urgentes
        ],

        "anuncios": sorted(anuncios, key=lambda x: x["score"], reverse=True),

        "historico": historico,

        "glosario": {
            "score": {
                "nombre": "Score (Conversiones Ponderadas)",
                "descripcion": "Valor total de acciones: mensajes (1.0), clics (0.15), visitas IG (0.3)",
                "interpretacion": "Mayor score = mejor rendimiento"
            },
            "cpa": {
                "nombre": "CPA (Costo Por Adquisición)",
                "descripcion": "Gasto ÷ Score = cuánto pagas por cada conversión",
                "interpretacion": "Menor CPA = más eficiente"
            },
            "mediana_cpa": {
                "nombre": "Mediana CPA",
                "descripcion": "El CPA del anuncio 'del medio' - tu punto de referencia",
                "interpretacion": "CPA < mediana = mejor que promedio"
            },
            "eficiencia": {
                "nombre": "Eficiencia",
                "descripcion": "Comparación del CPA vs la mediana",
                "categorias": {
                    "MUY_EFICIENTE": "CPA < 70% de mediana",
                    "EFICIENTE": "CPA < mediana",
                    "NORMAL": "CPA < 150% de mediana",
                    "CARO": "CPA > 150% de mediana"
                }
            },
            "actividad": {
                "nombre": "Actividad (últimos 7 días)",
                "categorias": {
                    "ACTIVO": "Generó conversiones en 7 días",
                    "GASTANDO": "Gastó pero no convirtió en 7 días",
                    "INACTIVO": "Sin gasto ni conversiones en 7 días"
                }
            }
        }
    }
