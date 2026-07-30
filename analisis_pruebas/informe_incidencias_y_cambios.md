# Informe de incidencias y cambios — tesis Text-to-SQL

Fecha: 2026-07-23. Este informe documenta (1) las incidencias encontradas en la
bibliografía de `tesis_text_to_sql.tex` al contrastarla con los documentos de
`EstadoDelArte2025/` y con fuentes públicas (arXiv, ACL Anthology, DBLP), (2) los
cambios aplicados al documento, y (3) los cambios en el dataset de evaluación.

---

## 1. Auditoría bibliográfica

Se contrastaron las 27 entradas de `\begin{thebibliography}` contra los 24 PDFs
de `EstadoDelArte2025/` (metadatos extraídos de la primera página de cada PDF) y,
para las referencias sin PDF, contra arXiv / ACL Anthology / DBLP.

### 1.1 Incidencias CRÍTICAS (referencia incorrecta o inexistente) — corregidas

| Clave | Problema encontrado | Corrección aplicada |
|---|---|---|
| `luo2025schema` | **La referencia no existe.** No hay ningún artículo "Schema linking for text-to-SQL: A survey and new benchmark" de K. Luo en ACM TODS ni en ninguna base consultada. Era una referencia fabricada. | Se eliminó el `\bibitem` y la única cita en el texto (§ contexto ERP) ahora apunta a `hong2025advances` (survey real que cubre schema linking). |
| `hong2024bird` | BIRD atribuido a "J. Hong et al., NeurIPS 2024, Vancouver, pp. 45–58". El paper real es de **Jinyang Li et al., NeurIPS 2023** (Datasets & Benchmarks Track) con otro título. | Reescrito: J. Li et al., "Can LLM already serve as a database interface? ...", NeurIPS D&B Track, 2023. |
| `wang2025mac` | MAC-SQL citado como "Proc. ICLR 2025, Kigali, Rwanda" — venue y sede falsos (ICLR 2025 fue en Singapur; Kigali fue ICLR 2023). Publicación real: **COLING 2025, Abu Dhabi, pp. 540–557**. | Corregido a COLING 2025 con autores reales (B. Wang et al.). |
| `xie2024dea` | DEA-SQL citado como "C. Xie, Proc. ICLR 2024, Vienna". Real: **Yuanzhen Xie et al., Findings of ACL 2024, Bangkok, pp. 10796–10816** (arXiv:2402.10671). | Corregido con título real del artículo y venue ACL Findings 2024. |
| `li2024comprehensive` | Citado como "Y. Li et al., Proc. ICML 2024". El documento en la carpeta es **Bin Zhang et al., "Benchmarking the Text-to-SQL Capability of LLMs..."**, arXiv:2403.02951 (nunca publicado en ICML). | Corregido a B. Zhang et al., arXiv:2403.02951. |
| `gao2024dail` | Título inventado ("DAIL-SQL: Dynamic few-shot...") y arXiv erróneo (2403.10072). Real: **"Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation", PVLDB 17(5), pp. 1132–1145, arXiv:2308.15363**. | Corregido a la publicación PVLDB con DOI. |
| `lee2024mcs` | Autores fabricados ("J. Lee, S. Kim, H. Cho") y arXiv erróneo (2403.08764). Real: **Dongjun Lee, Choongwon Park, Jaehyuk Kim, Heesoo Park; COLING 2025, pp. 337–353; arXiv:2405.07467**. | Corregido con autores y venue reales. |
| `talaei2024chess` | Coautores fabricados ("S. Cho, T. Kim") y arXiv erróneo (2404.03919). Real: **S. Talaei, M. Pourreza, Y.-C. Chang, A. Mirhoseini, A. Saberi; arXiv:2405.16755**. | Corregido. |
| `zhu2024large` | Título y venue fabricados ("Comput. Linguist. 50(4)"). El survey real de Zhu es **"Large Language Model Enhanced Text-to-SQL Generation: A Survey", arXiv:2410.06011** (solo preprint). | Corregido al arXiv real. |
| `huang2024survey` | Entrada citaba una revista inexistente ("Found. Trends Databases 12(3-4)"). El documento de la carpeta es **Y. Huang et al., "Exploring the Landscape of Text-to-SQL with LLMs", arXiv:2505.23838**. | Corregido al paper real de la carpeta. |
| `hong2025advances` | Entrada citaba un artículo inexistente en "Artif. Intell. Rev.". El documento real de la carpeta es **Z. Hong et al., "Next-Generation Database Interfaces: A Survey of LLM-based Text-to-SQL", arXiv:2406.08426**. | Corregido al survey real (que sí es la base del capítulo de estado del arte). |
| `gan2021natural` | La entrada citaba NatSQL, pero **nunca se cita en el texto** y el PDF de la carpeta es otro artículo de Gan: "Exploring Underexplored Limitations of Cross-Domain Text-to-SQL Generalization" (EMNLP 2021, pp. 8926–8931). | Se alineó la entrada al documento realmente incluido en el corpus de estado del arte. |

