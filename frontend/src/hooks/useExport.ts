import { useMutation } from '@tanstack/react-query';
import { exportService } from '../services/exportService';

// Export to CSV
export const useExportToCsv = () => {
  return useMutation({
    mutationFn: exportService.exportToCsv,
    onSuccess: (blob) => {
      const timestamp = new Date().toISOString().split('T')[0];
      exportService.downloadBlob(blob, `evaluations-${timestamp}.csv`);
    },
  });
};

// Export to LaTeX
export const useExportToLatex = () => {
  return useMutation({
    mutationFn: exportService.exportToLatex,
    onSuccess: (blob) => {
      const timestamp = new Date().toISOString().split('T')[0];
      exportService.downloadBlob(blob, `evaluations-summary-${timestamp}.tex`);
    },
  });
};