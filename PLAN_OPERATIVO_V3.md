# 📘 PLAN OPERATIVO v3.0
### Pipeline Inteligente de Análisis para Meta Ads  
**Uso interno – Ian Franco**

## 1. Propósito Maestro
Este sistema convierte archivos crudos de Meta Ads en:
- datasets limpios y estandarizados
- análisis profundos con lógica de marketing real
- recomendaciones accionables (duplicar, pausar, revisar)
- informes profesionales en PDF
- dashboards visuales para lectura rápida

El objetivo es funcionar como un analista de performance senior, eliminando cálculos erróneos y decisiones basadas en métricas superficiales.

## 2. Filosofía del Sistema
### A. Cada objetivo se evalúa según su propósito
No se castiga tráfico por no generar mensajes ni se premian interacciones irrelevantes.

### B. Ventanas temporales estratégicas
- 30 días: rendimiento estable
- 7 días: tendencia
- meses completos: contexto histórico

### C. El valor importa más que el volumen
Conversiones ponderadas por impacto.

## 3. Arquitectura del Proyecto
```
scripts/
 ├── config.py
 ├── data_loader.py
 ├── cleaner.py
 ├── metrics.py
 ├── analyzer.py
 ├── recommender.py
 ├── pdf_report.py
 ├── json_exporter.py
 └── main.py

crudo/
limpios/
informes/
dashboard/
```

## 4. Estándar de Nombres para Archivos
| Archivo | Significado |
|---------|-------------|
| Cliente-7d.xlsx | últimos 7 días |
| Cliente-30d.xlsx | últimos 30 días |
| Cliente-sep.xlsx | mes |
| Cliente-oct.xlsx | mes |
| Cliente-nov.xlsx | mes |

## 5. Lectura Inteligente de Columnas
Detección robusta de columnas aunque cambien de nombre:
- gasto, conversaciones, resultados, contactos
- visitas al perfil, clics
- impresiones, alcance
- objetivo, nombre del anuncio
- ubicación/resultados
- fechas

Columnas limpias finales:
```
mes, cliente, ad_name, adset_name, objetivo, gasto,
msg_init, results, msg_contacts, profile_visits,
link_clicks, clicks_salientes, interactions,
fecha_inicio, fecha_fin, indicador_resultado,
score, cpa, eficiencia, actividad
```

## 6. Score v3.0 (Conversión Ponderada)
| Acción | Peso |
|--------|------|
| Resultados web | 1.5 |
| Mensajes iniciados | 1.0 |
| Contactos | 1.0 |
| Perfil | 0.25 |
| Enlace | 0.15 |
| Interacciones | 0.05 |

Fórmula:
```
score = 1.5*results + 1.0*msg_init + 1.0*msg_contacts +
        0.25*profile_visits + 0.15*link_clicks +
        0.05*interactions
```

## 7. CPA Inteligente
```
cpa = gasto / score
```

## 8. Eficiencia
| Nivel | Regla |
|-------|--------|
| ⭐ Muy eficiente | CPA < 0.7×mediana |
| 🟢 Eficiente | CPA < mediana |
| 🟡 Normal | CPA < 1.5×mediana |
| 🔴 Caro | CPA > 1.5×mediana |

## 9. Actividad (7d)
| Estado | Condición |
|--------|-----------|
| ACTIVO | score_7d > 0 |
| GASTANDO | score_7d = 0 y gasto_7d > 0 |
| INACTIVO | gasto_7d = 0 |

## 10. Ventanas Temporales
- 30d: base de decisiones
- 7d: tendencia (% cambio)
- histórico: comparación mensual

## 11. Decisiones Estratégicas
### Duplicar
- score_30d ≥ 10
- cpa ≤ 1.2×mediana
- activo 7d
- tendencia ≥ 0

### Pausar
- gasto ≥ 4000
- score = 0
- gastando

### Revisar
- cpa > 2×mediana
- score > 0

## 12. Rankings en el Informe
- top por score
- top por CPA
- top por inversión
- peores anuncios

## 13. Informe PDF
Debe incluir:
- portada
- resumen ejecutivo
- KPIs clave
- gráficos
- ranking top 10
- recomendaciones
- tabla completa

## 14. Dashboard Web
Características:
- KPIs
- rankings
- filtros avanzados
- modo oscuro
- carga de JSON

## 15. Escalabilidad
- configuración por cliente
- exportación JSON
- backup automático
- alerts futuras

## 16. Flujo Diario
1. Exportar 7d/30d/mes
2. Guardar en crudo/
3. Ejecutar main.py
4. Revisar PDF + dashboard

## 17. Checklist de Calidad
- columnas detectadas
- score no vacío
- fechas válidas
- pdf generado
- json correcto
