'use client';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

export default function LoadingSpinner({ 
  size = 'md', 
  text = 'Loading...', 
  className = '' 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const textSizes = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className={`flex flex-col items-center justify-center space-y-3 ${className}`}>
      <div className="relative">
        {/* Main spinner */}
        <div className={`animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 ${sizeClasses[size]}`}>
        </div>
        
        {/* Hospital cross decoration */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-blue-600 opacity-80">
            {size === 'sm' && '🏥'}
            {size === 'md' && '🏥'}
            {size === 'lg' && '🏥'}
          </div>
        </div>
        
        {/* Outer pulse ring */}
        <div className={`absolute inset-0 rounded-full border-2 border-blue-200 animate-ping opacity-50 ${sizeClasses[size]}`}>
        </div>
      </div>
      
      {text && (
        <p className={`text-gray-600 font-medium ${textSizes[size]}`}>
          {text}
        </p>
      )}
    </div>
  );
}