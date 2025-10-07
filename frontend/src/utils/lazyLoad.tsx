/**
 * Lazy Loading Utilities
 * 
 * Provides utilities for code splitting and lazy loading components.
 * This reduces initial bundle size by loading components only when needed.
 * 
 * Usage:
 * ```tsx
 * // In App.tsx or router configuration
 * const IncentiveDetailPage = lazyLoad(() => import('./pages/IncentiveDetailPage'));
 * const CompanyDetailPage = lazyLoad(() => import('./pages/CompanyDetailPage'));
 * 
 * // In routes
 * <Route path="/incentive/:id" element={<IncentiveDetailPage />} />
 * ```
 */

import React, { Suspense } from 'react';
import type { ComponentType } from 'react';

/**
 * Loading fallback component
 */
export const LoadingFallback: React.FC<{ message?: string }> = ({ 
  message = 'Loading...' 
}) => {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        {/* Spinner */}
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
};

/**
 * Error boundary for lazy loaded components
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class LazyLoadErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Lazy load error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center max-w-md p-6">
            <div className="text-red-500 mb-4">
              <svg
                className="w-16 h-16 mx-auto"
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
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Failed to Load Component
            </h2>
            <p className="text-gray-600 mb-4">
              {this.state.error?.message || 'An error occurred while loading this page.'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Lazy load a component with automatic code splitting
 * 
 * @param importFunc - Dynamic import function
 * @param fallback - Optional custom loading fallback
 * @returns Lazy loaded component wrapped in Suspense
 */
export function lazyLoad<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: React.ReactNode
): React.FC<React.ComponentProps<T>> {
  const LazyComponent = React.lazy(importFunc);

  return (props: React.ComponentProps<T>) => (
    <LazyLoadErrorBoundary>
      <Suspense fallback={fallback || <LoadingFallback />}>
        <LazyComponent {...props} />
      </Suspense>
    </LazyLoadErrorBoundary>
  );
}

/**
 * Preload a lazy component
 * Useful for prefetching components before they're needed
 * 
 * Usage:
 * ```tsx
 * const IncentiveDetailPage = lazyLoad(() => import('./pages/IncentiveDetailPage'));
 * 
 * // Preload on hover or mount
 * <button onMouseEnter={() => preloadComponent(() => import('./pages/IncentiveDetailPage'))}>
 *   View Details
 * </button>
 * ```
 */
export function preloadComponent(importFunc: () => Promise<any>): void {
  importFunc().catch((error) => {
    console.error('Failed to preload component:', error);
  });
}

/**
 * Example usage in App.tsx:
 * 
 * ```tsx
 * import { lazyLoad } from './utils/lazyLoad';
 * 
 * // Lazy load page components
 * const IncentiveDetailPage = lazyLoad(
 *   () => import('./pages/IncentiveDetailPage'),
 *   <LoadingFallback message="Loading incentive details..." />
 * );
 * 
 * const CompanyDetailPage = lazyLoad(
 *   () => import('./pages/CompanyDetailPage'),
 *   <LoadingFallback message="Loading company details..." />
 * );
 * 
 * // In routes
 * <Routes>
 *   <Route path="/" element={<HomePage />} />
 *   <Route path="/incentive/:id" element={<IncentiveDetailPage />} />
 *   <Route path="/company/:id" element={<CompanyDetailPage />} />
 * </Routes>
 * ```
 */
