import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { usePendingGoldQueries, useGoldQuery } from '../hooks/useGoldQueries';

const EvaluationPageSimple: React.FC = () => {
  const navigate = useNavigate();
  const { queryId } = useParams<{ queryId: string }>();
  const { data: pendingQueries, isLoading: pendingLoading } = usePendingGoldQueries();
  const { data: goldQuery, isLoading: isLoadingQuery, error: queryError } = useGoldQuery(queryId ?? '');

  // Auto-navigate to first pending query if no queryId provided
  useEffect(() => {
    if (!queryId && pendingQueries && pendingQueries.length > 0) {
      navigate(`/evaluation/${pendingQueries[0].id}`, { replace: true });
    }
  }, [queryId, pendingQueries, navigate]);

  // If no queryId and no pending queries
  if (!queryId && pendingQueries && pendingQueries.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <h2 className="text-lg font-semibold text-green-900 mb-2">
          ¡Evaluación Completa!
        </h2>
        <p className="text-green-700 mb-4">
          No hay consultas pendientes de evaluación.
        </p>
        <button
          onClick={() => navigate('/')}
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
        >
          Volver al Dashboard
        </button>
      </div>
    );
  }

  // If no queryId and still loading
  if (!queryId && pendingLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Buscando consultas pendientes...</p>
        </div>
      </div>
    );
  }

  // If no queryId and no pending queries loaded yet
  if (!queryId) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
        <h2 className="text-lg font-semibold text-yellow-900 mb-2">
          Selecciona una consulta para evaluar
        </h2>
        <p className="text-yellow-700 mb-4">
          Ve al dashboard para seleccionar una consulta pendiente.
        </p>
        <button
          onClick={() => navigate('/')}
          className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700"
        >
          Ir al Dashboard
        </button>
      </div>
    );
  }

  // Loading state for query
  if (isLoadingQuery) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando consulta...</p>
        </div>
      </div>
    );
  }

  // Error state for query
  if (queryError || !goldQuery) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-red-900 mb-2">Error</h2>
        <p className="text-red-700 mb-4">
          {queryError ? 'Error al cargar la consulta' : 'Consulta no encontrada'}
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

  // If we have a queryId and goldQuery, show the evaluation interface
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
              onClick={() => {
                console.log('Navegando al dashboard...');
                navigate('/');
              }}
              className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
            >
              Volver al Dashboard
            </button>
            <button
              onClick={() => {
                console.log('Recargando página...');
                window.location.href = '/';
              }}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Dashboard (Recargar)
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
          <p className="text-gray-800">{goldQuery.chatInput}</p>
        </div>
      </div>

      {/* SQL de Referencia */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          SQL de Referencia (Gold Standard)
        </h3>
        <div className="bg-gray-900 p-4 rounded-lg">
          <pre className="text-green-400 text-sm overflow-x-auto">
            <code>{goldQuery.sqlReference}</code>
          </pre>
        </div>
      </div>

      {/* Campo para SQL Generado */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          SQL Generado por IA
        </h3>
        <textarea
          rows={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
          placeholder="Pega aquí la consulta SQL generada por el modelo de IA..."
        />
        <div className="mt-4">
          <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">
            Evaluar Consulta
          </button>
        </div>
      </div>

      {/* Esquema de Base de Datos */}
      {goldQuery.tablasColumnasDdl && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Esquema de Base de Datos
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap">
              {goldQuery.tablasColumnasDdl}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default EvaluationPageSimple;