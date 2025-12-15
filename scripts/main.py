"""
Pipeline principal de Meta Ads V4.
Orquesta todos los módulos para procesamiento completo.

Características V4:
- Detección automática de tipo de archivo
- Normalización flexible con schema JSON
- Clasificación inteligente por objetivos
- Score normalizado 0-100
- Detección de tendencias y anomalías
- Generación de PDF profesional
- Dashboard web (próximamente)
"""
import json
import os
from datetime import datetime

from data_loader import cargar_datos_cliente, identificar_clientes
from objective_classifier import clasificar_objetivos_dataframe
from metrics import enriquecer_dataframe, calcular_score_basico
from analyzer import (generar_rankings, generar_resumen, generar_historico, 
                      detectar_anomalias, analizar_por_objetivo)
from recommendations import (identificar_duplicar, identificar_pausar, 
                             analizar_no_candidatos, generar_resumen_acciones)
from report_formatter import generar_informe_txt
from json_exporter import generar_json
from pdf_generator import generar_pdf
from config import INFORMES_DIR, LIMPIOS_DIR


def procesar_cliente(cliente, generar_pdf_flag=True):
    """
    Ejecuta el pipeline completo V4 para un cliente.
    
    Args:
        cliente: Nombre del cliente
        generar_pdf_flag: Si generar o no el PDF
        
    Returns:
        dict con resultados del procesamiento
    """
    print(f"\n{'='*60}")
    print(f"Procesando: {cliente}")
    print(f"{'='*60}")
    
    # 1. CARGAR DATOS
    print("\n[1/8] Cargando datos...")
    datos = cargar_datos_cliente(cliente)
    
    df_30 = datos['30d']
    df_7 = datos['7d']
    df_hist = datos['historico']
    
    if df_30.empty:
        print(f"  [ERROR] No se encontró archivo de 30 días para {cliente}")
        return None
    
    # 2. CLASIFICAR POR OBJETIVOS
    print("\n[2/8] Clasificando por objetivos...")
    df_30 = clasificar_objetivos_dataframe(df_30)
    objetivos_detectados = df_30['objetivo_detectado'].value_counts().to_dict()
    print(f"  Objetivos detectados: {objetivos_detectados}")
    
    # 3. ENRIQUECER CON MÉTRICAS
    print("\n[3/8] Calculando métricas...")
    df_30, mediana_cpa = enriquecer_dataframe(df_30, df_7)
    print(f"  Anuncios procesados: {len(df_30)}")
    print(f"  Mediana CPA: ${mediana_cpa:.2f}")
    print(f"  Score promedio 0-100: {df_30['score_100'].mean():.1f}")
    
    # 4. GENERAR ANÁLISIS
    print("\n[4/8] Generando análisis...")
    resumen = generar_resumen(df_30, mediana_cpa)
    rankings = generar_rankings(df_30)
    historico = generar_historico(df_hist)
    anomalias = detectar_anomalias(df_30)
    analisis_objetivo = analizar_por_objetivo(df_30)
    
    print(f"  Héroes: {resumen['clasificacion']['heroes']}")
    print(f"  En alerta: {resumen['clasificacion']['alertas']}")
    print(f"  Anomalías: {len(anomalias)}")
    
    # 5. GENERAR RECOMENDACIONES
    print("\n[5/8] Generando recomendaciones...")
    candidatos_duplicar = identificar_duplicar(df_30, mediana_cpa)
    acciones_urgentes = identificar_pausar(df_30, mediana_cpa)
    no_candidatos = analizar_no_candidatos(df_30, mediana_cpa) if not candidatos_duplicar else []
    resumen_acciones = generar_resumen_acciones(candidatos_duplicar, acciones_urgentes, analisis_objetivo)
    
    print(f"  Para escalar: {len(candidatos_duplicar)}")
    print(f"  Para pausar: {resumen_acciones['total_pausar']}")
    print(f"  Para revisar: {resumen_acciones['total_revisar']}")
    
    # 6. EXPORTAR DATOS LIMPIOS
    print("\n[6/8] Exportando datos limpios...")
    df_30.to_excel(f"{LIMPIOS_DIR}/{cliente}-30d-clean.xlsx", index=False)
    
    if not df_7.empty:
        df_7_enriquecido = calcular_score_basico(df_7)
        df_7_enriquecido.to_excel(f"{LIMPIOS_DIR}/{cliente}-7d-clean.xlsx", index=False)
    
    # 7. GENERAR INFORMES
    print("\n[7/8] Generando informes...")
    
    # TXT
    informe_txt = generar_informe_txt(
        cliente, resumen, rankings, candidatos_duplicar,
        no_candidatos, acciones_urgentes, anomalias,
        historico, df_30, mediana_cpa
    )
    
    txt_path = f"{INFORMES_DIR}/{cliente}-informe.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(informe_txt)
    print(f"  Informe TXT: {txt_path}")
    
    # JSON
    informe_json = generar_json(
        cliente, resumen, rankings, candidatos_duplicar,
        acciones_urgentes, anomalias, historico, analisis_objetivo,
        df_30, mediana_cpa
    )
    
    json_path = f"{INFORMES_DIR}/{cliente}-informe.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(informe_json, f, ensure_ascii=False, indent=2)
    print(f"  Informe JSON: {json_path}")
    
    # PDF
    if generar_pdf_flag:
        print("\n[8/8] Generando PDF...")
        pdf_path = generar_pdf(
            cliente, resumen, rankings, candidatos_duplicar,
            acciones_urgentes, anomalias, historico, mediana_cpa
        )
        if pdf_path:
            print(f"  Informe PDF: {pdf_path}")
        else:
            print("  [AVISO] PDF no generado (instalar reportlab)")
    
    return informe_json


def ejecutar_pipeline(generar_pdf_flag=True):
    """
    Ejecuta el pipeline para todos los clientes detectados.
    
    Args:
        generar_pdf_flag: Si generar PDFs
        
    Returns:
        dict con resultados por cliente
    """
    print("╔" + "═" * 58 + "╗")
    print("║" + " META ADS ANALYZER V4 ".center(58) + "║")
    print("║" + " Sistema Inteligente de Análisis ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    clientes = identificar_clientes()
    
    if not clientes:
        print("\n[ERROR] No se encontraron archivos de clientes.")
        print("Asegúrate de tener archivos en formato: crudo/CLIENTE-30d.xlsx")
        return {}
    
    print(f"\nClientes encontrados: {', '.join(clientes)}")
    
    resultados = {}
    exitosos = 0
    fallidos = 0
    
    for cliente in clientes:
        try:
            resultado = procesar_cliente(cliente, generar_pdf_flag)
            if resultado:
                resultados[cliente] = resultado
                exitosos += 1
        except Exception as e:
            print(f"\n  [ERROR] Falló al procesar {cliente}: {e}")
            import traceback
            traceback.print_exc()
            fallidos += 1
    
    # Resumen final
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETADO")
    print("=" * 60)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"📁 Informes en: {INFORMES_DIR}/")
    print("=" * 60)
    
    return resultados


if __name__ == "__main__":
    ejecutar_pipeline()
