import React, { useState, useCallback } from 'react';
import { ChartGenerationRequest } from '../services/chartsService';

export type ChartType = 'execution-accuracy' | 'component-matching' | 'time-distribution';

interface ChartViewerProps {
  chartType: ChartType;
  title: string;
  description?: string;
  onGenerate: (options?: ChartGenerationRequest) => Promise<Blob>;
  className?: string;
  defaultOptions?: ChartGenerationRequest;
}

const ChartViewer: React.FC<ChartViewerProps> = ({
  chartType,
  title,
  description,
  onGenerate,
  className = '',
  defaultOptions = { width: 800, height: 600, dpi: 300 },
}) => {
  const [chartBlob, setChartBlob] = useState<Blob | null>(null);
  const [chartUrl, setChartUrl] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [options, setOptions] = useState<ChartGenerationRequest>(defaultOptions);

  const generateChart = useCallback(async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      const blob = await onGenerate(options);
      setChartBlob(blob);
      
      // Create object URL for display
      if (chartUrl) {
        URL.revokeObjectURL(chartUrl);
      }
      const newUrl = URL.createObjectURL(blob);
      setChartUrl(newUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error generando la gráfica');
      console.error('Error generating chart:', err);
    } finally {
      setIsGenerating(false);
    }
  }, [onGenerate, options, chartUrl]);

  const downloadChart = useCallback(() => {
    if (!chartBlob) return;

    const url = URL.createObjectURL(chartBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${chartType}-chart-${new Date().toISOString().split('T')[0]}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [chartBlob, chartType]);

  const handleOptionChange = (key: keyof ChartGenerationRequest, value: number) => {
    setOptions(prev => ({ ...prev, [key]: value }));
  };

  // Cleanup object URL on unmount
  React.useEffect(() => {
    return () => {
      if (chartUrl) {
        URL.revokeObjectURL(chartUrl);
      }
    };
  }, [chartUrl]);

  return (
    <div className={`bg-white shadow rounded-lg p-6 ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        {description && (
          <p className="text-sm text-gray-600">{description}</p>
        )}
      </div>

      {/* Chart Options */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Opciones de Gráfica</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Ancho (px)
            </label>
            <input
              type="number"
              value={options.width || 800}
              onChange={(e) => handleOptionChange('width', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              min="400"
              max="2000"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Alto (px)
            </label>
            <input
              type="number"
              value={options.height || 600}
              onChange={(e) => handleOptionChange('height', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              min="300"
              max="1500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              DPI
            </label>
            <select
              value={options.dpi || 300}
              onChange={(e) => handleOptionChange('dpi', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={150}>150 DPI (Web)</option>
              <option value={300}>300 DPI (Impresión)</option>
              <option value={600}>600 DPI (Alta calidad)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={generateChart}
          disabled={isGenerating}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generando...
            </>
          ) : (
            <>
              <svg className="-ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Generar Gráfica
            </>
          )}
        </button>

        {chartBlob && (
          <button
            onClick={downloadChart}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg className="-ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Descargar PNG
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
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

      {/* Chart Display */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        {chartUrl ? (
          <div className="relative">
            <img
              src={chartUrl}
              alt={title}
              className="w-full h-auto"
              style={{ maxHeight: '600px', objectFit: 'contain' }}
            />
            <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
              {options.width}×{options.height} @ {options.dpi} DPI
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-64 bg-gray-50">
            <div className="text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Sin gráfica</h3>
              <p className="mt-1 text-sm text-gray-500">
                Haz clic en "Generar Gráfica" para crear la visualización
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Chart Info */}
      {chartBlob && (
        <div className="mt-4 text-xs text-gray-500 text-center">
          Gráfica generada: {new Date().toLocaleString('es-ES')} | 
          Tamaño: {(chartBlob.size / 1024).toFixed(1)} KB
        </div>
      )}
    </div>
  );
};

export default ChartViewer;