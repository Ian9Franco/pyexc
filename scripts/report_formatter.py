"""
Módulo de formateo del informe TXT.
Genera el informe legible para humanos.
"""
from datetime import datetime


def generar_glosario():
    """Genera la sección de glosario con explicaciones claras."""
    return [
        "## GLOSARIO - QUE SIGNIFICA CADA METRICA",
        "=" * 60,
        "",
        "SCORE (Conversiones Ponderadas)",
        "   Qué es: Un número que representa el VALOR TOTAL de todas las",
        "   acciones que generó el anuncio, no solo la cantidad.",
        "   ",
        "   Cómo se calcula:",
        "   - Mensajes iniciados: valen 1.0 (contacto directo = alto valor)",
        "   - Contactos de mensaje: valen 1.0",
        "   - Resultados de Meta: valen 1.0",
        "   - Clics en enlace: valen 0.15 (solo muestran interés)",
        "   - Visitas al perfil IG: valen 0.3",
        "   ",
        "   Ejemplo: Un anuncio con 5 mensajes + 20 clics = 5×1 + 20×0.15 = 8 score",
        "",
        "-" * 60,
        "",
        "CPA (Costo Por Adquisición)",
        "   Qué es: Cuánto pagaste en promedio por cada conversión.",
        "   Fórmula: Gasto Total ÷ Score",
        "   ",
        "   Ejemplo: Gastaste $10,000 y tienes score de 8 = CPA de $1,250",
        "   ",
        "   Interpretación:",
        "   - CPA BAJO = BUENO (pagas poco por cada resultado)",
        "   - CPA ALTO = MALO (pagas mucho por cada resultado)",
        "",
        "-" * 60,
        "",
        "MEDIANA CPA",
        "   Qué es: El CPA 'del medio' de todos tus anuncios.",
        "   Si ordenas todos los CPA de menor a mayor, la mediana es el del centro.",
        "   ",
        "   Para qué sirve: Es tu PUNTO DE REFERENCIA.",
        "   - Si un anuncio tiene CPA < mediana = es más eficiente que la mayoría",
        "   - Si un anuncio tiene CPA > mediana = es menos eficiente que la mayoría",
        "",
        "-" * 60,
        "",
        "EFICIENCIA (comparación con mediana)",
        "   MUY EFICIENTE: CPA es menos del 70% de la mediana (excelente)",
        "   EFICIENTE: CPA es menor que la mediana (bueno)",
        "   NORMAL: CPA es hasta 50% mayor que mediana (aceptable)",
        "   CARO: CPA es más de 50% mayor que mediana (revisar)",
        "",
        "-" * 60,
        "",
        "ACTIVIDAD (estado reciente)",
        "   ACTIVO: El anuncio generó conversiones en los últimos 7 días",
        "   GASTANDO: Gastó dinero en 7 días pero no generó conversiones",
        "   INACTIVO: No gastó ni convirtió en los últimos 7 días",
        "",
        "=" * 60,
        ""
    ]


def formatear_resumen(resumen, mediana_cpa):
    """Genera la sección de resumen."""
    lines = [
        "## A: RESUMEN DE LA CUENTA (últimos 30 días)",
        "=" * 60,
        "",
        f"Gasto Total: ${resumen['gasto_total']:,.2f} ARS",
        f"Conversiones Totales (Score): {resumen['score_total']:.1f}",
        f"CPA Promedio: ${resumen['cpa_global']:,.2f}",
        f"CPA Mediana: ${mediana_cpa:,.2f}",
        "",
        f"Total de anuncios: {resumen['total_anuncios']}",
        f"Anuncios con conversiones: {resumen['con_conversiones']}",
        "",
        "Estado de los anuncios (últimos 7 días):",
        f"   ACTIVOS (convirtiendo): {resumen['actividad']['activos']}",
        f"   GASTANDO (sin convertir): {resumen['actividad']['gastando']}",
        f"   INACTIVOS: {resumen['actividad']['inactivos']}",
    ]
    
    if resumen['actividad']['sin_datos_7d'] > 0:
        lines.append(f"   Sin datos de 7d: {resumen['actividad']['sin_datos_7d']}")
    
    lines.extend(["", ""])
    return lines


