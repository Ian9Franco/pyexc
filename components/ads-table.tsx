"use client"

import { useState } from "react"
import { ArrowUpDown, Activity, Zap, PauseCircle, AlertCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { Anuncio } from "@/lib/types"

interface AdsTableProps {
  anuncios: Anuncio[]
  medianaCpa: number
}

type SortKey = "score" | "cpa" | "gasto" | "score_7d"

export function AdsTable({ anuncios, medianaCpa }: AdsTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("score")
  const [sortAsc, setSortAsc] = useState(false)

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc)
    } else {
      setSortKey(key)
      setSortAsc(false)
    }
  }

  const sorted = [...anuncios].sort((a, b) => {
    let aVal = a[sortKey] ?? 0
    let bVal = b[sortKey] ?? 0

    if (sortKey === "cpa") {
      aVal = a.cpa ?? 999999
      bVal = b.cpa ?? 999999
    }

    return sortAsc ? aVal - bVal : bVal - aVal
  })

  const actividadIcon = {
    ACTIVO: <Activity className="w-4 h-4 text-success" />,
    GASTANDO: <Zap className="w-4 h-4 text-warning" />,
    INACTIVO: <PauseCircle className="w-4 h-4 text-muted-foreground" />,
    SIN_DATOS_7D: <AlertCircle className="w-4 h-4 text-muted-foreground" />,
  }

  const eficienciaColor = {
    MUY_EFICIENTE: "text-success",
    EFICIENTE: "text-success",
    NORMAL: "text-foreground",
    CARO: "text-danger",
    SIN_DATOS: "text-muted-foreground",
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle>Todos los Anuncios ({anuncios.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Nombre</th>
                {[
                  { key: "score", label: "Score" },
                  { key: "cpa", label: "CPA" },
                  { key: "gasto", label: "Gasto" },
                  { key: "score_7d", label: "Score 7d" },
                ].map((col) => (
                  <th key={col.key} className="text-right py-3 px-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleSort(col.key as SortKey)}
                      className={`text-sm font-medium ${sortKey === col.key ? "text-primary" : "text-muted-foreground"}`}
                    >
                      {col.label}
                      <ArrowUpDown className="w-3 h-3 ml-1" />
                    </Button>
                  </th>
                ))}
                <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">Eficiencia</th>
                <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">Actividad</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((ad) => (
                <tr key={ad.nombre} className="border-b border-border/50 hover:bg-secondary/30 transition-colors">
                  <td className="py-3 px-4">
                    <p className="font-medium text-foreground truncate max-w-xs" title={ad.nombre}>
                      {ad.nombre}
                    </p>
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-foreground">{ad.score.toFixed(1)}</td>
                  <td
                    className={`py-3 px-4 text-right font-mono ${
                      ad.cpa && ad.cpa <= medianaCpa
                        ? "text-success"
                        : ad.cpa && ad.cpa > medianaCpa * 1.5
                          ? "text-danger"
                          : "text-foreground"
                    }`}
                  >
                    {ad.cpa ? `$${ad.cpa.toLocaleString("es-AR", { maximumFractionDigits: 0 })}` : "N/A"}
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-foreground">
                    ${ad.gasto.toLocaleString("es-AR", { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-muted-foreground">{ad.score_7d.toFixed(1)}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-center">
                      <Badge variant="outline" className={`text-xs ${eficienciaColor[ad.eficiencia]}`}>
                        {ad.eficiencia.replace("_", " ")}
                      </Badge>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-center gap-2">
                      {actividadIcon[ad.actividad]}
                      <span className="text-xs text-muted-foreground">{ad.actividad}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
