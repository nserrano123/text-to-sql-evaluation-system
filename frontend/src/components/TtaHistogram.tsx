import React from 'react';
import ChartViewer from './ChartViewer';
import { chartsService } from '../services/chartsService';

interface TtaHistogramProps {
  className?: string;
}

const TtaHistogram: React.FC<TtaHistogramProps> = ({ className }) => {
  return (
    <ChartViewer
      chartType="time-distribution"
      title="Time-to-Answer Distribution"
      description="Histograma mostrando la distribución de tiempos de respuesta (TTA) en segundos"
      onGenerate={chartsService.generateTimeDistributionChart}
      className={className}
      defaultOptions={{ width: 900, height: 600, dpi: 300 }}
    />
  );
};

export default TtaHistogram;