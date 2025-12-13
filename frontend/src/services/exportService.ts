import api from './api';

export const exportService = {
  // Export data to CSV
  exportToCsv: async (): Promise<Blob> => {
    const response = await api.get('/api/export/csv', {
      responseType: 'blob',
    });
    return response.data;
  },

  // Export data to LaTeX
  exportToLatex: async (): Promise<Blob> => {
    const response = await api.get('/api/export/latex', {
      responseType: 'blob',
    });
    return response.data;
  },

  // Helper function to download blob as file
  downloadBlob: (blob: Blob, filename: string): void => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};