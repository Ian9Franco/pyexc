
# 📘 README V4 – Sistema Inteligente y Escalable de Análisis de Meta Ads

Este documento describe una arquitectura completa, moderna y escalable para analizar campañas publicitarias de **Meta Ads (Facebook, Instagram, WhatsApp)** a partir de archivos exportados en Excel. Está pensado para **cualquier cliente**, sin importar su rubro, sus objetivos de campaña o el set de métricas disponibles.

El sistema combina tres enfoques:
- **Técnico**: arquitectura, flujos, módulos, normalización y procesamiento.
- **Operativo**: lógica de marketing, interpretación de métricas, tendencias y decisiones.
- **Analítico**: score, rendimiento, detección de anomalías, ranking de anuncios.

El objetivo final es entregar **informes profesionales**, **PDF con análisis avanzado**, y una **web-dashboard** para visualizar datos históricos.

---

# 1. 🎯 Propósito General del Proyecto

Crear un sistema capaz de:
1. **Leer cualquier archivo de Meta Ads Export** (7 días, 30 días, 1 mes, meses históricos).
2. **Detectar automáticamente el tipo de dataset** según el nombre del archivo:
   - `Cliente-7d.xlsx` → últimos 7 días  
   - `Cliente-30d.xlsx` → últimos 30 días  
   - `Cliente-sep.xlsx`, `Cliente-oct.xlsx`, etc. → meses históricos  
3. **Normalizar columnas**, independientemente del idioma, la estructura o la versión del reporte.
4. **Clasificar campañas por objetivo real**.
5. **Calcular métricas específicas según objetivo**.
6. **Detectar anuncios en caída, en ascenso, muertos o héroes**.
7. **Generar un informe profesional en PDF** con charts, insights y recomendaciones accionables.
8. **Visualizar todo desde un dashboard web**.

---

# 2. 📁 Estructura de Carpetas

```
/crudo
    Cliente-7d.xlsx
    Cliente-30d.xlsx
    Cliente-sep.xlsx
    Cliente-oct.xlsx
    Cliente-nov.xlsx
/limpios
    Cliente-limpio.xlsx
/informes
    Cliente-informe.pdf
/web
    dashboard.py
/schema
    columnas.json
    objetivos.json
/util
    normalizador.py
    score.py
    helpers.py
main.py
README.md
```

---

# 3. 🔍 Tipos de Dataset y Detección Automática

Basado en nombre del archivo:

| Sufijo     | Significado | Uso |
|------------|-------------|-----|
| `-7d`      | Últimos 7 días | Tendencia inmediata |
| `-30d`     | Últimos 30 días | Rendimiento reciente |
| `-sep` `-oct` `-nov` | Mes histórico | Benchmark histórico |

El sistema identifica el *formato esperado* de cada archivo para procesarlo adecuadamente.

---

# 4. 🔧 Normalización de Columnas

Meta usa nombres inconsistentes, por idioma o versión.

Ejemplo:
- “Importe gastado (ARS)”
- “Amount spent”
- “Gasto”
- “Spend”

El sistema usa un **diccionario de mapeo flexible**, almacenado en `/schema/columnas.json`:

```json
{
  "gasto": ["Importe gastado (ARS)", "Amount spent", "Spend"],
  "conversaciones": ["Conversaciones con mensajes iniciadas", "Messaging conversations", "Message conversations started"],
  "contactos_mensajes": ["Contactos de mensajes", "Messaging contacts"]
}
```

Esto permite:
- tolerancia a columnas faltantes
- tolerancia a nuevos idiomas
- modelos de Meta Ads futuros

---

# 5. 🎯 Clasificación Inteligente por Objetivos

El reporte trae “Objetivo” pero no siempre es fiable.  
El sistema detecta objetivo real usando:

### Señales de tráfico
- Clics en el enlace  
- Clics salientes  
- Visitas al perfil  
- Visitas a la landing

### Señales de interacción
- Interacciones  
- Likes  
- Comentarios  
- Reproducciones de video  
- ThruPlays  

### Señales de clientes potenciales
- Formularios  
- Leads  
- Leads únicos  
- Costo por lead

### Señales de ventas
- ROAS  
- Conversiones  
- “Valor de conversión”

### Señales de mensajes
- Conversaciones iniciadas  
- Contactos nuevos/recurrentes  
- Costo por conversación  

---

# 6. 📈 Métricas Analíticas por Objetivo

Cada objetivo se analiza con su propio set de KPIs correctos.

---

## 6.1 Mensajes (Messenger, Instagram, WhatsApp)
**Métricas clave:**
- Conversaciones iniciadas  
- Contactos nuevos  
- Costo por conversación  
- Tasa de contacto  
- Alcance efectivo  
- Frecuencia aceptable  

