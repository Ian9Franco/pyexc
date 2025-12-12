import { DollarSign, Target, Users, Activity } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import type { Resumen } from "@/lib/types"

interface KpiCardsProps {
  resumen: Resumen
  medianaCpa: number
}

export function KpiCards({ resumen, medianaCpa }: KpiCardsProps) {
  const { activos, gastando, inactivos } = resumen.actividad

  const kpis = [
    {
      label: "Gasto Total",
      value: `$${resumen.gasto_total.toLocaleString("es-AR", { maximumFractionDigits: 0 })}`,
      sublabel: "ARS en 30 días",
      icon: DollarSign,
      color: "text-primary",
    },
    {
      label: "CPA Promedio",
      value: `$${resumen.cpa_global.toLocaleString("es-AR", { maximumFractionDigits: 0 })}`,
      sublabel: `Mediana: $${medianaCpa.toLocaleString("es-AR", { maximumFractionDigits: 0 })}`,
      icon: Target,
      color: "text-warning",
    },
    {
      label: "Score Total",
      value: resumen.score_total.toFixed(1),
      sublabel: `${resumen.con_conversiones} de ${resumen.total_anuncios} anuncios convirtieron`,
      icon: Users,
      color: "text-success",
    },
    {
      label: "Actividad (7 días)",
      value: `${activos} activos`,
      sublabel: `${gastando} gastando, ${inactivos} inactivos`,
      icon: Activity,
      color: activos > gastando ? "text-success" : "text-warning",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi, i) => (
        <Card key={i} className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{kpi.label}</p>
                <p className="text-2xl font-semibold mt-1 text-foreground">{kpi.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{kpi.sublabel}</p>
              </div>
              <div className={`p-2 rounded-lg bg-secondary ${kpi.color}`}>
                <kpi.icon className="w-5 h-5" />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
