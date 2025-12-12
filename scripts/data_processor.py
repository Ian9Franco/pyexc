import pandas as pd
import glob
import os
from config import META_COLS, COLUMNAS_CLAVE, CRUDA_DIR, LIMPIOS_DIR
import warnings
warnings.filterwarnings('ignore')


def normalizar_columnas(df):
    """
    Renombra columnas al formato interno estándar (spend, results, etc.)
    """
    mapping = {}

    for col in df.columns:
        col_clean = col.strip()

        # Buscar coincidencias exactas
        if col_clean in META_COLS:
            mapping[col] = META_COLS[col_clean]

        # Buscar columnas de gasto aunque vengan con variaciones
        elif "Importe gastado" in col_clean:
            mapping[col] = "spend"

        # Resultados
        elif "Resultado" in col_clean:
            mapping[col] = "results"

        # Clics
        elif "Clics" in col_clean:
            mapping[col] = "link_clicks"

    df = df.rename(columns=mapping)
    return df


def limpiar_y_enriquecer(df):
    """
    Limpia, normaliza y calcula métricas nuevas.
    """

    df = normalizar_columnas(df)

    # Asegurar columnas mínimas
    for newcol in META_COLS.values():
        if newcol not in df.columns:
            df[newcol] = 0

    # Convertir numéricos
    numeric_cols = ["spend", "results", "msg_init", "msg_contacts",
                    "ig_profile", "link_clicks"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Eventos de alto valor (peso 1.0): results, msg_init, msg_contacts
    # Eventos de menor valor: link_clicks (0.15), ig_profile (0.3)
    df["conv_count"] = (
        df["results"] * 1.0 +
        df["msg_init"] * 1.0 +
        df["msg_contacts"] * 1.0 +
        df["link_clicks"] * 0.15 +
        df["ig_profile"] * 0.3
    )

    # Score estratégico
    def score_row(r):
        obj = str(r["objective"]).lower()
        plc = str(r["placement"]).lower()

        # Prioridad: Leads / ventas
        if any(k in obj for k in ["lead", "venta", "conversion"]):
            return 4
        # Contacto directo (mensajes)
        if any(k in obj for k in ["mensaje", "messaging"]):
            return 3
        # Clics / tráfico
        if any(k in obj for k in ["clic", "traffic"]):
            return 2
        # Awareness
        return 1

    df["conversion_score"] = df.apply(score_row, axis=1)
    df["conv_weighted"] = df["conversion_score"] * df["conv_count"]

    # Esto permite que la mediana ignore anuncios sin conversiones
    def calc_cpa(r):
        if r["conv_count"] > 0:
            return r["spend"] / r["conv_count"]
        return None  # None en lugar de 0 para anuncios sin conversiones
    
    df["cpa"] = df.apply(calc_cpa, axis=1)

    return df


def cargar_y_limpiar_cliente(cliente):
    """
    Devuelve df_30, df_7 y df_hist normalizados.
    """

    data = {'30d': pd.DataFrame(), '7d': pd.DataFrame(), 'historico': pd.DataFrame()}

    for dias in ["30d", "7d"]:
        fpath = f"{CRUDA_DIR}/{cliente}-{dias}.xlsx"
        print(f"  -> Buscando archivo: {fpath}")

        if os.path.exists(fpath):
            df = pd.read_excel(fpath)
            data[dias] = limpiar_y_enriquecer(df)


    # Cargar históricos (sep, oct, nov…)
    hist_files = glob.glob(f"{CRUDA_DIR}/{cliente}-*.xlsx")
    hist_files = [f for f in hist_files if not any(x in f for x in ["30d", "7d"])]

    hist_list = []
    for f in hist_files:
        df = pd.read_excel(f)
        df = limpiar_y_enriquecer(df)
        df["Origen"] = os.path.basename(f).split("-")[-1].split(".")[0]
        hist_list.append(df)

    if hist_list:
        data["historico"] = pd.concat(hist_list, ignore_index=True)

    return data


def guardar_limpios(cliente, data):
    for key, df in data.items():
        if not df.empty:
            df.to_excel(f"{LIMPIOS_DIR}/{cliente}-{key}-clean.xlsx", index=False)
