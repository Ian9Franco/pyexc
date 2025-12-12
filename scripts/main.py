"""
Pipeline principal de Meta Ads.
Orquesta todos los módulos para procesar datos y generar informes.
"""
import json
from data_loader import cargar_datos_cliente, identificar_clientes
from metrics import enriquecer_dataframe, calcular_score
from analyzer import generar_rankings, generar_resumen, generar_historico
from recommendations import identificar_duplicar, identificar_pausar, analizar_no_candidatos
from report_formatter import generar_informe_txt
from json_exporter import generar_json
from config import INFORMES_DIR, LIMPIOS_DIR


def procesar_cliente(cliente):
    """
    Ejecuta el pipeline completo para un cliente.
    """
    print(f"\nProcesando: {cliente}")
    print("-" * 40)
    
    # 1. CARGAR DATOS
    datos = cargar_datos_cliente(cliente)
    
    df_30 = datos['30d']
    df_7 = datos['7d']
    df_hist = datos['historico']
    
    if df_30.empty:
        print(f"  [ERROR] No se encontró archivo de 30 días para {cliente}")
        return
    
    # 2. ENRIQUECER CON MÉTRICAS
    df_30, mediana_cpa = enriquecer_dataframe(df_30, df_7)
    print(f"  Anuncios procesados: {len(df_30)}")
    print(f"  Mediana CPA: ${mediana_cpa:.2f}")
    
    # 3. GENERAR ANÁLISIS
    resumen = generar_resumen(df_30, mediana_cpa)
    rankings = generar_rankings(df_30)
    historico = generar_historico(df_hist)
    
    # 4. GENERAR RECOMENDACIONES
    candidatos_duplicar = identificar_duplicar(df_30, mediana_cpa)
    acciones_urgentes = identificar_pausar(df_30, mediana_cpa)
    no_candidatos = analizar_no_candidatos(df_30, mediana_cpa) if not candidatos_duplicar else []
    
    # 5. EXPORTAR DATOS LIMPIOS
    df_30.to_excel(f"{LIMPIOS_DIR}/{cliente}-30d-clean.xlsx", index=False)
    if not df_7.empty:
        df_7_enriquecido = calcular_score(df_7)
        df_7_enriquecido.to_excel(f"{LIMPIOS_DIR}/{cliente}-7d-clean.xlsx", index=False)
    
    # 6. GENERAR INFORME TXT
    informe_txt = generar_informe_txt(
        cliente, resumen, rankings, candidatos_duplicar,
        no_candidatos, acciones_urgentes, historico,
        df_30, mediana_cpa
    )
    
    txt_path = f"{INFORMES_DIR}/{cliente}-informe.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(informe_txt)
    print(f"  Informe TXT: {txt_path}")
    
    # 7. GENERAR JSON
    informe_json = generar_json(
        cliente, resumen, rankings, candidatos_duplicar,
        acciones_urgentes, historico, df_30, mediana_cpa
    )
    
    json_path = f"{INFORMES_DIR}/{cliente}-informe.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(informe_json, f, ensure_ascii=False, indent=2)
    print(f"  Informe JSON: {json_path}")
    
    return informe_json


def ejecutar_pipeline():
    """
    Ejecuta el pipeline para todos los clientes detectados.
    """
    print("=" * 60)
    print("PIPELINE META ADS v2.0")
    print("=" * 60)
    
    clientes = identificar_clientes()
    
    if not clientes:
        print("\n[ERROR] No se encontraron archivos de clientes.")
        print("Asegúrate de tener archivos en formato: crudo/CLIENTE-30d.xlsx")
        return
    
    print(f"\nClientes encontrados: {', '.join(clientes)}")
    
    resultados = {}
    for cliente in clientes:
        try:
            resultado = procesar_cliente(cliente)
            if resultado:
                resultados[cliente] = resultado
        except Exception as e:
            print(f"  [ERROR] Falló al procesar {cliente}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETADO")
    print(f"Clientes procesados: {len(resultados)}/{len(clientes)}")
    print("=" * 60)
    
    return resultados


if __name__ == "__main__":
    ejecutar_pipeline()
