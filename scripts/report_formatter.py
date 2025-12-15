"""
Módulo de formateo del informe TXT V4.
Genera el informe legible para humanos con análisis completo.
"""
from datetime import datetime
import pandas as pd


def generar_glosario():
    """Genera la sección de glosario con explicaciones claras."""
    return [
        "## GLOSARIO - QUÉ SIGNIFICA CADA MÉTRICA",
        "=" * 60,
        "",
        "SCORE (Conversiones Ponderadas)",
        "   Qué es: Valor TOTAL de todas las acciones del anuncio.",
        "   Mensajes valen 1.0, clics 0.15, visitas perfil 0.3",
        "   Mayor score = más resultados generados",
        "",
        "SCORE 0-100 (Rendimiento Normalizado)",
        "   Qué es: Calificación relativa comparando con otros anuncios",
        "   90-100: HÉROE → Escalar/duplicar",
        "   70-89: SANO → Mantener",
        "   40-69: ALERTA → Revisar",
        "   0-39: MUERTO → Pausar/eliminar",
        "",
        "CPA (Costo Por Adquisición)",
        "   Qué es: Gasto ÷ Score = cuánto pagas por resultado",
        "   Menor CPA = más eficiente",
        "",
        "TENDENCIA (7d vs 30d)",
        "   EN_ASCENSO: Mejorando (+20%)",
        "   ESTABLE: Constante (±20%)",
        "   EN_CAIDA: Bajando (-20%)",
        "   CRITICO: Caída severa (-50%)",
        "",
        "=" * 60,
        ""
    ]


def formatear_resumen(resumen, mediana_cpa):
    """Genera la sección de resumen con clasificaciones."""
    clasificacion = resumen.get('clasificacion', {})
    tendencia = resumen.get('tendencia', {})
    
    lines = [
        "## A: RESUMEN DE LA CUENTA",
        "=" * 60,
        "",
        f"💰 Gasto Total: ${resumen['gasto_total']:,.2f} ARS",
        f"🎯 Conversiones (Score): {resumen['score_total']:.1f}",
        f"📊 CPA Promedio: ${resumen['cpa_global']:,.2f}",
        f"📈 CPA Mediana: ${mediana_cpa:,.2f}",
        f"⭐ Score Promedio (0-100): {resumen.get('score_100_promedio', 0):.1f}",
        "",
        f"Total de anuncios: {resumen['total_anuncios']}",
        f"Con conversiones: {resumen['con_conversiones']}",
        "",
        "CLASIFICACIÓN DE ANUNCIOS:",
        f"   🏆 Héroes (escalar): {clasificacion.get('heroes', 0)}",
        f"   ✅ Sanos (mantener): {clasificacion.get('sanos', 0)}",
        f"   ⚠️ Alerta (revisar): {clasificacion.get('alertas', 0)}",
        f"   💀 Muertos (pausar): {clasificacion.get('muertos', 0)}",
        "",
        "TENDENCIA (últimos 7 días):",
        f"   📈 En ascenso: {tendencia.get('en_ascenso', 0)}",
        f"   ➡️ Estables: {tendencia.get('estables', 0)}",
        f"   📉 En caída: {tendencia.get('en_caida', 0)}",
        f"   🚨 Críticos: {tendencia.get('criticos', 0)}",
        "",
        ""
    ]
    return lines


def formatear_acciones_urgentes(acciones):
    """Genera la sección de acciones urgentes."""
    lines = [
        "## B: ACCIONES URGENTES",
        "=" * 60,
        ""
    ]
    
    if not acciones:
        lines.append("✅ Sin acciones urgentes.")
        lines.append("   Todos los anuncios dentro de parámetros aceptables.")
    else:
        pausar = [a for a in acciones if a['tipo'] == 'PAUSAR']
        revisar = [a for a in acciones if a['tipo'] == 'REVISAR']
        
        if pausar:
            lines.append(f"🛑 PAUSAR INMEDIATAMENTE ({len(pausar)} anuncios):")
            lines.append("-" * 40)
            for a in pausar:
                lines.append(f"   • {a['nombre'][:45]}")
                lines.append(f"     Razón: {a['razon']}")
                lines.append(f"     Acción: {a['accion']}")
                lines.append("")
        
        if revisar:
            lines.append(f"⚠️ REVISAR ({len(revisar)} anuncios):")
            lines.append("-" * 40)
            for a in revisar[:5]:
                lines.append(f"   • {a['nombre'][:45]}")
                lines.append(f"     Razón: {a['razon']}")
                lines.append("")
    
    lines.extend(["", ""])
    return lines