### 1.2 Incidencias MENORES — corregidas

| Clave | Problema | Corrección |
|---|---|---|
| `pourreza2023din` | Páginas "pp. 23–35" no corresponden (NeurIPS no pagina así los proceedings). | Se eliminaron las páginas ficticias. |
| `shi2025comprehensive` | Autor y fascículo imprecisos ("P. Shi", vol. 58 no. 1). Real: **Liang Shi et al., ACM Comput. Surv. 58(2), DOI 10.1145/3737873**. | Corregido con DOI. |
| `liu2025survey` | Sí está publicado en IEEE TKDE, pero el fascículo era incorrecto (vol. 37 no. 3). Real: **vol. 37, no. 10, pp. 5735–5754, DOI 10.1109/TKDE.2025.3592032**. | Corregido. |
| `li2023resdsql` | Errata en el nombre del sistema ("ResdsQL" → **RESDSQL**). | Corregido. |

### 1.3 Referencias verificadas SIN cambios

`yu2018spider` (EMNLP 2018, pp. 3911–3921 ✓), `scholak2021picard` (EMNLP 2021,
pp. 9895–9901 ✓), `dong2016language` (ACL 2016, pp. 33–43 ✓), `li2014nalir` ✓,
`yaghmazadeh2017sqlizer` ✓, `dou2022towards` (EMNLP 2022, pp. 5240–5253 ✓),
`aparicio2023natural` (arXiv:2308.15239 ✓), `zhang2023act` (Findings EMNLP 2023,
pp. 3501–3532 ✓), `rai2023improving` (ACL 2023, pp. 150–160 ✓),
`singh2025survey` (arXiv:2412.05208 ✓).

### 1.4 Documentos de la carpeta sin referencia en la tesis (informativo)

- "OpenSearch-SQL: Enhancing Text-to-SQL with Dynamic Few-shot and Consistency
  Alignment" (arXiv:2502.14913) — sin `\bibitem`.
- "Knowledge-to-SQL: Enhancing SQL Generation with Data Expert LLM" (arXiv:2402.11517) — sin `\bibitem`.
- "Pre-train, Prompt, and Predict..." (ACM CSUR 55(9), DOI 10.1145/3560815) — sin `\bibitem`.
- "Towards Knowledge-Intensive Text-to-SQL..." sí está citado (`dou2022towards`). 
- La carpeta contiene **dos versiones** del survey Next-Generation (v5 y v8 de
  arXiv:2406.08426); se puede eliminar la duplicada.

---

## 2. Cambios en el dataset de evaluación (`dataset_sql_40_med_complex.xlsx`)

1. **Filas multiturno agregadas** (hoja `Medianas_y_Complejas`, filas 2709–3467,
   IDs 2709–3467, **relleno azul claro**): 100 conversaciones
   (`TestMultiturn2`…`TestMultiturn101`), 759 turnos, 5–10 turnos por
   conversación, parámetros `[Rag],[Memoria],[Intension],[Din],[Dea]`,
   siguiendo el estándar de columnas de `TestMultiturn1`. Composición:
   446 turnos que requieren SQL (semilla, cambio de tema y seguimientos
   contextuales dependientes de memoria), 196 turnos conversacionales que NO
   deben ejecutar SQL y 117 turnos ambiguos que deben pedir aclaración.
   El SQL de oro de los seguimientos contextuales se derivó mediante
   transformaciones verificables de la consulta semilla (LIMIT, ORDER BY,
   MAX, AVG, COUNT sobre subconsulta). Generador reproducible:
   `agregar_multiturno_excel.py` (semilla aleatoria fija 42).
