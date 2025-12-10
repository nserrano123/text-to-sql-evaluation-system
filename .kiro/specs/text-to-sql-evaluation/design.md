# Design Document

## Overview

El sistema de evaluación de modelos text-to-SQL es una aplicación web full-stack que permite evaluar la calidad de consultas SQL generadas por modelos de IA. El sistema consta de tres componentes principales:

1. **Base de datos Supabase**: Almacena datos gold y evaluaciones
2. **Backend API**: Proporciona endpoints para CRUD de evaluaciones y cálculo de métricas
3. **Frontend Web**: Interfaz de usuario para calificación y visualización de resultados

El sistema implementa tres métricas estándar de evaluación text-to-SQL:

- **Execution Accuracy (EX)**: Porcentaje de consultas con resultados correctos
- **Time-to-Answer (TTA)**: Tiempo promedio de respuesta
- **Component Matching**: Evaluación granular de componentes SQL con F1 score

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React +      │
│   TypeScript)   │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend API   │
│   (Python +     │
│   FastAPI)      │
└────────┬────────┘
         │ PostgreSQL
         │ Protocol
┌────────▼────────┐
│   Supabase      │
│   (PostgreSQL)  │
└─────────────────┘
```

### Technology Stack

**Frontend:**

- React 18+ con TypeScript
- Recharts para visualización de gráficas
- TailwindCSS para estilos
- React Query para gestión de estado del servidor

**Backend:**

- Python 3.10+ con FastAPI
- Supabase Python Client para interacción con base de datos
- Matplotlib/Seaborn para generación de gráficas PNG
- Pandas para procesamiento de datos y exportación CSV
- Pydantic para validación de datos

**Database:**

- Supabase (PostgreSQL)
- Row Level Security (RLS) para seguridad

## Components and Interfaces

### Database Schema

#### Table: `gold_queries`

```sql
CREATE TABLE gold_queries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  chat_input TEXT NOT NULL,
  session_id VARCHAR(255),
  member_id VARCHAR(255),
  clasificacion VARCHAR(100),
  pregunta_descompuesta TEXT,
  tablas_columnas_ddl TEXT NOT NULL,
  sql_reference TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Table: `evaluations`

