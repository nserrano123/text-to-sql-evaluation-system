# Requirements Document

## Introduction

Este documento especifica los requisitos para un sistema de evaluación de modelos text-to-SQL. El sistema permitirá a un evaluador calificar manualmente las consultas SQL generadas por un modelo de inteligencia artificial, utilizando métricas estándar de la industria para validar la calidad del modelo. El sistema incluirá una base de datos en Supabase para almacenar tanto los datos de referencia (gold standard) como las evaluaciones, una interfaz web para facilitar el proceso de calificación, y generación de gráficas para documentación de tesis.

## Glossary

- **Sistema**: El sistema de evaluación de modelos text-to-SQL
- **Evaluador**: Usuario humano que califica las respuestas del modelo
- **Investigador**: Usuario que realiza las evaluaciones y genera reportes para la tesis
- **Consulta de Referencia**: Consulta SQL correcta que sirve como gold standard
- **Consulta Generada**: Consulta SQL producida por el modelo de IA
- **Gold Database**: Base de datos que contiene las consultas de referencia y contexto
- **Evaluation Database**: Base de datos que almacena las métricas y calificaciones
- **Supabase**: Plataforma de base de datos PostgreSQL utilizada para almacenamiento
- **EX (Execution Accuracy)**: Métrica que mide el porcentaje de consultas con resultados correctos
- **TTA (Time-to-Answer)**: Métrica que mide el tiempo promedio de respuesta
- **Component Matching**: Métrica que evalúa la coincidencia exacta de componentes SQL
- **DDL**: Data Definition Language, lenguaje de definición de datos
- **Interfaz de Calificación**: Aplicación web frontend para evaluar consultas
- **F1 Score**: Métrica que combina precisión y recall para evaluar la calidad de coincidencia de componentes

## Requirements

### Requirement 1

**User Story:** Como administrador del sistema, quiero almacenar los datos de referencia en Supabase, para que sirvan como base gold para todas las evaluaciones del modelo.

#### Acceptance Criteria

1. WHEN el sistema se inicializa THEN el Sistema SHALL crear una tabla llamada `gold_queries` en Supabase con los campos: id, chat_input, session_id, member_id, clasificacion, pregunta_descompuesta, tablas_columnas_ddl, sql_reference, created_at
2. WHEN se inserta un registro en `gold_queries` THEN el Sistema SHALL validar que todos los campos obligatorios estén presentes
3. WHEN se consulta la tabla `gold_queries` THEN el Sistema SHALL retornar todos los registros con sus relaciones intactas
4. WHEN se migran datos existentes THEN el Sistema SHALL preservar la integridad referencial de todos los registros

### Requirement 2

**User Story:** Como administrador del sistema, quiero almacenar las evaluaciones y métricas en una base de datos separada, para que pueda analizar el rendimiento del modelo de manera estructurada.

#### Acceptance Criteria

1. WHEN el sistema se inicializa THEN el Sistema SHALL crear una tabla llamada `evaluations` en Supabase con los campos: id, gold_query_id, generated_sql, evaluation_date, created_at
2. WHEN el sistema se inicializa THEN el Sistema SHALL crear una tabla llamada `execution_accuracy` en Supabase con los campos: id, evaluation_id, results_match, is_correct, evaluator_notes, created_at
3. WHEN el sistema se inicializa THEN el Sistema SHALL crear una tabla llamada `time_to_answer` en Supabase con los campos: id, evaluation_id, start_time, end_time, duration_seconds, created_at
4. WHEN el sistema se inicializa THEN el Sistema SHALL crear una tabla llamada `component_matching` en Supabase con los campos: id, evaluation_id, select_correct, where_correct, group_by_correct, order_by_correct, keywords_correct, f1_score, evaluator_notes, created_at
5. WHEN se inserta un registro de evaluación THEN el Sistema SHALL crear una foreign key válida hacia `gold_queries`

### Requirement 3

**User Story:** Como evaluador, quiero calcular la métrica Execution Accuracy (EX), para que pueda determinar el porcentaje de consultas que producen resultados correctos.

#### Acceptance Criteria

