# Text-to-SQL Evaluation System

Sistema completo de evaluación para modelos text-to-SQL con métricas académicas estándar y interfaz web interactiva.

## 🚀 Características

- **Evaluación completa**: Métricas EX (Execution Accuracy), TTA (Time-to-Answer) y Component Matching
- **Interfaz web moderna**: Dashboard interactivo con React + TypeScript
- **API robusta**: Backend FastAPI con base de datos PostgreSQL/Supabase
- **Integración N8n**: Soporte para consultas generadas por modelos N8n
- **Exportación**: Datos en CSV y LaTeX para publicaciones académicas
- **Visualizaciones**: Gráficas y métricas en tiempo real

## 📊 Métricas Implementadas

### Execution Accuracy (EX)

Porcentaje de consultas SQL que producen resultados correctos cuando se ejecutan contra la base de datos.

### Time-to-Answer (TTA)

Tiempo transcurrido desde el inicio de la evaluación hasta la finalización, medido en segundos.

### Component Matching

Evaluación granular de componentes SQL individuales:

- SELECT correctness
- WHERE correctness
- GROUP BY correctness
- ORDER BY correctness
- Keywords correctness
- F1 Score calculado

## 🛠️ Tecnologías

### Backend

- **FastAPI**: Framework web moderno y rápido
- **PostgreSQL/Supabase**: Base de datos con soporte completo SQL
- **Pydantic**: Validación de datos y serialización
- **Asyncio**: Operaciones asíncronas para mejor rendimiento

### Frontend

- **React 18**: Biblioteca de interfaz de usuario
- **TypeScript**: Tipado estático para mejor desarrollo
- **Tailwind CSS**: Framework de estilos utilitarios
- **React Router**: Navegación entre páginas
- **Recharts**: Visualizaciones y gráficas

## 🚀 Instalación y Uso

### Prerrequisitos

- Python 3.8+
- Node.js 16+
- PostgreSQL o cuenta de Supabase

### Backend

1. **Configurar entorno**:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configurar variables de entorno**:

```bash
cp .env.example .env
# Editar .env con tus credenciales de Supabase
```

3. **Ejecutar migraciones**:

```bash
# Ejecutar migrations/001_initial_schema.sql en tu base de datos
```

4. **Iniciar servidor**:

```bash
python run_server.py
# O usar: ./run.sh
```

El backend estará disponible en `http://localhost:8002`

### Frontend

1. **Instalar dependencias**:

```bash
cd frontend
npm install
```

2. **Iniciar desarrollo**:

```bash
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## 📝 Uso del Sistema

### 1. Dashboard

- Visualiza consultas pendientes de evaluación
- Carga datos desde la API
- Navega a evaluaciones individuales

### 2. Evaluación

- Revisa la consulta del usuario y SQL de referencia
- Usa consultas N8n pre-generadas o ingresa SQL manualmente
- Completa evaluación con checkboxes y notas
- Guarda automáticamente con métricas de tiempo

### 3. Resultados

- Visualiza métricas agregadas
- Revisa estadísticas por componente
- Exporta datos para análisis

### 4. Exportación

- Genera reportes en CSV para análisis de datos
- Crea tablas LaTeX para publicaciones académicas

## 🗃️ Estructura del Proyecto

```
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── models/         # Modelos Pydantic
│   │   ├── repositories/   # Acceso a datos
│   │   ├── services/       # Lógica de negocio
│   │   └── database.py     # Configuración DB
│   ├── migrations/         # Scripts SQL
│   └── requirements.txt
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── components/     # Componentes reutilizables
│   │   ├── pages/          # Páginas principales
│   │   ├── services/       # Clientes API
│   │   ├── hooks/          # Hooks personalizados
│   │   └── types/          # Definiciones TypeScript
│   └── package.json
└── migrations/             # Migraciones de base de datos
```

## 🔧 Configuración

### Variables de Entorno (Backend)

```env
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-publica

# FastAPI
API_HOST=0.0.0.0
API_PORT=8002
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 📊 Carga de Datos

El sistema incluye scripts para cargar datos desde Excel:

```bash
cd backend
python load_excel_data.py          # Cargar consultas gold
python load_excel_with_evaluations.py  # Cargar con evaluaciones
python create_evaluations_from_excel.py  # Crear evaluaciones
```

## 🧪 Testing

### Backend

```bash
cd backend
python -m pytest tests/
```

### Frontend

```bash
cd frontend
npm test
```

## 📈 Métricas y Análisis

El sistema calcula automáticamente:

- **Execution Accuracy**: Porcentaje de consultas correctas
- **Average TTA**: Tiempo promedio de respuesta
- **Component F1 Scores**: Precisión por componente SQL
- **Distribuciones**: Histogramas de tiempo y accuracy

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Reconocimientos

- Basado en métricas estándar de evaluación text-to-SQL
- Inspirado en trabajos académicos de NLP y bases de datos
- Construido con tecnologías modernas de desarrollo web

## 📞 Contacto

**Autor**: [Tu Nombre]
**Email**: [tu-email@ejemplo.com]
**GitHub**: [@nserrano123](https://github.com/nserrano123)

---

⭐ **¡Dale una estrella si este proyecto te fue útil!**
