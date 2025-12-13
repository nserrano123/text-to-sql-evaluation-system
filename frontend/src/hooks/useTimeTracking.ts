import { useState, useEffect, useRef } from 'react';

interface TimeTrackingData {
  startTime: Date | null;
  endTime: Date | null;
  durationSeconds: number;
}

interface UseTimeTrackingReturn {
  timeData: TimeTrackingData;
  startTracking: () => void;
  stopTracking: () => void;
  resetTracking: () => void;
  isTracking: boolean;
  elapsedSeconds: number;
}

export const useTimeTracking = (): UseTimeTrackingReturn => {
  const [timeData, setTimeData] = useState<TimeTrackingData>({
    startTime: null,
    endTime: null,
    durationSeconds: 0,
  });
  
  const [isTracking, setIsTracking] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Start tracking time
  const startTracking = () => {
    const now = new Date();
    setTimeData(prev => ({
      ...prev,
      startTime: now,
      endTime: null,
      durationSeconds: 0,
    }));
    setIsTracking(true);
    setElapsedSeconds(0);
  };

  // Stop tracking time
  const stopTracking = () => {
    setTimeData(prev => {
      if (!prev.startTime) return prev;
      
      const now = new Date();
      const duration = (now.getTime() - prev.startTime.getTime()) / 1000;
      
      return {
        ...prev,
        endTime: now,
        durationSeconds: duration,
      };
    });
    setIsTracking(false);
  };

  // Reset tracking
  const resetTracking = () => {
    setTimeData({
      startTime: null,
      endTime: null,
      durationSeconds: 0,
    });
    setIsTracking(false);
    setElapsedSeconds(0);
  };

  // Update elapsed time every second while tracking
  useEffect(() => {
    if (isTracking && timeData.startTime) {
      intervalRef.current = setInterval(() => {
        const now = new Date();
        const elapsed = (now.getTime() - timeData.startTime!.getTime()) / 1000;
        setElapsedSeconds(Math.floor(elapsed));
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isTracking, timeData.startTime]);

  return {
    timeData,
    startTracking,
    stopTracking,
    resetTracking,
    isTracking,
    elapsedSeconds,
  };
};