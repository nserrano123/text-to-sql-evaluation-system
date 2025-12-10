# Implementation Plan

- [x] 1. Configurar estructura del proyecto y dependencias

  - Crear estructura de directorios para backend (Python/FastAPI) y frontend (React/TypeScript)
  - Configurar archivo requirements.txt con: fastapi, uvicorn, supabase, pydantic, pandas, matplotlib, seaborn, hypothesis, pytest
  - Configurar package.json con: react, typescript, recharts, tailwindcss, react-query, fast-check, jest
  - Crear archivos de configuración: .env.example, pytest.ini, jest.config.js
  - _Requirements: 1.1, 2.1-2.4_

- [ ] 2. Implementar esquema de base de datos en Supabase

  - [x] 2.1 Crear script de migración SQL para todas las tablas

    - Escribir CREATE TABLE statements para: gold_queries, evaluations, execution_accuracy, time_to_answer, component_matching
    - Definir todas las foreign keys y constraints
    - Agregar índices en campos clave
    - _Requirements: 1.1, 2.1-2.4_

  - [-] 2.2 Escribir property test para validación de campos requeridos

    - **Property 1: Required field validation**
    - **Validates: Requirements 1.2**

  - [ ] 2.3 Escribir property test para integridad de datos

    - **Property 2: Data integrity on query**
    - **Validates: Requirements 1.3**

  - [ ] 2.4 Escribir property test para foreign keys
    - **Property 4: Foreign key enforcement**
    - **Validates: Requirements 2.5**

- [ ] 3. Implementar modelos Pydantic y validación de datos

  - [ ] 3.1 Crear modelos Pydantic para todas las entidades

    - Implementar clases: GoldQuery, Evaluation, ExecutionAccuracy, TimeToAnswer, ComponentMatching, MetricsSummary
    - Agregar validadores personalizados (ej: duration_seconds debe coincidir con diferencia de timestamps)
    - _Requirements: 1.2, 2.5_

  - [ ]\* 3.2 Escribir unit tests para validadores Pydantic
    - Test que verifica rechazo de campos faltantes
    - Test que verifica validación de timestamps
    - _Requirements: 1.2_

- [ ] 4. Implementar cliente Supabase y operaciones CRUD

  - [ ] 4.1 Crear módulo de conexión a Supabase

    - Implementar singleton para cliente Supabase
    - Configurar manejo de credenciales desde variables de entorno
    - _Requirements: 1.1, 2.1_

  - [ ] 4.2 Implementar repositorio para gold_queries

    - Métodos: create, get_by_id, get_all, get_pending
    - _Requirements: 1.1-1.4_

  - [ ] 4.3 Implementar repositorio para evaluations

    - Métodos: create, get_by_id, get_all, update, delete
    - _Requirements: 2.1, 3.1_

  - [ ]\* 4.4 Escribir property test para persistencia de evaluaciones

    - **Property 5: Evaluation storage**
    - **Validates: Requirements 3.1**

  - [ ]\* 4.5 Escribir property test para round-trip de notas
    - **Property 8: Notes round-trip**
    - **Validates: Requirements 3.4, 5.5, 10.3**

