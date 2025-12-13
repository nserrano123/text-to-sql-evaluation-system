import React from 'react';
import { QueryComparisonData } from '../types';

interface QueryComparisonProps {
  data: QueryComparisonData;
  className?: string;
}

const QueryComparison: React.FC<QueryComparisonProps> = ({ data, className = '' }) => {
  const { goldQuery, generatedSql } = data;

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Context Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Contexto</h3>
        
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-blue-800 mb-1">
              Entrada del Chat:
            </label>
            <div className="bg-white border border-blue-200 rounded p-3 text-sm">
              {goldQuery.chatInput}
            </div>
          </div>

          {goldQuery.preguntaDescompuesta && (
            <div>
              <label className="block text-sm font-medium text-blue-800 mb-1">
                Pregunta Descompuesta:
              </label>
              <div className="bg-white border border-blue-200 rounded p-3 text-sm">
                {goldQuery.preguntaDescompuesta}
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-blue-800 mb-1">
              Esquema de Tablas (DDL):
            </label>
            <div className="bg-white border border-blue-200 rounded p-3">
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                {goldQuery.tablasColumnasDdl}
              </pre>
            </div>
          </div>
        </div>
      </div>

      {/* SQL Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gold Standard Query */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-900 mb-3 flex items-center">
            <span className="mr-2">✅</span>
            Consulta de Referencia (Gold)
          </h3>
          <div className="bg-white border border-green-200 rounded p-3">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
              {goldQuery.sqlReference}
            </pre>
          </div>
        </div>

        {/* Generated Query */}
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-orange-900 mb-3 flex items-center">
            <span className="mr-2">🤖</span>
            Consulta Generada por IA
          </h3>
          <div className="bg-white border border-orange-200 rounded p-3">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
              {generatedSql}
            </pre>
          </div>
        </div>
      </div>

      {/* Additional Metadata */}
      {(goldQuery.sessionId || goldQuery.memberId || goldQuery.clasificacion) && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Metadatos</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            {goldQuery.sessionId && (
              <div>
                <span className="font-medium text-gray-700">ID de Sesión:</span>
                <div className="text-gray-600">{goldQuery.sessionId}</div>
              </div>
            )}
            {goldQuery.memberId && (
              <div>
                <span className="font-medium text-gray-700">ID de Miembro:</span>
                <div className="text-gray-600">{goldQuery.memberId}</div>
              </div>
            )}
            {goldQuery.clasificacion && (
              <div>
                <span className="font-medium text-gray-700">Clasificación:</span>
                <div className="text-gray-600">{goldQuery.clasificacion}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryComparison;