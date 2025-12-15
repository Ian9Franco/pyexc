"use client"

import { useState } from "react"
import {
  ArrowLeft,
  HelpCircle,
  Activity,
  Zap,
  PauseCircle,
  TrendingUp,
  AlertTriangle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { KpiCards } from "@/components/kpi-cards"
import { RankingTabs } from "@/components/ranking-tabs"
import { ActionCards } from "@/components/action-cards"
import { AdsTable } from "@/components/ads-table"
import { HistoricoChart } from "@/components/historico-chart"
import { GlosarioDialog } from "@/components/glosario-dialog"
import type { ReportData } from "@/lib/types"

interface DashboardProps {
  data: ReportData
  onReset: () => void
}

export function Dashboard({ data, onReset }: DashboardProps) {
  const [showGlosario, setShowGlosario] = useState(false)

  const actividad = data.resumen?.actividad ?? {
    activos: 0,
    gastando: 0,
    inactivos: 0,
  }

  const { activos, gastando, inactivos } = actividad

  const tieneHistorico = Array.isArray(data.historico) && data.historico.length > 0

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={onReset}>
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div>
              <h1 className="text-xl font-semibold text-foreground">
                {data.meta?.cliente ?? "Cliente"}
              </h1>
              <p className="text-sm text-muted-foreground">
                Reporte del {data.meta?.fecha_generacion}

              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 px-3 py-1.5 bg-card rounded-full border border-border">
              <div className="flex items-center gap-1">
                <Activity className="w-4 h-4 text-success" />
                <span className="text-sm font-mono text-success">{activos}</span>
              </div>
              <div className="flex items-center gap-1">
                <Zap className="w-4 h-4 text-warning" />
                <span className="text-sm font-mono text-warning">{gastando}</span>
              </div>
              <div className="flex items-center gap-1">
                <PauseCircle className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm font-mono text-muted-foreground">{inactivos}</span>
              </div>
            </div>

            <Button variant="outline" size="sm" onClick={() => setShowGlosario(true)}>
              <HelpCircle className="w-4 h-4 mr-2" />
              Glosario
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <KpiCards resumen={data.resumen} medianaCpa={data.mediana_cpa} />

        <Tabs defaultValue="rankings" className="mt-8">
          <TabsList className="bg-card border border-border">
            <TabsTrigger value="rankings">Rankings</TabsTrigger>
            <TabsTrigger value="acciones">Acciones</TabsTrigger>
            <TabsTrigger value="anuncios">Todos los Anuncios</TabsTrigger>
            {tieneHistorico && <TabsTrigger value="historico">Histórico</TabsTrigger>}
          </TabsList>

          <TabsContent value="rankings" className="mt-6">
            <RankingTabs rankings={data.rankings} medianaCpa={data.mediana_cpa} />
          </TabsContent>

          <TabsContent value="acciones" className="mt-6">
            <ActionCards
              duplicar={data.duplicar}
              urgentes={data.acciones_urgentes}
              medianaCpa={data.mediana_cpa}
            />
          </TabsContent>

          <TabsContent value="anuncios" className="mt-6">
            <AdsTable anuncios={data.anuncios} medianaCpa={data.mediana_cpa} />
          </TabsContent>

          {tieneHistorico && (
            <TabsContent value="historico" className="mt-6">
              <HistoricoChart historico={data.historico} />
            </TabsContent>
          )}
        </Tabs>
      </div>

      <GlosarioDialog
        open={showGlosario}
        onOpenChange={setShowGlosario}
        glosario={data.glosario}
      />
    </div>
  )
}
