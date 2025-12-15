"""
Módulo de carga de datos V4.
Maneja la lectura de archivos Excel con normalización flexible
usando el schema JSON de columnas.
"""
import pandas as pd
import glob
import os
import json
import re
from config import CRUDA_DIR, COLUMNAS_NUMERICAS, SCHEMA_DIR
import warnings
warnings.filterwarnings('ignore')


def cargar_schema_columnas():
    """
    Carga el schema de mapeo de columnas desde el archivo JSON.
    Permite flexibilidad para diferentes idiomas y versiones de Meta Ads.
    
    Returns:
        dict: Diccionario con mapeo de columnas normalizadas a variantes
    """
    schema_path = f"{SCHEMA_DIR}/columnas.json"
    
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
            # Remover claves de metadatos
            return {k: v for k, v in schema.items() if not k.startswith('_')}
    
    # Fallback si no existe el archivo
    print("  [AVISO] No se encontró schema/columnas.json, usando mapeo básico")
    return {}


def normalizar_columnas(df):
    """
    Renombra columnas de Meta Ads al formato interno estándar.
    Usa el schema JSON para máxima flexibilidad.
    
    Args:
        df: DataFrame con columnas originales de Meta Ads
        
    Returns:
        DataFrame con columnas normalizadas
    """
    schema = cargar_schema_columnas()
    mapping = {}
    
    for col in df.columns:
        col_clean = col.strip()
        
        # Buscar en el schema JSON
        for nombre_normalizado, variantes in schema.items():
            if col_clean in variantes:
                mapping[col] = nombre_normalizado
                break
        
        # Si no está en el schema, intentar detección heurística
        if col not in mapping:
            col_lower = col_clean.lower()
            
            # Detectar gasto
            if any(x in col_lower for x in ['gasto', 'spent', 'spend', 'importe']):
                mapping[col] = 'spend'
            # Detectar resultados
            elif col_lower in ['resultados', 'results', 'result']:
                mapping[col] = 'results'
            # Detectar clics
            elif 'clic' in col_lower and 'enlace' in col_lower:
                mapping[col] = 'link_clicks'
            elif col_lower in ['clics', 'clicks']:
                mapping[col] = 'link_clicks'
    
    df = df.rename(columns=mapping)
    return df


def asegurar_columnas(df):
    """
    Asegura que todas las columnas numéricas necesarias existan.
    Crea columnas faltantes con valor 0.
    
    Args:
        df: DataFrame a completar
        
    Returns:
        DataFrame con todas las columnas necesarias
    """
    for col in COLUMNAS_NUMERICAS:
        if col not in df.columns:
            df[col] = 0
    
    # Asegurar columna de nombre de anuncio
    if 'ad_name' not in df.columns:
        # Buscar alternativas
        for alt in ['nombre', 'name', 'anuncio']:
            for col in df.columns:
                if alt in col.lower():
                    df['ad_name'] = df[col]
                    break
        
        # Si todavía no existe, crear una genérica
        if 'ad_name' not in df.columns:
            df['ad_name'] = [f"Anuncio_{i}" for i in range(len(df))]
    
    return df


def convertir_numericos(df):
    """
    Convierte columnas numéricas al tipo correcto.
    Maneja valores no numéricos, porcentajes y formatos especiales.
    
    Args:
        df: DataFrame a convertir
        
    Returns:
        DataFrame con tipos numéricos correctos
    """
    for col in COLUMNAS_NUMERICAS:
        if col in df.columns:
            # Manejar valores de porcentaje (ej: "2.5%")
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace('%', '').str.replace(',', '.')
            
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    return df


