import pandas as pd
import json
from datetime import datetime
from config import UMBRALES, INFORMES_DIR


def generar_txt_informe(cliente, df30, df7, dfhist):

    lines = []
    fecha = datetime.now().strftime("%Y-%m-%d")

    lines.append(f"CLIENTE: {cliente}")
    lines.append(f"FECHA DE REPORTE: {fecha}")
    lines.append("=" * 40)

    lines.append("\n## GLOSARIO DE TERMINOS:")
    lines.append("-" * 40)
    lines.append("* Score: Conversiones ponderadas (msgs iniciados + contactos + clics x 0.15 + visitas IG x 0.3)")
    lines.append("* CPA: Costo Por Adquisicion = Gasto / Conversiones. Menor = mejor.")
    lines.append("* Actividad: Mide si el anuncio sigue generando resultados en los ultimos 7 dias.")
    lines.append("         ACTIVO = tuvo actividad reciente, INACTIVO = sin actividad en 7d, SIN DATOS = falta info de 7d")
    lines.append("* Eficiencia: CPA del anuncio comparado con la mediana. Bajo mediana = eficiente.")
    lines.append("* Mediana CPA: El CPA del anuncio 'del medio'. Si tu CPA > mediana, es caro.")
    lines.append("-" * 40)

    # -------------------------
    # VALIDACIONES BASICAS
    # -------------------------
    if df30.empty:
        lines.append("ERROR: No existe archivo 30d para calcular metricas.")
        return

    # -------------------------
    # JOIN 7d -> 30d
    # -------------------------
    df7_small = df7[["ad_name", "conv_weighted", "spend", "conv_count"]].rename(
        columns={
            "conv_weighted": "conv_w_7",
            "spend": "spend_7",
            "conv_count": "conv_count_7"
        }
    ) if not df7.empty else pd.DataFrame()

    merged = df30.merge(df7_small, on="ad_name", how="left").fillna(0)

    def calcular_actividad(r):
        """
        Determina si el anuncio sigue activo basándose en datos de 7 días.
        Retorna: 'activo', 'inactivo', 'sin_datos'
        """
        tiene_datos_7d = r["conv_w_7"] > 0 or r["spend_7"] > 0
        if not tiene_datos_7d and r["spend"] > 0:
            # Tiene gasto en 30d pero no aparece en 7d
            return "sin_datos"
        elif r["conv_count_7"] > 0:
            return "activo"
        elif r["spend_7"] > 0:
            # Gastó pero no convirtió en 7d
            return "gastando"
        else:
            return "inactivo"

    merged["actividad"] = merged.apply(calcular_actividad, axis=1)
    
    cpa_validos = merged["cpa"].dropna()
    med_cpa = cpa_validos.median() if len(cpa_validos) > 0 else 0
    
    def calcular_eficiencia(r):
        if pd.isna(r["cpa"]) or r["cpa"] == 0:
            return "sin_cpa"
        ratio = r["cpa"] / med_cpa if med_cpa > 0 else 1
        if ratio <= 0.7:
            return "muy_eficiente"
        elif ratio <= 1.0:
            return "eficiente"
        elif ratio <= 1.5:
            return "normal"
        else:
            return "caro"
    
    merged["eficiencia"] = merged.apply(calcular_eficiencia, axis=1)

    # -------------------------
    # SECCION A: RESUMEN
    # -------------------------
    lines.append("\n--- A: RESUMEN 30 DIAS ---")

    gasto = merged["spend"].sum()
    total_conv = merged["conv_count"].sum()
    cpa_global = gasto / total_conv if total_conv > 0 else 0

    lines.append(f"Gasto Total: ${gasto:,.2f} ARS")
    lines.append(f"CPA Promedio Global: ${cpa_global:,.2f} | Mediana CPA: ${med_cpa:,.2f}")
    lines.append(f"Anuncios con conversiones: {len(cpa_validos)} de {len(merged)}")

    activos = len(merged[merged["actividad"] == "activo"])
    gastando = len(merged[merged["actividad"] == "gastando"])
    inactivos = len(merged[merged["actividad"] == "inactivo"])
    
    lines.append(f"\n>> ESTADO DE LA CUENTA:")
    lines.append(f"   Anuncios ACTIVOS (convirtiendo en 7d): {activos}")
    lines.append(f"   Anuncios GASTANDO sin convertir (7d): {gastando}")
    lines.append(f"   Anuncios INACTIVOS: {inactivos}")
    
    if activos == 0:
        lines.append("   [ALERTA] Ningún anuncio convirtió en los últimos 7 días.")
    elif activos < len(merged) * 0.3:
        lines.append("   [ATENCION] Pocos anuncios están convirtiendo activamente.")

    lines.append("\n[TROFEO] TOP 5 POR IMPACTO (mas conversiones ponderadas en 30d):")
    top_impacto = merged.sort_values("conv_weighted", ascending=False).head(5)
    for _, r in top_impacto.iterrows():
        cpa_str = f"${r['cpa']:.0f}" if pd.notna(r['cpa']) else "N/A"
        act_str = r['actividad'].upper()
        lines.append(f"  - {r['ad_name'][:40]}... | Score: {r['conv_weighted']:.1f} | CPA: {cpa_str} | {act_str}")

    lines.append("\n[DINERO] TOP 5 POR VOLUMEN (mas gasto en 30d):")
    top_gasto = merged.sort_values("spend", ascending=False).head(5)
    for _, r in top_gasto.iterrows():
        cpa_str = f"${r['cpa']:.0f}" if pd.notna(r['cpa']) else "N/A"
        lines.append(f"  - {r['ad_name'][:40]}... | Gasto: ${r['spend']:,.0f} | CPA: {cpa_str}")

    lines.append("\n[RAYO] TOP 5 POR EFICIENCIA (menor CPA con al menos 1 conversion):")
    MIN_CONV_EFICIENCIA = 1.0
    merged_con_cpa = merged[
        merged["cpa"].notna() & 
        (merged["cpa"] > 0) & 
        (merged["conv_count"] >= MIN_CONV_EFICIENCIA)
    ]
    if not merged_con_cpa.empty:
        top_eficiencia = merged_con_cpa.sort_values("cpa", ascending=True).head(5)
        for _, r in top_eficiencia.iterrows():
            diff_med = ((r['cpa'] / med_cpa) - 1) * 100 if med_cpa > 0 else 0
            diff_str = f"{diff_med:+.0f}% vs mediana" if diff_med != 0 else "= mediana"
            lines.append(f"  - {r['ad_name'][:40]}... | CPA: ${r['cpa']:.0f} ({diff_str}) | Conv: {r['conv_count']:.1f}")
    else:
        lines.append("  -> No hay anuncios con suficientes conversiones para evaluar eficiencia.")

    # -------------------------
    # SECCION: ANUNCIOS PARA DUPLICAR - Explicación mejorada
    # -------------------------
    lines.append("\n" + "=" * 40)
    lines.append("--- ANUNCIOS PARA DUPLICAR/ESCALAR ---")
    lines.append("=" * 40)
    lines.append("")
    lines.append("Buscamos anuncios que cumplan TODOS estos criterios:")
    lines.append("  1. Score >= 10 (volumen de conversiones significativo)")
    lines.append("  2. CPA <= mediana x 1.2 (costo eficiente)")
    lines.append("  3. Actividad reciente (sigue funcionando)")
    lines.append("")

    candidatos_duplicar = []
    for _, r in merged.iterrows():
        cpa_valido = pd.notna(r["cpa"]) and r["cpa"] > 0
        
        cumple_score = r["conv_weighted"] >= UMBRALES["DUPLICAR_CONV30"]
        cumple_cpa = cpa_valido and r["cpa"] <= med_cpa * 1.2
        cumple_actividad = r["actividad"] in ["activo", "gastando", "sin_datos"]
        
        if cumple_score and cumple_cpa and cumple_actividad:
            candidatos_duplicar.append({
                'name': r['ad_name'],
                'score': r['conv_weighted'],
                'cpa': r['cpa'],
                'spend': r['spend'],
                'conv_count': r['conv_count'],
                'actividad': r['actividad'],
                'eficiencia': r['eficiencia'],
                'conv_count_7': r['conv_count_7']
            })
    
    candidatos_duplicar.sort(key=lambda x: x['score'], reverse=True)
    
    if candidatos_duplicar:
        for i, c in enumerate(candidatos_duplicar[:3], 1):
            lines.append(f"{'='*50}")
            lines.append(f"[OK] #{i} DUPLICAR: {c['name'][:50]}")
            lines.append(f"{'='*50}")
            lines.append(f"")
            lines.append(f"   METRICAS:")
            lines.append(f"   * Score: {c['score']:.1f} conversiones ponderadas en 30 dias")
            lines.append(f"   * CPA: ${c['cpa']:.0f} (mediana es ${med_cpa:.0f})")
            
            ahorro = med_cpa - c['cpa']
            if ahorro > 0:
                lines.append(f"   * Ahorro vs mediana: ${ahorro:.0f} por conversion")
            
            lines.append(f"   * Gasto total: ${c['spend']:,.0f}")
            lines.append(f"   * Conversiones reales: {c['conv_count']:.1f}")
            lines.append(f"")
            lines.append(f"   POR QUE DUPLICAR ESTE ANUNCIO:")
            
            razones = []
            if c['score'] >= 20:
                razones.append(f"   - ALTO VOLUMEN: Con {c['score']:.0f} conversiones, es uno de tus mejores performers")
            elif c['score'] >= 10:
                razones.append(f"   - BUEN VOLUMEN: {c['score']:.0f} conversiones demuestran que el mensaje funciona")
            
            if c['cpa'] <= med_cpa * 0.7:
                razones.append(f"   - MUY EFICIENTE: CPA ${c['cpa']:.0f} es {((1 - c['cpa']/med_cpa)*100):.0f}% menor que la mediana")
            elif c['cpa'] <= med_cpa:
                razones.append(f"   - EFICIENTE: CPA por debajo de la mediana, buena relacion costo/resultado")
            
            if c['actividad'] == 'activo':
                razones.append(f"   - ACTIVO: Sigue generando conversiones esta semana ({c['conv_count_7']:.1f} en 7d)")
            
            for razon in razones:
                lines.append(razon)
            
            lines.append(f"")
            lines.append(f"   QUE HACER:")
            lines.append(f"   1. Duplicar el anuncio manteniendo copy e imagen")
            lines.append(f"   2. Probar con una audiencia similar o lookalike")
            lines.append(f"   3. Aumentar presupuesto 20-30% en el original")
            lines.append(f"")
    else:
        lines.append("[INFO] No hay anuncios que cumplan TODOS los criterios para duplicar.")
        lines.append("")
        
        lines.append("Analisis de los mejores candidatos:")
        lines.append("")
        top3 = merged.sort_values("conv_weighted", ascending=False).head(3)
        for _, r in top3.iterrows():
            cpa_str = f"${r['cpa']:.0f}" if pd.notna(r['cpa']) else "N/A"
            lines.append(f"   {r['ad_name'][:40]}...")
            lines.append(f"   Score: {r['conv_weighted']:.1f} | CPA: {cpa_str} | Actividad: {r['actividad'].upper()}")
            
            problemas = []
            if r['conv_weighted'] < UMBRALES["DUPLICAR_CONV30"]:
                problemas.append(f"Score bajo ({r['conv_weighted']:.1f} < 10)")
            if pd.notna(r['cpa']) and r['cpa'] > med_cpa * 1.2:
                problemas.append(f"CPA alto (${r['cpa']:.0f} > ${med_cpa * 1.2:.0f})")
            if r['actividad'] == 'inactivo':
                problemas.append("Sin actividad reciente")
            
            if problemas:
                lines.append(f"   -> No califica porque: {', '.join(problemas)}")
            lines.append("")

    # -------------------------
    # SECCION D: ACCIONES URGENTES
    # -------------------------
    lines.append("\n" + "=" * 40)
    lines.append("--- ACCIONES URGENTES ---")
    lines.append("=" * 40)

    rec = []

    for _, r in merged.iterrows():
        cpa_valido = pd.notna(r["cpa"]) and r["cpa"] > 0

        # PAUSAR - solo con 0 conversiones y gasto alto
        if r["conv_count"] == 0 and r["spend"] > UMBRALES["PAUSAR_GASTO"]:
            rec.append(
                f"[STOP] PAUSAR: {r['ad_name'][:50]}\n"
                f"   POR QUE: Gasto ${r['spend']:.0f} sin generar ninguna conversion en 30 dias.\n"
                f"   ACCION: Pausar inmediatamente o revisar segmentacion/creatividad."
            )

        elif cpa_valido and r["cpa"] > med_cpa * 2 and r["actividad"] == "gastando":
            rec.append(
                f"[ALERTA] REVISAR: {r['ad_name'][:50]}\n"
                f"   POR QUE: CPA muy alto (${r['cpa']:.0f} = {r['cpa']/med_cpa:.1f}x la mediana) y sigue gastando sin convertir.\n"
                f"   ACCION: Bajar puja 20% o pausar si no mejora en 3 dias."
            )

    if not rec:
        lines.append("[OK] Sin acciones urgentes. Todos los anuncios estan dentro de parametros aceptables.")
    else:
        lines.extend(rec)

    # -------------------------
    # SECCION B: DETALLE POR ANUNCIO - Sin ritmo engañoso
    # -------------------------
    lines.append("\n--- B: DETALLE DE ANUNCIOS ---")
    lines.append("Anuncio | Score | CPA | Eficiencia | Actividad")
    lines.append("-" * 70)

    for _, r in merged.sort_values("conv_weighted", ascending=False).iterrows():
        cpa_str = f"${r['cpa']:.0f}" if pd.notna(r['cpa']) else "N/A"
        efic_str = r['eficiencia'].upper().replace('_', ' ')
        act_str = r['actividad'].upper().replace('_', ' ')
        lines.append(f"{r['ad_name'][:25]}... | {r['conv_weighted']:.1f} | {cpa_str} | {efic_str} | {act_str}")

    # -------------------------
    # SECCION C: HISTORICO
    # -------------------------
    lines.append("\n--- C: CONTEXTO HISTORICO ---")

    if dfhist.empty:
        lines.append("No hay data historica.")
    else:
        resumen = dfhist.groupby("Origen")["conv_weighted"].sum()
        lines.append("Score ponderado por mes:")
        lines.append(resumen.to_string())

    # -------------------------
    # GUARDAR ARCHIVO TXT
    # -------------------------
    out = f"{INFORMES_DIR}/{cliente}-informe.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  -> Informe generado: {out}")

    # -------------------------
    # GENERAR JSON
    # -------------------------
    json_data = generar_json_informe(cliente, fecha, merged, dfhist, med_cpa, gasto, total_conv, cpa_global, candidatos_duplicar, rec)
    
    json_out = f"{INFORMES_DIR}/{cliente}-informe.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"  -> JSON generado: {json_out}")


