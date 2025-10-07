/**
 * QueryInput Component Usage Example
 * 
 * This file demonstrates how to use the QueryInput component
 * in your application.
 */

import React, { useState } from 'react';
import { QueryInput } from './QueryInput';
import { queryIncentivesOrCompanies } from '../services/api';
import type { QueryResponse } from '../types/api';

export const QueryInputExample: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (query: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await queryIncentivesOrCompanies(query);
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8 text-center">
          Incentive Query System
        </h1>

        {/* QueryInput Component */}
        <QueryInput
          onSubmit={handleSubmit}
          isLoading={isLoading}
          placeholder="Ask about incentives or companies..."
        />

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Response Display */}
        {response && (
          <div className="mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
            <div className="mb-4">
              <span className="inline-block px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm font-medium">
                {response.query_type}
              </span>
            </div>
            <pre className="text-sm text-gray-700 dark:text-gray-300 overflow-auto">
              {JSON.stringify(response, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default QueryInputExample;
