/**
 * Unit tests for ComponentChart component
 * 
 * Tests the Component Matching F1 scores chart component
 * according to Requirements 8.2
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ComponentChart from '../ComponentChart';
import { chartsService } from '../../services/chartsService';

// Mock the charts service
jest.mock('../../services/chartsService', () => ({
  chartsService: {
    generateComponentMatchingChart: jest.fn(),
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

describe('ComponentChart Component', () => {
  test('renders with correct title and description', () => {
    render(<ComponentChart />);
    
    expect(screen.getByText('Component Matching F1 Scores')).toBeInTheDocument();
    expect(screen.getByText('Comparación de F1 scores por componente SQL (SELECT, WHERE, GROUP BY, ORDER BY, KEYWORDS)')).toBeInTheDocument();
  });

  test('uses correct default options with wider width for component comparison', () => {
    render(<ComponentChart />);
    
    // Check default dimensions (wider for component comparison)
    expect(screen.getByDisplayValue('1000')).toBeInTheDocument(); // width
    expect(screen.getByDisplayValue('600')).toBeInTheDocument(); // height
    
    // Check default DPI
    const dpiSelect = screen.getByRole('combobox');
    expect(dpiSelect).toHaveValue('300');
  });

  test('calls component matching chart service when generating', async () => {
    const mockBlob = new Blob(['mock chart data'], { type: 'image/png' });
    mockChartsService.generateComponentMatchingChart.mockResolvedValue(mockBlob);
    
    render(<ComponentChart />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(mockChartsService.generateComponentMatchingChart).toHaveBeenCalledWith({
        width: 1000,
        height: 600,
        dpi: 300,
      });
    });
  });

  test('passes custom options to service', async () => {
    const mockBlob = new Blob(['mock chart data'], { type: 'image/png' });
    mockChartsService.generateComponentMatchingChart.mockResolvedValue(mockBlob);
    
    render(<ComponentChart />);
    
    // Change height
    const heightInput = screen.getByDisplayValue('600');
    fireEvent.change(heightInput, { target: { value: '800' } });
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(mockChartsService.generateComponentMatchingChart).toHaveBeenCalledWith({
        width: 1000,
        height: 800,
        dpi: 300,
      });
    });
  });

  test('applies custom className', () => {
    const { container } = render(<ComponentChart className="custom-class" />);
    
    const chartContainer = container.querySelector('.custom-class');
    expect(chartContainer).toBeInTheDocument();
  });

  test('handles service errors gracefully', async () => {
    const errorMessage = 'Failed to generate component chart';
    mockChartsService.generateComponentMatchingChart.mockRejectedValue(new Error(errorMessage));
    
    render(<ComponentChart />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
});