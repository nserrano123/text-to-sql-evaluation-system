import React from 'react';

const DashboardPageSimple: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dashboard de Evaluación - Versión Simple
        </h1>
        <p className="text-gray-600">
          Esta es una versión simplificada para diagnosticar problemas
        </p>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Estado del Sistema
        </h2>
        <p className="text-green-600">✅ Frontend cargando correctamente</p>
        <p className="text-blue-600">🔄 Probando conexión con backend...</p>
      </div>
    </div>
  );
};

export default DashboardPageSimple;