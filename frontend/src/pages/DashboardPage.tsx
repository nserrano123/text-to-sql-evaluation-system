import React from 'react';
import { useNavigate } from 'react-router-dom';
import ProgressIndicator from '../components/ProgressIndicator';
import MetricsCard from '../components/MetricsCard';
import PendingQueriesList from '../components/PendingQueriesList';
import { useMetricsSummary } from '../hooks/useMetrics';
import { usePendingGoldQueries, useGoldQueries } from '../hooks/useGoldQueries';
import { useEvaluations } from '../hooks/useEvaluations';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  
  // Fetch data using React Query hooks
  const { data: metricsSummary, isLoading: metricsLoading, error: metricsError } = useMetricsSummary();
  const { data: pendingQueries = [], isLoading: pendingLoading, error: pendingError } = usePendingGoldQueries();
  const { data: allQueries = [], isLoading: queriesLoading } = useGoldQueries();
  const { data: evaluations = [], isLoading: evaluationsLoading } = useEvaluations();

  // Calculate progress data
  const totalQueries = allQueries.length;
  const evaluatedQueries = evaluations.length;

  // Handle query selection for evaluation
  const handleSelectQuery = (queryId: string) => {
    navigate(`/evaluation/${queryId}`);
  };

  // Handle loading and error states
  const isLoading = metricsLoading || pendingLoading || queriesLoading || evaluationsLoading;
  const hasError = metricsError || pendingError;

  if (hasError) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-bold text-red-800 mb-2">Error al cargar el dashboard</h2>
          <p className="text-red-600">
            Hubo un problema al cargar los datos. Por favor, intenta recargar la página.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
          >
            Recargar página
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dashboard de Evaluación
        </h1>
        <p className="text-gray-600">
          Vista general del progreso de evaluación de consultas text-to-SQL
        </p>
      </div>

      {/* Progress and Metrics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Progress Indicator */}
        <ProgressIndicator
          totalQueries={totalQueries}
          evaluatedQueries={evaluatedQueries}
          className="h-fit"
        />

        {/* Metrics Card */}
        {metricsSummary ? (
          <MetricsCard
            metrics={metricsSummary}
            isLoading={metricsLoading}
            className="h-fit"
          />
        ) : (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Métricas de Evaluación
            </h3>
            <div className="text-center py-8">
              <div className="text-gray-400 text-sm">
                📊 No hay métricas disponibles
              </div>
              <div className="text-gray-500 text-xs mt-1">
                Completa algunas evaluaciones para ver las métricas
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Pending Queries List */}
      <PendingQueriesList
        queries={pendingQueries}
        isLoading={pendingLoading}
        onSelectQuery={handleSelectQuery}
      />

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Acciones Rápidas
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => navigate('/evaluation')}
            className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors text-center"
            disabled={pendingQueries.length === 0}
          >
            <div className="text-sm font-medium">Comenzar Evaluación</div>
            <div className="text-xs opacity-90">
              {pendingQueries.length > 0 
                ? `${pendingQueries.length} pendientes`
                : 'No hay pendientes'
              }
            </div>
          </button>
          
          <button
            onClick={() => navigate('/results')}
            className="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors text-center"
            disabled={evaluatedQueries === 0}
          >
            <div className="text-sm font-medium">Ver Resultados</div>
            <div className="text-xs opacity-90">
              {evaluatedQueries > 0 
                ? `${evaluatedQueries} evaluaciones`
                : 'Sin evaluaciones'
              }
            </div>
          </button>
          
          <button
            onClick={() => navigate('/export')}
            className="bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 transition-colors text-center"
            disabled={evaluatedQueries === 0}
          >
            <div className="text-sm font-medium">Exportar Datos</div>
            <div className="text-xs opacity-90">CSV y LaTeX</div>
          </button>
          
          <button
            onClick={() => window.location.reload()}
            className="bg-gray-600 text-white px-4 py-3 rounded-lg hover:bg-gray-700 transition-colors text-center"
          >
            <div className="text-sm font-medium">Actualizar</div>
            <div className="text-xs opacity-90">Recargar datos</div>
          </button>
        </div>
      </div>

      {/* Status Summary */}
      {!isLoading && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 text-center">
            Última actualización: {new Date().toLocaleString('es-ES')}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;