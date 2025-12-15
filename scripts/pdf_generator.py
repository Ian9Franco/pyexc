"""
Módulo de generación de PDF V4.
Genera informes profesionales con charts, tablas y recomendaciones.
Usa reportlab para crear PDFs de alta calidad.
"""
from datetime import datetime
import os

# Intentar importar reportlab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus import Image as RLImage
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("[AVISO] reportlab no disponible. Instalar con: pip install reportlab")

from config import PDF_CONFIG, INFORMES_DIR


def crear_estilos():
    """
    Crea los estilos personalizados para el PDF.
    
    Returns:
        dict con estilos de párrafo
    """
    styles = getSampleStyleSheet()
    
    # Título principal
    styles.add(ParagraphStyle(
        name='TituloPrincipal',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1a365d'),
        alignment=TA_CENTER
    ))
    
    # Subtítulo
    styles.add(ParagraphStyle(
        name='Subtitulo',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2c5282')
    ))
    
    # Sección
    styles.add(ParagraphStyle(
        name='Seccion',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#2d3748')
    ))
    
    # Texto normal
    styles.add(ParagraphStyle(
        name='TextoNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leading=14
    ))
    
    # Texto destacado
    styles.add(ParagraphStyle(
        name='Destacado',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        textColor=colors.HexColor('#2b6cb0'),
        fontName='Helvetica-Bold'
    ))
    
    # Alerta
    styles.add(ParagraphStyle(
        name='Alerta',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.HexColor('#c53030'),
        backColor=colors.HexColor('#fed7d7'),
        borderPadding=5
    ))
    
    return styles


def crear_tabla_resumen(resumen, mediana_cpa):
    """
    Crea la tabla de resumen de la cuenta.
    
    Args:
        resumen: dict con métricas de resumen
        mediana_cpa: float con la mediana del CPA
        
    Returns:
        Table de reportlab
    """
    datos = [
        ['Métrica', 'Valor', 'Descripción'],
        ['Gasto Total', f"${resumen['gasto_total']:,.2f}", 'Inversión total en el período'],
        ['Conversiones (Score)', f"{resumen['score_total']:.1f}", 'Total de acciones ponderadas'],
        ['CPA Global', f"${resumen['cpa_global']:,.2f}", 'Costo por adquisición promedio'],
        ['CPA Mediana', f"${mediana_cpa:,.2f}", 'Punto de referencia'],
        ['Score Promedio (0-100)', f"{resumen.get('score_100_promedio', 0):.1f}", 'Rendimiento promedio normalizado'],
        ['Total Anuncios', str(resumen['total_anuncios']), 'Anuncios analizados'],
        ['Con Conversiones', str(resumen['con_conversiones']), 'Anuncios que generaron resultados'],
    ]
    
    tabla = Table(datos, colWidths=[4*cm, 3*cm, 7*cm])
    tabla.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Cuerpo
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        # Bordes y padding
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        # Alternar colores de filas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))
    
    return tabla


def crear_tabla_clasificacion(resumen):
    """
    Crea tabla con la distribución de clasificaciones.
    """
    clasificacion = resumen.get('clasificacion', {})
    tendencia = resumen.get('tendencia', {})
    
    datos = [
        ['Clasificación', 'Cantidad', 'Tendencia', 'Cantidad'],
        ['🏆 Héroes', str(clasificacion.get('heroes', 0)), '📈 En Ascenso', str(tendencia.get('en_ascenso', 0))],
        ['✅ Sanos', str(clasificacion.get('sanos', 0)), '➡️ Estables', str(tendencia.get('estables', 0))],
        ['⚠️ Alerta', str(clasificacion.get('alertas', 0)), '📉 En Caída', str(tendencia.get('en_caida', 0))],
        ['💀 Muertos', str(clasificacion.get('muertos', 0)), '🚨 Críticos', str(tendencia.get('criticos', 0))],
    ]
    
    tabla = Table(datos, colWidths=[3.5*cm, 2*cm, 3.5*cm, 2*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    return tabla


def crear_tabla_ranking(ranking, titulo, columnas):
    """
    Crea tabla para un ranking específico.
    
    Args:
        ranking: list de dicts con datos del ranking
        titulo: str con nombre del ranking
        columnas: list de tuples (nombre_mostrar, key, ancho)
    """
    if not ranking:
        return None
    
    # Encabezados
    headers = [col[0] for col in columnas]
    datos = [headers]
    
    # Filas
    for item in ranking[:5]:
        fila = []
        for _, key, _ in columnas:
            valor = item.get(key, '')
            if isinstance(valor, float):
                if 'cpa' in key.lower() or 'gasto' in key.lower() or 'spend' in key.lower():
                    fila.append(f"${valor:,.0f}")
                elif 'score' in key.lower() and '100' not in key:
                    fila.append(f"{valor:.1f}")
                else:
                    fila.append(f"{valor:.1f}")
            else:
                # Truncar nombres largos
                if key == 'ad_name':
                    fila.append(str(valor)[:35] + '...' if len(str(valor)) > 35 else str(valor))
                else:
                    fila.append(str(valor))
        datos.append(fila)
    
    anchos = [col[2]*cm for col in columnas]
    tabla = Table(datos, colWidths=anchos)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#48bb78')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
    ]))
    
    return tabla


