import React from 'react';
import { GoldQuery } from '../types';

interface PendingQueriesListProps {
  queries: GoldQuery[];
  isLoading?: boolean;
  onSelectQuery: (queryId: string) => void;
  className?: string;
}

const PendingQueriesList: React.FC<PendingQueriesListProps> = ({
  queries,
  isLoading = false,
  onSelectQuery,
  className = '',
}) => {
  if (isLoading) {
    return (
      <div className={`bg-white shadow rounded-lg p-6 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Consultas Pendientes
        </h3>
        <div className="animate-pulse space-y-3">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const truncateText = (text: string, maxLength: number = 100): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(date));
  };

  return (
    <div className={`bg-white shadow rounded-lg p-6 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Consultas Pendientes
        </h3>
        <span className="bg-orange-100 text-orange-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
          {queries.length} pendientes
        </span>
      </div>
      
      {queries.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-400 text-sm">
            🎉 ¡No hay consultas pendientes!
          </div>
          <div className="text-gray-500 text-xs mt-1">
            Todas las consultas han sido evaluadas
          </div>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {queries.map((query) => (
            <div
              key={query.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer"
              onClick={() => onSelectQuery(query.id)}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900 mb-1">
                    {truncateText(query.chatInput)}
                  </div>
                  {query.clasificacion && (
                    <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                      {query.clasificacion}
                    </span>
                  )}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectQuery(query.id);
                  }}
                  className="ml-3 bg-blue-600 text-white text-xs px-3 py-1 rounded hover:bg-blue-700 transition-colors"
                >
                  Evaluar
                </button>
              </div>
              
              <div className="text-xs text-gray-500 space-y-1">
                <div>
                  <span className="font-medium">Creada:</span> {formatDate(query.createdAt)}
                </div>
                {query.sessionId && (
                  <div>
                    <span className="font-medium">Sesión:</span> {query.sessionId}
                  </div>
                )}
                {query.memberId && (
                  <div>
                    <span className="font-medium">Usuario:</span> {query.memberId}
                  </div>
                )}
              </div>
              
              {query.preguntaDescompuesta && (
                <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
                  <span className="font-medium">Pregunta descompuesta:</span>
                  <div className="mt-1">{truncateText(query.preguntaDescompuesta, 150)}</div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      
      {queries.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            Haz clic en cualquier consulta para comenzar la evaluación
          </div>
        </div>
      )}
    </div>
  );
};

export default PendingQueriesList;