import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import QueryComparison from '../components/QueryComparison';
import ExecutionAccuracyForm from '../components/ExecutionAccuracyForm';
import ComponentEvaluator from '../components/ComponentEvaluator';
import { useGoldQuery, usePendingGoldQueries } from '../hooks/useGoldQueries';
import { useCreateEvaluation } from '../hooks/useEvaluations';
import { useTimeTracking } from '../hooks/useTimeTracking';
import { EvaluationFormData, QueryComparisonData } from '../types';

interface ComponentScores {
  selectCorrect: boolean;
  whereCorrect: boolean;
  groupByCorrect: boolean;
  orderByCorrect: boolean;
  keywordsCorrect: boolean;
}

const EvaluationPage: React.FC = () => {
  const navigate = useNavigate();
  const { queryId } = useParams<{ queryId: string }>();
  
  // Hooks for data fetching
  const { data: goldQuery, isLoading: isLoadingQuery, error: queryError } = useGoldQuery(queryId ?? '');
  const { data: pendingQueries, refetch: refetchPending } = usePendingGoldQueries();
  const createEvaluationMutation = useCreateEvaluation();
  
  // Time tracking
  const { timeData, startTracking, stopTracking, resetTracking, elapsedSeconds } = useTimeTracking();
  
  // Form state
  const [formData, setFormData] = useState<EvaluationFormData>({
    isCorrect: false,
    evaluatorNotes: '',
    selectCorrect: false,
    whereCorrect: false,
    groupByCorrect: false,
    orderByCorrect: false,
    keywordsCorrect: false,
    componentNotes: '',
  });
  
  const [generatedSql, setGeneratedSql] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Start time tracking when query loads
  useEffect(() => {
    if (goldQuery) {
      // Reset and start fresh tracking for each new query
      resetTracking();
      startTracking();
    }
  }, [goldQuery?.id, resetTracking, startTracking]);

  // Auto-navigate to next pending query if no queryId provided
  useEffect(() => {
    if (!queryId && pendingQueries && pendingQueries.length > 0) {
      navigate(`/evaluation/${pendingQueries[0].id}`, { replace: true });
    } else if (!queryId && pendingQueries && pendingQueries.length === 0) {
      // If no queryId and no pending queries, show completion message
      return;
    }
  }, [queryId, pendingQueries, navigate]);

  // Handle form field changes
  const handleIsCorrectChange = (isCorrect: boolean) => {
    setFormData(prev => ({ ...prev, isCorrect }));
  };

  const handleNotesChange = (evaluatorNotes: string) => {
    setFormData(prev => ({ ...prev, evaluatorNotes }));
  };

  const handleComponentScoreChange = (component: keyof ComponentScores, isCorrect: boolean) => {
    setFormData(prev => ({ ...prev, [component]: isCorrect }));
  };

  const handleComponentNotesChange = (componentNotes: string) => {
    setFormData(prev => ({ ...prev, componentNotes }));
  };

  // Calculate F1 score for components
  const calculateF1Score = (scores: ComponentScores): number => {
    const correctComponents = Object.values(scores).filter(Boolean).length;
    const totalComponents = Object.values(scores).length;
    
    if (totalComponents === 0) return 0;
    
    // For component matching, we treat it as precision = recall = correctComponents/totalComponents
    const precision = correctComponents / totalComponents;
    const recall = precision; // In this context, precision equals recall
    
    if (precision + recall === 0) return 0;
    return (2 * precision * recall) / (precision + recall);
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!goldQuery || !generatedSql.trim()) {
      alert('Por favor ingrese la consulta SQL generada');
      return;
    }

    setIsSaving(true);
    stopTracking();

    try {
      const componentScores: ComponentScores = {
        selectCorrect: formData.selectCorrect,
        whereCorrect: formData.whereCorrect,
        groupByCorrect: formData.groupByCorrect,
        orderByCorrect: formData.orderByCorrect,
        keywordsCorrect: formData.keywordsCorrect,
      };

      const evaluationRequest = {
        gold_query_id: goldQuery.id,
        generated_sql: generatedSql.trim(),
        execution_accuracy: {
          resultsMatch: undefined, // This could be determined programmatically in the future
          isCorrect: formData.isCorrect,
          evaluatorNotes: formData.evaluatorNotes || undefined,
        },
        time_to_answer: {
          startTime: timeData.startTime!,
          endTime: timeData.endTime!,
          durationSeconds: timeData.durationSeconds,
        },
        component_matching: {
          selectCorrect: componentScores.selectCorrect,
          whereCorrect: componentScores.whereCorrect,
          groupByCorrect: componentScores.groupByCorrect,
          orderByCorrect: componentScores.orderByCorrect,
          keywordsCorrect: componentScores.keywordsCorrect,
          f1Score: calculateF1Score(componentScores),
          evaluatorNotes: formData.componentNotes || undefined,
        },
      };

      await createEvaluationMutation.mutateAsync(evaluationRequest);
      
      // Refetch pending queries to get updated list
      await refetchPending();
      
      // Navigate to next pending query or dashboard
      const updatedPending = await refetchPending();
      if (updatedPending.data && updatedPending.data.length > 0) {
        // Find next query (not the current one)
        const nextQuery = updatedPending.data.find(q => q.id !== goldQuery.id);
        if (nextQuery) {
          navigate(`/evaluation/${nextQuery.id}`);
        } else {
          navigate('/dashboard');
        }
      } else {
        navigate('/dashboard');
      }
      
      // Reset form for next evaluation
      setFormData({
        isCorrect: false,
        evaluatorNotes: '',
        selectCorrect: false,
        whereCorrect: false,
        groupByCorrect: false,
        orderByCorrect: false,
        keywordsCorrect: false,
        componentNotes: '',
      });
      setGeneratedSql('');
      
    } catch (error) {
      console.error('Error saving evaluation:', error);
      alert('Error al guardar la evaluación. Por favor intente nuevamente.');
    } finally {
      setIsSaving(false);
    }
  };

  // Loading state
  if (isLoadingQuery) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando consulta...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (queryError || !goldQuery) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-red-900 mb-2">Error</h2>
        <p className="text-red-700 mb-4">
          {queryError ? 'Error al cargar la consulta' : 'Consulta no encontrada'}
        </p>
        <button
          onClick={() => navigate('/dashboard')}
          className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
        >
          Volver al Dashboard
        </button>
      </div>
    );
  }

  // No pending queries
  if (pendingQueries && pendingQueries.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <h2 className="text-lg font-semibold text-green-900 mb-2">
          ¡Evaluación Completa!
        </h2>
        <p className="text-green-700 mb-4">
          No hay consultas pendientes de evaluación.
        </p>
        <button
          onClick={() => navigate('/dashboard')}
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
        >
          Ver Resultados
        </button>
      </div>
    );
  }

  const queryComparisonData: QueryComparisonData = {
    goldQuery,
    generatedSql,
  };

  const componentScores: ComponentScores = {
    selectCorrect: formData.selectCorrect,
    whereCorrect: formData.whereCorrect,
    groupByCorrect: formData.groupByCorrect,
    orderByCorrect: formData.orderByCorrect,
    keywordsCorrect: formData.keywordsCorrect,
  };

  return (
    <div className="space-y-6">
      {/* Header with progress and timer */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Evaluación de Consulta SQL
          </h1>
          <div className="flex items-center space-x-4">
            {pendingQueries && (
              <span className="text-sm text-gray-600">
                Pendientes: {pendingQueries.length}
              </span>
            )}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Tiempo:</span>
              <span className="font-mono text-lg text-blue-600">
                {Math.floor(elapsedSeconds / 60)}:{(elapsedSeconds % 60).toString().padStart(2, '0')}
              </span>
            </div>
          </div>
        </div>
        
        {/* Generated SQL Input */}
        <div className="mb-4">
          <label htmlFor="generated-sql" className="block text-sm font-medium text-gray-700 mb-2">
            Consulta SQL Generada por IA *
          </label>
          <textarea
            id="generated-sql"
            value={generatedSql}
            onChange={(e) => setGeneratedSql(e.target.value)}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
            placeholder="Pegue aquí la consulta SQL generada por el modelo de IA..."
            required
          />
        </div>
      </div>

      {/* Query Comparison */}
      {generatedSql && (
        <QueryComparison data={queryComparisonData} />
      )}

      {/* Evaluation Forms */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Execution Accuracy Form */}
        <ExecutionAccuracyForm
          isCorrect={formData.isCorrect}
          evaluatorNotes={formData.evaluatorNotes || ''}
          onIsCorrectChange={handleIsCorrectChange}
          onNotesChange={handleNotesChange}
          disabled={isSaving}
        />

        {/* Component Evaluator */}
        <ComponentEvaluator
          scores={componentScores}
          componentNotes={formData.componentNotes || ''}
          onScoreChange={handleComponentScoreChange}
          onNotesChange={handleComponentNotesChange}
          disabled={isSaving}
        />
      </div>

      {/* Action Buttons */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            disabled={isSaving}
          >
            Cancelar
          </button>
          
          <button
            onClick={handleSubmit}
            disabled={isSaving || !generatedSql.trim()}
            className={`
              px-6 py-2 rounded-md font-medium
              ${isSaving || !generatedSql.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            {isSaving ? 'Guardando...' : 'Guardar Evaluación'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EvaluationPage;