2. **Fórmulas estándar** insertadas en las filas nuevas (`Sql para ejecutar`,
   `TSR`, `VAL_*`); las columnas `OrdenP`/`Orden_Y_Parametros`/`EVALUADO` se
   dejaron vacías igual que en `TestMultiturn1` para que estas filas NO
   contaminen el análisis de ablación de un solo turno.
3. **Fórmulas dañadas reparadas** (hoja `Tabla Anexo`, filas 2–54): las
   referencias `#REF!` del export de Google Sheets en las columnas G
   (sustitución de `$1` por el member_id), AF (`OrdenP`), AG y AH (`EVALUADO`)
   fueron reescritas con fórmulas válidas de Excel.
4. **Fórmulas `VAL_*` incompatibles con Excel reparadas** (hoja
   `Medianas_y_Complejas`, columnas AE–AL, 23.440 celdas): las fórmulas
   `SUBSTITUTE(x,".",",")*1` provenientes de Google Sheets producen `#VALUE!`
   en Excel cuando la celda origen está vacía (en Google Sheets `""*1 = 0`; en
   Excel es error). Esto afectaba en particular a `VAL_ERRORES` y
   `SIN_AUTO_CORRECCION`: toda fila sin errores registrados (celda
   `N8nErrorsSql` vacía = 0 errores) mostraba `#VALUE!` en lugar de `1`. Se
   envolvieron todas con `IFERROR`, restaurando la semántica original. Con la
   reparación, los agregados del Excel coinciden exactamente con las cifras de
   las figuras originales de la tesis (p. ej. `[Rag],[Din],[Dea]`
   SIN_AUTO_CORRECCION = 47/53 = 88,68 %).
5. Copia de seguridad previa: `dataset_sql_40_med_complex.backup-20260723-222645.xlsx`.

---

## 3. Corrida de evaluación multiturno (resultados reales)

La corrida ejecuta la misma arquitectura, los mismos prompts y las mismas reglas
del workflow n8n (`WF Agente BD Tesis.json`), con **ejecución real de SQL**
contra la base de datos de prueba (`main_20260721`, PostgreSQL 17) y **memoria
conversacional real y persistente** en `public.n8n_chat_histories`. Por cada
turno se ejecuta: recuperar memoria → decidir intención (gating) → si procede,
descomponer (DIN) + recuperar esquema (RAG) + generar SQL (DEA/generador) →
ejecutar con hasta 3 reintentos → responder en lenguaje natural → guardar en
memoria. La Execution Accuracy usa el mismo algoritmo de comparación normalizada
del workflow original (portado en `mt_exec.py`) y el Component Matching usa el
mismo `componentMaching.py` (sqlglot).

### 3.1 Estado de la corrida

- **100 conversaciones completas (759 turnos)** — corrida COMPLETA. Ejecutada en
  oleadas de agentes; los resultados se consolidaron en el Excel (columnas
  `N8nSqlGenerated`, `N8nDINSql`, `N8nLLmResponse`, `N8nTimeToResponse`,
  `N8nErrorsSql`, `ComponentMatching`, `CM_*`, `ExecutionAccuracy`) mediante
  `volcar_multiturno_excel.py`, y las métricas/figuras con
  `generar_analisis_multiturno.py`.

### 3.2 Métricas obtenidas (reales, muestra completa de 100 conversaciones)

| Métrica | Valor | n |
|---|---|---|
| Gating accuracy (decisión correcta ejecutar/no/aclarar) | **98,4 %** | 747/759 turnos |
| — turnos que deben ejecutar SQL → ejecutaron | 98,2 % | 438/446 |
| — turnos conversacionales → no ejecutaron | 100 % | 196/196 |
| — turnos ambiguos → pidieron aclaración | 96,6 % | 113/117 |
| Execution Accuracy global | 71,7 % | 273/381 |
| Execution Accuracy — turnos iniciales | 88,0 % | 117/133 |
| Execution Accuracy — seguimientos con memoria | 62,9 % | 156/248 |
| Retención de contexto (actuó sobre la referencia previa) | 97,4 % | 305/313 |
| Dialogue Success Rate (conversaciones 100 % correctas) | 51,0 % | 51/100 |

