# Implementation Plan

- [x] 1. Configurar estructura del proyecto y dependencias

  - Crear estructura de directorios para backend (Python/FastAPI) y frontend (React/TypeScript)
  - Configurar archivo requirements.txt con: fastapi, uvicorn, supabase, pydantic, pandas, matplotlib, seaborn, hypothesis, pytest
  - Configurar package.json con: react, typescript, recharts, tailwindcss, react-query, fast-check, jest
  - Crear archivos de configuración: .env.example, pytest.ini, jest.config.js
  - _Requirements: 1.1, 2.1-2.4_

- [x] 2. Implementar esquema de base de datos en Supabase

  - [x] 2.1 Crear script de migración SQL para todas las tablas

    - Escribir CREATE TABLE statements para: gold_queries, evaluations, execution_accuracy, time_to_answer, component_matching
    - Definir todas las foreign keys y constraints
    - Agregar índices en campos clave
    - _Requirements: 1.1, 2.1-2.4_

  - [x] 2.2 Escribir property test para validación de campos requeridos

    - **Property 1: Required field validation**
    - **Validates: Requirements 1.2**

  - [x] 2.3 Escribir property test para integridad de datos

    - **Property 2: Data integrity on query**
    - **Validates: Requirements 1.3**

  - [x] 2.4 Escribir property test para foreign keys

    - **Property 4: Foreign key enforcement**
    - **Validates: Requirements 2.5**

  - [x] 2.5 Escribir property tests adicionales para timestamp y componentes
    - **Property 9: Timestamp recording**
    - **Property 10: TTA calculation correctness**
    - **Property 12: Component evaluation completeness**
    - **Validates: Requirements 4.1, 4.2, 4.3, 5.1**

- [x] 3. Implementar modelos Pydantic y validación de datos

  - [x] 3.1 Crear modelos Pydantic para todas las entidades

    - Implementar clases: GoldQuery, Evaluation, ExecutionAccuracy, TimeToAnswer, ComponentMatching, MetricsSummary
    - Agregar validadores personalizados (ej: duration_seconds debe coincidir con diferencia de timestamps)
    - _Requirements: 1.2, 2.5_

  - [x] 3.2 Escribir unit tests para validadores Pydantic
    - Test que verifica rechazo de campos faltantes
    - Test que verifica validación de timestamps
    - _Requirements: 1.2_

- [x] 4. Implementar cliente Supabase y operaciones CRUD

  - [x] 4.1 Crear módulo de conexión a Supabase

    - Implementar singleton para cliente Supabase
    - Configurar manejo de credenciales desde variables de entorno
    - _Requirements: 1.1, 2.1_

  - [x] 4.2 Implementar repositorio para gold_queries

    - Métodos: create, get_by_id, get_all, get_pending
    - _Requirements: 1.1-1.4_

  - [x] 4.3 Implementar repositorio para evaluations

    - Métodos: create, get_by_id, get_all, update, delete
    - _Requirements: 2.1, 3.1_

  - [x] 4.4 Implementar repositorios para métricas

    - Repositorios para execution_accuracy, time_to_answer, component_matching
    - Métodos CRUD básicos para cada tabla de métricas
    - _Requirements: 2.2-2.4_

  - [x] 4.5 Escribir property test para persistencia de evaluaciones

    - **Property 5: Evaluation storage**
    - **Validates: Requirements 3.1**

  - [x] 4.6 Escribir property test para round-trip de notas
    - **Property 8: Notes round-trip**
    - **Validates: Requirements 3.4, 5.5, 10.3**

