import React from 'react';
import { useNavigate } from 'react-router-dom';

const DashboardPageClean: React.FC = () => {
  const navigate = useNavigate();
  
  const [data, setData] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const loadData = async () => {
    if (loading) return; // Prevent multiple calls
    
    try {
      setLoading(true);
      setError(null);
      
      console.log('Fetching data...');
      const response = await fetch('http://localhost:8002/api/gold-queries/pending');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Data received:', result.length, 'items');
      setData(result);
    } catch (err) {
      console.error('Error:', err);
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dashboard - Versión Limpia
        </h1>
        <p className="text-gray-600">
          Sistema de evaluación de consultas SQL
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex gap-4 items-center">
          <button
            onClick={loadData}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Cargando...' : 'Cargar Consultas'}
          </button>
          
          <div className="text-sm text-gray-600">
            Estado: {loading ? 'Cargando' : 'Listo'} | 
            Datos: {data.length} consultas
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}

      {/* Data */}
      {data.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">
            Consultas Disponibles ({data.length})
          </h3>
          <div className="space-y-2">
            {data.slice(0, 5).map((query, index) => (
              <div key={query.id || index} className="border rounded p-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="text-sm text-gray-800">
                      {query.chat_input?.substring(0, 80)}...
                    </p>
                    {query.clasificacion && (
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded mt-1 inline-block">
                        {query.clasificacion}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => navigate(`/evaluation/${query.id}`)}
                    className="bg-green-600 text-white text-xs px-3 py-1 rounded hover:bg-green-700"
                  >
                    Evaluar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Debug */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="text-xs text-gray-600">
          Debug: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default DashboardPageClean;