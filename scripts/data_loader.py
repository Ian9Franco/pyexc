"""
Módulo de carga de datos V4 – FIX DEFINITIVO
- Corrige error df.dtype
- Soporta columnas mal definidas
- Robusto ante Excel sucio de Meta
"""

import pandas as pd
import glob
import os
import json
import re
from pathlib import Path
from config import CRUDA_DIR, COLUMNAS_NUMERICAS, SCHEMA_DIR
from pandas.api.types import is_numeric_dtype
import warnings

warnings.filterwarnings("ignore")
print(">>> DATA_LOADER V4 FIX DEFINITIVO CARGADO <<<")

# -----------------------------------------------------------------------------
# SCHEMA
# -----------------------------------------------------------------------------

def cargar_schema_columnas():
    schema_path = Path(SCHEMA_DIR) / "columnas.json"

    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
            return {k: v for k, v in schema.items() if not k.startswith("_")}

    print("  [AVISO] No se encontró schema/columnas.json, usando mapeo básico")
    return {}

# -----------------------------------------------------------------------------
# NORMALIZACIÓN
# -----------------------------------------------------------------------------

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    schema = cargar_schema_columnas()
    mapping = {}

    for col in df.columns:
        col_clean = str(col).strip()

        for nombre_normalizado, variantes in schema.items():
            if col_clean in variantes:
                mapping[col] = nombre_normalizado
                break

        if col not in mapping:
            col_lower = col_clean.lower()

            if any(x in col_lower for x in ["gasto", "spent", "spend", "importe"]):
                mapping[col] = "spend"
            elif col_lower in ["resultados", "results", "result"]:
                mapping[col] = "results"
            elif "clic" in col_lower and "enlace" in col_lower:
                mapping[col] = "link_clicks"
            elif col_lower in ["clics", "clicks"]:
                mapping[col] = "link_clicks"

    return df.rename(columns=mapping)

def asegurar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    for col in COLUMNAS_NUMERICAS:
        if isinstance(col, str) and col not in df.columns:
            df[col] = 0

    if "ad_name" not in df.columns:
        for c in df.columns:
            if any(x in c.lower() for x in ["nombre", "name", "anuncio"]):
                df["ad_name"] = df[c]
                break

    if "ad_name" not in df.columns:
        df["ad_name"] = [f"Anuncio_{i}" for i in range(len(df))]

    return df

def convertir_numericos(df: pd.DataFrame) -> pd.DataFrame:
    """
    FIX CLAVE:
    - Evita df[col].dtype cuando col no es Serie
    - Convierte solo Series válidas
    """

    for col in COLUMNAS_NUMERICAS:
        if not isinstance(col, str):
            continue

        if col not in df.columns:
            continue

        serie = df[col]

        # Si por error vino como DataFrame (defensa extra)
        if isinstance(serie, pd.DataFrame):
            serie = serie.iloc[:, 0]

        if not is_numeric_dtype(serie):
            serie = (
                serie.astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", ".", regex=False)
            )

        df[col] = pd.to_numeric(serie, errors="coerce").fillna(0)

    return df

# -----------------------------------------------------------------------------
# ARCHIVOS
# -----------------------------------------------------------------------------

def detectar_tipo_archivo(filepath):
    filename = os.path.basename(filepath).lower()

    if re.search(r"[-_]30d\b", filename):
        return "30d", "30d"
    if re.search(r"[-_]7d\b", filename):
        return "7d", "7d"

    match_mes = re.search(r"[-_](ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\b", filename)
    if match_mes:
        return "mes", match_mes.group(1)

    return "otro", "n/a"

def cargar_archivo(filepath):
    try:
        df = pd.read_excel(filepath)

        df = normalizar_columnas(df)
        df = asegurar_columnas(df)
        df = convertir_numericos(df)

        tipo, periodo = detectar_tipo_archivo(filepath)
        df["_tipo_archivo"] = tipo
        df["_periodo"] = periodo
        df["_archivo_origen"] = os.path.basename(filepath)

        nombre_archivo = os.path.basename(filepath).lower()
        df["manager"] = "Ian" if "ian" in nombre_archivo else "General"

        return df

    except Exception as e:
        print(f"  -> Error cargando {filepath}: {e}")
        return None

# -----------------------------------------------------------------------------
# CLIENTES
# -----------------------------------------------------------------------------

def cargar_datos_cliente(cliente):
    data = {"30d": None, "7d": None, "historico": None}
    print("[1/8] Cargando datos...")

    cliente_regex = re.compile(cliente, re.IGNORECASE)
    archivos = []

    for ext in ("*.xlsx", "*.xlxs"):
        for f in glob.glob(os.path.join(CRUDA_DIR, ext)):
            if cliente_regex.search(os.path.basename(f)):
                archivos.append(f)

    archivos = list(set(archivos))
    print(f"  -> Archivos encontrados: {len(archivos)}")

    hist = []

    for filepath in archivos:
        tipo, periodo = detectar_tipo_archivo(filepath)
        df = cargar_archivo(filepath)

        if df is None:
            continue

        if tipo == "30d":
            data["30d"] = df
            print(f"     [30D] {os.path.basename(filepath)} ({len(df)})")
        elif tipo == "7d":
            data["7d"] = df
            print(f"     [7D] {os.path.basename(filepath)} ({len(df)})")
        elif tipo == "mes":
            df["periodo"] = periodo
            hist.append(df)
            print(f"     [HIST-{periodo.upper()}] {os.path.basename(filepath)} ({len(df)})")

    if data["30d"] is None:
        raise RuntimeError("No se encontraron datos válidos de 30 días")

    if hist:
        data["historico"] = pd.concat(hist, ignore_index=True)

    return data

def identificar_clientes():
    archivos = glob.glob(os.path.join(CRUDA_DIR, "*.xlsx")) + glob.glob(
        os.path.join(CRUDA_DIR, "*.xlxs")
    )

    clientes = set()
    for f in archivos:
        nombre = os.path.splitext(os.path.basename(f))[0]
        cliente = re.split(r"[-_]", nombre)[0].upper().strip()
        if len(cliente) > 2:
            clientes.add(cliente)

    return sorted(clientes)