def detectar_tipo_archivo(filepath):
    """
    Detecta el tipo de dataset según el nombre del archivo.
    
    Tipos soportados:
        - 7d: Últimos 7 días (tendencia inmediata)
        - 30d: Últimos 30 días (rendimiento reciente)
        - mes: Datos históricos mensuales
    
    Args:
        filepath: Ruta al archivo
        
    Returns:
        tuple: (tipo, periodo) ej: ('7d', '7d') o ('mes', 'sep')
    """
    nombre = os.path.basename(filepath).lower()
    
    # Detectar 7 días
    if '-7d' in nombre or '_7d' in nombre:
        return ('7d', '7d')
    
    # Detectar 30 días
    if '-30d' in nombre or '_30d' in nombre:
        return ('30d', '30d')
    
    # Detectar meses
    meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 
             'jul', 'ago', 'sep', 'oct', 'nov', 'dic',
             'jan', 'feb', 'mar', 'apr', 'may', 'jun',
             'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    
    for mes in meses:
        if f'-{mes}' in nombre or f'_{mes}' in nombre:
            return ('mes', mes[:3])
    
    # Si no se detecta, asumir 30d por defecto
    return ('30d', 'default')


def cargar_archivo(filepath):
    """
    Carga un archivo Excel y aplica normalización completa.
    
    Args:
        filepath: Ruta al archivo .xlsx
        
    Returns:
        DataFrame normalizado o None si hay error
    """
    try:
        # Intentar leer con diferentes engines
        try:
            df = pd.read_excel(filepath, engine='openpyxl')
        except:
            df = pd.read_excel(filepath)
        
        # Pipeline de normalización
        df = normalizar_columnas(df)
        df = asegurar_columnas(df)
        df = convertir_numericos(df)
        
        # Agregar metadatos del archivo
        tipo, periodo = detectar_tipo_archivo(filepath)
        df['_tipo_archivo'] = tipo
        df['_periodo'] = periodo
        df['_archivo_origen'] = os.path.basename(filepath)
        
        return df
        
    except Exception as e:
        print(f"  -> Error cargando {filepath}: {e}")
        return None


def cargar_datos_cliente(cliente):
    """
    Carga todos los archivos de un cliente: 30d, 7d e históricos.
    Detecta automáticamente el tipo de cada archivo.
    
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
    
    # Buscar todos los archivos del cliente
    patron = f"{CRUDA_DIR}/{cliente}-*.xlsx"
    archivos = glob.glob(patron)
    
    if not archivos:
        # Intentar sin guión
        patron = f"{CRUDA_DIR}/{cliente}*.xlsx"
        archivos = glob.glob(patron)
    
    print(f"  -> Archivos encontrados: {len(archivos)}")
    
    hist_list = []
    
    for filepath in archivos:
        tipo, periodo = detectar_tipo_archivo(filepath)
        df = cargar_archivo(filepath)
        
        if df is None:
            continue
            
        if tipo == '7d':
            data['7d'] = df
            print(f"     [7D] {os.path.basename(filepath)}: {len(df)} anuncios")
            
        elif tipo == '30d':
            data['30d'] = df
            print(f"     [30D] {os.path.basename(filepath)}: {len(df)} anuncios")
            
        elif tipo == 'mes':
            df['periodo'] = periodo
            hist_list.append(df)
            print(f"     [HIST-{periodo.upper()}] {os.path.basename(filepath)}: {len(df)} anuncios")
    
    # Combinar históricos
    if hist_list:
        data['historico'] = pd.concat(hist_list, ignore_index=True)
    
    return data


def identificar_clientes():
    """
    Escanea la carpeta crudo/ para identificar clientes disponibles.
    
    Returns:
        Lista ordenada de nombres de cliente únicos
    """
    archivos = glob.glob(f"{CRUDA_DIR}/*.xlsx")
    clientes = set()
    
    for f in archivos:
        nombre_base = os.path.basename(f)
        # Extraer nombre del cliente (antes del primer guión o guión bajo)
        match = re.match(r'^([A-Za-z0-9]+)', nombre_base)
        if match:
            clientes.add(match.group(1))
    
    return sorted(list(clientes))