def formatear_rankings(rankings, mediana_cpa):
    """Genera la sección de rankings."""
    lines = [
        "## B: RANKINGS - LOS MEJORES ANUNCIOS",
        "=" * 60,
        ""
    ]
    
    # Top por Impacto
    lines.append("[TROFEO] TOP 5 POR IMPACTO (más conversiones)")
    lines.append("-" * 40)
    for r in rankings['impacto']:
        cpa_str = f"${r['cpa']:.0f}" if r.get('cpa') else "N/A"
        lines.append(f"  {r['ad_name'][:45]}...")
        lines.append(f"     Score: {r['score']:.1f} | CPA: {cpa_str} | {r['actividad']}")
    lines.append("")
    
    # Top por Volumen
    lines.append("[DINERO] TOP 5 POR GASTO (más inversión)")
    lines.append("-" * 40)
    for r in rankings['volumen']:
        cpa_str = f"${r['cpa']:.0f}" if r.get('cpa') else "N/A"
        lines.append(f"  {r['ad_name'][:45]}...")
        lines.append(f"     Gasto: ${r['spend']:,.0f} | CPA: {cpa_str}")
    lines.append("")
    
    # Top por Eficiencia
    lines.append("[RAYO] TOP 5 POR EFICIENCIA (menor CPA)")
    lines.append("       (Solo anuncios con al menos 1 conversión)")
    lines.append("-" * 40)
    if rankings['eficiencia']:
        for r in rankings['eficiencia']:
            diff = ((r['cpa'] / mediana_cpa) - 1) * 100 if mediana_cpa > 0 else 0
            diff_str = f"{diff:+.0f}% vs mediana" if diff != 0 else "= mediana"
            lines.append(f"  {r['ad_name'][:45]}...")
            lines.append(f"     CPA: ${r['cpa']:.0f} ({diff_str}) | Score: {r['score']:.1f}")
    else:
        lines.append("  No hay suficientes datos para este ranking.")
    
    lines.extend(["", ""])
    return lines


