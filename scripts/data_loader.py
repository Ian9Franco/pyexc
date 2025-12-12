"""
Módulo de carga de datos.
Maneja la lectura de archivos Excel y la normalización de columnas.
"""
import pandas as pd
import glob
import os
from config import META_COLS, CRUDA_DIR, COLUMNAS_NUMERICAS
import warnings
warnings.filterwarnings('ignore')


def normalizar_columnas(df):
    """
    Renombra columnas de Meta Ads al formato interno estándar.
    Maneja variaciones comunes en los nombres de columnas.
    """
    mapping = {}
    
    for col in df.columns:
        col_clean = col.strip()
        
        # Coincidencia exacta
        if col_clean in META_COLS:
            mapping[col] = META_COLS[col_clean]
        # Variaciones de gasto
        elif "Importe gastado" in col_clean:
            mapping[col] = "spend"
        # Variaciones de resultados
        elif "Resultado" in col_clean and "Resultado" not in mapping.values():
            mapping[col] = "results"
        # Variaciones de clics
        elif "Clics" in col_clean and "link_clicks" not in mapping.values():
            mapping[col] = "link_clicks"
    
    df = df.rename(columns=mapping)
    return df


def asegurar_columnas(df):
    """
    Asegura que todas las columnas necesarias existan en el DataFrame.
    Crea columnas faltantes con valor 0.
    """
    for newcol in META_COLS.values():
        if newcol not in df.columns:
            df[newcol] = 0
    return df


def convertir_numericos(df):
    """
    Convierte columnas numéricas al tipo correcto.
    Maneja valores no numéricos reemplazándolos por 0.
    """
    for col in COLUMNAS_NUMERICAS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def cargar_archivo(filepath):
    """
    Carga un archivo Excel y aplica normalización básica.
    
    Args:
        filepath: Ruta al archivo .xlsx
        
    Returns:
        DataFrame normalizado o None si hay error
    """
    try:
        df = pd.read_excel(filepath)
        df = normalizar_columnas(df)
        df = asegurar_columnas(df)
        df = convertir_numericos(df)
        return df
    except Exception as e:
        print(f"  -> Error cargando {filepath}: {e}")
        return None


def cargar_datos_cliente(cliente):
    """
    Carga todos los archivos de un cliente: 30d, 7d e históricos.
    
    Args:
        cliente: Nombre del cliente (ej: "Panichella")
        
    Returns:
        dict con keys '30d', '7d', 'historico' conteniendo DataFrames
    """
    data = {
        '30d': pd.DataFrame(),
        '7d': pd.DataFrame(),
        'historico': pd.DataFrame()
    }
    
    # Cargar 30d y 7d
    for periodo in ["30d", "7d"]:
        fpath = f"{CRUDA_DIR}/{cliente}-{periodo}.xlsx"
        print(f"  -> Buscando: {fpath}")
        
        if os.path.exists(fpath):
            df = cargar_archivo(fpath)
            if df is not None:
                data[periodo] = df
                print(f"     Encontrado: {len(df)} anuncios")
    
    # Cargar históricos (cualquier archivo que no sea 30d o 7d)
    hist_files = glob.glob(f"{CRUDA_DIR}/{cliente}-*.xlsx")
    hist_files = [f for f in hist_files if not any(x in f for x in ["30d", "7d"])]
    
    hist_list = []
    for f in hist_files:
        df = cargar_archivo(f)
        if df is not None:
            # Extraer nombre del período del archivo (ej: "sep", "oct", "nov")
            periodo_nombre = os.path.basename(f).split("-")[-1].split(".")[0]
            df["periodo"] = periodo_nombre
            hist_list.append(df)
            print(f"  -> Histórico {periodo_nombre}: {len(df)} anuncios")
    
    if hist_list:
        data["historico"] = pd.concat(hist_list, ignore_index=True)
    
    return data


def identificar_clientes():
    """
    Escanea la carpeta crudo/ para identificar clientes disponibles.
    
    Returns:
        Lista ordenada de nombres de cliente
    """
    archivos = glob.glob(f"{CRUDA_DIR}/*.xlsx")
    clientes = set()
    
    for f in archivos:
        nombre_base = os.path.basename(f)
        if '-' in nombre_base:
            cliente = nombre_base.split('-')[0]
            clientes.add(cliente)
    
    return sorted(list(clientes))
