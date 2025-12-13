/**
 * Unit tests for ExChart component
 * 
 * Tests the Execution Accuracy chart component
 * according to Requirements 8.1
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ExChart from '../ExChart';
import { chartsService } from '../../services/chartsService';

// Mock the charts service
jest.mock('../../services/chartsService', () => ({
  chartsService: {
    generateExecutionAccuracyChart: jest.fn(),
  },
}));

const mockChartsService = chartsService as jest.Mocked<typeof chartsService>;

// Mock URL methods
const mockCreateObjectURL = jest.fn();
const mockRevokeObjectURL = jest.fn();

beforeAll(() => {
  global.URL.createObjectURL = mockCreateObjectURL;
  global.URL.revokeObjectURL = mockRevokeObjectURL;
});

beforeEach(() => {
  jest.clearAllMocks();
  mockCreateObjectURL.mockReturnValue('mock-url');
});

describe('ExChart Component', () => {
  test('renders with correct title and description', () => {
    render(<ExChart />);
    
    expect(screen.getByText('Execution Accuracy (EX)')).toBeInTheDocument();
    expect(screen.getByText('Porcentaje de consultas SQL que producen resultados correctos')).toBeInTheDocument();
  });

  test('uses correct default options', () => {
    render(<ExChart />);
    
    // Check default dimensions
    expect(screen.getByDisplayValue('800')).toBeInTheDocument(); // width
    expect(screen.getByDisplayValue('600')).toBeInTheDocument(); // height
    
    // Check default DPI
    const dpiSelect = screen.getByRole('combobox');
    expect(dpiSelect).toHaveValue('300');
  });

  test('calls execution accuracy chart service when generating', async () => {
    const mockBlob = new Blob(['mock chart data'], { type: 'image/png' });
    mockChartsService.generateExecutionAccuracyChart.mockResolvedValue(mockBlob);
    
    render(<ExChart />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(mockChartsService.generateExecutionAccuracyChart).toHaveBeenCalledWith({
        width: 800,
        height: 600,
        dpi: 300,
      });
    });
  });

  test('passes custom options to service', async () => {
    const mockBlob = new Blob(['mock chart data'], { type: 'image/png' });
    mockChartsService.generateExecutionAccuracyChart.mockResolvedValue(mockBlob);
    
    render(<ExChart />);
    
    // Change width
    const widthInput = screen.getByDisplayValue('800');
    fireEvent.change(widthInput, { target: { value: '1000' } });
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(mockChartsService.generateExecutionAccuracyChart).toHaveBeenCalledWith({
        width: 1000,
        height: 600,
        dpi: 300,
      });
    });
  });

  test('applies custom className', () => {
    const { container } = render(<ExChart className="custom-class" />);
    
    const chartContainer = container.querySelector('.custom-class');
    expect(chartContainer).toBeInTheDocument();
  });

  test('handles service errors gracefully', async () => {
    const errorMessage = 'Failed to generate EX chart';
    mockChartsService.generateExecutionAccuracyChart.mockRejectedValue(new Error(errorMessage));
    
    render(<ExChart />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
});