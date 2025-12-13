/**
 * Unit tests for useTimeTracking hook
 * Validates Requirements 4.1 and 4.2
 */

import { renderHook, act } from '@testing-library/react';
import { useTimeTracking } from '../useTimeTracking';

describe('useTimeTracking', () => {

  /**
   * Test for Requirement 4.1: Start time recording
   * WHEN se inicia una evaluación THEN el Sistema SHALL registrar el timestamp de inicio en `start_time`
   */
  test('should record start_time when startTracking is called', () => {
    const { result } = renderHook(() => useTimeTracking());

    // Initially, no time data should be set
    expect(result.current.timeData.startTime).toBeNull();
    expect(result.current.timeData.endTime).toBeNull();
    expect(result.current.isTracking).toBe(false);

    // Start tracking
    act(() => {
      result.current.startTracking();
    });

    // Verify start_time is recorded
    expect(result.current.timeData.startTime).toBeInstanceOf(Date);
    expect(result.current.timeData.endTime).toBeNull();
    expect(result.current.timeData.durationSeconds).toBe(0);
    expect(result.current.isTracking).toBe(true);
  });

  /**
   * Test for Requirement 4.2: End time recording
   * WHEN se completa una evaluación THEN el Sistema SHALL registrar el timestamp de finalización en `end_time`
   */
  test('should record end_time when stopTracking is called', async () => {
    const { result } = renderHook(() => useTimeTracking());

    // Start tracking first
    act(() => {
      result.current.startTracking();
    });

    const startTime = result.current.timeData.startTime;
    expect(startTime).toBeInstanceOf(Date);

    // Wait a small amount of time to ensure different timestamps
    await new Promise(resolve => setTimeout(resolve, 10));

    // Stop tracking
    act(() => {
      result.current.stopTracking();
    });

    // Verify end_time is recorded and duration is calculated
    expect(result.current.timeData.endTime).toBeInstanceOf(Date);
    expect(result.current.timeData.durationSeconds).toBeGreaterThan(0);
    expect(result.current.isTracking).toBe(false);

    // Verify end_time is after start_time
    expect(result.current.timeData.endTime!.getTime()).toBeGreaterThan(startTime!.getTime());
  });

  /**
   * Test for complete workflow: start -> stop -> data integrity
   */
  test('should maintain data integrity throughout complete workflow', async () => {
    const { result } = renderHook(() => useTimeTracking());

    // Start tracking
    act(() => {
      result.current.startTracking();
    });

    // Verify start time is recorded
    expect(result.current.timeData.startTime).toBeInstanceOf(Date);

    // Wait a small amount of time to ensure measurable duration
    await new Promise(resolve => setTimeout(resolve, 50));

    // Stop tracking
    act(() => {
      result.current.stopTracking();
    });

    const { timeData } = result.current;

    // Verify all timestamps are present
    expect(timeData.startTime).toBeInstanceOf(Date);
    expect(timeData.endTime).toBeInstanceOf(Date);
    expect(timeData.durationSeconds).toBeGreaterThan(0);

    // Verify chronological order
    expect(timeData.endTime!.getTime()).toBeGreaterThan(timeData.startTime!.getTime());

    // Verify duration calculation is reasonable (should be at least 0.04 seconds)
    expect(timeData.durationSeconds).toBeGreaterThanOrEqual(0.04);
    expect(timeData.durationSeconds).toBeLessThanOrEqual(1.0); // Should be less than 1 second
  });

  /**
   * Test for reset functionality
   */
  test('should reset all time data when resetTracking is called', async () => {
    const { result } = renderHook(() => useTimeTracking());

    // Start and stop tracking to populate data
    act(() => {
      result.current.startTracking();
    });

    await new Promise(resolve => setTimeout(resolve, 10));

    act(() => {
      result.current.stopTracking();
    });

    // Verify data is populated
    expect(result.current.timeData.startTime).toBeInstanceOf(Date);
    expect(result.current.timeData.endTime).toBeInstanceOf(Date);
    expect(result.current.timeData.durationSeconds).toBeGreaterThan(0);

    // Reset tracking
    act(() => {
      result.current.resetTracking();
    });

    // Verify all data is reset
    expect(result.current.timeData.startTime).toBeNull();
    expect(result.current.timeData.endTime).toBeNull();
    expect(result.current.timeData.durationSeconds).toBe(0);
    expect(result.current.isTracking).toBe(false);
    expect(result.current.elapsedSeconds).toBe(0);
  });

  /**
   * Test for elapsed time counter initialization
   */
  test('should initialize elapsed seconds correctly', () => {
    const { result } = renderHook(() => useTimeTracking());

    // Initially should be 0
    expect(result.current.elapsedSeconds).toBe(0);

    // Start tracking
    act(() => {
      result.current.startTracking();
    });

    // Should still be 0 initially
    expect(result.current.elapsedSeconds).toBe(0);
    expect(result.current.isTracking).toBe(true);
  });

  /**
   * Test edge case: stopTracking without startTracking
   */
  test('should handle stopTracking gracefully when not tracking', () => {
    const { result } = renderHook(() => useTimeTracking());

    // Try to stop tracking without starting
    act(() => {
      result.current.stopTracking();
    });

    // Should remain in initial state
    expect(result.current.timeData.startTime).toBeNull();
    expect(result.current.timeData.endTime).toBeNull();
    expect(result.current.timeData.durationSeconds).toBe(0);
    expect(result.current.isTracking).toBe(false);
  });
});