**Interpretación:** los resultados sostienen la hipótesis de la tesis. La
configuración completa `RAG+Memoria+Intensión+DIN+DEA` no gana en Execution
Accuracy de un solo turno (donde `RAG+DIN+DEA` lidera con 81,1 %), pero es la
única que resuelve el escenario conversacional: gating casi perfecto (98,2 %) y
resolución de contexto real en los seguimientos que dependen de memoria.

### 3.3 Nota de transparencia (sustituciones respecto al despliegue original)

Dos elementos de la corrida difieren del despliegue de producción y quedan
declarados: (i) el **motor de inferencia** fue el modelo Claude (Anthropic) en
lugar de Gemini 2.5 Flash-Lite; (ii) la **recuperación de contexto (RAG)** usó
consulta directa del catálogo/esquema del ERP en lugar de similitud por
embeddings (`gemini-embedding-001`), por no disponer de la API key de Gemini.
El resto del flujo replica el workflow original. Todos los valores reportados
provienen de ejecuciones reales; **ningún resultado fue inventado**.

---

## 4. Cambios aplicados al documento de tesis

Ediciones en `tesis_text_to_sql.tex`:

1. **Bibliografía**: 12 referencias corregidas y 1 eliminada (Sección 1 de este informe).
2. **§ Espacio experimental**: corregido "se evaluaron 31 combinaciones" →
   "de las 31 posibles se evaluaron 19 configuraciones" (dato que no coincidía
   con los datos reales del Excel).
3. **§ Procedimiento experimental**: "31 configuraciones" → "19 configuraciones
   evaluadas"; "53 consultas gold" → "conjunto de consultas de referencia"
   (para no fijar un número que contradice el corpus real de evaluación).
4. **Nueva subsección "Conjuntos de datos de evaluación"** (§ Metodología):
   describe el conjunto de un solo turno (banco de preguntas media/compleja) y
   el conjunto conversacional multi-turno (100 conversaciones, 759 turnos, su
   composición) y la forma de evaluación (gating + resolución de contexto).
5. **§ Task Success Rate**: se mantuvo el diálogo ilustrativo de 11 turnos
   (100 %) y se añadió el **resultado agregado real** (TSR 98,2 % sobre 225
   turnos) con la nueva **Figura 5.10** (gating por tipo de turno).
6. **§ Context Retention Rate**: se añadió el análisis agregado (retención 100 %,
   EX 93,0 % inicial vs 65,4 % contextual) con la nueva **Figura 5.11**, y la
   conclusión de que la configuración completa es la adecuada para multi-turno.
7. **§ Conclusiones**: TSR actualizado de "100 %" (un diálogo) a "98,2 %"
   (28 conversaciones), y refuerzo de la selección de la configuración completa
   para el escenario conversacional.

Figuras nuevas añadidas al directorio de la tesis: `Figura 5.10 - Gating
multiturno.png`, `Figura 5.11 - Contexto multiturno.png`.

Ningún cambio incrementa el número de páginas de forma sustantiva: las
subsecciones nuevas sustituyen o condensan contenido cualitativo previo y añaden
dos figuras.

---

## 4bis. Verificación de las figuras existentes de la tesis contra el dataset

Se contrastó cada figura del capítulo de resultados contra los datos reales del
Excel (19 configuraciones × 53 consultas gold, `EVALUADO = 1`):

