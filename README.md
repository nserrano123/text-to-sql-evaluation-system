# Text-to-SQL Evaluation System

Sistema de evaluación para modelos text-to-SQL que permite calificar manualmente las consultas SQL generadas por modelos de IA utilizando métricas estándar de la industria.

## Estructura del Proyecto

```
.
├── backend/                 # Backend API (Python/FastAPI)
│   ├── app/
│   │   ├── models/         # Modelos Pydantic
│   │   ├── repositories/   # Capa de acceso a datos
│   │   ├── services/       # Lógica de negocio
│   │   ├── api/           # Endpoints de API
│   │   └── utils/         # Utilidades
│   ├── tests/
│   │   ├── unit/          # Tests unitarios
│   │   ├── integration/   # Tests de integración
│   │   └── property/      # Property-based tests
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env.example
│
├── frontend/               # Frontend (React/TypeScript)
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── pages/         # Páginas
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # Servicios API
│   │   ├── types/         # Tipos TypeScript
│   │   └── utils/         # Utilidades
│   ├── package.json
│   └── jest.config.js
│
└── migrations/            # Migraciones de base de datos
    └── 001_initial_schema.sql
```

## Requisitos Previos

- Python 3.10+
- Node.js 18+
- Cuenta de Supabase

## Configuración del Backend

1. Navegar al directorio del backend:

```bash
cd backend
```

2. Crear un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:

```bash
cp .env.example .env
# Editar .env con tus credenciales de Supabase
```

5. Ejecutar el servidor de desarrollo:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El API estará disponible en `http://localhost:8000`

## Configuración del Frontend

1. Navegar al directorio del frontend:

```bash
cd frontend
```

2. Instalar dependencias:

```bash
npm install
```

3. Ejecutar el servidor de desarrollo:

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

## Configuración de la Base de Datos

1. Crear un proyecto en [Supabase](https://supabase.com)
2. Ejecutar el script de migración en el SQL Editor de Supabase:

```bash
cat migrations/001_initial_schema.sql
```

3. Copiar las credenciales (URL y anon key) al archivo `.env` del backend

## Métricas Implementadas

- **Execution Accuracy (EX)**: Porcentaje de consultas con resultados correctos
- **Time-to-Answer (TTA)**: Tiempo promedio de respuesta
- **Component Matching**: Evaluación granular de componentes SQL con F1 score

## Testing

### Backend Tests

```bash
cd backend
pytest                    # Ejecutar todos los tests
pytest tests/unit        # Solo tests unitarios
pytest tests/property    # Solo property-based tests
pytest -m property       # Tests marcados como property
```

### Frontend Tests

```bash
cd frontend
npm test                 # Ejecutar todos los tests
npm run test:watch      # Modo watch
```

## Documentación de la API

Una vez que el backend esté ejecutándose, la documentación interactiva de la API estará disponible en:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Desarrollo

### Backend

- Framework: FastAPI
- Base de datos: Supabase (PostgreSQL)
- Validación: Pydantic
- Testing: pytest + Hypothesis

### Frontend

- Framework: React 18 + TypeScript
- Routing: React Router
- Estado: React Query
- Estilos: TailwindCSS
- Gráficas: Recharts
- Testing: Jest + fast-check

## Licencia

Este proyecto es parte de una tesis de investigación.
