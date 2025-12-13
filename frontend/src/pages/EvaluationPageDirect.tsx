import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

interface GoldQueryAPI {
  id: string;
  chat_input: string;
  session_id?: string;
  member_id?: string;
  clasificacion?: string;
  pregunta_descompuesta?: string;
  tablas_columnas_ddl: string;
  sql_reference: string;
  created_at: string;
}

const EvaluationPageDirect: React.FC = () => {
  const navigate = useNavigate();
  const { queryId } = useParams<{ queryId: string }>();
  const [goldQuery, setGoldQuery] = useState<GoldQueryAPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generatedSql, setGeneratedSql] = useState('');
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  
  // Evaluation form state
  const [evaluationForm, setEvaluationForm] = useState({
    isCorrect: false,
    resultsMatch: false,
    selectCorrect: false,
    whereCorrect: false,
    groupByCorrect: false,
    orderByCorrect: false,
    keywordsCorrect: false,
    evaluatorNotes: '',
    componentNotes: ''
  });

  useEffect(() => {
    if (!queryId) {
      setError('No se proporcionó ID de consulta');
      setLoading(false);
      return;
    }

    const fetchQuery = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('Fetching query:', queryId);
        const response = await fetch(`http://localhost:8002/api/gold-queries/${queryId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Query data received:', data);
        setGoldQuery(data);
        // Set start time when query loads
        setStartTime(new Date());
      } catch (err) {
        console.error('Error fetching query:', err);
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    fetchQuery();
  }, [queryId]);

  const handleEvaluate = async () => {
    if (!generatedSql.trim()) {
      alert('Por favor ingresa la consulta SQL generada');
      return;
    }

    if (!startTime) {
      alert('Error: No se pudo determinar el tiempo de inicio');
      return;
    }

    try {
      setIsEvaluating(true);
      
      const endTime = new Date();
      const durationSeconds = (endTime.getTime() - startTime.getTime()) / 1000;

      const evaluationData = {
        gold_query_id: queryId,
        generated_sql: generatedSql,
        execution_accuracy: {
          results_match: evaluationForm.resultsMatch,
          is_correct: evaluationForm.isCorrect,
          evaluator_notes: evaluationForm.evaluatorNotes || null
        },
        time_to_answer: {
          start_time: startTime.toISOString(),
          end_time: endTime.toISOString(),
          duration_seconds: durationSeconds
        },
        component_matching: {
          select_correct: evaluationForm.selectCorrect,
          where_correct: evaluationForm.whereCorrect,
          group_by_correct: evaluationForm.groupByCorrect,
          order_by_correct: evaluationForm.orderByCorrect,
          keywords_correct: evaluationForm.keywordsCorrect,
          f1_score: null,
          evaluator_notes: evaluationForm.componentNotes || null
        }
      };

      console.log('Sending evaluation:', evaluationData);

      const response = await fetch('http://localhost:8002/api/evaluations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(evaluationData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log('Evaluation created:', result);
      
      alert('¡Evaluación guardada exitosamente!');
      navigate('/');
      
    } catch (err) {
      console.error('Error creating evaluation:', err);
      alert(`Error al guardar la evaluación: ${err instanceof Error ? err.message : 'Error desconocido'}`);
    } finally {
      setIsEvaluating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando consulta...</p>
        </div>
      </div>
    );
  }

  if (error || !goldQuery) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-red-900 mb-2">Error</h2>
        <p className="text-red-700 mb-4">
          {error || 'Consulta no encontrada'}
        </p>
        <button
          onClick={() => navigate('/')}
          className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
        >
          Volver al Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Evaluación de Consulta SQL
        </h1>
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-600">Query ID: {queryId}</p>
            <p className="text-sm text-gray-600">Clasificación: {goldQuery.clasificacion}</p>
          </div>
          <div className="space-x-2">
            <button
              onClick={() => navigate('/')}
              className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
            >
              Volver al Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Consulta del Usuario */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Consulta del Usuario
        </h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-gray-800">{goldQuery.chat_input}</p>
        </div>
      </div>

      {/* Campo para SQL Generado */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          SQL Generado por IA
        </h3>
        <textarea
          value={generatedSql}
          onChange={(e) => setGeneratedSql(e.target.value)}
          rows={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
          placeholder="Pega aquí la consulta SQL generada por el modelo de IA..."
        />
      </div>

      {/* Formulario de Evaluación */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Evaluación de la Consulta
        </h3>
        
        {/* Exactitud de Ejecución */}
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-800 mb-3">Exactitud de Ejecución</h4>
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={evaluationForm.isCorrect}
                onChange={(e) => setEvaluationForm(prev => ({...prev, isCorrect: e.target.checked}))}
                className="mr-2"
              />
              <span className="text-sm">La consulta produce resultados correctos</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={evaluationForm.resultsMatch}
                onChange={(e) => setEvaluationForm(prev => ({...prev, resultsMatch: e.target.checked}))}
                className="mr-2"
              />
              <span className="text-sm">Los resultados coinciden exactamente con la consulta de referencia</span>
            </label>
          </div>
        </div>

        {/* Evaluación por Componentes */}
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-800 mb-3">Evaluación por Componentes</h4>
          <div className="grid grid-cols-2 gap-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={evaluationForm.selectCorrect}
                onChange={(e) => setEvaluationForm(prev => ({...prev, selectCorrect: e.target.checked}))}
                className="mr-2"
              />
              <span className="text-sm">SELECT correcto</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={evaluationForm.whereCorrect}
                onChange={(e) => setEvaluationForm(prev => ({...prev, whereCorrect: e.target.checked}))}
                className="mr-2"
              />
              <span className="text-sm">WHERE correcto</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={evaluationForm.groupByCorrect}
                onChange={(e) => setEvaluationForm(prev => ({...prev, groupByCorrect: e.target.checked}))}
                className="mr-2"
              />
              <span className="text-sm">GROUP BY correcto</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={evaluationForm.orderByCorrect}
                onChange={(e) => setEvaluationForm(prev => ({...prev, orderByCorrect: e.target.checked}))}
                className="mr-2"
              />
              <span className="text-sm">ORDER BY correcto</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={evaluationForm.keywordsCorrect}
                onChange={(e) => setEvaluationForm(prev => ({...prev, keywordsCorrect: e.target.checked}))}
                className="mr-2"
              />
              <span className="text-sm">Palabras clave correctas</span>
            </label>
          </div>
        </div>

        {/* Notas del Evaluador */}
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-800 mb-3">Notas del Evaluador</h4>
          <textarea
            value={evaluationForm.evaluatorNotes}
            onChange={(e) => setEvaluationForm(prev => ({...prev, evaluatorNotes: e.target.value}))}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
            placeholder="Observaciones generales sobre la evaluación..."
          />
        </div>

        {/* Notas de Componentes */}
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-800 mb-3">Notas sobre Componentes</h4>
          <textarea
            value={evaluationForm.componentNotes}
            onChange={(e) => setEvaluationForm(prev => ({...prev, componentNotes: e.target.value}))}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm"
            placeholder="Detalles específicos sobre cada componente SQL..."
          />
        </div>

        {/* Botón de Evaluación */}
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {startTime && `Tiempo transcurrido: ${Math.floor((new Date().getTime() - startTime.getTime()) / 1000)}s`}
          </div>
          <button 
            onClick={handleEvaluate}
            disabled={isEvaluating || !generatedSql.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isEvaluating ? 'Guardando...' : 'Guardar Evaluación'}
          </button>
        </div>
      </div>

      {/* SQL de Referencia */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          SQL de Referencia (Gold Standard)
        </h3>
        <div className="bg-gray-900 p-4 rounded-lg">
          <pre className="text-green-400 text-sm overflow-x-auto">
            <code>{goldQuery.sql_reference}</code>
          </pre>
        </div>
      </div>

      {/* Esquema de Base de Datos */}
      {goldQuery.tablas_columnas_ddl && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Esquema de Base de Datos
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap">
              {goldQuery.tablas_columnas_ddl}
            </pre>
          </div>
        </div>
      )}

      {/* Pregunta Descompuesta */}
      {goldQuery.pregunta_descompuesta && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Análisis de la Consulta
          </h3>
          <div className="bg-blue-50 p-4 rounded-lg">
            <pre className="text-blue-800 text-sm whitespace-pre-wrap">
              {goldQuery.pregunta_descompuesta}
            </pre>
          </div>
        </div>
      )}

      {/* Debug Info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="text-sm text-gray-600">
          Creado: {new Date(goldQuery.created_at).toLocaleString('es-ES')}
        </div>
      </div>
    </div>
  );
};

export default EvaluationPageDirect;