export interface Anuncio {
  nombre: string
  score: number
  cpa: number | null
  gasto: number
  eficiencia: "MUY_EFICIENTE" | "EFICIENTE" | "NORMAL" | "CARO" | "SIN_DATOS"
  actividad: "ACTIVO" | "GASTANDO" | "INACTIVO" | "SIN_DATOS_7D"
  score_7d: number
  gasto_7d: number
}

export interface CandidatoDuplicar {
  nombre: string
  score: number
  cpa: number
  gasto: number
  actividad: string
  razones: string[]
  acciones: string[]
}

export interface AccionUrgente {
  tipo: "PAUSAR" | "REVISAR"
  nombre: string
  razon: string
  accion: string
}

export interface HistoricoMes {
  periodo: string
  score: number
}

export interface Resumen {
  gasto_total: number
  score_total: number
  cpa_global: number
  total_anuncios: number
  con_conversiones: number
  actividad: {
    activos: number
    gastando: number
    inactivos: number
    sin_datos_7d: number
  }
}

export interface RankingItem {
  ad_name: string
  score: number
  cpa: number | null
  spend: number
  actividad: string
  eficiencia?: string
}

/* --------------------------
   GLOSARIO TIPOS REALES
--------------------------- */

export interface GlosarioEntry {
  nombre: string
  descripcion: string
  interpretacion?: string
  categorias?: Record<string, string>
}

export type Glosario = Record<string, GlosarioEntry>

/* --------------------------
       REPORT DATA
--------------------------- */

export interface ReportData {
  meta: {
    cliente: string
    fecha: string
    version: string
  }
  resumen: Resumen
  mediana_cpa: number
  rankings: {
    impacto: RankingItem[]
    volumen: RankingItem[]
    eficiencia: RankingItem[]
  }
  duplicar: CandidatoDuplicar[]
  acciones_urgentes: AccionUrgente[]
  anuncios: Anuncio[]
  historico: HistoricoMes[]
  glosario: Glosario
}
