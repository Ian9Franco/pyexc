"""
Módulo de cálculo de métricas V4.
Calcula score inteligente 0-100, CPA, eficiencia y tendencias.
Soporta diferentes objetivos de campaña.
"""
import pandas as pd
import numpy as np
from config import PESOS_CONVERSIONES, PESOS_POR_OBJETIVO, UMBRALES

def limpiar_columnas_duplicadas(df):
    """
    Elimina columnas duplicadas conservando la primera
    """
    return df.loc[:, ~df.columns.duplicated()]


def calcular_score_basico(df):
    """
    Calcula el score básico ponderado de conversiones para cada anuncio.
    FIX: maneja columnas duplicadas y asegura Series válidas.
    """
    # 🔑 FIX CLAVE
    df = limpiar_columnas_duplicadas(df)

    # Asegurar columnas base
    columnas_score = [
        "results",
        "msg_init",
        "msg_contacts",
        "link_clicks",
        "ig_profile",
        "leads",
        "purchases",
    ]

    for col in columnas_score:
        if col not in df.columns:
            df[col] = 0

        # Si quedó como DataFrame (por duplicados previos)
        if isinstance(df[col], pd.DataFrame):
            df[col] = df[col].iloc[:, 0]

        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["score"] = (
        df["results"] * PESOS_CONVERSIONES.get("results", 1.0) +
        df["msg_init"] * PESOS_CONVERSIONES.get("msg_init", 0.0) +
        df["msg_contacts"] * PESOS_CONVERSIONES.get("msg_contacts", 0.0) +
        df["link_clicks"] * PESOS_CONVERSIONES.get("link_clicks", 0.0) +
        df["ig_profile"] * PESOS_CONVERSIONES.get("ig_profile", 0.0) +
        df["leads"] * PESOS_CONVERSIONES.get("leads", 1.0) +
        df["purchases"] * PESOS_CONVERSIONES.get("purchases", 2.0)
    )

    return df



def calcular_score_normalizado(df, objetivo='general'):
    """
    Calcula un score normalizado 0-100 considerando:
    - Rendimiento vs otros anuncios del mismo objetivo
    - Eficiencia del CPA
    - Volumen de conversiones
    
    Args:
        df: DataFrame con métricas calculadas
        objetivo: Tipo de objetivo para usar pesos específicos
        
    Returns:
        DataFrame con columna 'score_100' añadida (score 0-100)
    """
    pesos = PESOS_POR_OBJETIVO.get(objetivo, PESOS_POR_OBJETIVO['general'])
    
    # Calcular componentes del score
    componentes = pd.DataFrame(index=df.index)
    
    # Normalizar cada métrica al rango 0-1 usando percentiles
    for metrica, peso in pesos.items():
        if metrica in df.columns:
            valores = df[metrica].fillna(0)
            
            # Para métricas donde menor es mejor (CPA, CPC, CPL)
            if metrica in ['cpa', 'cpc', 'cpl', 'cpm']:
                # Invertir: valores bajos = score alto
                max_val = valores[valores > 0].max() if (valores > 0).any() else 1
                componentes[metrica] = 1 - (valores / max_val).clip(0, 1)
            else:
                # Normal: valores altos = score alto
                max_val = valores.max() if valores.max() > 0 else 1
                componentes[metrica] = (valores / max_val).clip(0, 1)
            
            componentes[metrica] *= peso
    
    # Sumar componentes
    df['score_100'] = componentes.sum(axis=1) * 100
    
    # Ajustar para que esté en rango 0-100
    max_score = df['score_100'].max()
    if max_score > 0:
        df['score_100'] = (df['score_100'] / max_score * 100).clip(0, 100)
    
    return df


def calcular_cpa(df):
    """
    Calcula el Costo Por Adquisición (CPA) para cada anuncio.
    CPA = Gasto / Score
    
    Anuncios sin conversiones tienen CPA = None para no afectar medianas.
    
    Returns:
        DataFrame con columna 'cpa' añadida
    """
    def _cpa(row):
        if row["score"] > 0:
            return row["spend"] / row["score"]
        return None
    
    df["cpa"] = df.apply(_cpa, axis=1)
    return df


def calcular_mediana_cpa(df):
    """
    Calcula la mediana del CPA (punto de referencia de la cuenta).
    La mediana es robusta a valores extremos.
    
    Returns:
        float: Mediana del CPA, o 0 si no hay datos
    """
    cpa_validos = df["cpa"].dropna()
    cpa_validos = cpa_validos[cpa_validos > 0]
    
    if len(cpa_validos) > 0:
        return cpa_validos.median()
    return 0


def calcular_eficiencia(df, mediana_cpa):
    """
    Categoriza cada anuncio por eficiencia de CPA vs mediana.
    
    Categorías:
        - MUY_EFICIENTE: CPA < 70% de mediana
        - EFICIENTE: CPA < 100% de mediana
        - NORMAL: CPA < 150% de mediana
        - CARO: CPA >= 150% de mediana
        - SIN_DATOS: Sin conversiones
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
    Determina el estado de actividad basándose en los últimos 7 días.
    
    Estados:
        - ACTIVO: Generó conversiones en 7 días
        - GASTANDO: Gastó pero no convirtió en 7 días
        - INACTIVO: Sin gasto ni conversiones en 7 días
        - SIN_DATOS_7D: No hay datos de 7 días
    """
    if df_7d.empty:
        df["actividad"] = "SIN_DATOS_7D"
        df["score_7d"] = 0
        df["gasto_7d"] = 0
        return df
    
    # Preparar datos de 7d
    df_7d_agg = df_7d[["ad_name", "score", "spend"]].rename(columns={
        "score": "score_7d",
        "spend": "gasto_7d"
    })
    
    # Merge
    df = df.merge(df_7d_agg, on="ad_name", how="left")
    df["score_7d"] = df["score_7d"].fillna(0)
    df["gasto_7d"] = df["gasto_7d"].fillna(0)
    
    def _actividad(row):
        if row["score_7d"] > 0:
            return "ACTIVO"
        elif row["gasto_7d"] > 0:
            return "GASTANDO"
        else:
            return "INACTIVO"
    
    df["actividad"] = df.apply(_actividad, axis=1)
    return df


