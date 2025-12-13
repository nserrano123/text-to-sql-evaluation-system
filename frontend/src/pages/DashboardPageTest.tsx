import React from 'react';
import { useNavigate } from 'react-router-dom';

const DashboardPageTest: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dashboard de Evaluación - Versión Test
        </h1>
        <p className="text-gray-600">
          Vista general del progreso de evaluación de consultas text-to-SQL
        </p>
      </div>

      {/* Test básico sin hooks */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Prueba de Navegación
        </h3>
        <button
          onClick={() => navigate('/evaluation')}
          className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Ir a Evaluación (Test)
        </button>
      </div>

      {/* Status Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="text-sm text-gray-600 text-center">
          Última actualización: {new Date().toLocaleString('es-ES')}
        </div>
      </div>
    </div>
  );
};

export default DashboardPageTest;