def formatear_duplicar(candidatos, no_candidatos, mediana_cpa):
    """Genera la sección de anuncios para duplicar."""
    lines = [
        "## C: ANUNCIOS PARA ESCALAR (DUPLICAR)",
        "=" * 60,
        "",
        "QUE SIGNIFICA 'DUPLICAR UN ANUNCIO':",
        "   No es copiar el texto o imagen. Es crear un NUEVO ANUNCIO",
        "   usando los mismos parámetros de segmentación y configuración",
        "   del anuncio exitoso, pero con creativos frescos (nueva imagen,",
        "   video o copy) que no esté actualmente en ninguna campaña.",
        "",
        "   Esto permite:",
        "   - Escalar el éxito sin saturar la audiencia con el mismo creativo",
        "   - Probar nuevas piezas con una configuración que ya funciona",
        "   - Aumentar el alcance sin competir contigo mismo",
        "",
        "-" * 60,
        "",
        "CRITERIOS DE SELECCIÓN:",
        f"   1. Score >= 10 (volumen significativo de conversiones)",
        f"   2. CPA <= ${mediana_cpa * 1.2:.0f} (máximo 120% de la mediana ${mediana_cpa:.0f})",
        "   3. Actividad reciente (no anuncios abandonados)",
        ""
    ]
    
    if candidatos:
        lines.append(f"ENCONTRAMOS {len(candidatos)} ANUNCIO(S) PARA ESCALAR:")
        lines.append("")
        
        for i, c in enumerate(candidatos, 1):
            lines.append("=" * 50)
            lines.append(f"[ESCALAR] #{i}: {c['nombre'][:50]}")
            lines.append("=" * 50)
            lines.append("")
            lines.append("   MÉTRICAS DEL ANUNCIO:")
            lines.append(f"   - Score: {c['score']:.1f} conversiones ponderadas")
            lines.append(f"   - CPA: ${c['cpa']:.0f} (mediana: ${mediana_cpa:.0f})")
            
            # Calcular qué tan eficiente es vs mediana
            eficiencia_pct = (c['cpa'] / mediana_cpa * 100) if mediana_cpa > 0 else 0
            if eficiencia_pct < 70:
                lines.append(f"   - Eficiencia: EXCELENTE ({eficiencia_pct:.0f}% de la mediana)")
            elif eficiencia_pct < 100:
                lines.append(f"   - Eficiencia: BUENA ({eficiencia_pct:.0f}% de la mediana)")
            else:
                lines.append(f"   - Eficiencia: ACEPTABLE ({eficiencia_pct:.0f}% de la mediana)")
            
            lines.append(f"   - Gasto acumulado: ${c['gasto']:,.0f}")
            lines.append(f"   - Actividad: {c['actividad']}")
            lines.append("")
            lines.append("   POR QUÉ ESCALAR ESTE ANUNCIO:")
            for razon in c['razones']:
                lines.append(f"   - {razon}")
            lines.append("")
            lines.append("   CÓMO ESCALARLO:")
            lines.append("   1. Ve a Ads Manager y selecciona este anuncio")
            lines.append("   2. Click en 'Duplicar' > 'Duplicar en mismo conjunto'")
            lines.append("   3. En el nuevo anuncio, CAMBIA SOLO el creativo:")
            lines.append("      - Nueva imagen/video que no esté en otras campañas")
            lines.append("      - Puedes probar nuevo copy también")
            lines.append("   4. Mantén la misma audiencia y configuración")
            lines.append("   5. Empieza con presupuesto igual al original")
            lines.append("")
    else:
        lines.append("[INFO] No hay anuncios que cumplan TODOS los criterios.")
        lines.append("")
        lines.append("Esto puede significar:")
        lines.append("   - Los anuncios con buen volumen tienen CPA alto")
        lines.append("   - Los anuncios eficientes tienen poco volumen")
        lines.append("   - Faltan datos recientes para evaluar")
        lines.append("")
        
        if no_candidatos:
            lines.append("Los mejores candidatos y por qué no califican:")
            lines.append("-" * 40)
            for nc in no_candidatos[:5]:
                cpa_str = f"${nc['cpa']:.0f}" if nc['cpa'] else "Sin conversiones"
                lines.append(f"  {nc['nombre'][:40]}...")
                lines.append(f"     Score: {nc['score']:.1f} | CPA: {cpa_str}")
                lines.append(f"     Problema: {', '.join(nc['problemas'])}")
                lines.append("")
    
    lines.append("")
    return lines


def formatear_acciones_urgentes(acciones):
    """Genera la sección de acciones urgentes."""
    lines = [
        "## D: ACCIONES URGENTES",
        "=" * 60,
        ""
    ]
    
    if not acciones:
        lines.append("[OK] Sin acciones urgentes.")
        lines.append("    Todos los anuncios están dentro de parámetros aceptables.")
    else:
        for a in acciones:
            icono = "[STOP]" if a['tipo'] == 'PAUSAR' else "[ALERTA]"
            lines.append(f"{icono} {a['tipo']}: {a['nombre'][:50]}")
            lines.append(f"   Por qué: {a['razon']}")
            lines.append(f"   Detalle: {a['detalle']}")
            lines.append(f"   Acción: {a['accion']}")
            lines.append("")
    
    lines.extend(["", ""])
    return lines


def formatear_detalle_anuncios(df):
    """Genera la sección de detalle por anuncio."""
    lines = [
        "## E: DETALLE DE TODOS LOS ANUNCIOS",
        "=" * 60,
        "",
        "Anuncio | Score | CPA | Eficiencia | Actividad",
        "-" * 70,
    ]
    
    for _, r in df.sort_values('score', ascending=False).iterrows():
        cpa_str = f"${r['cpa']:.0f}" if pd.notna(r['cpa']) else "N/A"
        lines.append(
            f"{r['ad_name'][:25]}... | {r['score']:.1f} | {cpa_str} | "
            f"{r['eficiencia']} | {r['actividad']}"
        )
    
    lines.extend(["", ""])
    return lines


