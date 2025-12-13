import React from 'react';

interface ComponentScores {
  selectCorrect: boolean;
  whereCorrect: boolean;
  groupByCorrect: boolean;
  orderByCorrect: boolean;
  keywordsCorrect: boolean;
}

interface ComponentEvaluatorProps {
  scores: ComponentScores;
  componentNotes: string;
  onScoreChange: (component: keyof ComponentScores, isCorrect: boolean) => void;
  onNotesChange: (notes: string) => void;
  disabled?: boolean;
  className?: string;
}

const ComponentEvaluator: React.FC<ComponentEvaluatorProps> = ({
  scores,
  componentNotes,
  onScoreChange,
  onNotesChange,
  disabled = false,
  className = '',
}) => {
  const components = [
    { key: 'selectCorrect' as keyof ComponentScores, label: 'SELECT', description: 'Cláusula SELECT correcta' },
    { key: 'whereCorrect' as keyof ComponentScores, label: 'WHERE', description: 'Cláusula WHERE correcta' },
    { key: 'groupByCorrect' as keyof ComponentScores, label: 'GROUP BY', description: 'Cláusula GROUP BY correcta' },
    { key: 'orderByCorrect' as keyof ComponentScores, label: 'ORDER BY', description: 'Cláusula ORDER BY correcta' },
    { key: 'keywordsCorrect' as keyof ComponentScores, label: 'KEYWORDS', description: 'Palabras clave SQL correctas' },
  ];

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-4 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Component Matching
      </h3>
      
      <p className="text-sm text-gray-600 mb-4">
        Evalúe la correctitud de cada componente SQL individualmente:
      </p>

      {/* Component Checkboxes */}
      <div className="space-y-3 mb-4">
        {components.map(({ key, label, description }) => (
          <div key={key} className="flex items-center">
            <input
              id={`component-${key}`}
              type="checkbox"
              checked={scores[key]}
              onChange={(e) => onScoreChange(key, e.target.checked)}
              disabled={disabled}
              className={`
                h-4 w-4 text-blue-600 border-gray-300 rounded
                focus:ring-blue-500 focus:ring-2
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            />
            <label 
              htmlFor={`component-${key}`}
              className={`ml-3 flex-1 ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium text-gray-900">
                    {label}
                  </span>
                  <span className="text-xs text-gray-500 ml-2">
                    {description}
                  </span>
                </div>
                <span className={`
                  text-xs px-2 py-1 rounded-full
                  ${scores[key] 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-600'
                  }
                `}>
                  {scores[key] ? 'Correcto' : 'Incorrecto'}
                </span>
              </div>
            </label>
          </div>
        ))}
      </div>

      {/* Component Summary */}
      <div className="bg-gray-50 border border-gray-200 rounded p-3 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-700">Componentes correctos:</span>
          <span className="font-medium text-gray-900">
            {Object.values(scores).filter(Boolean).length} / {Object.values(scores).length}
          </span>
        </div>
      </div>

      {/* Component Notes Field */}
      <div>
        <label htmlFor="component-notes" className="block text-sm font-medium text-gray-700 mb-2">
          Notas sobre componentes (opcional)
        </label>
        <textarea
          id="component-notes"
          value={componentNotes}
          onChange={(e) => onNotesChange(e.target.value)}
          disabled={disabled}
          rows={3}
          className={`
            w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
            focus:ring-blue-500 focus:border-blue-500 text-sm
            ${disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white'}
          `}
          placeholder="Agregue observaciones específicas sobre cada componente SQL..."
        />
      </div>
    </div>
  );
};

export default ComponentEvaluator;