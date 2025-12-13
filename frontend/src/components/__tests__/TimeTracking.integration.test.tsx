/**
 * Integration test for time tracking functionality in EvaluationPage
 * Tests Requirements 4.1 and 4.2
 */

import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import EvaluationPage from '../../pages/EvaluationPage';

// Mock the API and services
jest.mock('../../services/api', () => ({
  default: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  }
}));

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ queryId: 'test-query-id' }),
}));

// Mock the hooks with real time tracking behavior
jest.mock('../../hooks/useGoldQueries', () => ({
  useGoldQuery: jest.fn(),
  usePendingGoldQueries: jest.fn(),
}));

jest.mock('../../hooks/useEvaluations', () => ({
  useCreateEvaluation: jest.fn(),
}));

// Use the real useTimeTracking hook
jest.unmock('../../hooks/useTimeTracking');

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Time Tracking Integration', () => {
  let useGoldQuery: jest.MockedFunction<any>;
  let usePendingGoldQueries: jest.MockedFunction<any>;
  let useCreateEvaluation: jest.MockedFunction<any>;

  const mockGoldQuery = {
    id: 'test-query-id',
    chatInput: 'Test chat input',
    tablasColumnasDdl: 'CREATE TABLE test (id INT);',
    sqlReference: 'SELECT * FROM test;',
    createdAt: new Date(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();

    // Get mocked hooks
    useGoldQuery = require('../../hooks/useGoldQueries').useGoldQuery;
    usePendingGoldQueries = require('../../hooks/useGoldQueries').usePendingGoldQueries;
    useCreateEvaluation = require('../../hooks/useEvaluations').useCreateEvaluation;

    // Setup default mocks
    useGoldQuery.mockReturnValue({
      data: mockGoldQuery,
      isLoading: false,
      error: null,
    });

    usePendingGoldQueries.mockReturnValue({
      data: [mockGoldQuery],
      refetch: jest.fn().mockResolvedValue({ data: [] }),
    });

    useCreateEvaluation.mockReturnValue({
      mutateAsync: jest.fn().mockResolvedValue({}),
    });
  });

  /**
   * Test for Requirement 4.1: Start time recording
   * WHEN se inicia una evaluación THEN el Sistema SHALL registrar el timestamp de inicio en `start_time`
   */
  test('should start time tracking when query loads', async () => {
    render(
      <TestWrapper>
        <EvaluationPage />
      </TestWrapper>
    );

    // Wait for component to load and start tracking
    await waitFor(() => {
      expect(screen.getByText(/Tiempo:/)).toBeInTheDocument();
    });

    // Check that timer is displayed (starts at 0:00)
    expect(screen.getByText(/0:00/)).toBeInTheDocument();

    // Wait a moment and check that time is progressing
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 1100)); // Wait slightly over 1 second
    });

    // Time should have progressed (should show 0:01 or similar)
    await waitFor(() => {
      const timeElement = screen.getByText(/\d+:\d{2}/);
      expect(timeElement).toBeInTheDocument();
      // Should not still be 0:00 after waiting
      expect(timeElement.textContent).not.toBe('0:00');
    });
  });

  /**
   * Test for Requirement 4.2: End time recording
   * WHEN se completa una evaluación THEN el Sistema SHALL registrar el timestamp de finalización en `end_time`
   */
  test('should stop time tracking when evaluation is saved', async () => {
    const mockMutateAsync = jest.fn().mockResolvedValue({});
    useCreateEvaluation.mockReturnValue({
      mutateAsync: mockMutateAsync,
    });

    render(
      <TestWrapper>
        <EvaluationPage />
      </TestWrapper>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText(/Tiempo:/)).toBeInTheDocument();
    });

    // Wait for time to progress
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 1100));
    });

    // Add generated SQL to enable save button
    const sqlTextarea = screen.getByPlaceholderText(/Pegue aquí la consulta SQL/);
    await act(async () => {
      sqlTextarea.focus();
      // Simulate typing
      (sqlTextarea as HTMLTextAreaElement).value = 'SELECT * FROM test WHERE id = 1;';
      sqlTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    });

    // Find and click the save button
    const saveButton = screen.getByText(/Guardar Evaluación/);
    expect(saveButton).not.toBeDisabled();

    await act(async () => {
      saveButton.click();
    });

    // Verify that the evaluation was created with time tracking data
    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({
          time_to_answer: expect.objectContaining({
            startTime: expect.any(Date),
            endTime: expect.any(Date),
            durationSeconds: expect.any(Number),
          }),
        })
      );
    });

    // Verify that end time is after start time
    const callArgs = mockMutateAsync.mock.calls[0][0];
    const timeToAnswer = callArgs.time_to_answer;
    expect(timeToAnswer.endTime.getTime()).toBeGreaterThan(timeToAnswer.startTime.getTime());
    expect(timeToAnswer.durationSeconds).toBeGreaterThan(0);
  });

  /**
   * Test for complete time tracking workflow
   */
  test('should track complete evaluation workflow with proper timestamps', async () => {
    const mockMutateAsync = jest.fn().mockResolvedValue({});
    useCreateEvaluation.mockReturnValue({
      mutateAsync: mockMutateAsync,
    });

    render(
      <TestWrapper>
        <EvaluationPage />
      </TestWrapper>
    );

    // Record start time for comparison
    const testStartTime = new Date();

    // Wait for component to load and tracking to start
    await waitFor(() => {
      expect(screen.getByText(/Tiempo:/)).toBeInTheDocument();
    });

    // Wait for some time to pass
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 1500)); // 1.5 seconds
    });

    // Fill in the evaluation form
    const sqlTextarea = screen.getByPlaceholderText(/Pegue aquí la consulta SQL/);
    await act(async () => {
      sqlTextarea.focus();
      (sqlTextarea as HTMLTextAreaElement).value = 'SELECT * FROM test WHERE id = 1;';
      sqlTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    });

    // Mark as correct
    const correctButton = screen.getByText(/Correcto/);
    await act(async () => {
      correctButton.click();
    });

    // Save the evaluation
    const saveButton = screen.getByText(/Guardar Evaluación/);
    await act(async () => {
      saveButton.click();
    });

    const testEndTime = new Date();

    // Verify the complete evaluation was created with proper time tracking
    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({
          gold_query_id: mockGoldQuery.id,
          generated_sql: 'SELECT * FROM test WHERE id = 1;',
          execution_accuracy: expect.objectContaining({
            isCorrect: true,
          }),
          time_to_answer: expect.objectContaining({
            startTime: expect.any(Date),
            endTime: expect.any(Date),
            durationSeconds: expect.any(Number),
          }),
          component_matching: expect.objectContaining({
            selectCorrect: expect.any(Boolean),
            whereCorrect: expect.any(Boolean),
            groupByCorrect: expect.any(Boolean),
            orderByCorrect: expect.any(Boolean),
            keywordsCorrect: expect.any(Boolean),
          }),
        })
      );
    });

    // Verify timing constraints
    const callArgs = mockMutateAsync.mock.calls[0][0];
    const timeToAnswer = callArgs.time_to_answer;
    
    // Start time should be after test start but before test end
    expect(timeToAnswer.startTime.getTime()).toBeGreaterThanOrEqual(testStartTime.getTime() - 100); // Allow 100ms tolerance
    expect(timeToAnswer.startTime.getTime()).toBeLessThanOrEqual(testEndTime.getTime());
    
    // End time should be after start time and before test end
    expect(timeToAnswer.endTime.getTime()).toBeGreaterThan(timeToAnswer.startTime.getTime());
    expect(timeToAnswer.endTime.getTime()).toBeLessThanOrEqual(testEndTime.getTime() + 100); // Allow 100ms tolerance
    
    // Duration should match the time difference
    const expectedDuration = (timeToAnswer.endTime.getTime() - timeToAnswer.startTime.getTime()) / 1000;
    expect(Math.abs(timeToAnswer.durationSeconds - expectedDuration)).toBeLessThan(0.01);
    
    // Duration should be reasonable (at least 1 second, less than test duration + tolerance)
    expect(timeToAnswer.durationSeconds).toBeGreaterThanOrEqual(1.0);
    expect(timeToAnswer.durationSeconds).toBeLessThan(10.0); // Should complete within 10 seconds
  });

  /**
   * Test timer display updates
   */
  test('should display elapsed time correctly', async () => {
    render(
      <TestWrapper>
        <EvaluationPage />
      </TestWrapper>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText(/Tiempo:/)).toBeInTheDocument();
    });

    // Initially should show 0:00
    expect(screen.getByText(/0:00/)).toBeInTheDocument();

    // Wait for timer to update
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 2100)); // Wait over 2 seconds
    });

    // Should show elapsed time (0:02 or similar)
    await waitFor(() => {
      const timeDisplay = screen.getByText(/\d+:\d{2}/);
      expect(timeDisplay).toBeInTheDocument();
      
      // Parse the displayed time
      const timeText = timeDisplay.textContent || '';
      const [minutes, seconds] = timeText.split(':').map(Number);
      const totalSeconds = minutes * 60 + seconds;
      
      // Should show at least 2 seconds have passed
      expect(totalSeconds).toBeGreaterThanOrEqual(2);
    });
  });
});