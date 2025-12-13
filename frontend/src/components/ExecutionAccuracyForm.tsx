import React from 'react';

interface ExecutionAccuracyFormProps {
  isCorrect: boolean;
  evaluatorNotes: string;
  onIsCorrectChange: (isCorrect: boolean) => void;
  onNotesChange: (notes: string) => void;
  disabled?: boolean;
  className?: string;
}

const ExecutionAccuracyForm: React.FC<ExecutionAccuracyFormProps> = ({
  isCorrect,
  evaluatorNotes,
  onIsCorrectChange,
  onNotesChange,
  disabled = false,
  className = '',
}) => {
  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-4 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Execution Accuracy (EX)
      </h3>
      
      {/* Correctness Buttons */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ¿La consulta generada produce resultados correctos?
        </label>
        <div className="flex space-x-3">
          <button
            type="button"
            onClick={() => onIsCorrectChange(true)}
            disabled={disabled}
            className={`
              flex items-center px-4 py-2 rounded-md border font-medium text-sm transition-colors
              ${isCorrect
                ? 'bg-green-100 border-green-300 text-green-800 ring-2 ring-green-500 ring-opacity-50'
                : 'bg-white border-gray-300 text-gray-700 hover:bg-green-50 hover:border-green-300'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <span className="mr-2">✅</span>
            Correcto
          </button>
          
          <button
            type="button"
            onClick={() => onIsCorrectChange(false)}
            disabled={disabled}
            className={`
              flex items-center px-4 py-2 rounded-md border font-medium text-sm transition-colors
              ${!isCorrect
                ? 'bg-red-100 border-red-300 text-red-800 ring-2 ring-red-500 ring-opacity-50'
                : 'bg-white border-gray-300 text-gray-700 hover:bg-red-50 hover:border-red-300'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <span className="mr-2">❌</span>
            Incorrecto
          </button>
        </div>
      </div>

      {/* Notes Field */}
      <div>
        <label htmlFor="execution-notes" className="block text-sm font-medium text-gray-700 mb-2">
          Notas de evaluación (opcional)
        </label>
        <textarea
          id="execution-notes"
          value={evaluatorNotes}
          onChange={(e) => onNotesChange(e.target.value)}
          disabled={disabled}
          rows={3}
          className={`
            w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
            focus:ring-blue-500 focus:border-blue-500 text-sm
            ${disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white'}
          `}
          placeholder="Agregue observaciones sobre la correctitud de la consulta..."
        />
      </div>
    </div>
  );
};

export default ExecutionAccuracyForm;