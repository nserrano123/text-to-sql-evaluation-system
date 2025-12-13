import React from 'react';

export type ExportType = 'csv' | 'latex' | 'chart';

interface ExportButtonProps {
  type: ExportType;
  label: string;
  description?: string;
  onExport: () => Promise<void>;
  isLoading?: boolean;
  disabled?: boolean;
  className?: string;
  icon?: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
}

const ExportButton: React.FC<ExportButtonProps> = ({
  type,
  label,
  description,
  onExport,
  isLoading = false,
  disabled = false,
  className = '',
  icon,
  variant = 'primary',
}) => {
  const handleClick = async () => {
    if (isLoading || disabled) return;
    
    try {
      await onExport();
    } catch (error) {
      console.error(`Error exporting ${type}:`, error);
    }
  };

  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 border-transparent';
      case 'secondary':
        return 'text-white bg-gray-600 hover:bg-gray-700 focus:ring-gray-500 border-transparent';
      case 'outline':
        return 'text-gray-700 bg-white hover:bg-gray-50 focus:ring-blue-500 border-gray-300';
      default:
        return 'text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 border-transparent';
    }
  };

  const getDefaultIcon = () => {
    switch (type) {
      case 'csv':
        return (
          <svg className="-ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'latex':
        return (
          <svg className="-ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        );
      case 'chart':
        return (
          <svg className="-ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      default:
        return (
          <svg className="-ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
    }
  };

  const loadingSpinner = (
    <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  );

  return (
    <div className={`${className}`}>
      <button
        onClick={handleClick}
        disabled={isLoading || disabled}
        className={`
          inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md
          focus:outline-none focus:ring-2 focus:ring-offset-2
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors duration-200
          ${getVariantClasses()}
        `}
      >
        {isLoading ? loadingSpinner : (icon || getDefaultIcon())}
        {isLoading ? 'Exportando...' : label}
      </button>
      
      {description && (
        <p className="mt-1 text-xs text-gray-500">{description}</p>
      )}
    </div>
  );
};

export default ExportButton;