```sql
CREATE TABLE evaluations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  gold_query_id UUID NOT NULL REFERENCES gold_queries(id) ON DELETE CASCADE,
  generated_sql TEXT NOT NULL,
  evaluation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Table: `execution_accuracy`

```sql
CREATE TABLE execution_accuracy (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  evaluation_id UUID NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
  results_match BOOLEAN,
  is_correct BOOLEAN NOT NULL,
  evaluator_notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Table: `time_to_answer`

```sql
CREATE TABLE time_to_answer (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  evaluation_id UUID NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
  start_time TIMESTAMP WITH TIME ZONE NOT NULL,
  end_time TIMESTAMP WITH TIME ZONE NOT NULL,
  duration_seconds NUMERIC(10, 2) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Table: `component_matching`

```sql
CREATE TABLE component_matching (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  evaluation_id UUID NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
  select_correct BOOLEAN NOT NULL,
  where_correct BOOLEAN NOT NULL,
  group_by_correct BOOLEAN NOT NULL,
  order_by_correct BOOLEAN NOT NULL,
  keywords_correct BOOLEAN NOT NULL,
  f1_score NUMERIC(5, 4),
  evaluator_notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Backend API Endpoints

#### Evaluations

- `GET /api/evaluations` - Listar todas las evaluaciones
- `GET /api/evaluations/:id` - Obtener evaluación específica
- `POST /api/evaluations` - Crear nueva evaluación
- `PUT /api/evaluations/:id` - Actualizar evaluación
- `DELETE /api/evaluations/:id` - Eliminar evaluación

#### Gold Queries

- `GET /api/gold-queries` - Listar consultas gold
- `GET /api/gold-queries/:id` - Obtener consulta gold específica
- `POST /api/gold-queries` - Crear consulta gold
- `GET /api/gold-queries/pending` - Obtener consultas pendientes de evaluación

#### Metrics

- `GET /api/metrics/execution-accuracy` - Calcular EX global
- `GET /api/metrics/time-to-answer` - Calcular TTA promedio
- `GET /api/metrics/component-matching` - Calcular F1 scores por componente
- `GET /api/metrics/summary` - Obtener resumen de todas las métricas

#### Export & Visualization

- `GET /api/export/csv` - Exportar datos en CSV
- `GET /api/export/latex` - Exportar tabla resumen en LaTeX
- `POST /api/charts/execution-accuracy` - Generar gráfico EX (PNG)
- `POST /api/charts/component-matching` - Generar gráfico componentes (PNG)
- `POST /api/charts/time-distribution` - Generar histograma TTA (PNG)

### Frontend Components

#### Pages

- `DashboardPage` - Vista principal con estadísticas y progreso
- `EvaluationPage` - Interfaz de calificación de consultas
- `ResultsPage` - Visualización de resultados y gráficas
- `ExportPage` - Exportación de datos y gráficas

#### Components

- `QueryComparison` - Muestra consulta gold vs generada lado a lado
- `ComponentEvaluator` - Checkboxes para evaluar componentes SQL
- `ExecutionAccuracyForm` - Formulario para marcar correctitud
- `ProgressIndicator` - Barra de progreso de evaluaciones
- `MetricsCard` - Tarjeta con métrica individual
- `ChartViewer` - Visualizador de gráficas generadas

## Data Models

### Python Models (Pydantic)

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from uuid import UUID

class GoldQuery(BaseModel):
    id: UUID
    chat_input: str
    session_id: Optional[str] = None
    member_id: Optional[str] = None
    clasificacion: Optional[str] = None
    pregunta_descompuesta: Optional[str] = None
    tablas_columnas_ddl: str
    sql_reference: str
    created_at: datetime

class Evaluation(BaseModel):
    id: UUID
    gold_query_id: UUID
    generated_sql: str
    evaluation_date: datetime
    created_at: datetime

class ExecutionAccuracy(BaseModel):
    id: UUID
    evaluation_id: UUID
    results_match: Optional[bool] = None
    is_correct: bool
    evaluator_notes: Optional[str] = None
    created_at: datetime

class TimeToAnswer(BaseModel):
    id: UUID
    evaluation_id: UUID
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    created_at: datetime

    @validator('duration_seconds')
    def validate_duration(cls, v, values):
        if 'start_time' in values and 'end_time' in values:
            expected = (values['end_time'] - values['start_time']).total_seconds()
            if abs(v - expected) > 0.01:
                raise ValueError('duration_seconds must match end_time - start_time')
        return v

class ComponentMatching(BaseModel):
    id: UUID
    evaluation_id: UUID
    select_correct: bool
    where_correct: bool
    group_by_correct: bool
    order_by_correct: bool
    keywords_correct: bool
    f1_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    evaluator_notes: Optional[str] = None
    created_at: datetime

class MetricsSummary(BaseModel):
    execution_accuracy: float  # Percentage
    average_time_to_answer: float  # Seconds
    component_scores: dict[str, float]  # F1 scores per component
    total_evaluations: int
    completed_evaluations: int
```

### TypeScript Interfaces

```typescript
interface GoldQuery {
  id: string;
  chatInput: string;
  sessionId?: string;
  memberId?: string;
  clasificacion?: string;
  preguntaDescompuesta?: string;
  tablasColumnasDdl: string;
  sqlReference: string;
  createdAt: Date;
}

interface Evaluation {
  id: string;
  goldQueryId: string;
  generatedSql: string;
  evaluationDate: Date;
  createdAt: Date;
}

interface ExecutionAccuracy {
  id: string;
  evaluationId: string;
  resultsMatch?: boolean;
  isCorrect: boolean;
  evaluatorNotes?: string;
  createdAt: Date;
}

interface TimeToAnswer {
  id: string;
  evaluationId: string;
  startTime: Date;
  endTime: Date;
  durationSeconds: number;
  createdAt: Date;
}

interface ComponentMatching {
  id: string;
  evaluationId: string;
  selectCorrect: boolean;
  whereCorrect: boolean;
  groupByCorrect: boolean;
  orderByCorrect: boolean;
  keywordsCorrect: boolean;
  f1Score?: number;
  evaluatorNotes?: string;
  createdAt: Date;
}

interface MetricsSummary {
  executionAccuracy: number; // Percentage
  averageTimeToAnswer: number; // Seconds
  componentScores: {
    select: number;
    where: number;
    groupBy: number;
    orderBy: number;
    keywords: number;
  };
  totalEvaluations: number;
  completedEvaluations: number;
}
```

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

### Property 1: Required field validation

_For any_ attempt to insert a record into `gold_queries`, if any required field (chat_input, tablas_columnas_ddl, sql_reference) is missing, the insertion should be rejected
**Validates: Requirements 1.2**

### Property 2: Data integrity on query

_For any_ set of records inserted into `gold_queries`, querying the table should return exactly those records with all fields intact
**Validates: Requirements 1.3**

### Property 3: Migration preserves data

_For any_ valid set of existing data, after migration, all records should be present with referential integrity maintained
**Validates: Requirements 1.4**

### Property 4: Foreign key enforcement

_For any_ evaluation record, attempting to insert with an invalid gold_query_id should fail
**Validates: Requirements 2.5**

### Property 5: Evaluation storage

_For any_ evaluation marked as correct or incorrect, a corresponding record should exist in the `execution_accuracy` table
**Validates: Requirements 3.1**

### Property 6: EX calculation correctness

_For any_ set of evaluations, the calculated EX should equal (count of is_correct=true / total count) × 100
**Validates: Requirements 3.2**

### Property 7: EX formatting

_For any_ calculated EX value, when displayed, it should be formatted with exactly two decimal places
**Validates: Requirements 3.3**

### Property 8: Notes round-trip

_For any_ text stored in evaluator_notes, retrieving it should return the exact same text
**Validates: Requirements 3.4, 5.5, 10.3**

### Property 9: Timestamp recording

_For any_ evaluation started, a start_time timestamp should be recorded; for any evaluation completed, an end_time timestamp should be recorded
**Validates: Requirements 4.1, 4.2**

### Property 10: TTA calculation correctness

_For any_ evaluation with start_time and end_time, duration_seconds should equal the difference in seconds between end_time and start_time
**Validates: Requirements 4.3**

### Property 11: Average TTA calculation

_For any_ set of completed evaluations, the average TTA should equal the mean of all duration_seconds values
**Validates: Requirements 4.4**

### Property 12: Component evaluation completeness

_For any_ component evaluation, all five components (SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS) should have boolean values recorded
**Validates: Requirements 5.1**

### Property 13: F1 score calculation

_For any_ set of component evaluations, the F1 score should be calculated correctly using the standard formula: F1 = 2 × (precision × recall) / (precision + recall)
**Validates: Requirements 5.3**

### Property 14: Component data round-trip

_For any_ component evaluation with boolean values, storing and retrieving should preserve all five boolean values exactly
**Validates: Requirements 5.4**

### Property 15: Pending queries listing

_For any_ database state, the list of pending queries should include exactly those gold_queries that have no associated evaluation
**Validates: Requirements 6.1**

### Property 16: Query display completeness

_For any_ selected query, the display should include sql_reference, generated_sql, chat_input, and tablas_columnas_ddl
**Validates: Requirements 6.2**

### Property 17: Evaluation persistence

_For any_ completed evaluation, all associated data (execution_accuracy, time_to_answer, component_matching) should be persisted in Supabase
**Validates: Requirements 6.5**

### Property 18: Next query navigation

_For any_ saved evaluation, if pending queries remain, the next pending query should be displayed automatically
**Validates: Requirements 6.6**

### Property 19: Dashboard counts accuracy

_For any_ database state, the dashboard should display correct counts for: total queries, evaluated queries, and progress percentage
**Validates: Requirements 7.1, 7.2, 7.3**

### Property 20: Aggregated metrics accuracy

_For any_ set of evaluations, the dashboard should display correctly calculated aggregated metrics: average EX, average TTA, and average F1 scores per component
**Validates: Requirements 7.4**

### Property 21: Chart generation validity

_For any_ request to generate charts (EX bar chart, component F1 bar chart, TTA histogram), a valid PNG file should be generated
**Validates: Requirements 8.1, 8.2, 8.3**

### Property 22: Chart resolution requirement

_For any_ generated chart PNG, the resolution should be at least 300 DPI
**Validates: Requirements 8.4**

### Property 23: Chart language requirement

_For any_ generated chart, labels, legends, and titles should contain Spanish text
**Validates: Requirements 8.5**

### Property 24: CSV export completeness

_For any_ export request, the generated CSV should include all fields from evaluations, execution_accuracy, time_to_answer, component_matching, and relevant gold_queries fields
**Validates: Requirements 9.1, 9.2, 9.3**

### Property 25: Export download availability

_For any_ completed export, a valid download link should be provided
**Validates: Requirements 9.4**

### Property 26: LaTeX export validity

_For any_ export request, the generated LaTeX table should be valid IEEEtran-compatible syntax
**Validates: Requirements 9.5**

### Property 27: Notes display consistency

_For any_ evaluation with stored notes, viewing that evaluation should display the notes
**Validates: Requirements 10.4**

## Error Handling

### Database Errors

- **Connection failures**: Retry with exponential backoff (max 3 attempts)
- **Constraint violations**: Return 400 Bad Request with descriptive error message
- **Foreign key violations**: Return 400 Bad Request indicating invalid reference
- **Timeout errors**: Return 504 Gateway Timeout after 30 seconds

### Validation Errors

- **Missing required fields**: Return 400 Bad Request with list of missing fields
- **Invalid data types**: Return 400 Bad Request with type mismatch details
- **Invalid timestamps**: Return 400 Bad Request if end_time < start_time

### Chart Generation Errors

- **Insufficient data**: Return 422 Unprocessable Entity if no evaluations exist
- **File system errors**: Return 500 Internal Server Error with error details
- **Memory errors**: Implement streaming for large datasets

### Export Errors

- **Empty dataset**: Return 422 Unprocessable Entity with message
- **File generation failure**: Return 500 Internal Server Error
- **Large dataset timeout**: Implement pagination for exports > 10,000 records

## Testing Strategy

### Unit Testing

**Backend Unit Tests (Python - pytest):**

- Funciones de cálculo de métricas (EX, TTA, F1 score)
- Validadores de datos de entrada con Pydantic
- Formateadores de exportación (CSV con Pandas, LaTeX)
- Generadores de consultas SQL
- Funciones de generación de gráficas con Matplotlib

**Frontend Unit Tests (Jest + React Testing Library):**

- Componentes de React individuales
- Funciones de formateo de datos
- Validación de formularios
- Utilidades de cálculo del lado del cliente

**Ejemplos específicos:**

- Test que verifica que EX = 75% cuando 3 de 4 consultas son correctas
- Test que verifica que TTA se calcula correctamente para timestamps específicos
- Test que verifica que el formato de dos decimales se aplica correctamente
- Test que verifica que la validación Pydantic rechaza registros sin campos requeridos

### Property-Based Testing

**Backend:** El sistema utilizará **Hypothesis** (Python) para pruebas basadas en propiedades.

**Frontend:** El sistema utilizará **fast-check** (JavaScript/TypeScript) para pruebas basadas en propiedades.

**Configuración:**

- Cada prueba de propiedad ejecutará un mínimo de 100 iteraciones
- Cada prueba estará etiquetada con el formato: `**Feature: text-to-sql-evaluation, Property {number}: {property_text}**`
- Cada propiedad de corrección del documento de diseño será implementada por UNA SOLA prueba basada en propiedades

**Property-Based Tests a implementar:**

- Property 1-27 como se definieron en la sección de Correctness Properties

**Generadores necesarios (Hypothesis para backend):**

- `gold_query_strategy`: Genera objetos GoldQuery válidos con campos aleatorios
- `evaluation_strategy`: Genera objetos Evaluation válidos
- `component_matching_strategy`: Genera evaluaciones de componentes con valores booleanos aleatorios
- `timestamp_pair_strategy`: Genera pares de timestamps donde end_time > start_time
- `evaluation_list_strategy`: Genera listas de evaluaciones para probar cálculos agregados

**Ejemplo de estructura de test (Python/Hypothesis):**

```python
# Feature: text-to-sql-evaluation, Property 6: EX calculation correctness
from hypothesis import given, strategies as st, settings

@given(st.lists(evaluation_strategy, min_size=1))
@settings(max_examples=100)
def test_ex_calculation_correctness(evaluations):
    """For any set of evaluations, EX should equal (correct / total) × 100"""
    correct_count = sum(1 for e in evaluations if e.is_correct)
    expected = (correct_count / len(evaluations)) * 100
    actual = calculate_ex(evaluations)
    assert abs(actual - expected) < 0.01
```

### Integration Testing

**Database Integration:**

- Tests que verifican la creación correcta del esquema
- Tests que verifican las foreign keys y cascadas
- Tests que verifican transacciones complejas

**API Integration:**

- Tests end-to-end de flujos completos de evaluación
- Tests de exportación con datos reales
- Tests de generación de gráficas con diferentes tamaños de datasets

**Frontend-Backend Integration:**

- Tests que verifican el flujo completo desde UI hasta persistencia
- Tests de navegación entre consultas
- Tests de actualización en tiempo real del dashboard

## Performance Considerations

### Database Optimization

- Índices en `gold_queries.id`, `evaluations.gold_query_id`, `evaluations.evaluation_date`
- Índices en todas las foreign keys
- Materialized views para métricas agregadas si el dataset crece > 10,000 registros

### Caching Strategy

- Cache de métricas agregadas con invalidación al crear nueva evaluación
- Cache de consultas pendientes con TTL de 60 segundos
- Cache de gráficas generadas con hash del dataset

### Frontend Optimization

- Lazy loading de componentes de visualización
- Paginación de listas de evaluaciones (20 por página)
- Debouncing de búsquedas y filtros (300ms)

## Security Considerations

### Authentication

- Supabase Auth para autenticación del evaluador
- JWT tokens con expiración de 24 horas

### Authorization

- Row Level Security (RLS) en Supabase
- Solo el evaluador autenticado puede crear/modificar evaluaciones

### Data Validation

- Sanitización de inputs en backend antes de insertar en BD
- Validación de tipos en TypeScript
- Prepared statements para prevenir SQL injection

### API Security

- Rate limiting: 100 requests por minuto por IP
- CORS configurado solo para dominio del frontend
- HTTPS obligatorio en producción

## Deployment Strategy

### Development Environment

- Local Supabase instance con Docker
- Frontend en localhost:3000
- Backend en localhost:3001

### Production Environment

- Supabase hosted instance
- Frontend en Vercel/Netlify
- Backend en Railway/Render
- Environment variables para configuración

### CI/CD Pipeline

- GitHub Actions para tests automáticos
- Deploy automático a staging en merge a main
- Deploy manual a producción con aprobación

## Future Enhancements

- Soporte para múltiples evaluadores con asignación de consultas
- Comparación de resultados entre diferentes versiones del modelo
- Análisis de patrones de errores comunes
- Sugerencias automáticas de mejoras basadas en evaluaciones
- API pública para integración con otros sistemas de evaluación
