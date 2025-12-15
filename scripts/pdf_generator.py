from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime
import os

BASE_DIR = Path(__file__).resolve().parent.parent
FONTS_DIR = BASE_DIR / "assets" / "fonts"
LOGO_PATH = BASE_DIR / "assets" / "fanger_logo.png"

# Colors
YELLOW = colors.HexColor("#D6DB2A")
DARK = colors.HexColor("#0B0F19")
TEXT = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#8F8F8F")
BG = colors.HexColor("#F8FAFC")
BORDER = colors.HexColor("#E5E7EB")

def register_fonts():
    pdfmetrics.registerFont(TTFont("DM", FONTS_DIR / "DMSans-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("DM-Medium", FONTS_DIR / "DMSans-Medium.ttf"))
    pdfmetrics.registerFont(TTFont("DM-Bold", FONTS_DIR / "DMSans-Bold.ttf"))

def footer(canvas, doc):
    w, _ = A4
    if LOGO_PATH.exists():
        canvas.drawImage(
            str(LOGO_PATH),
            w - 3.2 * cm,
            0.8 * cm,
            width=2.2 * cm,
            height=2.2 * cm,
            preserveAspectRatio=True,
            mask="auto",
        )
    canvas.setFont("DM", 7)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(
        w - 3.4 * cm,
        0.5 * cm,
        f"Fanger · Performance Marketing · {datetime.now().strftime('%d/%m/%Y')}",
    )

def generar_pdf(
    cliente,
    resumen,
    rankings,
    candidatos_duplicar,
    acciones_urgentes,
    anomalias,
    historico,
    mediana_cpa,
    output_dir="informes",
):
    try:
        register_fonts()
        os.makedirs(output_dir, exist_ok=True)
        path = f"{output_dir}/{cliente}-informe.pdf"

        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2.2 * cm,   # ⬅️ MÁS AIRE ARRIBA
            bottomMargin=2.8 * cm,
        )

        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            name="Client",
            fontName="DM-Bold",
            fontSize=22,
            textColor=DARK,
            spaceAfter=6,
        ))

        styles.add(ParagraphStyle(
            name="Subtitle",
            fontName="DM",
            fontSize=10,
            textColor=MUTED,
            spaceAfter=14,
        ))

        styles.add(ParagraphStyle(
            name="Section",
            fontName="DM-Medium",
            fontSize=12,
            textColor=DARK,
            backColor=BG,
            borderPadding=6,
            spaceBefore=16,
            spaceAfter=8,
        ))

        styles.add(ParagraphStyle(
            name="Body",
            fontName="DM",
            fontSize=9,
            leading=12,
            textColor=TEXT,
            spaceAfter=6,
        ))

        story = []

        # ---------------- HEADER ----------------
        story.append(Paragraph(cliente.upper(), styles["Client"]))
        story.append(Paragraph("Meta Ads Performance Report", styles["Subtitle"]))
        story.append(Spacer(1, 6))  # ⬅️ CLAVE

        story.append(Paragraph(
            f"<font size='18' color='#D6DB2A'><b>${mediana_cpa:.2f}</b></font> "
            f"<font size='9' color='#8F8F8F'>CPA mediana · últimos 30 días</font>",
            styles["Body"],
        ))

        story.append(Spacer(1, 14))  # ⬅️ CLAVE

        # ---------------- KPIs ----------------
        kpis = [
            ["Gasto total", f"${resumen['gasto_total']:.0f}"],
            ["Score total", f"{resumen['score_total']:.0f}"],
            ["Anuncios", resumen["total_anuncios"]],
            ["Activos", resumen["actividad"]["activos"]],
        ]

        t = Table(kpis, colWidths=[4 * cm, 3 * cm] * 2)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG),
            ("FONT", (0, 0), (-1, -1), "DM-Medium", 10),
            ("GRID", (0, 0), (-1, -1), 0.25, BORDER),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)

        # ---------------- RESUMEN ----------------
        story.append(Paragraph("Resumen ejecutivo", styles["Section"]))
        story.append(Paragraph(
            "La cuenta presenta una inversión estable con oportunidades claras de optimización. "
            "Se detecta gasto relevante en anuncios con baja eficiencia y potencial de escalado "
            "en piezas con mejor performance.",
            styles["Body"],
        ))

        # ---------------- RANKINGS ----------------
        def ranking(title, items):
            story.append(Paragraph(title, styles["Section"]))
            data = [["Anuncio", "Score", "CPA"]]
            for a in items[:5]:
                data.append([
                    a["ad_name"][:42],
                    f"{a['score']:.0f}",
                    f"${a['cpa']:.1f}" if a.get("cpa") else "-",
                ])
            table = Table(data, colWidths=[8 * cm, 2 * cm, 2 * cm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), YELLOW),
                ("FONT", (0, 0), (-1, 0), "DM-Bold", 9),
                ("FONT", (0, 1), (-1, -1), "DM", 9),
                ("GRID", (0, 0), (-1, -1), 0.25, BORDER),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(table)

        ranking("Top impacto", rankings["impacto"])
        ranking("Top eficiencia", rankings["eficiencia"])

        # ---------------- ACCIONES ----------------
        if acciones_urgentes:
            story.append(Paragraph("Acciones prioritarias", styles["Section"]))
            for a in acciones_urgentes:
                story.append(Paragraph(
                    f"<b>{a['tipo']}</b> — {a['nombre']}<br/>"
                    f"<font color='#8F8F8F'>{a['razon']}</font>",
                    styles["Body"],
                ))

        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        return path

    except Exception as e:
        print(f"[ERROR PDF] {e}")
        return None
