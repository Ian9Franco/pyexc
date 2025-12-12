import { Copy, AlertTriangle, Pause, CheckCircle, ArrowRight } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { CandidatoDuplicar, AccionUrgente } from "@/lib/types"

interface ActionCardsProps {
  duplicar: CandidatoDuplicar[]
  urgentes: AccionUrgente[]
  medianaCpa: number
}

export function ActionCards({ duplicar, urgentes, medianaCpa }: ActionCardsProps) {
  return (
    <div className="space-y-6">
      {/* Explicación de duplicar */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-lg bg-success/10">
              <Copy className="w-5 h-5 text-success" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">¿Qué significa &quot;Duplicar&quot; un anuncio?</h3>
              <p className="text-sm text-muted-foreground mt-1">
                <strong>No es copiar el texto o imagen.</strong> Es crear un NUEVO anuncio usando los mismos parámetros
                de segmentación del anuncio exitoso, pero con creativos frescos (nueva imagen, video o copy) que no esté
                actualmente en ninguna campaña.
              </p>
              <div className="flex flex-wrap gap-2 mt-3">
                <Badge variant="outline" className="text-xs">Escalar sin saturar</Badge>
                <Badge variant="outline" className="text-xs">Probar nuevas piezas</Badge>
                <Badge variant="outline" className="text-xs">No competir contigo mismo</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Duplicar */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-success">
              <Copy className="w-5 h-5" />
              Anuncios para Escalar
            </CardTitle>
          </CardHeader>
          <CardContent>
            {duplicar.length > 0 ? (
              <div className="space-y-4">
                {duplicar.map((ad, i) => (
                  <div key={ad.nombre} className="p-4 bg-success/5 border border-success/20 rounded-lg">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="bg-success/10 text-success border-success/30">
                            #{i + 1}
                          </Badge>
                          <span className="font-medium text-foreground truncate">{ad.nombre}</span>
                        </div>

                        {/* Métricas */}
                        <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <p className="text-muted-foreground">Score</p>
                            <p className="font-semibold text-foreground">{ad.score.toFixed(1)}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">CPA</p>
                            <p className={`font-semibold ${ad.cpa <= medianaCpa ? "text-success" : "text-foreground"}`}>
                              ${ad.cpa.toLocaleString("es-AR", { maximumFractionDigits: 0 })}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Gasto</p>
                            <p className="font-semibold text-foreground">
                              ${ad.gasto.toLocaleString("es-AR", { maximumFractionDigits: 0 })}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Actividad</p>
                            <p className="font-semibold text-foreground">{ad.actividad}</p>
                          </div>
                        </div>

                        {/* Razones */}
                        <div className="mt-3 p-2 bg-background rounded">
                          <p className="text-xs font-medium text-success mb-1">Por qué escalar:</p>
                          <ul className="text-xs text-muted-foreground space-y-0.5">
                            {ad.razones.map((razon, j) => (
                              <li key={j} className="flex items-start gap-1">
                                <ArrowRight className="w-3 h-3 mt-0.5 shrink-0" />
                                {razon}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No hay candidatos para escalar actualmente.</p>
                <p className="text-sm mt-1">Necesitan: Score {">"}= 10 + CPA {"<"}= 120% de mediana (${(medianaCpa * 1.2).toFixed(0)})</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Urgentes */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-danger">
              <AlertTriangle className="w-5 h-5" />
              Acciones Urgentes
            </CardTitle>
          </CardHeader>
          <CardContent>
            {urgentes.length > 0 ? (
              <div className="space-y-4">
                {urgentes.map((accion, i) => (
                  <div
                    key={i}
                    className={`p-4 rounded-lg border ${
                      accion.tipo === "PAUSAR"
                        ? "bg-destructive/5 border-destructive/20"
                        : "bg-warning/5 border-warning/20"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {accion.tipo === "PAUSAR" ? (
                        <Pause className="w-5 h-5 text-destructive mt-0.5" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-warning mt-0.5" />
                      )}
                      <div className="flex-1">
                        <Badge
                          variant="outline"
                          className={
                            accion.tipo === "PAUSAR"
                              ? "bg-destructive/10 text-destructive border-destructive/30"
                              : "bg-warning/10 text-warning border-warning/30"
                          }
                        >
                          {accion.tipo}
                        </Badge>
                        <p className="mt-2 text-sm font-medium text-foreground truncate">{accion.nombre}</p>
                        <p className="mt-1 text-xs text-muted-foreground">{accion.razon}</p>
                        <p className="mt-2 text-xs text-foreground bg-background p-2 rounded">
                          <strong>Acción:</strong> {accion.accion}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle className="w-12 h-12 mx-auto mb-3 text-success opacity-50" />
                <p className="text-success">Sin acciones urgentes</p>
                <p className="text-sm mt-1">Todos los anuncios están dentro de parámetros aceptables.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
