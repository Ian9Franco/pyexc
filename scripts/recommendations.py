"""
Módulo de recomendaciones.
Genera recomendaciones de duplicar, pausar y revisar anuncios.
"""
import pandas as pd
from config import UMBRALES


def identificar_duplicar(df, mediana_cpa):
    """
    Identifica anuncios candidatos para duplicar/escalar.
    
    Criterios:
        1. Score >= 10 (volumen significativo de conversiones)
        2. CPA <= mediana × 1.2 (costo eficiente)
        3. Actividad reciente (no inactivo)
    
    Returns:
        list de dicts con candidatos y sus razones
    """
    candidatos = []
    
    for _, row in df.iterrows():
        cpa_valido = pd.notna(row['cpa']) and row['cpa'] > 0
        
        cumple_score = row['score'] >= UMBRALES['DUPLICAR_SCORE_MIN']
        cumple_cpa = cpa_valido and row['cpa'] <= mediana_cpa * UMBRALES['DUPLICAR_CPA_RATIO_MAX']
        cumple_actividad = row['actividad'] in ['ACTIVO', 'GASTANDO', 'SIN_DATOS_7D']
        
        if cumple_score and cumple_cpa and cumple_actividad:
            # Construir razones específicas
            razones = []
            
            if row['score'] >= 20:
                razones.append(f"ALTO VOLUMEN: {row['score']:.0f} conversiones ponderadas, es top performer")
            else:
                razones.append(f"BUEN VOLUMEN: {row['score']:.0f} conversiones demuestran que funciona")
            
            ahorro = mediana_cpa - row['cpa']
            if row['cpa'] <= mediana_cpa * 0.7:
                razones.append(f"MUY EFICIENTE: CPA ${row['cpa']:.0f} es {((1 - row['cpa']/mediana_cpa)*100):.0f}% menor que la mediana (${mediana_cpa:.0f})")
            elif row['cpa'] <= mediana_cpa:
                razones.append(f"EFICIENTE: CPA ${row['cpa']:.0f} está por debajo de la mediana (${mediana_cpa:.0f})")
            else:
                razones.append(f"CPA ACEPTABLE: ${row['cpa']:.0f} dentro del rango permitido (máx ${mediana_cpa * 1.2:.0f})")
            
            if row['actividad'] == 'ACTIVO':
                razones.append(f"SIGUE ACTIVO: Generó {row['score_7d']:.1f} conversiones en los últimos 7 días")
            
            candidatos.append({
                'nombre': row['ad_name'],
                'score': round(row['score'], 1),
                'cpa': round(row['cpa'], 0),
                'gasto': round(row['spend'], 0),
                'actividad': row['actividad'],
                'score_7d': round(row.get('score_7d', 0), 1),
                'razones': razones,
                'acciones': [
                    "Duplicar el ANUNCIO (configuración y audiencia), NO el creativo",
                    "Usar una nueva imagen/video que no esté en otras campañas",
                    "Mantener la misma segmentación que funciona",
                    "Empezar con presupuesto igual al original"
                ]
            })
    
    # Ordenar por score
    candidatos.sort(key=lambda x: x['score'], reverse=True)
    return candidatos[:3]


def identificar_pausar(df, mediana_cpa):
    """
    Identifica anuncios que deberían pausarse o revisarse urgentemente.
    
    Criterios para PAUSAR:
        - Gasto alto (> umbral) sin ninguna conversión
        
    Criterios para REVISAR:
        - CPA > 2× mediana y sigue gastando sin convertir
    
    Returns:
        list de dicts con acciones urgentes
    """
    acciones = []
    
    for _, row in df.iterrows():
        cpa_valido = pd.notna(row['cpa']) and row['cpa'] > 0
        
        # PAUSAR: Alto gasto, cero conversiones
        if row['score'] == 0 and row['spend'] > UMBRALES['PAUSAR_GASTO_MIN']:
            acciones.append({
                'tipo': 'PAUSAR',
                'nombre': row['ad_name'],
                'razon': f"Gastó ${row['spend']:,.0f} sin generar ninguna conversión en 30 días",
                'detalle': "El anuncio está consumiendo presupuesto sin resultados",
                'accion': "Pausar inmediatamente o revisar segmentación y creatividad"
            })
        
        # REVISAR: CPA muy alto y sigue gastando
        elif cpa_valido and row['cpa'] > mediana_cpa * UMBRALES['PAUSAR_CPA_RATIO']:
            if row['actividad'] == 'GASTANDO':
                ratio = row['cpa'] / mediana_cpa
                acciones.append({
                    'tipo': 'REVISAR',
                    'nombre': row['ad_name'],
                    'razon': f"CPA ${row['cpa']:,.0f} es {ratio:.1f}× la mediana (${mediana_cpa:.0f})",
                    'detalle': "Sigue gastando pero sin generar conversiones recientes",
                    'accion': "Bajar puja 20% o pausar si no mejora en 3 días"
                })
    
    return acciones


def analizar_no_candidatos(df, mediana_cpa):
    """
    Analiza los anuncios que NO califican para duplicar
    y explica por qué.
    
    Returns:
        list con análisis de los mejores no-candidatos
    """
    from recommendations import identificar_duplicar
    
    candidatos_nombres = [c['nombre'] for c in identificar_duplicar(df, mediana_cpa)]
    no_candidatos = df[~df['ad_name'].isin(candidatos_nombres)]
    
    # Tomar los 3 mejores por score que no calificaron
    top_no_candidatos = no_candidatos.nlargest(3, 'score')
    
    analisis = []
    for _, row in top_no_candidatos.iterrows():
        problemas = []
        
        if row['score'] < UMBRALES['DUPLICAR_SCORE_MIN']:
            problemas.append(f"Score bajo: {row['score']:.1f} (necesita >= {UMBRALES['DUPLICAR_SCORE_MIN']})")
        
        if pd.notna(row['cpa']) and row['cpa'] > mediana_cpa * UMBRALES['DUPLICAR_CPA_RATIO_MAX']:
            problemas.append(f"CPA alto: ${row['cpa']:.0f} (máximo ${mediana_cpa * UMBRALES['DUPLICAR_CPA_RATIO_MAX']:.0f})")
        
        if row['actividad'] == 'INACTIVO':
            problemas.append("Sin actividad en los últimos 7 días")
        
        if problemas:
            analisis.append({
                'nombre': row['ad_name'],
                'score': round(row['score'], 1),
                'cpa': round(row['cpa'], 0) if pd.notna(row['cpa']) else None,
                'actividad': row['actividad'],
                'problemas': problemas
            })
    
    return analisis
