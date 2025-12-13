/**
 * Unit tests for ChartViewer component
 * 
 * Tests the basic functionality of the generic chart viewer component
 * according to Requirements 8.1-8.5
 */

import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import ChartViewer from '../ChartViewer';

// Clean up after each test
afterEach(() => {
  cleanup();
  jest.clearAllMocks();
});

// Mock chart generation function
const mockGenerateChart = jest.fn();

// Mock blob for testing
const createMockBlob = (size: number = 1024) => {
  const blob = new Blob(['mock chart data'], { type: 'image/png' });
  Object.defineProperty(blob, 'size', { value: size });
  return blob;
};

// Mock URL.createObjectURL and revokeObjectURL
const mockCreateObjectURL = jest.fn();
const mockRevokeObjectURL = jest.fn();

beforeAll(() => {
  global.URL.createObjectURL = mockCreateObjectURL;
  global.URL.revokeObjectURL = mockRevokeObjectURL;
});

beforeEach(() => {
  mockGenerateChart.mockClear();
  mockCreateObjectURL.mockClear();
  mockRevokeObjectURL.mockClear();
  mockCreateObjectURL.mockReturnValue('mock-url');
});

describe('ChartViewer Component', () => {
  const defaultProps = {
    chartType: 'execution-accuracy' as const,
    title: 'Test Chart',
    description: 'Test chart description',
    onGenerate: mockGenerateChart,
  };

  test('renders chart viewer with title and description', () => {
    render(<ChartViewer {...defaultProps} />);
    
    expect(screen.getByText('Test Chart')).toBeInTheDocument();
    expect(screen.getByText('Test chart description')).toBeInTheDocument();
    expect(screen.getByText('Generar Gráfica')).toBeInTheDocument();
  });

  test('displays default chart options', () => {
    render(<ChartViewer {...defaultProps} />);
    
    // Check default values
    expect(screen.getByDisplayValue('800')).toBeInTheDocument(); // width
    expect(screen.getByDisplayValue('600')).toBeInTheDocument(); // height
    
    // For select elements, check the selected option
    const dpiSelect = screen.getByRole('combobox');
    expect(dpiSelect).toHaveValue('300');
  });

  test('allows changing chart options', () => {
    render(<ChartViewer {...defaultProps} />);
    
    const widthInput = screen.getByDisplayValue('800');
    const heightInput = screen.getByDisplayValue('600');
    const dpiSelect = screen.getByRole('combobox');
    
    fireEvent.change(widthInput, { target: { value: '1000' } });
    fireEvent.change(heightInput, { target: { value: '800' } });
    fireEvent.change(dpiSelect, { target: { value: '600' } });
    
    expect(screen.getByDisplayValue('1000')).toBeInTheDocument();
    expect(screen.getByDisplayValue('800')).toBeInTheDocument();
    expect(dpiSelect).toHaveValue('600');
  });

  test('generates chart when button is clicked', async () => {
    const mockBlob = createMockBlob();
    mockGenerateChart.mockResolvedValue(mockBlob);
    
    render(<ChartViewer {...defaultProps} />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    // Should show loading state
    expect(screen.getByText('Generando...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(mockGenerateChart).toHaveBeenCalledWith({
        width: 800,
        height: 600,
        dpi: 300,
      });
    });
    
    await waitFor(() => {
      expect(screen.getByText('Descargar PNG')).toBeInTheDocument();
    });
    
    expect(mockCreateObjectURL).toHaveBeenCalledWith(mockBlob);
  });

  test('passes custom options to generate function', async () => {
    const mockBlob = createMockBlob();
    mockGenerateChart.mockResolvedValue(mockBlob);
    
    render(<ChartViewer {...defaultProps} />);
    
    // Change options
    const widthInput = screen.getByDisplayValue('800');
    fireEvent.change(widthInput, { target: { value: '1200' } });
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(mockGenerateChart).toHaveBeenCalledWith({
        width: 1200,
        height: 600,
        dpi: 300,
      });
    });
  });

  test('displays error when chart generation fails', async () => {
    const errorMessage = 'Failed to generate chart';
    mockGenerateChart.mockRejectedValue(new Error(errorMessage));
    
    render(<ChartViewer {...defaultProps} />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
    
    // Should not show download button
    expect(screen.queryByText('Descargar PNG')).not.toBeInTheDocument();
  });

  test('shows chart image after successful generation', async () => {
    const mockBlob = createMockBlob();
    mockGenerateChart.mockResolvedValue(mockBlob);
    
    render(<ChartViewer {...defaultProps} />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      const image = screen.getByAltText('Test Chart');
      expect(image).toBeInTheDocument();
      expect(image).toHaveAttribute('src', 'mock-url');
    });
  });

  test('displays chart info after generation', async () => {
    const mockBlob = createMockBlob(2048);
    mockGenerateChart.mockResolvedValue(mockBlob);
    
    render(<ChartViewer {...defaultProps} />);
    
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Tamaño: 2\.0 KB/)).toBeInTheDocument();
      expect(screen.getByText(/800×600 @ 300 DPI/)).toBeInTheDocument();
    });
  });

  test('shows download button after chart generation', async () => {
    const mockBlob = createMockBlob();
    mockGenerateChart.mockResolvedValue(mockBlob);
    
    render(<ChartViewer {...defaultProps} />);
    
    // Generate chart first
    const generateButton = screen.getByText('Generar Gráfica');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText('Descargar PNG')).toBeInTheDocument();
    });
    
    expect(mockCreateObjectURL).toHaveBeenCalledWith(mockBlob);
  });

  test('uses custom default options when provided', () => {
    const customOptions = { width: 1000, height: 800, dpi: 600 };
    
    render(
      <ChartViewer 
        {...defaultProps} 
        defaultOptions={customOptions}
      />
    );
    
    expect(screen.getByDisplayValue('1000')).toBeInTheDocument();
    expect(screen.getByDisplayValue('800')).toBeInTheDocument();
    
    const dpiSelect = screen.getByRole('combobox');
    expect(dpiSelect).toHaveValue('600');
  });

  test('component unmounts without errors', () => {
    const { unmount } = render(<ChartViewer {...defaultProps} />);
    
    // Should unmount without throwing errors
    expect(() => unmount()).not.toThrow();
  });

  test('shows placeholder when no chart is generated', () => {
    render(<ChartViewer {...defaultProps} />);
    
    expect(screen.getByText('Sin gráfica')).toBeInTheDocument();
    expect(screen.getByText('Haz clic en "Generar Gráfica" para crear la visualización')).toBeInTheDocument();
  });
});