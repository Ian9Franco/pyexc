"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Upload, FileJson, AlertCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { ReportData } from "@/lib/types"

interface ReportUploaderProps {
  onDataLoaded: (data: ReportData) => void
}

export function ReportUploader({ onDataLoaded }: ReportUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFile = useCallback(
    (file: File) => {
      setError(null)

      if (!file.name.endsWith(".json")) {
        setError("Por favor sube un archivo JSON")
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string) as ReportData

          // Validar estructura basica
          if (!data.meta || !data.resumen || !data.anuncios) {
            setError("El archivo JSON no tiene la estructura esperada del informe")
            return
          }

          onDataLoaded(data)
        } catch {
          setError("Error al parsear el archivo JSON")
        }
      }
      reader.readAsText(file)
    },
    [onDataLoaded],
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  return (
    <div className="flex items-center justify-center min-h-screen p-8">
      <Card className="w-full max-w-lg bg-card border-border">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-semibold text-foreground">Meta Ads Dashboard</CardTitle>
          <CardDescription className="text-muted-foreground">
            Sube el archivo JSON generado por el pipeline para visualizar el informe
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`
              relative border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer
              ${isDragging ? "border-primary bg-primary/5" : "border-border hover:border-muted-foreground"}
            `}
          >
            <input
              type="file"
              accept=".json"
              onChange={handleInputChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex flex-col items-center gap-4">
              <div
                className={`
                p-4 rounded-full transition-colors
                ${isDragging ? "bg-primary/10" : "bg-secondary"}
              `}
              >
                {isDragging ? (
                  <FileJson className="w-8 h-8 text-primary" />
                ) : (
                  <Upload className="w-8 h-8 text-muted-foreground" />
                )}
              </div>
              <div>
                <p className="font-medium text-foreground">
                  {isDragging ? "Suelta el archivo aqui" : "Arrastra tu archivo JSON"}
                </p>
                <p className="text-sm text-muted-foreground mt-1">o haz clic para seleccionar</p>
              </div>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
              <AlertCircle className="w-4 h-4 text-destructive" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          <div className="mt-6 p-4 bg-secondary/50 rounded-lg">
            <p className="text-xs text-muted-foreground">
              <strong>Tip:</strong> Ejecuta el pipeline de Python para generar el archivo
              <code className="mx-1 px-1 py-0.5 bg-background rounded text-xs">cliente-informe.json</code>
              en la carpeta de informes.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