- [x] 5. Implementar servicios de cálculo de métricas

  - [x] 5.1 Implementar servicio de métricas EX

    - Función calculate_ex: (consultas correctas / total) × 100
    - Formatear resultado con 2 decimales
    - _Requirements: 3.2, 3.3_

  - [x] 5.2 Escribir property test para cálculo de EX

    - **Property 6: EX calculation correctness**
    - **Validates: Requirements 3.2**

  - [x] 5.3 Escribir property test para formato de EX

    - **Property 7: EX formatting**
    - **Validates: Requirements 3.3**

  - [x] 5.4 Implementar servicio de métricas TTA

    - Función calculate_tta: diferencia entre end_time y start_time
    - Función calculate_average_tta: promedio de duration_seconds
    - _Requirements: 4.3, 4.4_

  - [x] 5.5 Escribir property test para cálculo de TTA

    - **Property 10: TTA calculation correctness**
    - **Validates: Requirements 4.3**

  - [x] 5.6 Escribir property test para promedio de TTA

    - **Property 11: Average TTA calculation**
    - **Validates: Requirements 4.4**

  - [x] 5.7 Implementar servicio de métricas de componentes

    - Función calculate_f1_score: F1 = 2 × (precision × recall) / (precision + recall)
    - Calcular F1 por cada componente SQL
    - _Requirements: 5.3_

  - [x] 5.8 Escribir property test para cálculo de F1

    - **Property 13: F1 score calculation**
    - **Validates: Requirements 5.3**

  - [x] 5.9 Implementar servicio de resumen de métricas

    - Función get_metrics_summary: agregar todas las métricas en un solo objeto
    - _Requirements: 7.4_

  - [x] 5.10 Escribir property test para métricas agregadas
    - **Property 20: Aggregated metrics accuracy**
    - **Validates: Requirements 7.4**

- [x] 6. Checkpoint - Verificar que todas las pruebas pasen

  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implementar endpoints de API con FastAPI

  - [x] 7.1 Crear endpoints para gold_queries

    - GET /api/gold-queries, GET /api/gold-queries/:id, POST /api/gold-queries, GET /api/gold-queries/pending
    - Integrar con repositorios implementados
    - _Requirements: 1.1-1.4_

  - [x] 7.2 Crear endpoints para evaluations

    - GET /api/evaluations, GET /api/evaluations/:id, POST /api/evaluations, PUT /api/evaluations/:id, DELETE /api/evaluations/:id
    - Integrar con repositorios implementados
    - _Requirements: 2.1, 3.1, 6.5_

  - [x] 7.3 Escribir property test para persistencia completa

    - **Property 17: Evaluation persistence**
    - **Validates: Requirements 6.5**

  - [x] 7.4 Crear endpoints para métricas

    - GET /api/metrics/execution-accuracy, GET /api/metrics/time-to-answer, GET /api/metrics/component-matching, GET /api/metrics/summary
    - Integrar con servicios de métricas implementados
    - _Requirements: 3.2, 4.4, 5.3, 7.4_

  - [x] 7.5 Escribir property test para conteos del dashboard
    - **Property 19: Dashboard counts accuracy**
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [x] 8. Implementar servicios de generación de gráficas

  - [x] 8.1 Crear servicio de gráficas EX

    - Función generate_ex_chart: gráfico de barras para Execution Accuracy
    - Configurar resolución a 300 DPI y etiquetas en español
    - _Requirements: 8.1, 8.4, 8.5_

  - [x] 8.2 Crear servicio de gráficas de componentes

    - Función generate_component_chart: gráfico de barras comparando F1 scores por componente
    - Configurar resolución a 300 DPI y etiquetas en español
    - _Requirements: 8.2, 8.4, 8.5_

  - [ ] 8.3 Crear servicio de histograma TTA

    - Función generate_tta_histogram: histograma de distribución de TTA
    - Configurar resolución a 300 DPI y etiquetas en español
    - _Requirements: 8.3, 8.4, 8.5_

  - [x] 8.4 Escribir property test para validez de gráficas

    - **Property 21: Chart generation validity**
    - **Validates: Requirements 8.1, 8.2, 8.3**

  - [x] 8.5 Escribir property test para resolución de gráficas

    - **Property 22: Chart resolution requirement**
    - **Validates: Requirements 8.4**

  - [x] 8.6 Escribir property test para idioma de gráficas

    - **Property 23: Chart language requirement**
    - **Validates: Requirements 8.5**

  - [x] 8.7 Crear endpoints para generación de gráficas
    - POST /api/charts/execution-accuracy, POST /api/charts/component-matching, POST /api/charts/time-distribution
    - Integrar con servicios de gráficas implementados
    - _Requirements: 8.1-8.5_