def calcular_tendencia(df, df_7d):
    """
    Calcula la tendencia de cada anuncio comparando 7d vs 30d.
    
    Tendencias:
        - EN_ASCENSO: Rendimiento 7d > 120% del promedio
        - ESTABLE: Rendimiento dentro del ±20%
        - EN_CAIDA: Rendimiento 7d < 80% del promedio
        - CRITICO: Rendimiento 7d < 50% del promedio
        - NUEVO: No hay suficientes datos para comparar
    """
    if df_7d.empty:
        df["tendencia"] = "SIN_DATOS"
        df["ratio_tendencia"] = 1.0
        return df
    
    def _tendencia(row):
        score_30d = row.get("score", 0)
        score_7d = row.get("score_7d", 0)
        
        if score_30d == 0:
            if score_7d > 0:
                return "NUEVO"
            return "SIN_DATOS"
        
        # Calcular promedio diario de 30d y comparar con 7d
        promedio_diario_30d = score_30d / 30
        promedio_diario_7d = score_7d / 7 if score_7d > 0 else 0
        
        if promedio_diario_30d == 0:
            return "NUEVO" if promedio_diario_7d > 0 else "SIN_DATOS"
        
        ratio = promedio_diario_7d / promedio_diario_30d
        
        if ratio >= UMBRALES['TENDENCIA_SUBIDA']:
            return "EN_ASCENSO"
        elif ratio <= UMBRALES['TENDENCIA_CRITICA']:
            return "CRITICO"
        elif ratio <= UMBRALES['TENDENCIA_CAIDA']:
            return "EN_CAIDA"
        else:
            return "ESTABLE"
    
    df["tendencia"] = df.apply(_tendencia, axis=1)
    
    # Calcular ratio numérico para gráficos
    df["ratio_tendencia"] = df.apply(
        lambda r: (r.get("score_7d", 0) / 7) / (r["score"] / 30) 
                  if r["score"] > 0 else 1.0, 
        axis=1
    )
    
    return df


def clasificar_anuncio(row):
    """
    Clasifica un anuncio en categorías para acciones.
    
    Categorías:
        - HEROE: Score alto, eficiente, activo → Escalar
        - SANO: Buen rendimiento general → Mantener
        - ALERTA: Problemas detectados → Revisar
        - MUERTO: Sin rendimiento → Pausar
    """
    score_100 = row.get('score_100', 0)
    eficiencia = row.get('eficiencia', 'SIN_DATOS')
    actividad = row.get('actividad', 'SIN_DATOS_7D')
    tendencia = row.get('tendencia', 'SIN_DATOS')
    
    # Anuncio héroe: alto score, eficiente y activo
    if (score_100 >= UMBRALES['SCORE_HEROE'] and 
        eficiencia in ['MUY_EFICIENTE', 'EFICIENTE'] and 
        actividad == 'ACTIVO'):
        return 'HEROE'
    
    # Anuncio sano: buen score y sin problemas graves
    if (score_100 >= UMBRALES['SCORE_SANO'] and 
        eficiencia not in ['CARO'] and 
        tendencia not in ['CRITICO']):
        return 'SANO'
    
    # Anuncio muerto: sin actividad o tendencia crítica
    if (actividad == 'INACTIVO' or 
        tendencia == 'CRITICO' or 
        (row.get('score', 0) == 0 and row.get('spend', 0) > UMBRALES['PAUSAR_GASTO_MIN'])):
        return 'MUERTO'
    
    # En alerta: todo lo demás
    return 'ALERTA'


def enriquecer_dataframe(df, df_7d=None):
    """
    Aplica todos los cálculos de métricas a un DataFrame.
    Pipeline completo de enriquecimiento.
    
    Args:
        df: DataFrame principal (30d)
        df_7d: DataFrame de 7 días (opcional)
        
    Returns:
        tuple: (DataFrame enriquecido, mediana_cpa)
    """
    # Score básico
    df = calcular_score_basico(df)
    
    # CPA
    df = calcular_cpa(df)
    mediana_cpa = calcular_mediana_cpa(df)
    
    # Eficiencia
    df = calcular_eficiencia(df, mediana_cpa)
    
    # Actividad y tendencia (requieren datos de 7d)
    if df_7d is not None and not df_7d.empty:
        df_7d = calcular_score_basico(df_7d)
        df = calcular_actividad(df, df_7d)
        df = calcular_tendencia(df, df_7d)
    else:
        df["actividad"] = "SIN_DATOS_7D"
        df["score_7d"] = 0
        df["gasto_7d"] = 0
        df["tendencia"] = "SIN_DATOS"
        df["ratio_tendencia"] = 1.0
    
    # Score normalizado 0-100 (después de tener todas las métricas)
    df = calcular_score_normalizado(df)
    
    # Clasificación final
    df['clasificacion'] = df.apply(clasificar_anuncio, axis=1)
    
    return df, mediana_cpa
