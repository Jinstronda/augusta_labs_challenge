/**
 * ResultsDisplay Component
 * 
 * Routes query results to the appropriate card component based on query type.
 * Handles loading states, error messages, and empty results.
 * 
 * Query Types (from backend/app/services/classifier.py):
 * - INCENTIVE: Shows IncentiveCard with matched companies
 * - COMPANY: Shows CompanyCard with eligible incentives
 */

import React from 'react';
import type { QueryResponse } from '../types/api';
import { isIncentiveResults, isCompanyResults } from '../types/api';
import { IncentiveCard } from './IncentiveCard';
import { CompanyCard } from './CompanyCard';

interface ResultsDisplayProps {
  /** Query response from the API */
  response: QueryResponse | null;
  /** Loading state */
  isLoading: boolean;
  /** Error message if any */
  error: string | null;
  /** Callback when a company is clicked */
  onCompanyClick?: (companyId: number) => void;
  /** Callback when an incentive is clicked */
  onIncentiveClick?: (incentiveId: string) => void;
}

/**
 * Skeleton loader for card content
 */
const SkeletonLoader: React.FC = React.memo(() => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-4 animate-pulse">
      {/* Header skeleton */}
      <div className="border-b pb-4">
        <div className="h-8 bg-gray-300 rounded w-3/4 mb-2"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>

      {/* Description skeleton */}
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded w-full"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        <div className="h-4 bg-gray-200 rounded w-4/6"></div>
      </div>

      {/* Cards skeleton */}
      <div className="space-y-2">
        <div className="h-6 bg-gray-300 rounded w-1/3 mb-3"></div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-5 bg-gray-300 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                <div className="h-2 bg-gray-200 rounded w-full mt-3"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});

/**
 * Empty state when no results are found
 */
const EmptyState: React.FC<{ queryType: string }> = React.memo(({ queryType }) => {
  const suggestions = queryType === 'INCENTIVE' 
    ? [
        'Try using different keywords (e.g., "funding", "grants", "support")',
        'Check the spelling of incentive names',
        'Try a broader search term',
        'Search for a specific sector or region'
      ]
    : [
        'Try using the company name or industry',
        'Check the spelling of the company name',
        'Try searching for a related business activity',
        'Use broader terms like "technology" or "manufacturing"'
      ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 text-center">
      {/* Icon */}
      <div className="flex justify-center mb-4">
        <svg
          className="w-16 h-16 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>

      {/* Message */}
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        No Results Found
      </h3>
      <p className="text-gray-600 mb-6">
        We couldn't find any {queryType === 'INCENTIVE' ? 'incentives' : 'companies'} matching your query.
      </p>

      {/* Suggestions */}
      <div className="text-left max-w-md mx-auto">
        <p className="text-sm font-semibold text-gray-700 mb-2">
          Try these suggestions:
        </p>
        <ul className="space-y-1 text-sm text-gray-600">
          {suggestions.map((suggestion, index) => (
            <li key={index} className="flex items-start gap-2">
              <span className="text-blue-500 mt-1">•</span>
              <span>{suggestion}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
});

/**
 * Error state display
 */
const ErrorState: React.FC<{ error: string }> = React.memo(({ error }) => {
  // Parse error message to provide helpful feedback
  const isTimeout = error.toLowerCase().includes('timeout');
  const isNetworkError = error.toLowerCase().includes('network') || 
                         error.toLowerCase().includes('fetch') ||
                         error.toLowerCase().includes('unavailable');

  let title = 'Something Went Wrong';
  let message = error;
  let suggestions: string[] = [];

  if (isTimeout) {
    title = 'Request Timed Out';
    message = 'The request took too long to complete.';
    suggestions = [
      'Try a simpler or more specific query',
      'Check your internet connection',
      'Try again in a few moments'
    ];
  } else if (isNetworkError) {
    title = 'Service Unavailable';
    message = 'Unable to connect to the server.';
    suggestions = [
      'Check your internet connection',
      'The service may be temporarily down',
      'Try again in a few moments'
    ];
  } else {
    suggestions = [
      'Try rephrasing your query',
      'Check for any special characters',
      'Try again in a few moments'
    ];
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 text-center">
      {/* Icon */}
      <div className="flex justify-center mb-4">
        <svg
          className="w-16 h-16 text-red-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>

      {/* Message */}
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        {title}
      </h3>
      <p className="text-gray-600 mb-6">
        {message}
      </p>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="text-left max-w-md mx-auto">
          <p className="text-sm font-semibold text-gray-700 mb-2">
            What you can do:
          </p>
          <ul className="space-y-1 text-sm text-gray-600">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-500 mt-1">•</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
});

/**
 * Main ResultsDisplay component
 */
export const ResultsDisplay: React.FC<ResultsDisplayProps> = React.memo(({
  response,
  isLoading,
  error,
  onCompanyClick,
  onIncentiveClick
}) => {
  // Show loading state
  if (isLoading) {
    return <SkeletonLoader />;
  }

  // Show error state
  if (error) {
    return <ErrorState error={error} />;
  }

  // No response yet (initial state)
  if (!response) {
    return null;
  }

  // Show empty state if no results
  if (response.result_count === 0 || response.results.length === 0) {
    return <EmptyState queryType={response.query_type} />;
  }

  // Route to appropriate card based on query type
  if (isIncentiveResults(response)) {
    // INCENTIVE query - show IncentiveCard(s)
    return (
      <div className="space-y-4">
        {response.results.map((incentive) => (
          <IncentiveCard
            key={incentive.incentive_id}
            incentive={incentive}
            onCompanyClick={onCompanyClick}
          />
        ))}
        
        {/* Query metadata */}
        <div className="text-xs text-gray-500 text-center">
          Found {response.result_count} result{response.result_count !== 1 ? 's' : ''} in {response.processing_time.toFixed(2)}s
          {response.confidence && ` • Confidence: ${response.confidence}`}
        </div>
      </div>
    );
  }

  if (isCompanyResults(response)) {
    // COMPANY query - show CompanyCard(s)
    return (
      <div className="space-y-4">
        {response.results.map((company) => (
          <CompanyCard
            key={company.company_id}
            company={company}
            onIncentiveClick={onIncentiveClick}
          />
        ))}
        
        {/* Query metadata */}
        <div className="text-xs text-gray-500 text-center">
          Found {response.result_count} result{response.result_count !== 1 ? 's' : ''} in {response.processing_time.toFixed(2)}s
          {response.confidence && ` • Confidence: ${response.confidence}`}
        </div>
      </div>
    );
  }

  // Fallback for unexpected query type
  return (
    <ErrorState error={`Unknown query type: ${response.query_type}`} />
  );
});
