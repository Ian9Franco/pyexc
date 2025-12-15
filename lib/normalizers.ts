import type { Anuncio } from "@/lib/types"

export function normalizarAnuncios(raw: any[]): Anuncio[] {
  return raw.map((a, idx) => ({
    nombre:
      a.nombre ??
      a.ad_name ??
      a["Nombre del anuncio"] ??
      `Anuncio ${idx + 1}`,

    gasto:
      typeof a.gasto === "number"
        ? a.gasto
        : typeof a.spend === "number"
          ? a.spend
          : 0,

    cpa: typeof a.cpa === "number" ? a.cpa : null,

    score: Number(a.score ?? 0),
    score_7d: Number(a.score_7d ?? 0),
    gasto_7d: Number(a.gasto_7d ?? 0),

    eficiencia: a.eficiencia ?? "SIN_DATOS",
    actividad: a.actividad ?? "SIN_DATOS_7D",
  }))
}
