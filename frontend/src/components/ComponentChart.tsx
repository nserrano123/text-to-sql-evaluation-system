import React from 'react';
import ChartViewer from './ChartViewer';
import { chartsService } from '../services/chartsService';

interface ComponentChartProps {
  className?: string;
}

const ComponentChart: React.FC<ComponentChartProps> = ({ className }) => {
  return (
    <ChartViewer
      chartType="component-matching"
      title="Component Matching F1 Scores"
      description="Comparación de F1 scores por componente SQL (SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS)"
      onGenerate={chartsService.generateComponentMatchingChart}
      className={className}
      defaultOptions={{ width: 1000, height: 600, dpi: 300 }}
    />
  );
};

export default ComponentChart;