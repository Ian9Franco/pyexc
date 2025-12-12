import { Trophy, DollarSign, Zap } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { ReportData, RankingItem } from "@/lib/types"

interface RankingTabsProps {
  rankings: ReportData["rankings"]
  medianaCpa: number
}

function RankingList({ items, tipo, medianaCpa }: { items: RankingItem[]; tipo: string; medianaCpa: number }) {
  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={item.ad_name} className="flex items-center gap-4 p-4 bg-secondary/50 rounded-lg border border-border">
          <div
            className={`
            w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm
            ${
              i === 0
                ? "bg-yellow-500/20 text-yellow-500"
                : i === 1
                  ? "bg-gray-400/20 text-gray-400"
                  : i === 2
                    ? "bg-orange-600/20 text-orange-600"
                    : "bg-secondary text-muted-foreground"
            }
          `}
          >
            {i + 1}
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-foreground truncate">{item.ad_name}</p>
            <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
              <span>Score: {item.score.toFixed(1)}</span>
              {item.cpa && (
                <span className={item.cpa <= medianaCpa ? "text-success" : "text-danger"}>
                  CPA: ${item.cpa.toLocaleString("es-AR", { maximumFractionDigits: 0 })}
                </span>
              )}
              {item.actividad && (
                <Badge variant="outline" className="text-xs">
                  {item.actividad}
                </Badge>
              )}
            </div>
          </div>
          {tipo === "volumen" && (
            <div className="text-right">
              <p className="font-mono text-foreground">
                ${item.spend.toLocaleString("es-AR", { maximumFractionDigits: 0 })}
              </p>
            </div>
          )}
          {tipo === "eficiencia" && item.cpa && (
            <div className="text-right">
              <p className={`font-mono ${item.cpa <= medianaCpa ? "text-success" : "text-foreground"}`}>
                ${item.cpa.toLocaleString("es-AR", { maximumFractionDigits: 0 })}
              </p>
              <p className="text-xs text-muted-foreground">{((item.cpa / medianaCpa) * 100).toFixed(0)}% de mediana</p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export function RankingTabs({ rankings, medianaCpa }: RankingTabsProps) {
  const tabs = [
    { id: "impacto", label: "Impacto", icon: Trophy, data: rankings.impacto },
    { id: "volumen", label: "Volumen", icon: DollarSign, data: rankings.volumen },
    { id: "eficiencia", label: "Eficiencia", icon: Zap, data: rankings.eficiencia },
  ]

  return (
    <Tabs defaultValue="impacto">
      <TabsList className="bg-card border border-border">
        {tabs.map((tab) => (
          <TabsTrigger key={tab.id} value={tab.id} className="gap-2">
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>

      {tabs.map((tab) => (
        <TabsContent key={tab.id} value={tab.id} className="mt-4">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <tab.icon className="w-5 h-5 text-primary" />
                Top 5 por {tab.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {tab.data && tab.data.length > 0 ? (
                <RankingList items={tab.data} tipo={tab.id} medianaCpa={medianaCpa} />
              ) : (
                <p className="text-muted-foreground text-center py-8">No hay datos suficientes para este ranking</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      ))}
    </Tabs>
  )
}
