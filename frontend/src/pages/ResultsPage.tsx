import React, { useState } from 'react';
import ExChart from '../components/ExChart';
import ComponentChart from '../components/ComponentChart';
import TtaHistogram from '../components/TtaHistogram';
import { useMetricsSummary } from '../hooks/useMetrics';

const ResultsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'execution' | 'components' | 'timing'>('execution');
  const { data: metricsSummary, isLoading, error } = useMetricsSummary();

  const tabs = [
    {
      id: 'execution' as const,
      label: 'Execution Accuracy',
      description: 'Porcentaje de consultas con resultados correctos',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      id: 'components' as const,
      label: 'Component Matching',
      description: 'F1 scores por componente SQL',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
    },
    {
      id: 'timing' as const,
      label: 'Time Distribution',
      description: 'Distribución de tiempos de respuesta',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
  ];

  const renderMetricsSummary = () => {
    if (isLoading) {
      return (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center text-red-600">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Error cargando métricas: {error instanceof Error ? error.message : 'Error desconocido'}</span>
          </div>
        </div>
      );
    }

    if (!metricsSummary) {
      return (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-center text-gray-500">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p>No hay datos de métricas disponibles</p>
            <p className="text-sm mt-1">Completa algunas evaluaciones para ver los resultados</p>
          </div>
        </div>
      );
    }

    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Resumen de Métricas</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Execution Accuracy */}
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-blue-600">Execution Accuracy</p>
                <p className="text-2xl font-bold text-blue-900">{metricsSummary.executionAccuracy.toFixed(2)}%</p>
              </div>
            </div>
          </div>

          {/* Average TTA */}
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-green-600">TTA Promedio</p>
                <p className="text-2xl font-bold text-green-900">{metricsSummary.averageTimeToAnswer.toFixed(1)}s</p>
              </div>
            </div>
          </div>

          {/* Total Evaluations */}
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-purple-600">Evaluaciones</p>
                <p className="text-2xl font-bold text-purple-900">{metricsSummary.completedEvaluations}</p>
              </div>
            </div>
          </div>

          {/* Average Component F1 */}
          <div className="bg-orange-50 rounded-lg p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-orange-600">F1 Promedio</p>
                <p className="text-2xl font-bold text-orange-900">
                  {Object.values(metricsSummary.componentScores).length > 0
                    ? (Object.values(metricsSummary.componentScores).reduce((a, b) => a + b, 0) / Object.values(metricsSummary.componentScores).length).toFixed(3)
                    : '0.000'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderActiveChart = () => {
    switch (activeTab) {
      case 'execution':
        return <ExChart className="mt-6" />;
      case 'components':
        return <ComponentChart className="mt-6" />;
      case 'timing':
        return <TtaHistogram className="mt-6" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Resultados de Evaluación</h2>
            <p className="text-gray-600">
              Visualización de métricas y gráficas de evaluación del modelo text-to-SQL
            </p>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Actualizado automáticamente</span>
          </div>
        </div>
      </div>

      {/* Metrics Summary */}
      {renderMetricsSummary()}

      {/* Chart Navigation Tabs */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors duration-200`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Description */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <p className="text-sm text-gray-600">
            {tabs.find(tab => tab.id === activeTab)?.description}
          </p>
        </div>

        {/* Chart Content */}
        <div className="p-6">
          {renderActiveChart()}
        </div>
      </div>

      {/* Additional Information */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Información sobre las Gráficas</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <h4 className="font-medium text-gray-900 flex items-center">
              <svg className="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Execution Accuracy (EX)
            </h4>
            <p className="text-sm text-gray-600">
              Mide el porcentaje de consultas SQL que producen resultados correctos cuando se ejecutan contra la base de datos.
            </p>
          </div>
          
          <div className="space-y-2">
            <h4 className="font-medium text-gray-900 flex items-center">
              <svg className="w-4 h-4 mr-2 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              Component Matching
            </h4>
            <p className="text-sm text-gray-600">
              Evalúa la coincidencia exacta de componentes SQL individuales (SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS) usando F1 score.
            </p>
          </div>
          
          <div className="space-y-2">
            <h4 className="font-medium text-gray-900 flex items-center">
              <svg className="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Time-to-Answer (TTA)
            </h4>
            <p className="text-sm text-gray-600">
              Muestra la distribución de tiempos de respuesta del modelo, desde el inicio de la evaluación hasta la finalización.
            </p>
          </div>
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-blue-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h4 className="text-sm font-medium text-blue-800">Configuración de Gráficas</h4>
              <p className="text-sm text-blue-700 mt-1">
                Todas las gráficas se generan con resolución de 300 DPI por defecto, adecuada para publicación académica. 
                Puedes ajustar las dimensiones y resolución según tus necesidades antes de generar cada gráfica.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;