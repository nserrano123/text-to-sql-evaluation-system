import React from 'react';
import ChartViewer from './ChartViewer';
import { chartsService } from '../services/chartsService';

interface ExChartProps {
  className?: string;
}

const ExChart: React.FC<ExChartProps> = ({ className }) => {
  return (
    <ChartViewer
      chartType="execution-accuracy"
      title="Execution Accuracy (EX)"
      description="Porcentaje de consultas SQL que producen resultados correctos"
      onGenerate={chartsService.generateExecutionAccuracyChart}
      className={className}
      defaultOptions={{ width: 800, height: 600, dpi: 300 }}
    />
  );
};

export default ExChart;