# 📘 Meta Ads Analyzer — Sistema Inteligente de Análisis (v4 estable)

Sistema automatizado de análisis avanzado para **Meta Ads**, diseñado para funcionar como un **analista de performance senior**.

Procesa archivos exportados desde Meta Ads y genera:
- análisis multi-dimensional
- scoring inteligente 0–100
- detección de tendencias y anomalías
- recomendaciones priorizadas
- informes profesionales (TXT / PDF)
- JSON estructurado para dashboards

---

## 🧠 Qué problema resuelve

Reemplaza decisiones basadas en métricas aisladas por análisis contextual:
- evaluación por objetivo real
- comparación justa entre anuncios
- detección temprana de desgaste
- criterios claros de acción

---

## 📁 Estructura del Proyecto

```
crudo/
limpios/
informes/
schema/
web/
scripts/
```

---

## 📥 Input soportado

Archivos Excel exportados desde Meta Ads:

```
Cliente-30d.xlsx   # requerido
Cliente-7d.xlsx    # tendencia
Cliente-sep.xlsx   # histórico
```

---

## 📊 Análisis principal

### Clasificación por objetivo
- Mensajes
- Tráfico
- Interacción
- Leads
- Ventas

### Score 0–100
Índice de salud del anuncio:
- HÉROE (90–100)
- SANO (70–89)
- ALERTA (40–69)
- MUERTO (<40)

### Tendencias
Comparación 7d vs 30d:
- EN_ASCENSO
- ESTABLE
- EN_CAÍDA
- CRÍTICO

### Anomalías
- gasto sin resultados
- CTR anormalmente bajo
- frecuencia excesiva
- anuncios muertos gastando

---

## 🧾 Outputs

- TXT → informe legible
- PDF → informe profesional
- JSON → dashboard y visualización

---

## ▶️ Ejecución

```bash
python main.py
```

---

## 📌 Estado del proyecto

- ✅ Sistema de análisis completo
- ✅ Score 0–100
- ✅ Tendencias y anomalías
- ✅ PDF profesional
- ⏳ Dashboard web
- ⏳ Score específico por objetivo

Ver evolución futura en **VISION_V5.md**.

---

## 📚 Documentación

- README.md → estado actual
- PLAN_OPERATIVO.md → reglas de negocio
- CHANGELOG.md → historial real
- VISION_V5.md → evolución pendiente