def formatear_historico(historico):
    """Genera la sección de histórico con análisis."""
    lines = [
        "## F: CONTEXTO HISTÓRICO POR PERÍODO",
        "=" * 60,
        ""
    ]
    
    if not historico:
        lines.append("No hay datos históricos disponibles.")
        lines.append("")
        lines.append("Para ver el historial, agrega archivos con sufijo de mes:")
        lines.append("   Ejemplo: MiCliente-sep.xlsx, MiCliente-oct.xlsx")
        return lines
    
    # Ordenar por período si es posible
    meses_orden = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 
                   'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
    
    def orden_mes(h):
        periodo = h['periodo'].lower()[:3]
        try:
            return meses_orden.index(periodo)
        except ValueError:
            return 99  # Si no es un mes reconocido, al final
    
    historico_ordenado = sorted(historico, key=orden_mes)
    
    lines.append("SCORE TOTAL POR MES:")
    lines.append("-" * 40)
    
    scores = [h['score'] for h in historico_ordenado]
    max_score = max(scores) if scores else 1
    min_score = min(scores) if scores else 0
    avg_score = sum(scores) / len(scores) if scores else 0
    
    for h in historico_ordenado:
        # Crear barra visual
        barra_len = int((h['score'] / max_score) * 20) if max_score > 0 else 0
        barra = "█" * barra_len + "░" * (20 - barra_len)
        
        # Indicador vs promedio
        if h['score'] > avg_score * 1.1:
            indicador = "↑ sobre promedio"
        elif h['score'] < avg_score * 0.9:
            indicador = "↓ bajo promedio"
        else:
            indicador = "≈ promedio"
        
        lines.append(f"   {h['periodo'].upper():>5}: {barra} {h['score']:>6.1f} ({indicador})")
    
    lines.append("")
    lines.append(f"   Promedio mensual: {avg_score:.1f}")
    lines.append(f"   Mejor mes: {max_score:.1f}")
    lines.append(f"   Peor mes: {min_score:.1f}")
    lines.append("")
    
    # Análisis de tendencia
    if len(historico_ordenado) >= 2:
        primer_score = historico_ordenado[0]['score']
        ultimo_score = historico_ordenado[-1]['score']
        cambio = ((ultimo_score - primer_score) / primer_score * 100) if primer_score > 0 else 0
        
        lines.append("TENDENCIA GENERAL:")
        if cambio > 10:
            lines.append(f"   La cuenta MEJORÓ {cambio:.0f}% desde {historico_ordenado[0]['periodo']} hasta {historico_ordenado[-1]['periodo']}")
        elif cambio < -10:
            lines.append(f"   La cuenta CAYÓ {abs(cambio):.0f}% desde {historico_ordenado[0]['periodo']} hasta {historico_ordenado[-1]['periodo']}")
        else:
            lines.append(f"   La cuenta se mantuvo ESTABLE (variación de {cambio:.0f}%)")
    
    return lines


# Necesario para formatear_detalle_anuncios
import pandas as pd


def generar_informe_txt(cliente, resumen, rankings, candidatos_duplicar, 
                        no_candidatos, acciones_urgentes, historico, 
                        df, mediana_cpa):
    """
    Genera el informe completo en formato TXT.
    
    Returns:
        str con el contenido del informe
    """
    fecha = datetime.now().strftime("%Y-%m-%d")
    
    lines = [
        f"INFORME META ADS: {cliente.upper()}",
        f"Fecha: {fecha}",
        "=" * 60,
        ""
    ]
    
    lines.extend(generar_glosario())
    lines.extend(formatear_resumen(resumen, mediana_cpa))
    lines.extend(formatear_rankings(rankings, mediana_cpa))
    lines.extend(formatear_duplicar(candidatos_duplicar, no_candidatos, mediana_cpa))
    lines.extend(formatear_acciones_urgentes(acciones_urgentes))
    lines.extend(formatear_detalle_anuncios(df))
    lines.extend(formatear_historico(historico))
    
    return "\n".join(lines)
