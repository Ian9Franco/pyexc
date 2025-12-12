import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import type { Glosario } from "@/lib/types"

interface GlosarioDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  glosario: Glosario
}

export function GlosarioDialog({ open, onOpenChange, glosario }: GlosarioDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-card border-border max-w-lg">
        <DialogHeader>
          <DialogTitle>Glosario de Términos</DialogTitle>
          <DialogDescription>Explicación de las métricas usadas en el informe</DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {Object.entries(glosario).map(([key, entry]) => (
            <div key={key} className="p-3 bg-secondary/50 rounded-lg">
              <p className="font-semibold text-foreground capitalize">{entry.nombre}</p>
              <p className="text-sm text-muted-foreground mt-1">{entry.descripcion}</p>

              {entry.interpretacion && (
                <p className="text-sm text-accent-foreground mt-1">{entry.interpretacion}</p>
              )}

              {entry.categorias && (
                <ul className="list-disc pl-4 text-xs mt-1 text-muted-foreground">
                  {Object.entries(entry.categorias).map(([k, v]) => (
                    <li key={k}>{k}: {v}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}