1. WHEN un evaluador marca una consulta como correcta o incorrecta THEN el Sistema SHALL almacenar el resultado en la tabla `execution_accuracy`
2. WHEN se solicita el cálculo de EX THEN el Sistema SHALL computar (número de consultas correctas / número total de consultas) × 100
3. WHEN se muestra el resultado de EX THEN el Sistema SHALL presentar el porcentaje con dos decimales
4. WHEN un evaluador agrega notas a una evaluación THEN el Sistema SHALL almacenar las notas en el campo `evaluator_notes`

### Requirement 4

**User Story:** Como evaluador, quiero medir el Time-to-Answer (TTA), para que pueda evaluar la velocidad de respuesta del modelo.

#### Acceptance Criteria

1. WHEN se inicia una evaluación THEN el Sistema SHALL registrar el timestamp de inicio en `start_time`
2. WHEN se completa una evaluación THEN el Sistema SHALL registrar el timestamp de finalización en `end_time`
3. WHEN se calcula TTA THEN el Sistema SHALL computar la diferencia en segundos entre `end_time` y `start_time`
4. WHEN se solicita el TTA promedio THEN el Sistema SHALL calcular el promedio de `duration_seconds` para todas las evaluaciones completadas

### Requirement 5

**User Story:** Como evaluador, quiero evaluar Component Matching para cada componente SQL, para que pueda identificar qué partes del SQL el modelo genera correctamente.

#### Acceptance Criteria

1. WHEN un evaluador califica una consulta THEN el Sistema SHALL permitir marcar como correcto o incorrecto cada componente: SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS
2. WHEN se evalúan componentes THEN el Sistema SHALL tratar cada componente como un conjunto sin orden específico
3. WHEN se calcula el F1 score THEN el Sistema SHALL computar el F1 score basado en la coincidencia exacta de conjuntos para cada componente
4. WHEN se almacena la evaluación de componentes THEN el Sistema SHALL guardar los resultados booleanos en los campos correspondientes de `component_matching`
5. WHEN un evaluador agrega notas sobre componentes THEN el Sistema SHALL almacenar las notas en el campo `evaluator_notes` de `component_matching`

### Requirement 6

**User Story:** Como evaluador, quiero una interfaz web intuitiva para calificar consultas, para que pueda realizar evaluaciones de manera eficiente y sin errores.

#### Acceptance Criteria

1. WHEN un evaluador accede a la interfaz THEN el Sistema SHALL mostrar una lista de consultas pendientes de evaluación
2. WHEN un evaluador selecciona una consulta THEN el Sistema SHALL mostrar lado a lado: la consulta de referencia, la consulta generada, y el contexto (chat_input, tablas_columnas_ddl)
3. WHEN un evaluador califica una consulta THEN el Sistema SHALL proporcionar controles para marcar Execution Accuracy como correcta o incorrecta
4. WHEN un evaluador califica componentes THEN el Sistema SHALL proporcionar checkboxes individuales para SELECT, WHERE, GROUP BY, ORDER BY, y KEYWORDS
5. WHEN un evaluador completa una evaluación THEN el Sistema SHALL guardar automáticamente todos los datos en Supabase
6. WHEN un evaluador guarda una evaluación THEN el Sistema SHALL mostrar la siguiente consulta pendiente automáticamente

### Requirement 7

**User Story:** Como evaluador, quiero ver el progreso de mis evaluaciones, para que pueda saber cuántas consultas he evaluado y cuántas quedan pendientes.

#### Acceptance Criteria

1. WHEN un evaluador accede al dashboard THEN el Sistema SHALL mostrar el número total de consultas a evaluar
2. WHEN un evaluador accede al dashboard THEN el Sistema SHALL mostrar el número de consultas evaluadas por el evaluador actual
3. WHEN un evaluador accede al dashboard THEN el Sistema SHALL mostrar el porcentaje de progreso de evaluación
4. WHEN un evaluador accede al dashboard THEN el Sistema SHALL mostrar las métricas agregadas actuales: EX promedio, TTA promedio, y F1 score promedio por componente

### Requirement 8

**User Story:** Como investigador, quiero generar gráficas visuales de los resultados de evaluación, para que pueda incluirlas en mi documento de tesis.

#### Acceptance Criteria