**Insights automáticos:**
- creatividades desgastadas → frecuencia alta + conversación baja  
- ads tóxicos → alcance alto + costo por conversación muy alto  
- ads héroes → alto volumen + bajo costo  

---

## 6.2 Tráfico
**Métricas clave:**
- Clics en el enlace  
- Clics salientes únicos  
- CPC  
- CTR  
- Visitas al perfil  
- Visitas a la landing  

**Detecciones:**
- fake clicks → muchos clics y casi sin visitas  
- mala segmentación → CTR bajo  
- landing mala → visitas bajas pero CTR alto  

---

## 6.3 Interacción
**Métricas clave:**
- Interacciones totales  
- Reacciones  
- Comentarios  
- Guardados  
- Compartidos  
- Costo por interacción  

**Detecciones:**
- Ads “virales”  
- Ads “fantasma” (alcance alto pero interacción 0)  

---

## 6.4 Clientes potenciales
**Métricas clave:**
- Leads totales  
- Leads únicos  
- Costo por lead  
- Tasa de conversión sobre clics  

---

## 6.5 Ventas
**Métricas clave:**
- ROAS  
- Valor de conversión total  
- Costo por compra  
- Conversiones únicas  

---

# 7. 📊 Score Inteligente 0–100

El score evalúa cada anuncio comparándolo con:

- anuncios del mismo objetivo  
- su propio rendimiento histórico  
- los últimos 30 días  
- tendencia 7 días  

Un ejemplo de fórmula (variable por objetivo):

```
score = 
  (peso_kpi1 * normalizado1) +
  (peso_kpi2 * normalizado2) +
  (peso_tendencia * tendencia) +
  (peso_costo * costo_invertido)
```

Resultado:
- 90–100 → anuncio héroe  
- 70–89 → anuncio sano  
- 40–69 → anuncio en alerta  
- 0–39 → anuncio para pausar/eliminar  

---

# 8. 📉 Sistema de Detección de Tendencias (7 días)

Ejemplos:
- caída del 30% en conversaciones respecto al promedio de 30 días  
- subida del CTR  
- descenso del CPC  
- frecuencia en aumento  

Cada parámetro genera un **alert trigger**.

---

# 9. 🧠 Informe Profesional en PDF

El sistema genera:
- carátula con cliente y fecha  
- tabla resumen de KPIs por objetivo  
- ranking de anuncios por score  
- gráficos automáticos:
  - barras
  - líneas
  - heatmaps
- insights redactados automáticamente  
- recomendación final:
  - qué pausar  
  - qué duplicar  
  - qué aumentar presupuesto  
  - qué cambiar creativamente  

Exportado con:
- `reportlab`  
- estilos profesionales  
- tipografía limpia  
- diseño corporativo simple  

---

# 10. 🌐 Dashboard Web

Se incluye un mini-dashboard en `/web`:

### Funcionalidades:
- filtrar por cliente  
- filtrar por campaña  
- filtrar por fechas  
- ranking de anuncios  
- score en tiempo real  
- búsqueda por nombre  

### Indicadores visuales:
- color verde/amarillo/rojo  
- tendencia con flechas  
- gráficas rápidas  

Ideal para usar en escritorio.

---

# 11. 🔄 Flujo Completo del Sistema

```
1. Usuario deja archivos en /crudo
2. main.py detecta tipos (7d, 30d, meses)
3. limpieza.py normaliza y genera /limpios/Cliente-limpio.xlsx
4. análisis.py fusiona datasets
5. score.py calcula scoring
6. tendencias.py compara 7d vs 30d
7. informe.py genera PDF completo
8. dashboard lee /limpios y /informes
9. Usuario visualiza dashboard y lee PDF
```

---

# 12. 🧩 Escalabilidad

El diseño permite incorporar:
- nuevos objetivos
- nuevos tipos de columnas
- nuevas fuentes (Google Ads, TikTok)
- nuevos formatos de informe
- automatización por API

Todo sin reescribir el núcleo.

---

# 13. 🔐 Privacidad

Los informes y datos son locales.  
No se envía nada a servidores externos.

---

# 14. 📦 Conclusión

Este sistema permite:
- analizar *cualquier* campaña de Meta  
- interpretar el rendimiento según el verdadero objetivo  
- detectar problemas reales en los anuncios  
- identificar héroes y duplicarlos  
- mejorar presupuestos  
- generar informes profesionales  
- visualizar en un dashboard propio  

Ideal para un analista, un media buyer o un desarrollador que quiera **escalar procesos de marketing sin depender de plataformas externas**.

