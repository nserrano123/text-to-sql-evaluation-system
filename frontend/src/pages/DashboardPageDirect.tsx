import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface GoldQuery {
  id: string;
  chatInput: string;
  clasificacion?: string;
  createdAt: string;
}

const DashboardPageDirect: React.FC = () => {
  const navigate = useNavigate();
  const [pendingQueries, setPendingQueries] = useState<GoldQuery[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch data directly without React Query
  useEffect(() => {
    const fetchPendingQueries = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('http://localhost:8002/api/gold-queries/pending');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Datos recibidos:', data);
        setPendingQueries(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching pending queries:', err);
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPendingQueries();
  }, []);

  const handleSelectQuery = (queryId: string) => {
    navigate(`/evaluation/${queryId}`);
  };

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-bold text-red-800 mb-2">Error al cargar el dashboard</h2>
          <p className="text-red-600">
            Error: {error}
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
          Dashboard de Evaluación - Versión Directa
        </h1>
        <p className="text-gray-600">
          Vista general del progreso de evaluación de consultas text-to-SQL
        </p>
      </div>

      {/* Consultas Pendientes */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Consultas Pendientes
          </h3>
          <span className="bg-orange-100 text-orange-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
            {isLoading ? 'Cargando...' : `${pendingQueries.length} pendientes`}
          </span>
        </div>
        
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando consultas...</p>
          </div>
        ) : pendingQueries.length === 0 ? (
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
            {pendingQueries.slice(0, 10).map((query) => (
              <div
                key={query.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer"
                onClick={() => handleSelectQuery(query.id)}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900 mb-1">
                      {query.chatInput.substring(0, 100)}...
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
                      handleSelectQuery(query.id);
                    }}
                    className="ml-3 bg-blue-600 text-white text-xs px-3 py-1 rounded hover:bg-blue-700 transition-colors"
                  >
                    Evaluar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Acciones Rápidas
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => {
              if (pendingQueries.length > 0) {
                handleSelectQuery(pendingQueries[0].id);
              }
            }}
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
            onClick={() => window.location.reload()}
            className="bg-gray-600 text-white px-4 py-3 rounded-lg hover:bg-gray-700 transition-colors text-center"
          >
            <div className="text-sm font-medium">Actualizar</div>
            <div className="text-xs opacity-90">Recargar datos</div>
          </button>
        </div>
      </div>

      {/* Debug Info */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="text-sm text-gray-600 text-center">
          Estado: {isLoading ? 'Cargando' : 'Cargado'} | 
          Consultas: {pendingQueries.length} | 
          Última actualización: {new Date().toLocaleString('es-ES')}
        </div>
      </div>
    </div>
  );
};

export default DashboardPageDirect;