import React from 'react';
import { MetricsSummary } from '../types';

interface MetricsCardProps {
  metrics: MetricsSummary;
  isLoading?: boolean;
  className?: string;
}

const MetricsCard: React.FC<MetricsCardProps> = ({
  metrics,
  isLoading = false,
  className = '',
}) => {
  if (isLoading) {
    return (
      <div className={`bg-white shadow rounded-lg p-6 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Métricas de Evaluación
        </h3>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(1)}s`;
  };

  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  const formatF1Score = (value: number): string => {
    return value.toFixed(3);
  };

  return (
    <div className={`bg-white shadow rounded-lg p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        Métricas de Evaluación
      </h3>
      
      <div className="space-y-6">
        {/* Execution Accuracy */}
        <div className="border-b border-gray-200 pb-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-600">
              Execution Accuracy (EX)
            </span>
            <span className="text-lg font-bold text-blue-600">
              {formatPercentage(metrics.executionAccuracy)}
            </span>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Porcentaje de consultas con resultados correctos
          </div>
        </div>

        {/* Time to Answer */}
        <div className="border-b border-gray-200 pb-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-600">
              Time-to-Answer (TTA) Promedio
            </span>
            <span className="text-lg font-bold text-green-600">
              {formatTime(metrics.averageTimeToAnswer)}
            </span>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Tiempo promedio de evaluación por consulta
          </div>
        </div>

        {/* Component F1 Scores */}
        <div>
          <div className="text-sm font-medium text-gray-600 mb-3">
            F1 Scores por Componente
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-600">SELECT</span>
              <span className="text-sm font-semibold text-purple-600">
                {formatF1Score(metrics.componentScores.select)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-600">WHERE</span>
              <span className="text-sm font-semibold text-purple-600">
                {formatF1Score(metrics.componentScores.where)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-600">GROUP BY</span>
              <span className="text-sm font-semibold text-purple-600">
                {formatF1Score(metrics.componentScores.groupBy)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-600">ORDER BY</span>
              <span className="text-sm font-semibold text-purple-600">
                {formatF1Score(metrics.componentScores.orderBy)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-600">KEYWORDS</span>
              <span className="text-sm font-semibold text-purple-600">
                {formatF1Score(metrics.componentScores.keywords)}
              </span>
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="bg-gray-50 rounded-lg p-4 mt-4">
          <div className="text-xs text-gray-600 mb-2">Resumen</div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Evaluaciones Completadas:</span>
            <span className="font-semibold">{metrics.completedEvaluations}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Total de Evaluaciones:</span>
            <span className="font-semibold">{metrics.totalEvaluations}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsCard;