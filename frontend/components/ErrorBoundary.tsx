'use client';

import { ReactNode, useState, useEffect } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
}

export function ErrorBoundary({ children, fallback }: ErrorBoundaryProps) {
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      setError(event.error);
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  const reset = () => setError(null);

  if (error) {
    return (
      fallback?.(error, reset) || (
        <div className="min-h-screen flex items-center justify-center bg-red-50 p-4">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Error</h1>
            <details className="mb-6">
              <summary className="text-gray-700 font-semibold cursor-pointer hover:text-gray-900">
                Error Details
              </summary>
              <pre className="mt-2 p-4 bg-gray-100 rounded text-sm text-red-700 overflow-auto max-h-64">
                {error.message}
                {'\n\n'}
                {error.stack}
              </pre>
            </details>
            <button
              onClick={reset}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      )
    );
  }

  return children;
}