- [ ] 5. Implementar cálculo de métricas

  - [ ] 5.1 Implementar función calculate_ex

    - Calcular (consultas correctas / total) × 100
    - Formatear resultado con 2 decimales
    - _Requirements: 3.2, 3.3_

  - [ ]\* 5.2 Escribir property test para cálculo de EX

    - **Property 6: EX calculation correctness**
    - **Validates: Requirements 3.2**

  - [ ]\* 5.3 Escribir property test para formato de EX

    - **Property 7: EX formatting**
    - **Validates: Requirements 3.3**

  - [ ] 5.4 Implementar función calculate_tta

    - Calcular diferencia entre end_time y start_time
    - Calcular promedio de duration_seconds
    - _Requirements: 4.3, 4.4_

  - [ ]\* 5.5 Escribir property test para cálculo de TTA

    - **Property 10: TTA calculation correctness**
    - **Validates: Requirements 4.3**

  - [ ]\* 5.6 Escribir property test para promedio de TTA

    - **Property 11: Average TTA calculation**
    - **Validates: Requirements 4.4**

  - [ ] 5.7 Implementar función calculate_f1_score

    - Calcular F1 = 2 × (precision × recall) / (precision + recall)
    - Calcular F1 por cada componente SQL
    - _Requirements: 5.3_

  - [ ]\* 5.8 Escribir property test para cálculo de F1

    - **Property 13: F1 score calculation**
    - **Validates: Requirements 5.3**

  - [ ] 5.9 Implementar función get_metrics_summary

    - Agregar todas las métricas en un solo objeto
    - _Requirements: 7.4_

  - [ ]\* 5.10 Escribir property test para métricas agregadas
    - **Property 20: Aggregated metrics accuracy**
    - **Validates: Requirements 7.4**

- [ ] 6. Checkpoint - Verificar que todas las pruebas pasen

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implementar endpoints de API con FastAPI

  - [ ] 7.1 Crear endpoints para gold_queries

    - GET /api/gold-queries, GET /api/gold-queries/:id, POST /api/gold-queries, GET /api/gold-queries/pending
    - _Requirements: 1.1-1.4_

  - [ ] 7.2 Crear endpoints para evaluations

    - GET /api/evaluations, GET /api/evaluations/:id, POST /api/evaluations, PUT /api/evaluations/:id, DELETE /api/evaluations/:id
    - _Requirements: 2.1, 3.1, 6.5_

  - [ ]\* 7.3 Escribir property test para persistencia completa

    - **Property 17: Evaluation persistence**
    - **Validates: Requirements 6.5**

  - [ ] 7.4 Crear endpoints para métricas

    - GET /api/metrics/execution-accuracy, GET /api/metrics/time-to-answer, GET /api/metrics/component-matching, GET /api/metrics/summary
    - _Requirements: 3.2, 4.4, 5.3, 7.4_

  - [ ]\* 7.5 Escribir property test para conteos del dashboard
    - **Property 19: Dashboard counts accuracy**
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [ ] 8. Implementar generación de gráficas con Matplotlib

  - [ ] 8.1 Crear función generate_ex_chart

    - Generar gráfico de barras para Execution Accuracy
    - Configurar resolución a 300 DPI
    - Agregar etiquetas en español
    - _Requirements: 8.1, 8.4, 8.5_

  - [ ] 8.2 Crear función generate_component_chart

    - Generar gráfico de barras comparando F1 scores por componente
    - Configurar resolución a 300 DPI
    - Agregar etiquetas en español
    - _Requirements: 8.2, 8.4, 8.5_

  - [ ] 8.3 Crear función generate_tta_histogram

    - Generar histograma de distribución de TTA
    - Configurar resolución a 300 DPI
    - Agregar etiquetas en español
    - _Requirements: 8.3, 8.4, 8.5_

  - [ ]\* 8.4 Escribir property test para validez de gráficas

    - **Property 21: Chart generation validity**
    - **Validates: Requirements 8.1, 8.2, 8.3**

  - [ ]\* 8.5 Escribir property test para resolución de gráficas

    - **Property 22: Chart resolution requirement**
    - **Validates: Requirements 8.4**

  - [ ]\* 8.6 Escribir property test para idioma de gráficas

    - **Property 23: Chart language requirement**
    - **Validates: Requirements 8.5**

  - [ ] 8.7 Crear endpoints para generación de gráficas
    - POST /api/charts/execution-accuracy, POST /api/charts/component-matching, POST /api/charts/time-distribution
    - _Requirements: 8.1-8.5_