def formatear_rankings(rankings, mediana_cpa):
    """Genera la sección de rankings."""
    lines = [
        "## C: RANKINGS - LOS MEJORES ANUNCIOS",
        "=" * 60,
        ""
    ]
    
    # Top Héroes
    if rankings.get('heroes'):
        lines.append("🌟 TOP HÉROES (Score 0-100)")
        lines.append("-" * 40)
        for r in rankings['heroes']:
            lines.append(f"  {r['ad_name'][:45]}")
            lines.append(f"     Score: {r.get('score_100', 0):.1f}/100 | Clasificación: {r.get('clasificacion', 'N/A')}")
        lines.append("")
    
    # Top por Impacto
    lines.append("🏆 TOP 5 POR IMPACTO (más conversiones)")
    lines.append("-" * 40)
    for r in rankings.get('impacto', []):
        cpa_str = f"${r['cpa']:.0f}" if r.get('cpa') else "N/A"
        lines.append(f"  {r['ad_name'][:45]}")
        lines.append(f"     Score: {r['score']:.1f} | CPA: {cpa_str} | {r.get('actividad', 'N/A')}")
    lines.append("")
    
    # Top por Eficiencia
    lines.append("⚡ TOP 5 POR EFICIENCIA (menor CPA)")
    lines.append("-" * 40)
    if rankings.get('eficiencia'):
        for r in rankings['eficiencia']:
            diff = ((r['cpa'] / mediana_cpa) - 1) * 100 if mediana_cpa > 0 else 0
            diff_str = f"{diff:+.0f}% vs mediana"
            lines.append(f"  {r['ad_name'][:45]}")
            lines.append(f"     CPA: ${r['cpa']:.0f} ({diff_str}) | Score: {r['score']:.1f}")
    else:
        lines.append("  No hay suficientes datos para este ranking.")
    
    lines.extend(["", ""])
    return lines


def formatear_duplicar(candidatos, no_candidatos, mediana_cpa):
    """Genera la sección de anuncios para escalar."""
    lines = [
        "## D: ANUNCIOS PARA ESCALAR (DUPLICAR)",
        "=" * 60,
        "",
        "CÓMO ESCALAR UN ANUNCIO:",
        "   1. Duplicar la CONFIGURACIÓN (audiencia, ubicación, puja)",
        "   2. Cambiar el CREATIVO (nueva imagen/video)",
        "   3. Mantener presupuesto similar",
        "",
        "-" * 60,
        ""
    ]
    
    if candidatos:
        lines.append(f"✅ {len(candidatos)} CANDIDATO(S) IDENTIFICADO(S):")
        lines.append("")
        
        for i, c in enumerate(candidatos, 1):
            lines.append("=" * 50)
            lines.append(f"🚀 #{i}: {c['nombre'][:50]}")
            lines.append("=" * 50)
            lines.append(f"   Score: {c['score']:.1f} | Score 0-100: {c.get('score_100', 0):.1f}")
            lines.append(f"   CPA: ${c['cpa']:.0f} (mediana: ${mediana_cpa:.0f})")
            lines.append(f"   Tendencia: {c.get('tendencia', 'N/A')} | Clasificación: {c.get('clasificacion', 'N/A')}")
            lines.append("")
            lines.append("   POR QUÉ ESCALAR:")
            for razon in c['razones']:
                lines.append(f"   ✓ {razon}")
            lines.append("")
    else:
        lines.append("❌ No hay anuncios que cumplan TODOS los criterios.")
        lines.append("")
        
        if no_candidatos:
            lines.append("Los mejores candidatos y por qué no califican:")
            lines.append("-" * 40)
            for nc in no_candidatos[:3]:
                cpa_str = f"${nc['cpa']:.0f}" if nc['cpa'] else "Sin conversiones"
                lines.append(f"  {nc['nombre'][:40]}")
                lines.append(f"     Score: {nc['score']:.1f} | CPA: {cpa_str}")
                lines.append(f"     Problemas: {', '.join(nc['problemas'][:2])}")
                lines.append("")
    
    return lines


def formatear_anomalias(anomalias):
    """Genera la sección de anomalías detectadas."""
    lines = [
        "## E: ANOMALÍAS DETECTADAS",
        "=" * 60,
        ""
    ]
    
    if not anomalias:
        lines.append("✅ No se detectaron anomalías significativas.")
    else:
        for a in anomalias[:10]:
            icono = "🚨" if a['severidad'] == 'ALTA' else "⚠️"
            lines.append(f"{icono} [{a['severidad']}] {a['tipo']}")
            lines.append(f"   Anuncio: {a['anuncio'][:40]}")
            lines.append(f"   Detalle: {a['mensaje']}")
            lines.append(f"   Acción: {a['accion']}")
            lines.append("")
    
    lines.append("")
    return lines


