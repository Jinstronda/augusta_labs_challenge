/**
 * QueryInput Component - Standalone Demo
 * 
 * This is a minimal demo to test the QueryInput component visually.
 * To use: Import this in App.tsx temporarily to see the component in action.
 * 
 * Usage in App.tsx:
 * import { QueryInputDemo } from './components/QueryInput.demo';
 * 
 * function App() {
 *   return <QueryInputDemo />;
 * }
 */

import React, { useState } from 'react';
import { QueryInput } from './QueryInput';

export const QueryInputDemo: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [lastQuery, setLastQuery] = useState<string>('');
  const [queryHistory, setQueryHistory] = useState<string[]>([]);

  const handleSubmit = async (query: string) => {
    console.log('Query submitted:', query);
    setLastQuery(query);
    setQueryHistory(prev => [...prev, query]);
    
    // Simulate API call
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsLoading(false);
    
    console.log('Query processed!');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white text-center">
          QueryInput Component Demo
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 text-center mt-1">
          Test the auto-resize, validation, keyboard shortcuts, and loading states
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col justify-center p-4">
        {/* Query History */}
        {queryHistory.length > 0 && (
          <div className="max-w-4xl mx-auto w-full mb-8">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Query History ({queryHistory.length})
            </h2>
            <div className="space-y-2">
              {queryHistory.map((q, idx) => (
                <div
                  key={idx}
                  className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow border border-gray-200 dark:border-gray-700"
                >
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Query #{idx + 1}:
                  </span>
                  <p className="text-gray-900 dark:text-white mt-1">{q}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* QueryInput Component */}
        <div className="mb-8">
          <QueryInput
            onSubmit={handleSubmit}
            isLoading={isLoading}
            placeholder="Try typing a query... (Press Enter to submit, Shift+Enter for new line)"
          />
        </div>

        {/* Status Display */}
        <div className="max-w-4xl mx-auto w-full">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
              Component Status
            </h3>
            <div className="space-y-1 text-sm">
              <p className="text-blue-800 dark:text-blue-200">
                <span className="font-medium">Loading:</span>{' '}
                {isLoading ? '🔄 Yes' : '✅ No'}
              </p>
              <p className="text-blue-800 dark:text-blue-200">
                <span className="font-medium">Last Query:</span>{' '}
                {lastQuery || '(none)'}
              </p>
              <p className="text-blue-800 dark:text-blue-200">
                <span className="font-medium">Total Queries:</span>{' '}
                {queryHistory.length}
              </p>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="max-w-4xl mx-auto w-full mt-8">
          <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
              Test Instructions
            </h3>
            <ul className="space-y-1 text-sm text-gray-700 dark:text-gray-300">
              <li>✓ Type a query and watch the textarea auto-resize</li>
              <li>✓ Press Enter to submit (watch the loading spinner)</li>
              <li>✓ Press Shift+Enter to create a new line</li>
              <li>✓ Try typing more than 500 characters to see validation</li>
              <li>✓ Try submitting an empty query</li>
              <li>✓ Check the character counter at the bottom</li>
              <li>✓ Toggle dark mode to see styling</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
        <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
          Open browser console to see query submission logs
        </p>
      </div>
    </div>
  );
};

export default QueryInputDemo;
