import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { DollarSign, Target, Gauge, Users } from "lucide-react"
import { Badge } from "@/components/ui/badge"

// NOTA: Asumiendo que tienes un archivo types.ts o ReportData en algún lugar que defina ReportData
// Si no, puedes definir el tipo de datos aquí:
type ManagerMetrics = {
  gasto: number
  conversiones: number // Score total
  cpa_real: number
  calidad_promedio: number // Score 0-100 promedio
  cant_anuncios: number
}

// Interfaz para el objeto que viene del JSON: {"Ian": {...}, "General": {...}}
interface ComparativaManagers {
  Ian: ManagerMetrics
  General: ManagerMetrics
  [key: string]: ManagerMetrics // Permite otros managers
}
// ----------------------------------------------------------------------------------

interface ManagerComparisonProps {
  data: ComparativaManagers
}

export function ManagerComparison({ data }: ManagerComparisonProps) {
  const managers = Object.keys(data)
  
  if (managers.length < 2 || !data.Ian || !data.General) {
    // Solo mostrar si tenemos data para Ian Y General
    return null 
  }

  const ianData = data.Ian
  const generalData = data.General
  
  // Lógica para determinar la tendencia de CPA
  const cpaIan = ianData.cpa_real
  const cpaGeneral = generalData.cpa_real
  let cpaDiff: number = 0
  let cpaTrend: 'MEJOR' | 'PEOR' | 'IGUAL' = 'IGUAL'
  let cpaBadgeVariant: 'success' | 'destructive' | 'outline' = 'outline'
  
  if (cpaIan > 0 && cpaGeneral > 0) {
    if (cpaIan < cpaGeneral * 0.95) { // Si Ian es 5% mejor
      cpaDiff = ((cpaGeneral - cpaIan) / cpaGeneral) * 100
      cpaTrend = 'MEJOR'
      cpaBadgeVariant = 'success'
    } else if (cpaIan > cpaGeneral * 1.05) { // Si Ian es 5% peor
      cpaDiff = ((cpaIan - cpaGeneral) / cpaGeneral) * 100
      cpaTrend = 'PEOR'
      cpaBadgeVariant = 'destructive'
    }
  }

  // Helpers de formato
  const formatMoney = (n: number) => `$${n.toLocaleString("es-AR", { maximumFractionDigits: 0 })}`
  const formatScore = (n: number) => n.toFixed(1)
  const formatPercent = (n: number) => `${n.toFixed(1)}%`

  return (
    <Card className="bg-card border-border mt-8">
      <CardHeader>
        <CardTitle className="text-xl">
          Rendimiento por Gestión (Ian vs General)
        </CardTitle>
        <CardDescription>
          Métricas clave comparando las campañas etiquetadas con "-ian-" vs el resto de la cuenta.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Encabezados de la Tabla */}
        <div className="grid grid-cols-2 gap-4 border-b border-border pb-4 text-sm font-semibold text-muted-foreground">
          <div className="pl-4">MÉTRICA</div>
          <div className="grid grid-cols-2 text-center">
            <div>Ian ({ianData.cant_anuncios} Anuncios)</div>
            <div>General ({generalData.cant_anuncios} Anuncios)</div>
          </div>
        </div>
        
        {/* Fila: Gasto */}
        <div className="grid grid-cols-2 gap-4 items-center py-3 border-b border-border/50">
          <div className="flex items-center gap-2 pl-4 text-sm font-medium"><DollarSign className="w-4 h-4 text-primary" /> Gasto Total</div>
          <div className="grid grid-cols-2 text-center text-foreground font-mono">
            <div>{formatMoney(ianData.gasto)}</div>
            <div>{formatMoney(generalData.gasto)}</div>
          </div>
        </div>
        
        {/* Fila: Score / Conversiones */}
        <div className="grid grid-cols-2 gap-4 items-center py-3 border-b border-border/50">
          <div className="flex items-center gap-2 pl-4 text-sm font-medium"><Users className="w-4 h-4 text-success" /> Conversiones (Score)</div>
          <div className="grid grid-cols-2 text-center text-foreground font-mono">
            <div>{formatScore(ianData.conversiones)}</div>
            <div>{formatScore(generalData.conversiones)}</div>
          </div>
        </div>

        {/* Fila: CPA Real */}
        <div className="grid grid-cols-2 gap-4 items-center py-3 border-b border-border/50">
          <div className="flex items-center gap-2 pl-4 text-sm font-medium"><Target className="w-4 h-4 text-warning" /> CPA Real</div>
          <div className="grid grid-cols-2 text-center text-foreground font-mono">
            <div className={`font-semibold ${cpaTrend === 'MEJOR' ? 'text-success' : cpaTrend === 'PEOR' ? 'text-destructive' : 'text-foreground'}`}>
              {cpaIan > 0 ? formatMoney(cpaIan) : "N/A"}
            </div>
            <div>
              {cpaGeneral > 0 ? formatMoney(cpaGeneral) : "N/A"}
            </div>
          </div>
        </div>

        {/* Fila: Calidad Promedio */}
        <div className="grid grid-cols-2 gap-4 items-center py-3">
          <div className="flex items-center gap-2 pl-4 text-sm font-medium"><Gauge className="w-4 h-4 text-accent-foreground" /> Calidad Promedio (0-100)</div>
          <div className="grid grid-cols-2 text-center text-foreground font-mono">
            <div>{ianData.calidad_promedio.toFixed(1)}</div>
            <div>{generalData.calidad_promedio.toFixed(1)}</div>
          </div>
        </div>
        
        {/* Conclusión / Badge */}
        {cpaTrend !== 'IGUAL' && (
          <div className="mt-4 pt-4 border-t border-border flex items-center justify-center">
            <Badge 
              variant={cpaBadgeVariant === 'success' ? 'default' : cpaBadgeVariant === 'destructive' ? 'destructive' : 'outline'} 
              className={`text-sm ${cpaBadgeVariant === 'success' ? 'bg-success/20 text-success border-success/50' : cpaBadgeVariant === 'destructive' ? 'bg-destructive/20 text-destructive border-destructive/50' : ''}`}
            >
              {cpaTrend === 'MEJOR'
                ? `✅ Gestión Ian: ${formatPercent(cpaDiff)} más eficiente en CPA.`
                : cpaTrend === 'PEOR'
                  ? `❌ Gestión Ian: ${formatPercent(cpaDiff)} menos eficiente en CPA.`
                  : 'Comparativa de CPA similar'
              }
            </Badge>
          </div>
        )}

      </CardContent>
    </Card>
  )
}