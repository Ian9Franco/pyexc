"""
Módulo de recomendaciones V4.
Genera recomendaciones inteligentes basadas en el análisis completo.
"""
import pandas as pd
from config import UMBRALES


def identificar_duplicar(df, mediana_cpa):
    """
    Identifica anuncios candidatos para duplicar/escalar.
    
    Criterios V4:
        1. Score >= umbral mínimo
        2. CPA <= mediana × ratio máximo
        3. Actividad reciente
        4. Clasificación HEROE o SANO
        5. Tendencia no crítica
    
    Returns:
        list de candidatos con razones detalladas
    """
    candidatos = []
    
    for _, row in df.iterrows():
        cpa_valido = pd.notna(row['cpa']) and row['cpa'] > 0
        
        # Criterios de selección
        cumple_score = row['score'] >= UMBRALES['DUPLICAR_SCORE_MIN']
        cumple_cpa = cpa_valido and row['cpa'] <= mediana_cpa * UMBRALES['DUPLICAR_CPA_RATIO_MAX']
        cumple_actividad = row['actividad'] in ['ACTIVO', 'GASTANDO', 'SIN_DATOS_7D']
        cumple_clasificacion = row.get('clasificacion', '') in ['HEROE', 'SANO']
        cumple_tendencia = row.get('tendencia', '') not in ['CRITICO', 'EN_CAIDA']
        
        # Necesita cumplir criterios básicos + al menos uno avanzado
        if cumple_score and cumple_cpa and cumple_actividad:
            razones = []
            prioridad = 0
            
            # Analizar por qué es buen candidato
            if row['score'] >= 20:
                razones.append(f"ALTO VOLUMEN: {row['score']:.0f} conversiones ponderadas")
                prioridad += 3
            else:
                razones.append(f"BUEN VOLUMEN: {row['score']:.0f} conversiones")
                prioridad += 1
            
            if row['cpa'] <= mediana_cpa * 0.7:
                razones.append(f"MUY EFICIENTE: CPA ${row['cpa']:.0f} ({((1 - row['cpa']/mediana_cpa)*100):.0f}% menor que mediana)")
                prioridad += 3
            elif row['cpa'] <= mediana_cpa:
                razones.append(f"EFICIENTE: CPA ${row['cpa']:.0f} (bajo la mediana)")
                prioridad += 2
            else:
                razones.append(f"CPA ACEPTABLE: ${row['cpa']:.0f}")
                prioridad += 1
            
            if row['actividad'] == 'ACTIVO':
                razones.append(f"ACTIVO: {row.get('score_7d', 0):.1f} conversiones en 7 días")
                prioridad += 2
            
            if row.get('tendencia') == 'EN_ASCENSO':
                razones.append("TENDENCIA POSITIVA: rendimiento en aumento")
                prioridad += 2
            
            if row.get('clasificacion') == 'HEROE':
                razones.append("CLASIFICADO COMO HÉROE: rendimiento excepcional")
                prioridad += 3
            
            candidatos.append({
                'nombre': row['ad_name'],
                'score': round(row['score'], 1),
                'score_100': round(row.get('score_100', 0), 1),
                'cpa': round(row['cpa'], 0),
                'gasto': round(row['spend'], 0),
                'actividad': row['actividad'],
                'tendencia': row.get('tendencia', 'SIN_DATOS'),
                'clasificacion': row.get('clasificacion', 'SIN_DATOS'),
                'score_7d': round(row.get('score_7d', 0), 1),
                'razones': razones,
                'prioridad': prioridad,
                'acciones': [
                    "Duplicar configuración y audiencia, NO el creativo",
                    "Usar nueva imagen/video que no esté en otras campañas",
                    "Mantener la misma segmentación",
                    "Empezar con presupuesto igual al original"
                ]
            })
    
    # Ordenar por prioridad y luego por score
    candidatos.sort(key=lambda x: (x['prioridad'], x['score']), reverse=True)
    return candidatos[:5]  # Top 5 candidatos