- [ ] 9. Implementar exportación de datos

  - [ ] 9.1 Crear función export_to_csv con Pandas

    - Realizar joins entre todas las tablas
    - Generar CSV con todos los campos
    - _Requirements: 9.1, 9.2, 9.3_

  - [ ]\* 9.2 Escribir property test para completitud de CSV

    - **Property 24: CSV export completeness**
    - **Validates: Requirements 9.1, 9.2, 9.3**

  - [ ] 9.3 Crear función export_to_latex

    - Generar tabla resumen en formato IEEEtran
    - Incluir métricas principales
    - _Requirements: 9.5_

  - [ ]\* 9.4 Escribir property test para validez de LaTeX

    - **Property 26: LaTeX export validity**
    - **Validates: Requirements 9.5**

  - [ ] 9.5 Crear endpoints de exportación

    - GET /api/export/csv, GET /api/export/latex
    - Implementar generación de enlaces de descarga
    - _Requirements: 9.1-9.5_

  - [ ]\* 9.6 Escribir property test para disponibilidad de descarga
    - **Property 25: Export download availability**
    - **Validates: Requirements 9.4**

- [ ] 10. Checkpoint - Verificar que el backend esté completo

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implementar componentes base del frontend

  - [ ] 11.1 Configurar React Router y estructura de páginas

    - Crear rutas para: Dashboard, Evaluation, Results, Export
    - _Requirements: 6.1-6.6, 7.1-7.4_

  - [ ] 11.2 Configurar React Query para gestión de estado

    - Crear hooks personalizados para queries y mutations
    - _Requirements: 6.5, 6.6_

  - [ ] 11.3 Crear componente QueryComparison

    - Mostrar consulta gold vs generada lado a lado
    - Mostrar contexto: chat_input, tablas_columnas_ddl
    - _Requirements: 6.2_

  - [ ]\* 11.4 Escribir property test para completitud de display
    - **Property 16: Query display completeness**
    - **Validates: Requirements 6.2**

- [ ] 12. Implementar página de evaluación

  - [ ] 12.1 Crear componente ExecutionAccuracyForm

    - Botones para marcar correcto/incorrecto
    - Campo de texto para notas
    - _Requirements: 6.3, 10.1_

  - [ ] 12.2 Crear componente ComponentEvaluator

    - Checkboxes para SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS
    - Campo de texto para notas de componentes
    - _Requirements: 6.4, 10.2_

  - [ ]\* 12.3 Escribir property test para completitud de componentes

    - **Property 12: Component evaluation completeness**
    - **Validates: Requirements 5.1**

  - [ ] 12.4 Implementar lógica de guardado automático

    - Guardar evaluación al completar
    - Navegar automáticamente a siguiente consulta pendiente
    - _Requirements: 6.5, 6.6_

  - [ ]\* 12.5 Escribir property test para navegación automática

    - **Property 18: Next query navigation**
    - **Validates: Requirements 6.6**

  - [ ] 12.6 Implementar tracking de tiempo (TTA)

    - Registrar start_time al cargar consulta
    - Registrar end_time al guardar evaluación
    - _Requirements: 4.1, 4.2_

  - [ ]\* 12.7 Escribir property test para registro de timestamps
    - **Property 9: Timestamp recording**
    - **Validates: Requirements 4.1, 4.2**

- [ ] 13. Implementar página de dashboard

  - [ ] 13.1 Crear componente ProgressIndicator

    - Mostrar total de consultas, evaluadas, y porcentaje
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ] 13.2 Crear componente MetricsCard

    - Mostrar EX promedio, TTA promedio, F1 scores por componente
    - _Requirements: 7.4_

  - [ ] 13.3 Implementar lista de consultas pendientes

    - Mostrar consultas sin evaluación
    - Permitir seleccionar para evaluar
    - _Requirements: 6.1_

  - [ ]\* 13.4 Escribir property test para listado de pendientes
    - **Property 15: Pending queries listing**
    - **Validates: Requirements 6.1**