- [x] 9. Implementar servicios de exportación de datos

  - [x] 9.1 Crear servicio de exportación CSV

    - Función export_to_csv con Pandas: realizar joins entre todas las tablas
    - Generar CSV con todos los campos
    - _Requirements: 9.1, 9.2, 9.3_

  - [x] 9.2 Escribir property test para completitud de CSV

    - **Property 24: CSV export completeness**
    - **Validates: Requirements 9.1, 9.2, 9.3**

  - [x] 9.3 Crear servicio de exportación LaTeX

    - Función export_to_latex: generar tabla resumen en formato IEEEtran
    - Incluir métricas principales
    - _Requirements: 9.5_

  - [x] 9.4 Escribir property test para validez de LaTeX

    - **Property 26: LaTeX export validity**
    - **Validates: Requirements 9.5**

  - [x] 9.5 Crear endpoints de exportación

    - GET /api/export/csv, GET /api/export/latex
    - Implementar generación de enlaces de descarga
    - Integrar con servicios de exportación implementados
    - _Requirements: 9.1-9.5_

  - [x] 9.6 Escribir property test para disponibilidad de descarga
    - **Property 25: Export download availability**
    - **Validates: Requirements 9.4**

- [x] 10. Checkpoint - Verificar que el backend esté completo

  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implementar estructura base del frontend

  - [x] 11.1 Configurar React Router y estructura de páginas

    - Crear rutas para: Dashboard, Evaluation, Results, Export
    - Crear componentes de página básicos
    - _Requirements: 6.1-6.6, 7.1-7.4_

  - [x] 11.2 Crear servicios de API del frontend

    - Implementar funciones para llamar a todos los endpoints del backend
    - Configurar axios con base URL y manejo de errores
    - _Requirements: 6.5, 6.6_

  - [x] 11.3 Crear hooks personalizados de React Query

    - Hooks para queries y mutations de gold_queries, evaluations, métricas
    - _Requirements: 6.5, 6.6_

  - [x] 11.4 Crear tipos TypeScript para el frontend

    - Interfaces que correspondan a los modelos Pydantic del backend
    - _Requirements: 6.1-6.6_

  - [x] 11.5 Crear componente QueryComparison

    - Mostrar consulta gold vs generada lado a lado
    - Mostrar contexto: chat_input, tablas_columnas_ddl
    - _Requirements: 6.2_

  - [x] 11.6 Escribir property test para completitud de display
    - **Property 16: Query display completeness**
    - **Validates: Requirements 6.2**

- [x] 12. Implementar página de evaluación

  - [x] 12.1 Crear componente ExecutionAccuracyForm

    - Botones para marcar correcto/incorrecto
    - Campo de texto para notas
    - _Requirements: 6.3, 10.1_

  - [x] 12.2 Crear componente ComponentEvaluator

    - Checkboxes para SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS
    - Campo de texto para notas de componentes
    - _Requirements: 6.4, 10.2_

  - [x] 12.3 Escribir property test para completitud de componentes

    - **Property 12: Component evaluation completeness**
    - **Validates: Requirements 5.1**

  - [x] 12.4 Implementar página EvaluationPage completa

    - Integrar QueryComparison, ExecutionAccuracyForm, ComponentEvaluator
    - Implementar lógica de guardado automático
    - Navegar automáticamente a siguiente consulta pendiente
    - _Requirements: 6.5, 6.6_

  - [x] 12.5 Escribir property test para navegación automática

    - **Property 18: Next query navigation**
    - **Validates: Requirements 6.6**

  - [-] 12.6 Implementar tracking de tiempo (TTA)

    - Registrar start_time al cargar consulta
    - Registrar end_time al guardar evaluación
    - _Requirements: 4.1, 4.2_

  - [x] 12.7 Escribir property test para registro de timestamps
    - **Property 9: Timestamp recording**
    - **Validates: Requirements 4.1, 4.2**

- [x] 13. Implementar página de dashboard

  - [x] 13.1 Crear componente ProgressIndicator

    - Mostrar total de consultas, evaluadas, y porcentaje
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 13.2 Crear componente MetricsCard

    - Mostrar EX promedio, TTA promedio, F1 scores por componente
    - _Requirements: 7.4_

  - [x] 13.3 Crear componente PendingQueriesList

    - Mostrar consultas sin evaluación
    - Permitir seleccionar para evaluar
    - _Requirements: 6.1_

  - [x] 13.4 Implementar página DashboardPage completa

    - Integrar ProgressIndicator, MetricsCard, PendingQueriesList
    - Conectar con hooks de React Query para datos en tiempo real
    - _Requirements: 6.1, 7.1-7.4_

  - [ ] 13.5 Escribir property test para listado de pendientes
    - **Property 15: Pending queries listing**
    - **Validates: Requirements 6.1**

