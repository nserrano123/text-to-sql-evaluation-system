// Base types corresponding to backend Pydantic models

export interface GoldQuery {
  id: string;
  chatInput: string;
  sessionId?: string;
  memberId?: string;
  clasificacion?: string;
  preguntaDescompuesta?: string;
  tablasColumnasDdl: string;
  sqlReference: string;
  createdAt: Date;
}

export interface Evaluation {
  id: string;
  goldQueryId: string;
  generatedSql: string;
  evaluationDate: Date;
  createdAt: Date;
}

export interface ExecutionAccuracy {
  id: string;
  evaluationId: string;
  resultsMatch?: boolean;
  isCorrect: boolean;
  evaluatorNotes?: string;
  createdAt: Date;
}

export interface TimeToAnswer {
  id: string;
  evaluationId: string;
  startTime: Date;
  endTime: Date;
  durationSeconds: number;
  createdAt: Date;
}

export interface ComponentMatching {
  id: string;
  evaluationId: string;
  selectCorrect: boolean;
  whereCorrect: boolean;
  groupByCorrect: boolean;
  orderByCorrect: boolean;
  keywordsCorrect: boolean;
  f1Score?: number;
  evaluatorNotes?: string;
  createdAt: Date;
}

export interface MetricsSummary {
  executionAccuracy: number; // Percentage
  averageTimeToAnswer: number; // Seconds
  componentScores: {
    select: number;
    where: number;
    groupBy: number;
    orderBy: number;
    keywords: number;
  };
  totalEvaluations: number;
  completedEvaluations: number;
}

// UI-specific types

export interface EvaluationFormData {
  isCorrect: boolean;
  evaluatorNotes?: string;
  selectCorrect: boolean;
  whereCorrect: boolean;
  groupByCorrect: boolean;
  orderByCorrect: boolean;
  keywordsCorrect: boolean;
  componentNotes?: string;
}

export interface QueryComparisonData {
  goldQuery: GoldQuery;
  generatedSql: string;
}

export interface DashboardStats {
  totalQueries: number;
  evaluatedQueries: number;
  progressPercentage: number;
  pendingQueries: number;
}

// API Response types

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

// Chart types

export interface ChartData {
  label: string;
  value: number;
  color?: string;
}

export interface ComponentScoreData {
  component: string;
  score: number;
}

export interface TimeDistributionData {
  range: string;
  count: number;
}

// Export types

export interface ExportOptions {
  format: 'csv' | 'latex';
  includeNotes?: boolean;
  dateRange?: {
    start: Date;
    end: Date;
  };
}

// Navigation types

export interface NavItem {
  path: string;
  label: string;
  icon: string;
}

// Form validation types

export interface ValidationError {
  field: string;
  message: string;
}

export interface FormState<T> {
  data: T;
  errors: ValidationError[];
  isValid: boolean;
  isDirty: boolean;
}

// Loading states

export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

// Pagination types

export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}