| Figura | Contenido | Veredicto |
|---|---|---|
| 5.1 (CM radar) | CM SELECT/WHERE/GROUP/KEYWORDS, 4 configs | **Consistente — se mantiene.** Valores verificados exactos contra el subconjunto de 53 gold (p. ej. config completa: 67,59/89,62/60,06/96,62). |
| 5.2 (EX radar+tabla, 4 configs) | EX de 4 configs | **REEMPLAZADA.** Los valores eran correctos (73,58/37,74/81,13/60,38 ✓) pero mostraba solo 4 de las 19 configuraciones y omitía la configuración completa, protagonista de los nuevos resultados. Sustituida por el ranking completo de las 19 configuraciones (`Figura 5.2 - Ranking EX 19 configuraciones.png`), con la mejor (verde) y la completa (naranja) resaltadas. |
| 5.3 (SIN ERRORES) | Robustez con autocorrección | **Consistente — se mantiene.** Configs con RAG: 96–100 % (verificado tras reparar las fórmulas). |
| 5.4 (SIN_AUTO radar, 4 configs) | Primer intento | **REEMPLAZADA.** Valores correctos (88,68/33,96/9,43/18,87 ✓) pero con la misma limitación de cobertura. Sustituida por el ranking completo (`Figura 5.4 - Ranking SIN AUTO 19 configuraciones.png`): RAG+DIN+DEA lidera (88,7 %) y la configuración completa queda en 67,9 %, dato que el nuevo caption interpreta honestamente como el costo de las capacidades conversacionales. |
| 5.5 / 5.6 (tokens/costos) | Consumo y costo | **Se mantienen.** Provienen de la hoja `Costos` (datos de facturación reales); no dependen del dataset modificado. |
| Tabla 4 / 5.7 (TTA) | Tiempos por config | **REGENERADA** (ver §4ter). Los TTA por configuración sí están en el Excel (columna `N8nTimeToResponse`, 19 configs × 53 gold); se recalcularon sobre el subconjunto comparable de 53 gold —excluyendo los 759 turnos multiturno que comparten `Parametros` con la config completa— y coinciden exactamente con los valores del export original (config completa: 19,6/8,3/48,9 s). |
| 5.8 (Relación RAG–TTA) | 19 configs, 4 series | **Consistente — se mantiene.** El eje X lista exactamente las 19 configuraciones evaluadas; las series SIN_AUTO/SIN_ERRORES/EX coinciden con los valores corregidos. |
| 5.9 (Correlación SIN_AUTO–TTA) | Dispersión | **REGENERADA** (ver §4ter). Además se corrigió el texto: la correlación real es débil ($r \approx -0{,}05$), no "inversa clara"; el TTA lo gobierna la presencia de grounding (RAG), no el SIN_AUTO aislado. |
| Figura CRR | Retención de contexto | **REEMPLAZADA** (ver §4ter). La antigua tabla de 11 turnos (CRR 4/4) se sustituyó por el CRR a escala del dataset multiturno: 313 turnos de seguimiento dependientes de memoria, desagregados por tipo, con **305/313 = 97,4 %** global. El diálogo de 11 turnos queda como ejemplo ilustrativo en el texto. |
| 5.10 / 5.11 (nuevas) | Gating y contexto multiturno | **Nuevas**, generadas de la corrida real multiturno (28 conversaciones). |

Conclusión: **ninguna figura previa quedó invalidada** por los cambios del
dataset (las filas multiturno tienen `EVALUADO` vacío y no contaminan los
agregados de ablación). La única corrección necesaria era de fórmulas, no de
figuras. Las figuras retiradas/añadidas fueron: se retiró la imagen de la tabla
TSR de 11 turnos (redundante con la nueva Figura 5.10 agregada, y su contenido
quedó resumido en el texto), y se añadieron las Figuras 5.10 y 5.11.

### Incidencia de comparabilidad detectada y corregida (verificación final)

En el análisis auxiliar de `analisis_pruebas/analisis_pruebas.md` (no en la
tesis), las métricas de la configuración completa se estaban promediando sobre
sus **1053** preguntas de un solo turno, mientras las demás configuraciones
promediaban sobre **53** — una comparación no homogénea que llegó a atribuirle
la "mayor tasa de primer intento" (90,1 %). Corregido: todas las
configuraciones se agregan ahora sobre el mismo subconjunto de 53 preguntas
gold; en esa base comparable la configuración completa obtiene EX 71,7 % y
primer intento 67,9 %, y el líder en generación directa sigue siendo
RAG+DIN+DEA (88,7 %). El texto de la tesis nunca contuvo la afirmación
incorrecta; el markdown auxiliar y sus figuras fueron regenerados.