def generar_json_informe(cliente, fecha, merged, dfhist, med_cpa, gasto, total_conv, cpa_global, candidatos_duplicar, acciones_urgentes):
    """
    Genera un objeto JSON estructurado con todos los datos del informe
    para consumir desde una web.
    """
    
    # Construir lista de anuncios con todas sus metricas
    anuncios = []
    for _, r in merged.iterrows():
        anuncios.append({
            "nombre": r["ad_name"],
            "score": round(r["conv_weighted"], 2),
            "cpa": round(r["cpa"], 2) if pd.notna(r["cpa"]) else None,
            "gasto": round(r["spend"], 2),
            "conversiones": round(r["conv_count"], 2),
            "actividad": r["actividad"],
            "eficiencia": r["eficiencia"],
            "conv_7d": round(r["conv_count_7"], 2) if "conv_count_7" in r else 0,
        })
    
    # Ordenar por score para rankings
    por_impacto = sorted(anuncios, key=lambda x: x["score"], reverse=True)[:5]
    por_gasto = sorted(anuncios, key=lambda x: x["gasto"], reverse=True)[:5]
    por_eficiencia = sorted([a for a in anuncios if a["cpa"] and a["conversiones"] >= 1], key=lambda x: x["cpa"])[:5]
    
    # Historico por mes
    historico = []
    if not dfhist.empty:
        resumen = dfhist.groupby("Origen")["conv_weighted"].sum()
        for mes, valor in resumen.items():
            historico.append({"mes": mes, "score": round(valor, 2)})
    
    # Conteo de estados
    activos = len([a for a in anuncios if a["actividad"] == "activo"])
    gastando = len([a for a in anuncios if a["actividad"] == "gastando"])
    inactivos = len([a for a in anuncios if a["actividad"] == "inactivo"])
    
    return {
        "meta": {
            "cliente": cliente,
            "fecha": fecha,
            "generado_por": "Meta Ads Pipeline v2.1"
        },
        "resumen": {
            "gasto_total": round(gasto, 2),
            "cpa_promedio": round(cpa_global, 2),
            "cpa_mediana": round(med_cpa, 2),
            "conversiones_totales": round(total_conv, 2),
            "total_anuncios": len(anuncios),
            "anuncios_con_conversiones": len([a for a in anuncios if a["cpa"]]),
            "anuncios_activos": activos,
            "anuncios_gastando": gastando,
            "anuncios_inactivos": inactivos
        },
        "rankings": {
            "por_impacto": por_impacto,
            "por_gasto": por_gasto,
            "por_eficiencia": por_eficiencia
        },
        "duplicar": candidatos_duplicar,
        "acciones_urgentes": [
            {"tipo": "pausar" if "[STOP]" in a else "revisar", "mensaje": a}
            for a in acciones_urgentes
        ],
        "anuncios": sorted(anuncios, key=lambda x: x["score"], reverse=True),
        "historico": historico,
        "glosario": {
            "score": "Conversiones ponderadas (msgs iniciados + contactos + clics x 0.15 + visitas IG x 0.3)",
            "cpa": "Costo Por Adquisicion = Gasto / Conversiones. Menor = mejor.",
            "actividad": "ACTIVO = convirtio en 7d, GASTANDO = gasto sin convertir en 7d, INACTIVO = sin gasto ni conversiones",
            "eficiencia": "MUY EFICIENTE (CPA <70% mediana), EFICIENTE (<100%), NORMAL (<150%), CARO (>150%)"
        }
    }