- [ ] 14. Implementar página de resultados y visualización

  - [ ] 14.1 Crear componente ChartViewer

    - Integrar con Recharts para mostrar gráficas
    - Permitir descargar gráficas generadas por el backend
    - _Requirements: 8.1-8.5_

  - [ ] 14.2 Implementar vista de gráfico de EX

    - Solicitar gráfico al backend
    - Mostrar imagen PNG
    - _Requirements: 8.1_

  - [ ] 14.3 Implementar vista de gráfico de componentes

    - Solicitar gráfico al backend
    - Mostrar imagen PNG
    - _Requirements: 8.2_

  - [ ] 14.4 Implementar vista de histograma TTA
    - Solicitar gráfico al backend
    - Mostrar imagen PNG
    - _Requirements: 8.3_

- [ ] 15. Implementar página de exportación

  - [ ] 15.1 Crear botón de exportación CSV

    - Solicitar CSV al backend
    - Descargar archivo automáticamente
    - _Requirements: 9.1-9.4_

  - [ ] 15.2 Crear botón de exportación LaTeX

    - Solicitar LaTeX al backend
    - Descargar archivo automáticamente
    - _Requirements: 9.5_

  - [ ] 15.3 Crear botones de descarga de gráficas
    - Permitir descargar cada gráfica individualmente
    - _Requirements: 8.4_

- [ ] 16. Implementar manejo de errores y validación

  - [ ] 16.1 Agregar manejo de errores en backend

    - Implementar middleware de manejo de excepciones
    - Retornar códigos HTTP apropiados (400, 422, 500, 504)
    - _Requirements: 1.2, 2.5_

  - [ ] 16.2 Agregar manejo de errores en frontend

    - Mostrar mensajes de error amigables
    - Implementar retry logic para fallos de red
    - _Requirements: 6.5_

  - [ ]\* 16.3 Escribir unit tests para validación de errores
    - Test para campos faltantes
    - Test para foreign keys inválidas
    - Test para timestamps inválidos
    - _Requirements: 1.2, 2.5_

- [ ] 17. Implementar optimizaciones de performance

  - [ ] 17.1 Agregar índices a base de datos

    - Crear índices en gold_queries.id, evaluations.gold_query_id, evaluations.evaluation_date
    - _Requirements: 1.3, 2.1_

  - [ ] 17.2 Implementar caching de métricas

    - Cache con invalidación al crear evaluación
    - _Requirements: 7.4_

  - [ ] 17.3 Implementar paginación en frontend
    - Paginar listas de evaluaciones (20 por página)
    - _Requirements: 6.1_

- [ ] 18. Configurar autenticación y seguridad

  - [ ] 18.1 Configurar Supabase Auth

    - Implementar login/logout
    - Configurar JWT tokens
    - _Requirements: 6.1-6.6_

  - [ ] 18.2 Implementar Row Level Security en Supabase

    - Configurar políticas RLS para todas las tablas
    - _Requirements: 2.1-2.4_

  - [ ] 18.3 Configurar CORS y rate limiting en backend
    - Limitar a 100 requests por minuto
    - _Requirements: 6.5_

- [ ] 19. Checkpoint final - Verificar sistema completo

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 20. Crear documentación y scripts de deployment

  - [ ] 20.1 Crear README con instrucciones de instalación

    - Documentar setup de desarrollo
    - Documentar variables de entorno
    - _Requirements: 1.1, 2.1_

  - [ ] 20.2 Crear script de migración de datos

    - Script para migrar datos existentes a gold_queries
    - _Requirements: 1.4_

  - [ ]\* 20.3 Escribir property test para migración

    - **Property 3: Migration preserves data**
    - **Validates: Requirements 1.4**

  - [ ] 20.3 Configurar CI/CD con GitHub Actions
    - Ejecutar tests automáticamente
    - Deploy a staging
    - _Requirements: All_