- [ ] 14. Implementar página de resultados y visualización

  - [x] 14.1 Crear componente ChartViewer

    - Componente genérico para mostrar gráficas PNG del backend
    - Permitir descargar gráficas generadas
    - _Requirements: 8.1-8.5_

  - [x] 14.2 Crear componentes específicos de gráficas

    - ExChart: vista de gráfico de EX
    - ComponentChart: vista de gráfico de componentes
    - TtaHistogram: vista de histograma TTA
    - _Requirements: 8.1-8.3_

  - [x] 14.3 Implementar página ResultsPage completa

    - Integrar todos los componentes de gráficas
    - Conectar con servicios de API para generar gráficas
    - _Requirements: 8.1-8.5_

- [x] 15. Implementar página de exportación

  - [x] 15.1 Crear componente ExportButton

    - Componente genérico para botones de exportación
    - Manejar estados de carga y descarga
    - _Requirements: 9.1-9.5_

  - [ ] 15.2 Implementar página ExportPage completa

    - Botón de exportación CSV
    - Botón de exportación LaTeX
    - Botones de descarga de gráficas individuales
    - Conectar con servicios de API de exportación
    - _Requirements: 9.1-9.5, 8.4_

- [ ] 16. Implementar manejo de errores y validación

  - [ ] 16.1 Agregar manejo de errores en backend

    - Implementar middleware de manejo de excepciones en FastAPI
    - Retornar códigos HTTP apropiados (400, 422, 500, 504)
    - _Requirements: 1.2, 2.5_

  - [ ] 16.2 Agregar manejo de errores en frontend

    - Componente ErrorBoundary para errores de React
    - Mostrar mensajes de error amigables
    - Implementar retry logic para fallos de red en servicios de API
    - _Requirements: 6.5_

  - [ ]\* 16.3 Escribir unit tests para validación de errores
    - Test para campos faltantes
    - Test para foreign keys inválidas
    - Test para timestamps inválidos
    - _Requirements: 1.2, 2.5_

- [ ] 17. Implementar optimizaciones de performance

  - [ ] 17.1 Implementar caching de métricas en backend

    - Cache en memoria con invalidación al crear evaluación
    - _Requirements: 7.4_

  - [ ] 17.2 Implementar paginación en backend y frontend

        - Endpoints con paginación para listas grandes
        - Componentes de paginación en frontend (20 por página)
        - _Requirements: 6.1_

    <!--

- [ ] 18. Configurar autenticación y seguridad

  - [ ] 18.1 Configurar Supabase Auth en backend

    - Implementar middleware de autenticación JWT
    - Validar tokens en endpoints protegidos
    - _Requirements: 6.1-6.6_

  - [ ] 18.2 Implementar autenticación en frontend

    - Componentes de login/logout
    - Context de autenticación
    - Protección de rutas
    - _Requirements: 6.1-6.6_

  - [ ] 18.3 Configurar Row Level Security en Supabase

    - Configurar políticas RLS para todas las tablas
    - _Requirements: 2.1-2.4_

  - [ ] 18.4 Configurar rate limiting en backend
    - Limitar a 100 requests por minuto
    - _Requirements: 6.5_
      -->

- [ ] 19. Checkpoint final - Verificar sistema completo

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 20. Crear documentación y scripts de deployment

  - [ ] 20.1 Crear README con instrucciones de instalación

    - Documentar setup de desarrollo para backend y frontend
    - Documentar variables de entorno requeridas
    - Instrucciones de migración de base de datos
    - _Requirements: 1.1, 2.1_

  - [ ] 20.2 Crear script de migración de datos

    - Script para migrar datos existentes a gold_queries
    - _Requirements: 1.4_

  - [ ]\* 20.3 Escribir property test para migración

    - **Property 3: Migration preserves data**
    - **Validates: Requirements 1.4**

  - [ ] 20.4 Crear archivos de configuración de deployment

    - Docker files para backend y frontend
    - Scripts de deployment
    - _Requirements: All_
