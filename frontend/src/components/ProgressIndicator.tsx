import React from 'react';

interface ProgressIndicatorProps {
  totalQueries: number;
  evaluatedQueries: number;
  className?: string;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  totalQueries,
  evaluatedQueries,
  className = '',
}) => {
  const progressPercentage = totalQueries > 0 ? (evaluatedQueries / totalQueries) * 100 : 0;
  const pendingQueries = totalQueries - evaluatedQueries;

  return (
    <div className={`bg-white shadow rounded-lg p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Progreso de Evaluación
      </h3>
      
      <div className="space-y-4">
        {/* Progress Bar */}
        <div>
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progreso</span>
            <span>{progressPercentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-in-out"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-3 gap-4 pt-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {totalQueries}
            </div>
            <div className="text-sm text-gray-600">
              Total de Consultas
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {evaluatedQueries}
            </div>
            <div className="text-sm text-gray-600">
              Evaluadas
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {pendingQueries}
            </div>
            <div className="text-sm text-gray-600">
              Pendientes
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;