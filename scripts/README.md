# Meta Ads Data Processing Pipeline v2.0

Pipeline de análisis automatizado para datos de Meta Ads. Genera informes accionables con métricas de rendimiento y recomendaciones estratégicas.

## Estructura de Archivos

\`\`\`
scripts/
├── config.py              # Configuración centralizada y umbrales
├── data_loader.py         # Carga y normalización de archivos Excel
├── metrics.py             # Cálculo de Score, CPA, Eficiencia, Actividad
├── analyzer.py            # Rankings y estadísticas
├── recommendations.py     # Lógica de recomendaciones (duplicar/pausar)
├── report_formatter.py    # Formateo del informe TXT
├── json_exporter.py       # Exportación JSON para dashboard web
├── main.py                # Orquestador principal
└── README.md
\`\`\`

**Carpetas generadas automáticamente:**
- `crudo/` - Archivos Excel de Meta Ads (input)
- `limpios/` - Datos procesados (output intermedio)
- `informes/` - Reportes TXT y JSON generados (output final)

## Requisitos

\`\`\`bash
pip install pandas openpyxl
\`\`\`

## Uso Rápido

### 1. Preparar archivos de entrada

Coloca los archivos Excel exportados de Meta Ads en `crudo/`:

\`\`\`
crudo/
├── NombreCliente-30d.xlsx    # Últimos 30 días (REQUERIDO)
├── NombreCliente-7d.xlsx     # Últimos 7 días (para actividad)
├── NombreCliente-oct.xlsx    # Histórico (opcional)
├── NombreCliente-nov.xlsx    
└── NombreCliente-dic.xlsx    
\`\`\`

**El sistema acepta cualquier sufijo de mes:** `-sep`, `-oct`, `-nov`, `-dic`, `-ene`, etc.

### 2. Ejecutar

\`\`\`bash
python main.py
\`\`\`

### 3. Ver resultados

- `informes/NombreCliente-informe.txt` - Informe legible
- `informes/NombreCliente-informe.json` - Datos para dashboard web

---

## Métricas Explicadas

### SCORE (Conversiones Ponderadas)

**Qué es:** Un número que representa el VALOR TOTAL de todas las acciones generadas.

**Cómo se calcula:**

| Evento | Peso | Por qué |
|--------|------|---------|
| `results` | 1.0 | Resultado directo de campaña |
| `msg_init` | 1.0 | Contacto directo (alto valor) |
| `msg_contacts` | 1.0 | Contacto confirmado |
| `link_clicks` | 0.15 | Solo muestra interés |
| `ig_profile` | 0.30 | Interés medio |

**Ejemplo:** 5 mensajes + 20 clics = 5×1 + 20×0.15 = **8 score**

---

### CPA (Costo Por Adquisición)

**Qué es:** Cuánto pagaste en promedio por cada conversión.

**Fórmula:** `Gasto Total ÷ Score`

**Ejemplo:** $10,000 gastados con score de 8 = CPA de **$1,250**

**Interpretación:**
- CPA BAJO = BUENO (pagas poco por resultado)
- CPA ALTO = MALO (pagas mucho por resultado)

---

### MEDIANA CPA

**Qué es:** El CPA "del medio" de todos tus anuncios.

**Para qué sirve:** Es tu PUNTO DE REFERENCIA.
- CPA < mediana = más eficiente que la mayoría
- CPA > mediana = menos eficiente que la mayoría

---

### EFICIENCIA

Categorización automática comparando CPA vs mediana:

| Categoría | Condición | Significado |
|-----------|-----------|-------------|
| MUY_EFICIENTE | CPA < 70% mediana | Excelente |
| EFICIENTE | CPA < mediana | Bueno |
| NORMAL | CPA < 150% mediana | Aceptable |
| CARO | CPA > 150% mediana | Revisar |

---

### ACTIVIDAD

Estado del anuncio en los últimos 7 días:

| Estado | Significado |
|--------|-------------|
| ACTIVO | Generó conversiones en 7 días |
| GASTANDO | Gastó pero no convirtió en 7 días |
| INACTIVO | Sin gasto ni conversiones |

---

## Secciones del Informe

### A: Resumen
- Gasto total, CPA global, mediana
- Estado de la cuenta (anuncios activos/inactivos)

### B: Rankings
- **Por Impacto:** Mayor score (más conversiones)
- **Por Volumen:** Mayor inversión
- **Por Eficiencia:** Menor CPA (mínimo 1 conversión)

### C: Anuncios para Duplicar
Candidatos que cumplen TODOS estos criterios:
1. Score >= 10 (volumen significativo)
2. CPA <= mediana × 1.2 (eficiente)
3. Actividad reciente

Incluye explicación detallada de POR QUÉ cada anuncio califica.

### D: Acciones Urgentes
- **PAUSAR:** Gasto alto sin ninguna conversión
- **REVISAR:** CPA > 2× mediana y sigue gastando

### E: Detalle de Anuncios
Tabla completa con todas las métricas.

### F: Histórico
Score total por período (mes).

---

## Dashboard Web

El JSON generado puede visualizarse en el dashboard Next.js incluido:

1. Ejecuta `python main.py`
2. Abre el dashboard web
3. Arrastra el archivo `.json`
4. Explora métricas visualmente

**Funcionalidades:**
- KPIs principales con indicadores de salud
- Rankings interactivos
- Tabla ordenable de anuncios
- Gráfico histórico
- Glosario integrado

---

## Configuración

Edita `config.py` para ajustar umbrales:

\`\`\`python
# Pesos de conversiones
PESOS_CONVERSIONES = {
    'results': 1.0,
    'msg_init': 1.0,
    'msg_contacts': 1.0,
    'link_clicks': 0.15,
    'ig_profile': 0.3,
}

# Umbrales de decisión
UMBRALES = {
    'DUPLICAR_SCORE_MIN': 10,        # Score mínimo para duplicar
    'DUPLICAR_CPA_RATIO_MAX': 1.2,   # CPA máximo (ratio de mediana)
    'PAUSAR_GASTO_MIN': 4000,        # Gasto sin conversiones para alertar
    'PAUSAR_CPA_RATIO': 2.0,         # CPA para alertar (ratio de mediana)
}
\`\`\`

---

## Solución de Problemas

**"No se encontró archivo de 30 días"**
- Verifica que exista `crudo/NombreCliente-30d.xlsx`

**"Sin datos de 7 días"**
- Los estados de actividad mostrarán "SIN_DATOS_7D"
- El informe sigue funcionando con solo datos de 30d

**CPA muestra "N/A"**
- Normal para anuncios sin conversiones
- Se excluyen correctamente de la mediana

---

## Ejemplo de Ejecución

\`\`\`
$ python main.py

============================================================
PIPELINE META ADS v2.0
============================================================

Clientes encontrados: Panichella

Procesando: Panichella
----------------------------------------
  -> Buscando: crudo/Panichella-30d.xlsx
     Encontrado: 13 anuncios
  -> Buscando: crudo/Panichella-7d.xlsx
     Encontrado: 10 anuncios
  Anuncios procesados: 13
  Mediana CPA: $1408.82
  Informe TXT: informes/Panichella-informe.txt
  Informe JSON: informes/Panichella-informe.json

============================================================
PIPELINE COMPLETADO
Clientes procesados: 1/1
============================================================