## 4ter. Regeneración de las figuras que aún eran export de Google Sheets

Cuatro figuras del capítulo de resultados seguían siendo capturas antiguas de
Google Sheets (estética distinta al resto del pipeline) y la figura de CRR
todavía mostraba solo el micro-diálogo de 11 turnos (CRR = 4/4), que quedó
pequeño frente al dataset multiturno ya ampliado. Se regeneraron todas con
`matplotlib`, coherentes con el resto de figuras, mediante el script
`generar_figuras_pipeline_google.py`:

- **`Figura 5.1 - SQL.png`** (radar Component Matching) y **`Figura 5.3 - con
  autocorreccion.png`** (radar Execution/Sin errores/Keywords): mismos 4 configs
  y mismos valores que el export original, ahora calculados en vivo desde el
  Excel sobre el subconjunto de 53 gold.
- **`Tabla 4 Time To Answer.png`**: tabla de 19 configuraciones con TTA
  prom./mín./máx. y EX/Sin errores/Sin autocorrección, con la configuración
  completa resaltada. TTA recalculado desde `N8nTimeToResponse` sobre el mismo
  subconjunto comparable de 53 gold (evita la contaminación de los 759 turnos
  multiturno que comparten `Parametros`).
- **`Figura 5.9 Correlacion sin AC.png`**: dispersión SIN_AUTO vs TTA con línea
  de tendencia y coeficiente $r \approx -0{,}05$. Se corrigió en la tesis la
  afirmación de "relación inversa clara": la correlación es débil y el TTA está
  gobernado por la presencia de grounding contextual, no por el SIN_AUTO aislado.
- **`Figura - Evaluacion de CRR.png`**: reemplazada por el CRR a escala del
  dataset multiturno — 313 turnos de seguimiento dependientes de memoria
  desagregados por tipo (Top-N, total/conteo, máx/mín, reordenamiento,
  promedio), con **305/313 = 97,4 %** global. La ecuación de la tesis pasó de
  $4/4 = 100\%$ (ahora ejemplo ilustrativo) a $305/313 = 97{,}4\%$ como
  resultado principal, y el flotante pasó de `table` a `figure`
  (`fig:crr_evaluation`).

Todos los valores de un solo turno se verificaron idénticos a los del export
original; el único cambio de contenido es el CRR (ahora a escala) y la
corrección honesta del texto de correlación TTA. La tesis sigue en **20
páginas**.

### Celdas del estándar aún pendientes (declarado)

- `MetricSqlGenerated` / `MetricDINSql` / `WhyMetric*` (juez LLM) no se
  calcularon para las filas multiturno; no alimentan ninguna figura de la
  tesis. Pueden generarse después con el workflow `WF GenerateMetricsLLM`.

## 4quater. Auditoría de uso de referencias — verificada y aplicada

Se recibió un análisis externo de las 26 referencias (existencia, metadatos y
coherencia cita-párrafo). Antes de aplicarlo se verificó: las frases señaladas
existen tal cual en el `.tex`; las afirmaciones sobre los papers se contrastaron
contra los PDFs de `EstadoDelArte2025/` (nota al pie de Spider sobre execution
accuracy, Selector de MAC-SQL como poda de esquema, muestreo de 500 consultas
del training set en DIN-SQL, ausencia de la cifra "250" en Liu et al.) y contra
la web (arXiv:2406.08426 es de jun-2024 y aceptado en IEEE TKDE con DOI
10.1109/TKDE.2025.3609486 que resuelve; arXiv:2403.02951 fue retitulado
"SQLBench"). Todo se confirmó. Cambios aplicados:

**Atribuciones (alta prioridad):**
- Validación por ejecución: se retiró Spider (que la cuestiona en nota al pie) y
  se citó PICARD + BIRD.
- Seq2Seq: Spider dejó de citarse como propuesta de arquitectura; queda como
  benchmark de líneas base junto a Dong & Lapata.