def identificar_pausar(df, mediana_cpa):
    """
    Identifica anuncios que deberían pausarse urgentemente.
    
    Criterios:
        - PAUSAR: Gasto alto sin conversiones
        - PAUSAR: Clasificación MUERTO con gasto reciente
        - REVISAR: CPA > 2× mediana y tendencia negativa
    
    Returns:
        list de acciones urgentes
    """
    acciones = []
    
    for _, row in df.iterrows():
        cpa_valido = pd.notna(row['cpa']) and row['cpa'] > 0
        
        # PAUSAR: Alto gasto, cero conversiones
        if row['score'] == 0 and row['spend'] > UMBRALES['PAUSAR_GASTO_MIN']:
            acciones.append({
                'tipo': 'PAUSAR',
                'prioridad': 'ALTA',
                'nombre': row['ad_name'],
                'razon': f"Gastó ${row['spend']:,.0f} sin ninguna conversión",
                'detalle': "Consumiendo presupuesto sin resultados",
                'accion': "Pausar inmediatamente"
            })
        
        # PAUSAR: Clasificación MUERTO con gasto reciente
        elif row.get('clasificacion') == 'MUERTO' and row.get('gasto_7d', 0) > 0:
            acciones.append({
                'tipo': 'PAUSAR',
                'prioridad': 'ALTA',
                'nombre': row['ad_name'],
                'razon': f"Anuncio muerto que sigue gastando (${row.get('gasto_7d', 0):,.0f} en 7d)",
                'detalle': "Sin rendimiento pero consumiendo presupuesto",
                'accion': "Pausar y reasignar presupuesto"
            })
        
        # REVISAR: CPA muy alto y tendencia negativa
        elif (cpa_valido and 
              row['cpa'] > mediana_cpa * UMBRALES['PAUSAR_CPA_RATIO'] and
              row.get('tendencia') in ['EN_CAIDA', 'CRITICO']):
            ratio = row['cpa'] / mediana_cpa
            acciones.append({
                'tipo': 'REVISAR',
                'prioridad': 'MEDIA',
                'nombre': row['ad_name'],
                'razon': f"CPA ${row['cpa']:,.0f} es {ratio:.1f}× la mediana y en caída",
                'detalle': f"Tendencia: {row.get('tendencia')}",
                'accion': "Bajar puja 20% o pausar si no mejora en 3 días"
            })
        
        # REVISAR: Sigue gastando sin convertir
        elif (row['actividad'] == 'GASTANDO' and 
              cpa_valido and 
              row['cpa'] > mediana_cpa * UMBRALES['PAUSAR_CPA_RATIO']):
            acciones.append({
                'tipo': 'REVISAR',
                'prioridad': 'MEDIA',
                'nombre': row['ad_name'],
                'razon': f"Gastando sin convertir, CPA alto (${row['cpa']:,.0f})",
                'detalle': "Sin conversiones en los últimos 7 días",
                'accion': "Evaluar segmentación y creatividad"
            })
    
    # Ordenar por prioridad
    orden_prioridad = {'ALTA': 0, 'MEDIA': 1, 'BAJA': 2}
    acciones.sort(key=lambda x: orden_prioridad.get(x['prioridad'], 99))
    
    return acciones


def analizar_no_candidatos(df, mediana_cpa):
    """
    Analiza los mejores anuncios que NO califican para duplicar.
    Explica por qué no califican para dar contexto.
    
    Returns:
        list con análisis de no-candidatos
    """
    candidatos_nombres = [c['nombre'] for c in identificar_duplicar(df, mediana_cpa)]
    no_candidatos = df[~df['ad_name'].isin(candidatos_nombres)]
    
    # Tomar los 5 mejores por score que no calificaron
    top_no_candidatos = no_candidatos.nlargest(5, 'score')
    
    analisis = []
    for _, row in top_no_candidatos.iterrows():
        problemas = []
        
        if row['score'] < UMBRALES['DUPLICAR_SCORE_MIN']:
            problemas.append(f"Score insuficiente: {row['score']:.1f} (necesita {UMBRALES['DUPLICAR_SCORE_MIN']})")
        
        if pd.notna(row['cpa']) and row['cpa'] > mediana_cpa * UMBRALES['DUPLICAR_CPA_RATIO_MAX']:
            max_cpa = mediana_cpa * UMBRALES['DUPLICAR_CPA_RATIO_MAX']
            problemas.append(f"CPA alto: ${row['cpa']:.0f} (máximo ${max_cpa:.0f})")
        
        if row['actividad'] == 'INACTIVO':
            problemas.append("Sin actividad en 7 días")
        
        if row.get('tendencia') in ['CRITICO', 'EN_CAIDA']:
            problemas.append(f"Tendencia negativa: {row.get('tendencia')}")
        
        if row.get('clasificacion') == 'MUERTO':
            problemas.append("Clasificado como MUERTO")
        
        if problemas:
            analisis.append({
                'nombre': row['ad_name'],
                'score': round(row['score'], 1),
                'cpa': round(row['cpa'], 0) if pd.notna(row['cpa']) else None,
                'actividad': row['actividad'],
                'tendencia': row.get('tendencia', 'SIN_DATOS'),
                'problemas': problemas
            })
    
    return analisis


def generar_resumen_acciones(candidatos_duplicar, acciones_urgentes, analisis_objetivo=None):
    """
    Genera un resumen ejecutivo de las acciones recomendadas.
    
    Returns:
        dict con resumen de acciones
    """
    resumen = {
        'total_escalar': len(candidatos_duplicar),
        'total_pausar': len([a for a in acciones_urgentes if a['tipo'] == 'PAUSAR']),
        'total_revisar': len([a for a in acciones_urgentes if a['tipo'] == 'REVISAR']),
        'acciones_prioritarias': []
    }
    
    # Agregar acciones más urgentes
    for accion in acciones_urgentes[:3]:
        resumen['acciones_prioritarias'].append({
            'tipo': accion['tipo'],
            'anuncio': accion['nombre'],
            'razon': accion['razon']
        })
    
    # Agregar mejores candidatos para escalar
    for candidato in candidatos_duplicar[:2]:
        resumen['acciones_prioritarias'].append({
            'tipo': 'ESCALAR',
            'anuncio': candidato['nombre'],
            'razon': candidato['razones'][0] if candidato['razones'] else 'Buen rendimiento'
        })
    
    return resumen