1. WHEN se solicita generar gráficas THEN el Sistema SHALL crear un gráfico de barras mostrando el porcentaje de Execution Accuracy (EX)
2. WHEN se solicita generar gráficas THEN el Sistema SHALL crear un gráfico de barras comparando el F1 score de cada componente SQL (SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS)
3. WHEN se solicita generar gráficas THEN el Sistema SHALL crear un histograma mostrando la distribución de Time-to-Answer (TTA)
4. WHEN se generan gráficas THEN el Sistema SHALL permitir exportarlas en formato PNG con resolución mínima de 300 DPI para publicación
5. WHEN se generan gráficas THEN el Sistema SHALL incluir etiquetas claras, leyendas, y títulos descriptivos en español
6. WHEN se generan gráficas THEN el Sistema SHALL usar una paleta de colores profesional adecuada para documentos académicos
7. WHEN se generan gráficas THEN el Sistema SHALL permitir personalizar el estilo y formato de las gráficas para diferentes tipos de publicación
8. WHEN se generan gráficas THEN el Sistema SHALL incluir metadatos de la evaluación (fecha, número de consultas, versión del modelo)

### Requirement 9

**User Story:** Como investigador, quiero exportar los resultados de las evaluaciones, para que pueda realizar análisis estadísticos externos y generar tablas para mi tesis.

#### Acceptance Criteria

1. WHEN un investigador solicita exportar datos THEN el Sistema SHALL generar un archivo CSV con todas las evaluaciones
2. WHEN se exportan datos THEN el Sistema SHALL incluir todos los campos de las tablas `evaluations`, `execution_accuracy`, `time_to_answer`, y `component_matching`
3. WHEN se exportan datos THEN el Sistema SHALL incluir los campos relevantes de `gold_queries` mediante joins
4. WHEN se completa la exportación THEN el Sistema SHALL proporcionar un enlace de descarga del archivo CSV
5. WHEN se exportan datos THEN el Sistema SHALL generar una tabla resumen en formato LaTeX compatible con IEEEtran para inclusión directa en la tesis

### Requirement 10

**User Story:** Como evaluador, quiero poder agregar comentarios y notas a cada evaluación, para que pueda documentar observaciones específicas sobre las consultas generadas.

#### Acceptance Criteria

1. WHEN un evaluador está calificando una consulta THEN el Sistema SHALL proporcionar un campo de texto para notas generales
2. WHEN un evaluador está calificando componentes THEN el Sistema SHALL proporcionar un campo de texto para notas específicas de componentes
3. WHEN se guardan las notas THEN el Sistema SHALL almacenar el texto en los campos `evaluator_notes` correspondientes
4. WHEN se visualizan evaluaciones previas THEN el Sistema SHALL mostrar las notas asociadas a cada evaluación

### Requirement 11

**User Story:** Como administrador del sistema, quiero configurar diferentes modelos de IA para evaluación, para que pueda comparar el rendimiento entre diferentes versiones o tipos de modelos.

#### Acceptance Criteria

1. WHEN se configura un nuevo modelo THEN el Sistema SHALL almacenar información del modelo (nombre, versión, tipo, parámetros)
2. WHEN se realiza una evaluación THEN el Sistema SHALL asociar la evaluación con el modelo específico utilizado
3. WHEN se calculan métricas THEN el Sistema SHALL permitir filtrar y comparar resultados por modelo
4. WHEN se generan reportes THEN el Sistema SHALL incluir comparaciones entre diferentes modelos
5. WHEN se exportan datos THEN el Sistema SHALL incluir información del modelo en los archivos exportados

### Requirement 12

**User Story:** Como investigador, quiero realizar análisis estadísticos avanzados de los resultados, para que pueda generar insights más profundos sobre el rendimiento del modelo.

#### Acceptance Criteria

1. WHEN se solicita análisis estadístico THEN el Sistema SHALL calcular intervalos de confianza para las métricas principales
2. WHEN se comparan modelos THEN el Sistema SHALL realizar pruebas de significancia estadística
3. WHEN se analizan patrones THEN el Sistema SHALL identificar tipos de consultas con mayor/menor accuracy
4. WHEN se generan reportes THEN el Sistema SHALL incluir análisis de correlación entre métricas
5. WHEN se exportan análisis THEN el Sistema SHALL generar tablas estadísticas en formato LaTeX para publicación académica