def crear_tabla_acciones(acciones):
    """
    Crea tabla de acciones urgentes.
    """
    if not acciones:
        return None
    
    datos = [['Tipo', 'Anuncio', 'Razón', 'Acción']]
    
    for accion in acciones[:10]:
        datos.append([
            accion['tipo'],
            accion['nombre'][:25] + '...' if len(accion['nombre']) > 25 else accion['nombre'],
            accion['razon'][:40] + '...' if len(accion['razon']) > 40 else accion['razon'],
            accion['accion'][:30] + '...' if len(accion['accion']) > 30 else accion['accion']
        ])
    
    tabla = Table(datos, colWidths=[2*cm, 4*cm, 5*cm, 4*cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e53e3e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
    ]))
    
    return tabla


def generar_pdf(cliente, resumen, rankings, candidatos_duplicar, 
                acciones_urgentes, anomalias, historico, mediana_cpa):
    """
    Genera el informe completo en PDF.
    
    Args:
        cliente: Nombre del cliente
        resumen: dict con resumen de métricas
        rankings: dict con rankings
        candidatos_duplicar: list de candidatos
        acciones_urgentes: list de acciones
        anomalias: list de anomalías detectadas
        historico: list con datos históricos
        mediana_cpa: float con mediana del CPA
        
    Returns:
        str: Ruta al PDF generado, o None si hay error
    """
    if not REPORTLAB_AVAILABLE:
        print("  [ERROR] reportlab no disponible para generar PDF")
        return None
    
    fecha = datetime.now().strftime("%Y-%m-%d")
    pdf_path = f"{INFORMES_DIR}/{cliente}-informe-{fecha}.pdf"
    
    try:
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        styles = crear_estilos()
        elementos = []
        
        # === PORTADA ===
        elementos.append(Spacer(1, 3*cm))
        elementos.append(Paragraph(
            f"INFORME META ADS",
            styles['TituloPrincipal']
        ))
        elementos.append(Paragraph(
            cliente.upper(),
            styles['TituloPrincipal']
        ))
        elementos.append(Spacer(1, 1*cm))
        elementos.append(Paragraph(
            f"Fecha: {fecha}",
            ParagraphStyle('Fecha', parent=styles['TextoNormal'], alignment=TA_CENTER, fontSize=12)
        ))
        elementos.append(Paragraph(
            "Análisis completo de rendimiento publicitario",
            ParagraphStyle('Subtit', parent=styles['TextoNormal'], alignment=TA_CENTER, fontSize=11)
        ))
        elementos.append(PageBreak())
        
        # === RESUMEN EJECUTIVO ===
        elementos.append(Paragraph("RESUMEN EJECUTIVO", styles['Subtitulo']))
        elementos.append(crear_tabla_resumen(resumen, mediana_cpa))
        elementos.append(Spacer(1, 0.5*cm))
        
        # Distribución
        elementos.append(Paragraph("Distribución de Anuncios", styles['Seccion']))
        elementos.append(crear_tabla_clasificacion(resumen))
        elementos.append(Spacer(1, 0.5*cm))
        
        # === ACCIONES URGENTES ===
        if acciones_urgentes:
            elementos.append(Paragraph("⚠️ ACCIONES URGENTES", styles['Subtitulo']))
            tabla_acciones = crear_tabla_acciones(acciones_urgentes)
            if tabla_acciones:
                elementos.append(tabla_acciones)
            elementos.append(Spacer(1, 0.5*cm))
        
        # === RANKINGS ===
        elementos.append(PageBreak())
        elementos.append(Paragraph("📊 RANKINGS DE ANUNCIOS", styles['Subtitulo']))
        
        # Ranking por Impacto
        if rankings.get('impacto'):
            elementos.append(Paragraph("🏆 Top por Impacto (Mayor Score)", styles['Seccion']))
            tabla = crear_tabla_ranking(rankings['impacto'], 'Impacto', [
                ('Anuncio', 'ad_name', 5),
                ('Score', 'score', 2),
                ('CPA', 'cpa', 2),
                ('Estado', 'actividad', 2.5)
            ])
            if tabla:
                elementos.append(tabla)
            elementos.append(Spacer(1, 0.3*cm))
        
        # Ranking por Eficiencia
        if rankings.get('eficiencia'):
            elementos.append(Paragraph("⚡ Top por Eficiencia (Menor CPA)", styles['Seccion']))
            tabla = crear_tabla_ranking(rankings['eficiencia'], 'Eficiencia', [
                ('Anuncio', 'ad_name', 5),
                ('CPA', 'cpa', 2),
                ('Score', 'score', 2),
                ('Eficiencia', 'eficiencia', 2.5)
            ])
            if tabla:
                elementos.append(tabla)
            elementos.append(Spacer(1, 0.3*cm))
        
        # Ranking Héroes
        if rankings.get('heroes'):
            elementos.append(Paragraph("🌟 Top Héroes (Score 0-100)", styles['Seccion']))
            tabla = crear_tabla_ranking(rankings['heroes'], 'Heroes', [
                ('Anuncio', 'ad_name', 5),
                ('Score 100', 'score_100', 2),
                ('Clasificación', 'clasificacion', 2.5),
                ('Tendencia', 'tendencia', 2)
            ])
            if tabla:
                elementos.append(tabla)
        
        # === CANDIDATOS PARA ESCALAR ===
        if candidatos_duplicar:
            elementos.append(PageBreak())
            elementos.append(Paragraph("🚀 ANUNCIOS PARA ESCALAR", styles['Subtitulo']))
            
            for i, candidato in enumerate(candidatos_duplicar[:3], 1):
                elementos.append(Paragraph(
                    f"#{i}: {candidato['nombre'][:50]}",
                    styles['Destacado']
                ))
                elementos.append(Paragraph(
                    f"Score: {candidato['score']:.1f} | CPA: ${candidato['cpa']:.0f} | "
                    f"Estado: {candidato['actividad']} | Tendencia: {candidato.get('tendencia', 'N/A')}",
                    styles['TextoNormal']
                ))
                for razon in candidato['razones'][:3]:
                    elementos.append(Paragraph(f"• {razon}", styles['TextoNormal']))
                elementos.append(Spacer(1, 0.3*cm))
        
        # === ANOMALÍAS ===
        if anomalias:
            elementos.append(Paragraph("🔍 ANOMALÍAS DETECTADAS", styles['Subtitulo']))
            for anomalia in anomalias[:5]:
                elementos.append(Paragraph(
                    f"[{anomalia['severidad']}] {anomalia['tipo']}: {anomalia['anuncio'][:40]}",
                    styles['Alerta'] if anomalia['severidad'] == 'ALTA' else styles['TextoNormal']
                ))
                elementos.append(Paragraph(f"   {anomalia['mensaje']}", styles['TextoNormal']))
                elementos.append(Paragraph(f"   Acción: {anomalia['accion']}", styles['TextoNormal']))
                elementos.append(Spacer(1, 0.2*cm))
        
        # === HISTÓRICO ===
        if historico:
            elementos.append(PageBreak())
            elementos.append(Paragraph("📈 CONTEXTO HISTÓRICO", styles['Subtitulo']))
            
            datos_hist = [['Período', 'Score', 'Gasto', 'CPA', 'Anuncios']]
            for h in historico:
                datos_hist.append([
                    h['periodo'].upper(),
                    f"{h['score']:.1f}",
                    f"${h['gasto']:,.0f}",
                    f"${h['cpa']:,.0f}" if h['cpa'] > 0 else "N/A",
                    str(h['anuncios'])
                ])
            
            tabla_hist = Table(datos_hist, colWidths=[2.5*cm, 2.5*cm, 3*cm, 2.5*cm, 2*cm])
            tabla_hist.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#805ad5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elementos.append(tabla_hist)
        
        # Generar PDF
        doc.build(elementos)
        return pdf_path
        
    except Exception as e:
        print(f"  [ERROR] Generando PDF: {e}")
        return None
