"""
Módulo de cálculo de métricas.
Calcula score, CPA, eficiencia y otras métricas por anuncio.
"""
import pandas as pd
from config import PESOS_CONVERSIONES, UMBRALES


def calcular_score(df):
    """
    Calcula el score ponderado de conversiones para cada anuncio.
    
    El score representa el valor total de todas las acciones generadas,
    ponderadas según su importancia para el negocio.
    
    Formula:
        score = (results × 1.0) + (msg_init × 1.0) + (msg_contacts × 1.0) 
                + (link_clicks × 0.15) + (ig_profile × 0.3)
    """
    df["score"] = (
        df["results"] * PESOS_CONVERSIONES['results'] +
        df["msg_init"] * PESOS_CONVERSIONES['msg_init'] +
        df["msg_contacts"] * PESOS_CONVERSIONES['msg_contacts'] +
        df["link_clicks"] * PESOS_CONVERSIONES['link_clicks'] +
        df["ig_profile"] * PESOS_CONVERSIONES['ig_profile']
    )
    return df


def calcular_cpa(df):
    """
    Calcula el Costo Por Adquisición (CPA) para cada anuncio.
    
    CPA = Gasto / Score
    
    Anuncios sin conversiones (score = 0) tienen CPA = None,
    lo cual permite que no afecten el cálculo de la mediana.
    """
    def _cpa(row):
        if row["score"] > 0:
            return row["spend"] / row["score"]
        return None
    
    df["cpa"] = df.apply(_cpa, axis=1)
    return df


def calcular_mediana_cpa(df):
    """
    Calcula la mediana del CPA de todos los anuncios con conversiones.
    
    La mediana es el valor "del medio" - 50% de los anuncios tienen
    CPA mayor y 50% tienen CPA menor. Es más robusta que el promedio
    porque no se ve afectada por valores extremos.
    
    Returns:
        float: Mediana del CPA, o 0 si no hay datos válidos
    """
    cpa_validos = df["cpa"].dropna()
    if len(cpa_validos) > 0:
        return cpa_validos.median()
    return 0


def calcular_eficiencia(df, mediana_cpa):
    """
    Categoriza cada anuncio según qué tan eficiente es su CPA
    comparado con la mediana de la cuenta.
    
    Categorías:
        - MUY_EFICIENTE: CPA < 70% de mediana (muy por debajo del promedio)
        - EFICIENTE: CPA < 100% de mediana (mejor que promedio)
        - NORMAL: CPA < 150% de mediana (aceptable)
        - CARO: CPA >= 150% de mediana (costoso)
        - SIN_DATOS: No tiene conversiones para calcular CPA
    """
    def _eficiencia(row):
        if pd.isna(row["cpa"]) or row["cpa"] == 0:
            return "SIN_DATOS"
        
        if mediana_cpa == 0:
            return "NORMAL"
        
        ratio = row["cpa"] / mediana_cpa
        
        if ratio <= UMBRALES['EFICIENCIA_MUY_BUENA']:
            return "MUY_EFICIENTE"
        elif ratio <= UMBRALES['EFICIENCIA_BUENA']:
            return "EFICIENTE"
        elif ratio <= UMBRALES['EFICIENCIA_NORMAL']:
            return "NORMAL"
        else:
            return "CARO"
    
    df["eficiencia"] = df.apply(_eficiencia, axis=1)
    return df


def calcular_actividad(df, df_7d):
    """
    Determina el estado de actividad de cada anuncio basándose
    en su rendimiento en los últimos 7 días.
    
    Estados:
        - ACTIVO: Generó conversiones en los últimos 7 días
        - GASTANDO: Gastó dinero pero no convirtió en 7 días
        - INACTIVO: Sin gasto ni conversiones en 7 días
        - SIN_DATOS_7D: No hay información de 7 días disponible
    """
    if df_7d.empty:
        df["actividad"] = "SIN_DATOS_7D"
        df["score_7d"] = 0
        df["gasto_7d"] = 0
        return df
    
    # Preparar datos de 7d para merge
    df_7d_agg = df_7d[["ad_name", "score", "spend"]].rename(columns={
        "score": "score_7d",
        "spend": "gasto_7d"
    })
    
    # Merge con datos de 30d
    df = df.merge(df_7d_agg, on="ad_name", how="left")
    df["score_7d"] = df["score_7d"].fillna(0)
    df["gasto_7d"] = df["gasto_7d"].fillna(0)
    
    def _actividad(row):
        tiene_conv_7d = row["score_7d"] > 0
        tiene_gasto_7d = row["gasto_7d"] > 0
        
        if tiene_conv_7d:
            return "ACTIVO"
        elif tiene_gasto_7d:
            return "GASTANDO"
        else:
            return "INACTIVO"
    
    df["actividad"] = df.apply(_actividad, axis=1)
    return df


def enriquecer_dataframe(df, df_7d=None):
    """
    Aplica todos los cálculos de métricas a un DataFrame.
    
    Args:
        df: DataFrame principal (generalmente 30d)
        df_7d: DataFrame de 7 días (opcional, para calcular actividad)
        
    Returns:
        DataFrame enriquecido con score, cpa, eficiencia y actividad
    """
    df = calcular_score(df)
    df = calcular_cpa(df)
    
    mediana_cpa = calcular_mediana_cpa(df)
    df = calcular_eficiencia(df, mediana_cpa)
    
    if df_7d is not None and not df_7d.empty:
        df_7d = calcular_score(df_7d)
        df = calcular_actividad(df, df_7d)
    else:
        df["actividad"] = "SIN_DATOS_7D"
        df["score_7d"] = 0
        df["gasto_7d"] = 0
    
    return df, mediana_cpa
