# 📘 VISIÓN V4 – Roadmap Pendiente (Post-Implementación)

Este documento refleja **exclusivamente lo que NO está implementado aún**, tomando como base el CHANGELOG V4. Todo lo ya construido fue eliminado para evitar duplicación y confusión.

Su objetivo es funcionar como **visión futura clara y accionable** del proyecto Meta Ads Analyzer.

---

# 🎯 Propósito de esta Visión

Definir los **próximos pasos reales del sistema**, enfocados en:

* Visualización
* Profundización analítica por objetivo
* Automatización
* Escalabilidad

---

# 1. 🌐 Dashboard Web (PRIORIDAD ALTA)

Actualmente:

* Existe carpeta `/web`
* No hay implementación funcional

## Pendiente de implementar

### Funcionalidades core

* Dashboard interactivo (Streamlit o Flask)
* Lectura directa de JSON generado
* Vista resumen ejecutiva

### Filtros

* Cliente
* Campaña
* Objetivo
* Clasificación (HÉROE / SANO / ALERTA / MUERTO)
* Tendencia

### Visualizaciones

* Rankings dinámicos
* Score 0–100 con colores
* Flechas de tendencia
* Gráficos simples:

  * barras
  * líneas temporales

### UX

* Búsqueda por nombre de anuncio
* Tabs por objetivo
* Vista rápida de acciones recomendadas

---

# 2. 📈 Score Específico por Objetivo

Actualmente:

* Score general 0–100 ya implementado
* Pesos configurables existen

## Pendiente

* Fórmula de score **diferente por objetivo**
* Normalización independiente por tipo de campaña

### Ejemplos

**Mensajes**

* Peso fuerte en costo por conversación
* Penalización por frecuencia alta

**Tráfico**

* Peso fuerte en CTR y CPC
* Detección de clics falsos

**Leads**

* Peso fuerte en CPL y tasa de conversión

**Ventas**

* ROAS como métrica dominante

---

# 3. 🧠 Insights Automáticos por Objetivo

Actualmente:

* Reglas básicas de anomalías

## Pendiente

Generación de insights redactados según patrones:

### Mensajes

* Saturación de audiencia
* Creativo agotado

### Tráfico

* Landing deficiente
* Segmentación incorrecta

### Interacción

* Ads virales
* Ads fantasma

### Leads / Ventas

* Problemas de embudo
* Buen volumen pero mala calidad

Salida esperada:

* Texto automático en PDF y dashboard

---

# 4. ⏱️ Automatización

## Pendiente

* Conexión con API de Meta Ads
* Descarga automática de datasets
* Programación de informes:

  * diario
  * semanal
  * mensual

### Alertas

* Email
* Slack
* Condiciones críticas (ads muertos gastando)

---

# 5. 🤖 Machine Learning (Exploratorio)

No iniciado.

## Ideas futuras

* Predicción de rendimiento
* Clustering de anuncios exitosos
* Detección temprana de fatiga
* Recomendación automática de presupuesto

---

# 6. 🌍 Multi-plataforma

Actualmente:

* Solo Meta Ads

## Futuro

* Google Ads
* TikTok Ads
* Normalización cross-platform
* Score unificado

---

# 7. 📌 Estado Final Deseado

El sistema debería permitir:

* Subir datos o conectarse por API
* Analizar automáticamente
* Visualizar en dashboard
* Recibir recomendaciones claras
* Tomar decisiones sin abrir Meta Ads

---

# 🧭 Nota Final

Este documento es ahora **100% visión futura**.
Todo lo que figura aquí **no está implementado aún**, y sirve como:

* roadmap técnico
* guía de prioridades
* límite claro del alcance actual del sistema
