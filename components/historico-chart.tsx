"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import type { HistoricoMes } from "@/lib/types"

interface HistoricoChartProps {
  historico: HistoricoMes[]
}

export function HistoricoChart({ historico }: HistoricoChartProps) {
  if (historico.length === 0) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Contexto Historico</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-muted-foreground">
            <p>No hay datos historicos disponibles.</p>
            <p className="text-sm mt-1">Agrega archivos con sufijos de mes (ej: cliente-sep.xlsx, cliente-oct.xlsx)</p>
            <p className="text-sm mt-1">Funciona con cualquier mes: -ene, -feb, -mar, -abr, -may, -jun, etc.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const scores = historico.map((h) => h.score)
  const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length
  const maxScore = Math.max(...scores)
  const minScore = Math.min(...scores)

  // Calcular tendencia
  const primerScore = historico[0]?.score || 0
  const ultimoScore = historico[historico.length - 1]?.score || 0
  const cambio = primerScore > 0 ? ((ultimoScore - primerScore) / primerScore) * 100 : 0

  const tendenciaIcon =
    cambio > 10 ? (
      <TrendingUp className="w-5 h-5 text-success" />
    ) : cambio < -10 ? (
      <TrendingDown className="w-5 h-5 text-danger" />
    ) : (
      <Minus className="w-5 h-5 text-warning" />
    )

  const tendenciaTexto =
    cambio > 10
      ? `Mejora de ${cambio.toFixed(0)}%`
      : cambio < -10
        ? `Caída de ${Math.abs(cambio).toFixed(0)}%`
        : "Estable"

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Score Total por Período</CardTitle>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-secondary rounded-full">
            {tendenciaIcon}
            <span className="text-sm font-medium">{tendenciaTexto}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={historico} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="periodo" stroke="#a1a1aa" tick={{ fill: "#a1a1aa" }} />
              <YAxis stroke="#a1a1aa" tick={{ fill: "#a1a1aa" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#141416",
                  border: "1px solid #27272a",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "#fafafa" }}
                formatter={(value: number) => [`${value.toFixed(1)}`, "Score"]}
              />
              {/* Línea de promedio */}
              <ReferenceLine y={avgScore} stroke="#3b82f6" strokeDasharray="5 5" label="" />
              <Bar dataKey="score" radius={[4, 4, 0, 0]} name="Score">
                {historico.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={
                      entry.score > avgScore * 1.1 ? "#22c55e" : entry.score < avgScore * 0.9 ? "#ef4444" : "#3b82f6"
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Resumen */}
        <div className="mt-4 grid grid-cols-3 gap-4 text-center">
          <div className="p-3 bg-secondary rounded-lg">
            <p className="text-xs text-muted-foreground">Promedio</p>
            <p className="text-lg font-semibold text-foreground">{avgScore.toFixed(1)}</p>
          </div>
          <div className="p-3 bg-success/10 rounded-lg">
            <p className="text-xs text-muted-foreground">Mejor</p>
            <p className="text-lg font-semibold text-success">{maxScore.toFixed(1)}</p>
          </div>
          <div className="p-3 bg-danger/10 rounded-lg">
            <p className="text-xs text-muted-foreground">Peor</p>
            <p className="text-lg font-semibold text-danger">{minScore.toFixed(1)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
