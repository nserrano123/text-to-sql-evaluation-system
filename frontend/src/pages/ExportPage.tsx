import React, { useState } from 'react';
import { ExportButton } from '../components';
import { useExportToCsv, useExportToLatex } from '../hooks/useExport';
import { 
  useGenerateExecutionAccuracyChart, 
  useGenerateComponentMatchingChart, 
  useGenerateTimeDistributionChart 
} from '../hooks/useCharts';
import { exportService } from '../services/exportService';

const ExportPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Export mutations
  const exportToCsvMutation = useExportToCsv();
  const exportToLatexMutation = useExportToLatex();

  // Chart generation mutations
  const generateExChartMutation = useGenerateExecutionAccuracyChart();
  const generateComponentChartMutation = useGenerateComponentMatchingChart();
  const generateTtaChartMutation = useGenerateTimeDistributionChart();

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  const handleExportCsv = async () => {
    clearMessages();
    try {
      await exportToCsvMutation.mutateAsync();
      setSuccess('Archivo CSV descargado exitosamente');
    } catch (err) {
      setError('Error al exportar CSV: ' + (err instanceof Error ? err.message : 'Error desconocido'));
    }
  };

  const handleExportLatex = async () => {
    clearMessages();
    try {
      await exportToLatexMutation.mutateAsync();
      setSuccess('Archivo LaTeX descargado exitosamente');
    } catch (err) {
      setError('Error al exportar LaTeX: ' + (err instanceof Error ? err.message : 'Error desconocido'));
    }
  };

  const handleDownloadChart = async (
    chartType: 'execution-accuracy' | 'component-matching' | 'time-distribution',
    mutation: any
  ) => {
    clearMessages();
    try {
      const blob = await mutation.mutateAsync({ width: 800, height: 600, dpi: 300 });
      const timestamp = new Date().toISOString().split('T')[0];
      exportService.downloadBlob(blob, `${chartType}-chart-${timestamp}.png`);
      setSuccess(`Gráfica ${chartType} descargada exitosamente`);
    } catch (err) {
      setError(`Error al descargar gráfica ${chartType}: ` + (err instanceof Error ? err.message : 'Error desconocido'));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Exportación de Datos</h2>
        <p className="text-gray-600">
          Exporta los resultados de evaluación en diferentes formatos para análisis externos y documentación de tesis.
        </p>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Éxito</h3>
              <p className="text-sm text-green-700 mt-1">{success}</p>
            </div>
          </div>
        </div>
      )}

      {/* Data Export Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Exportación de Datos</h3>
        <p className="text-gray-600 mb-6">
          Descarga todos los datos de evaluación para análisis estadísticos externos.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* CSV Export */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="text-md font-medium text-gray-900 mb-2">Exportar CSV</h4>
            <p className="text-sm text-gray-600 mb-4">
              Archivo CSV con todas las evaluaciones, métricas y datos de referencia. 
              Ideal para análisis en Excel, R, Python o SPSS.
            </p>
            <ExportButton
              type="csv"
              label="Descargar CSV"
              description="Incluye todas las tablas con joins completos"
              onExport={handleExportCsv}
              isLoading={exportToCsvMutation.isPending}
              variant="primary"
            />
          </div>

          {/* LaTeX Export */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="text-md font-medium text-gray-900 mb-2">Exportar LaTeX</h4>
            <p className="text-sm text-gray-600 mb-4">
              Tabla resumen en formato LaTeX compatible con IEEEtran. 
              Lista para incluir directamente en tu documento de tesis.
            </p>
            <ExportButton
              type="latex"
              label="Descargar LaTeX"
              description="Formato IEEEtran con métricas principales"
              onExport={handleExportLatex}
              isLoading={exportToLatexMutation.isPending}
              variant="secondary"
            />
          </div>
        </div>
      </div>

      {/* Charts Export Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Descarga de Gráficas</h3>
        <p className="text-gray-600 mb-6">
          Descarga gráficas individuales en formato PNG de alta resolución (300 DPI) para documentación.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Execution Accuracy Chart */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="ml-3">
                <h4 className="text-md font-medium text-gray-900">Execution Accuracy</h4>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Gráfico de barras mostrando el porcentaje de consultas con resultados correctos.
            </p>
            <ExportButton
              type="chart"
              label="Descargar EX"
              description="PNG 800x600 @ 300 DPI"
              onExport={() => handleDownloadChart('execution-accuracy', generateExChartMutation)}
              isLoading={generateExChartMutation.isPending}
              variant="outline"
            />
          </div>

          {/* Component Matching Chart */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div className="ml-3">
                <h4 className="text-md font-medium text-gray-900">Component Matching</h4>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Gráfico comparando F1 scores de cada componente SQL (SELECT, WHERE, etc.).
            </p>
            <ExportButton
              type="chart"
              label="Descargar Componentes"
              description="PNG 800x600 @ 300 DPI"
              onExport={() => handleDownloadChart('component-matching', generateComponentChartMutation)}
              isLoading={generateComponentChartMutation.isPending}
              variant="outline"
            />
          </div>

          {/* Time Distribution Chart */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-purple-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h4 className="text-md font-medium text-gray-900">Time-to-Answer</h4>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Histograma mostrando la distribución de tiempos de respuesta (TTA).
            </p>
            <ExportButton
              type="chart"
              label="Descargar TTA"
              description="PNG 800x600 @ 300 DPI"
              onExport={() => handleDownloadChart('time-distribution', generateTtaChartMutation)}
              isLoading={generateTtaChartMutation.isPending}
              variant="outline"
            />
          </div>
        </div>
      </div>

      {/* Usage Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex">
          <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Instrucciones de Uso</h3>
            <div className="text-sm text-blue-700 mt-2">
              <ul className="list-disc list-inside space-y-1">
                <li><strong>CSV:</strong> Úsalo para análisis estadísticos detallados en herramientas como R, Python, Excel o SPSS.</li>
                <li><strong>LaTeX:</strong> Copia y pega directamente en tu documento de tesis. Compatible con IEEEtran.</li>
                <li><strong>Gráficas PNG:</strong> Resolución de 300 DPI, ideales para publicaciones académicas y presentaciones.</li>
                <li>Todos los archivos incluyen timestamp en el nombre para evitar conflictos.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportPage;