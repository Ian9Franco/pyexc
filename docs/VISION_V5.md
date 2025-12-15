# 📘 VISION V5 – Evolución Pendiente del Sistema de Análisis de Ads

> **Este documento describe únicamente lo que AÚN NO está implementado**.
> Todo lo ya cumplido fue consolidado en README.md, PLAN_OPERATIVO.md y CHANGELOG.md.

---

## 🧭 Propósito de V5

La versión V5 representa la siguiente frontera del sistema: evolucionar desde un analizador inteligente hacia una **plataforma autónoma, multi-objetivo y multi-plataforma**, con capacidades predictivas y operativas.

---

## 1. 📊 Scoring específico por objetivo

### Estado actual
- El sistema ya **clasifica correctamente el objetivo** de cada campaña.
- Existe un score 0–100, pero **no varía su lógica interna según el objetivo**.

### Propuesta V5
Implementar motores de scoring independientes por objetivo:
- KPIs específicos
- Pesos diferenciados
- Benchmarks propios

Ejemplos:
- Mensajes → costo por conversación, tasa de contacto
- Tráfico → CTR, CPC, visitas reales
- Leads → CPL, tasa de conversión
- Ventas → ROAS, valor de conversión

Objetivo: que el score sea **semánticamente correcto**, no solo comparable.

---

## 2. 🧠 Insights automáticos por objetivo

Generar narrativas automáticas específicas:
- Diagnóstico del rendimiento
- Causas probables
- Acciones sugeridas

---

## 3. 🌐 Dashboard web funcional

Implementar un dashboard real con:
- filtros por cliente, campaña y fechas
- rankings interactivos
- gráficos de tendencia
- búsqueda por anuncio
- vistas por objetivo

---

## 4. 🤖 Automatización

- Integración con API de Meta Ads
- Ejecuciones programadas
- Informes automáticos
- Alertas por email o Slack

---

## 5. 📈 Machine Learning (exploratorio)

- Predicción de rendimiento
- Detección temprana de ads en caída
- Sugerencias de redistribución de presupuesto

---

## 6. 🌍 Multi-plataforma

- Google Ads
- TikTok Ads
- Normalización cross-platform
- KPIs unificados

---

## 7. 🧩 Principio rector

Nada nuevo debe romper lo que ya funciona.
V5 se construye como **evolución**, no reescritura.

---

## 📌 Conclusión

VISION V5 describe únicamente las piezas que faltan para convertir el sistema actual en una plataforma completa de análisis de paid media.
