/**
 * Unit tests for TtaHistogram component
 * 
 * Tests the Time-to-Answer distribution histogram component
 * according to Requirements 8.3
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TtaHistogram from '../TtaHistogram';
import { chartsService } from '../../services/chartsService';

// Mock the charts service
jest.mock('../../services/chartsService', () => ({
  chartsService: {
    generateTimeDistributionChart: jest.fn(),
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

describe('TtaHistogram Component', () => {
  test('renders with correct title and description', () => {
    render(<TtaHistogram />);
    
    expect(screen.getByText('Time-to-Answer Distribution')).toBeInTheDocument();
    expect(screen.getByText('Histograma mostrando la distribución de tiempos de respuesta (TTA) en segundos')).toBeInTheDocument();
  });

  test('uses correct default options for histogram display', () => {
    render(<TtaHistogram />);
    
    // Check default dimensions (slightly wider for histogram)
    expect(screen.getByDisplayValue('900')).toBeInTheDocument(); // width
    expect(screen.getByDisplayValue('600')).toBeInTheDocument(); // height
    
    // Check default DPI
    const dpiSelect = screen.getByRole('combobox');
    expect(dpiSelect).toHaveValue('300');
  });

  test('calls time distribution chart service when generating', async () => {
    const mockBlob = new Blob(['mock chart data'], { type: 'image/png' });
    mockChartsService.generateTimeDistributionChart.mockResolvedValue(mockBlob);
    
    render(<TtaHistogram />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(mockChartsService.generateTimeDistributionChart).toHaveBeenCalledWith({
        width: 900,
        height: 600,
        dpi: 300,
      });
    });
  });

  test('passes custom options to service', async () => {
    const mockBlob = new Blob(['mock chart data'], { type: 'image/png' });
    mockChartsService.generateTimeDistributionChart.mockResolvedValue(mockBlob);
    
    render(<TtaHistogram />);
    
    // Change DPI
    const dpiSelect = screen.getByRole('combobox');
    fireEvent.change(dpiSelect, { target: { value: '600' } });
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(mockChartsService.generateTimeDistributionChart).toHaveBeenCalledWith({
        width: 900,
        height: 600,
        dpi: 600,
      });
    });
  });

  test('applies custom className', () => {
    const { container } = render(<TtaHistogram className="custom-class" />);
    
    const chartContainer = container.querySelector('.custom-class');
    expect(chartContainer).toBeInTheDocument();
  });

  test('handles service errors gracefully', async () => {
    const errorMessage = 'Failed to generate TTA histogram';
    mockChartsService.generateTimeDistributionChart.mockRejectedValue(new Error(errorMessage));
    
    render(<TtaHistogram />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
});