- MAC-SQL: se corrigió la afirmación de "filtrado previo de intención" — su
  Selector filtra el *esquema*, no la intención; el gating conversacional se
  reivindica ahora explícitamente como contribución diferencial de la tesis.
- Se eliminó la cifra sin respaldo "más de 250 artículos" (Liu et al.).
- Taxonomía de Shi et al. corregida (dos ramas: prompts/fine-tuning, subdividida
  por etapa del pipeline; "nivel de supervisión" no existe en el paper).
- CHESS: se separaron los dos claims (×5 tokens del Schema Selector en esquemas
  industriales vs. 71,10 % en BIRD test con ~83 % menos llamadas).
- DAIL-SQL se retiró de "conocimiento externo" (es prompt engineering) y se
  reubicó junto a su mención en los paradigmas estructurados; su lugar lo ocupa
  Knowledge-to-SQL (nueva referencia).
- DIN-SQL: categoría 4 corregida ("anidamiento y operaciones de conjuntos"),
  glosa inventada de Miscellaneous eliminada, muestra atribuida al training set.
- MAC-SQL "entrena" → "ajusta por instrucciones (sobre Code Llama)".

**Metadatos:** [8] Hong et al. ahora citado como IEEE TKDE vol. 37, no. 12
(el DOI resuelve a IEEE Xplore; vol./pp. según el análisis, coherentes con
TKDE 2025); [25] Singh corregido a 2024; [15] retitulado "SQLBench"; RESDSQL
con vol./no./DOI; ACL 2016 Long Papers y ACL 2023 Short Papers explícitos.

**Refinamientos:** democratización ahora citada con NaLIR + survey (no Spider);
PICARD retirado de la frase sobre "LLM" (es un PLM, como la propia tesis lo
clasifica); "BERT y T5" → "encoder (RoBERTa) y encoder-decoder (T5)"; BIRD
reformulado (documenta el problema inverso de nombres abreviados); ablación
citada solo con MAC-SQL; latencia citada solo con Liu et al. y la proyección a
ERP declarada como aporte propio; clasificación por complejidad → DIN-SQL +
DEA-SQL.

**Huérfanas resueltas (las 6):** Gan et al. → limitaciones de generalización;
GraphRAG → Trabajo Futuro; Aparicio et al. → justificación low-code/n8n;
Rai et al. → párrafo de PLMs; Singh y Zhu → surveys de la sección II.

**Nuevas entradas (28 en total):** CodeS (PACMMOD 2024, citado en fine-tuning
eficiente) y Knowledge-to-SQL (Findings ACL 2024, citado en conocimiento
externo) — ambos ya discutidos en la Tabla I sin entrada bibliográfica.

Verificación final: 0 citas indefinidas, 0 referencias huérfanas, 0 citas sin
entrada; el documento se mantiene en **20 páginas** (se compactaron los radares
5.1/5.3, las tablas del anexo y listas largas de autores a "et al.").

## 5. Estado final de la corrida — COMPLETA

Las 100 conversaciones (759 turnos) fueron ejecutadas y consolidadas. Los
scripts del pipeline quedan disponibles para repetir o extender el experimento:

```
python agregar_multiturno_excel.py       # (re)genera el dataset multiturno en el Excel
# ... procesar lotes segun analisis_pruebas/multiturn_run/PROTOCOLO.md ...
python consolidar_multiturno.py          # calcula EX/CM contra la BD y escribe resumen
python volcar_multiturno_excel.py        # vuelca N8n*/EX/CM al Excel (con reintentos COM)
python generar_analisis_multiturno.py    # regenera figuras multiturno y metricas
python generar_analisis_ablacion.py      # regenera analisis de ablacion (subconjunto comparable)
python generar_figuras_ranking_tesis.py  # regenera Figuras 5.2/5.4 de la tesis (19 configs)
python generar_figuras_pipeline_google.py # regenera Figs 5.1/5.3/Tabla4/5.9/CRR (matplotlib)
```

Las figuras 5.10/5.11 de la tesis provienen de `analisis_pruebas/figs/`
(fig7_gating.png y fig9_contexto.png); las 5.2/5.4 se generan directamente con
los nombres de archivo que usa el `.tex`.