def formatear_historico(historico):
    """Genera la sección de histórico con análisis."""
    lines = [
        "## F: CONTEXTO HISTÓRICO",
        "=" * 60,
        ""
    ]
    
    if not historico:
        lines.append("No hay datos históricos disponibles.")
        lines.append("Para ver historial, agrega archivos: Cliente-sep.xlsx, Cliente-oct.xlsx, etc.")
        return lines
    
    # Ordenar por período
    meses_orden = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 
                   'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
    
    def orden_mes(h):
        periodo = h['periodo'].lower()[:3]
        try:
            return meses_orden.index(periodo)
        except ValueError:
            return 99
    
    historico_ordenado = sorted(historico, key=orden_mes)
    
    lines.append("SCORE POR MES:")
    lines.append("-" * 40)
    
    scores = [h['score'] for h in historico_ordenado]
    max_score = max(scores) if scores else 1
    avg_score = sum(scores) / len(scores) if scores else 0
    
    for h in historico_ordenado:
        barra_len = int((h['score'] / max_score) * 20) if max_score > 0 else 0
        barra = "█" * barra_len + "░" * (20 - barra_len)
        
        if h['score'] > avg_score * 1.1:
            indicador = "↑"
        elif h['score'] < avg_score * 0.9:
            indicador = "↓"
        else:
            indicador = "→"
        
        lines.append(f"   {h['periodo'].upper():>5}: {barra} {h['score']:>6.1f} {indicador}")
    
    lines.append("")
    lines.append(f"   Promedio: {avg_score:.1f} | Mejor: {max(scores):.1f} | Peor: {min(scores):.1f}")
    
    return lines


def formatear_comparativa_managers(comparativa):
    """Genera la sección de comparación Ian vs General."""
    if not comparativa or len(comparativa) < 2:
        return []
        
    lines = [
        "## G: COMPARATIVA DE GESTIÓN (IAN vs GENERAL)",
        "=" * 60,
        ""
    ]
    
    # Encabezados
    lines.append(f"{'MANAGER':<10} | {'GASTO':<12} | {'CONV.':<8} | {'CPA':<10} | {'CALIDAD'}")
    lines.append("-" * 60)
    
    # Asegurar orden
    managers = sorted(comparativa.keys())
    
    for manager in managers:
        metrics = comparativa[manager]
        # Formato de gasto y conversiones con separador de miles
        gasto_str = f"${metrics['gasto']:,.0f}" 
        conv_str = f"{metrics['conversiones']:,.1f}"
        cpa_str = f"${metrics['cpa_real']:,.0f}" if metrics['cpa_real'] > 0 else "N/A"
        calidad_str = f"{metrics['calidad_promedio']:.1f}/100"
        
        lines.append(
            f"{manager:<10} | "
            f"{gasto_str:<12} | "
            f"{conv_str:<8} | "
            f"{cpa_str:<10} | "
            f"{calidad_str}"
        )
    
    lines.append("")
    
    # Conclusión rápida
    if 'Ian' in comparativa and 'General' in comparativa:
        cpa_ian = comparativa['Ian']['cpa_real']
        cpa_gen = comparativa['General']['cpa_real']
        
        if cpa_ian > 0 and cpa_gen > 0:
            if cpa_ian < cpa_gen:
                diff = ((cpa_gen - cpa_ian) / cpa_gen) * 100
                lines.append(f"✅ Las campañas de Ian son un {diff:.1f}% más eficientes en costos (CPA).")
            elif cpa_ian > cpa_gen:
                diff = ((cpa_ian - cpa_gen) / cpa_gen) * 100
                lines.append(f"⚠️ Las campañas de Ian tienen un CPA un {diff:.1f}% más alto que el promedio general.")
            else:
                lines.append(f"↔️ Las campañas de Ian y General tienen un CPA similar.")
            
    lines.extend(["", ""])
    return lines


def generar_informe_txt(cliente, resumen, rankings, candidatos_duplicar, 
                        no_candidatos, acciones_urgentes, anomalias,
                        historico, df, mediana_cpa):
    """
    Genera el informe completo en formato TXT.
    
    Returns:
        str con el contenido del informe
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # === Nuevo: Importar y calcular la comparativa de managers ===
    try:
        # Se asume que analyzer.py está en el mismo path.
        from analyzer import analizar_rendimiento_managers
        comparativa_managers = analizar_rendimiento_managers(df)
    except ImportError:
        comparativa_managers = None
    # =============================================================
    
    lines = [
        "╔" + "═" * 58 + "╗",
        "║" + f" INFORME META ADS V4: {cliente.upper()} ".center(58) + "║",
        "║" + f" Fecha: {fecha} ".center(58) + "║",
        "╚" + "═" * 58 + "╝",
        ""
    ]
    
    lines.extend(generar_glosario())
    lines.extend(formatear_resumen(resumen, mediana_cpa))
    lines.extend(formatear_acciones_urgentes(acciones_urgentes))
    lines.extend(formatear_rankings(rankings, mediana_cpa))
    lines.extend(formatear_duplicar(candidatos_duplicar, no_candidatos, mediana_cpa))
    lines.extend(formatear_anomalias(anomalias))
    lines.extend(formatear_historico(historico))
    
    # === Nuevo: Agregar la sección de comparativa ===
    if comparativa_managers:
        lines.extend(formatear_comparativa_managers(comparativa_managers))
    # ================================================
    
    lines.extend([
        "",
        "=" * 60,
        "FIN DEL INFORME",
        "Sistema Meta Ads Analyzer V4",
        "=" * 60
    ])
    
    return "\n".join(lines)