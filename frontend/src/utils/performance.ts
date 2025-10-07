/**
 * Performance Monitoring Utilities
 * 
 * Provides utilities for measuring and optimizing frontend performance.
 * Includes Web Vitals tracking and custom performance metrics.
 * 
 * Usage:
 * ```tsx
 * import { measurePerformance, reportWebVitals } from './utils/performance';
 * 
 * // Measure component render time
 * const stopMeasure = measurePerformance('ComponentRender');
 * // ... component logic
 * stopMeasure();
 * 
 * // Report Web Vitals
 * reportWebVitals(console.log);
 * ```
 */

/**
 * Measure performance of a code block
 * 
 * @param label - Label for the measurement
 * @returns Function to stop the measurement
 */
export function measurePerformance(label: string): () => void {
  const startTime = performance.now();
  const startMark = `${label}-start`;
  const endMark = `${label}-end`;
  const measureName = `${label}-measure`;

  // Create performance mark
  if (performance.mark) {
    performance.mark(startMark);
  }

  return () => {
    const endTime = performance.now();
    const duration = endTime - startTime;

    // Create end mark and measure
    if (performance.mark && performance.measure) {
      performance.mark(endMark);
      try {
        performance.measure(measureName, startMark, endMark);
      } catch (error) {
        // Ignore if marks don't exist
      }
    }

    // Log in development
    if (import.meta.env.DEV) {
      console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
    }

    return duration;
  };
}

/**
 * Measure async operation performance
 * 
 * @param label - Label for the measurement
 * @param fn - Async function to measure
 * @returns Result of the async function
 */
export async function measureAsync<T>(
  label: string,
  fn: () => Promise<T>
): Promise<T> {
  const stop = measurePerformance(label);
  try {
    const result = await fn();
    stop();
    return result;
  } catch (error) {
    stop();
    throw error;
  }
}

/**
 * Web Vitals metrics
 */
export interface WebVitalsMetric {
  name: 'CLS' | 'FCP' | 'LCP' | 'TTFB' | 'INP';
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
}

/**
 * Report Web Vitals metrics
 * 
 * Tracks Core Web Vitals: LCP, INP, CLS, FCP, TTFB
 * Note: FID has been deprecated in favor of INP (Interaction to Next Paint)
 * 
 * @param onReport - Callback to handle metric reports
 */
export function reportWebVitals(
  onReport?: (metric: WebVitalsMetric) => void
): void {
  if (!onReport) return;

  // Use web-vitals library if available
  if (typeof window !== 'undefined') {
    import('web-vitals').then(({ onCLS, onFCP, onLCP, onTTFB, onINP }) => {
      onCLS(onReport as any);
      onFCP(onReport as any);
      onLCP(onReport as any);
      onTTFB(onReport as any);
      onINP(onReport as any);
    }).catch((error) => {
      console.warn('[Performance] Failed to load web-vitals:', error);
    });
  }
}

/**
 * Get navigation timing metrics
 */
export function getNavigationTiming(): Record<string, number> | null {
  if (typeof window === 'undefined' || !window.performance) {
    return null;
  }

  const timing = performance.timing;
  const navigation = performance.navigation;

  return {
    // Navigation type
    navigationType: navigation.type,
    redirectCount: navigation.redirectCount,

    // Timing metrics (in milliseconds)
    dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
    tcpConnection: timing.connectEnd - timing.connectStart,
    request: timing.responseStart - timing.requestStart,
    response: timing.responseEnd - timing.responseStart,
    domProcessing: timing.domComplete - timing.domLoading,
    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
    pageLoad: timing.loadEventEnd - timing.navigationStart,

    // Time to first byte
    ttfb: timing.responseStart - timing.navigationStart,

    // Time to interactive
    tti: timing.domInteractive - timing.navigationStart,
  };
}

/**
 * Get resource timing metrics
 */
export function getResourceTiming(): PerformanceResourceTiming[] {
  if (typeof window === 'undefined' || !window.performance) {
    return [];
  }

  return performance.getEntriesByType('resource') as PerformanceResourceTiming[];
}

/**
 * Log performance summary
 */
export function logPerformanceSummary(): void {
  if (import.meta.env.PROD) return;

  console.group('[Performance Summary]');

  // Navigation timing
  const navTiming = getNavigationTiming();
  if (navTiming) {
    console.log('Navigation Timing:', navTiming);
  }

  // Resource timing
  const resources = getResourceTiming();
  const totalSize = resources.reduce((sum, r) => sum + (r.transferSize || 0), 0);
  const totalDuration = resources.reduce((sum, r) => sum + r.duration, 0);

  console.log('Resources:', {
    count: resources.length,
    totalSize: `${(totalSize / 1024).toFixed(2)} KB`,
    avgDuration: `${(totalDuration / resources.length).toFixed(2)}ms`,
  });

  // Memory usage (if available)
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    console.log('Memory:', {
      used: `${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
      total: `${(memory.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
      limit: `${(memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`,
    });
  }

  console.groupEnd();
}

/**
 * Performance observer for long tasks
 */
export function observeLongTasks(
  callback: (entries: PerformanceEntry[]) => void
): PerformanceObserver | null {
  if (typeof window === 'undefined' || !('PerformanceObserver' in window)) {
    return null;
  }

  try {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      callback(entries);
    });

    observer.observe({ entryTypes: ['longtask'] });
    return observer;
  } catch (error) {
    console.warn('[Performance] Failed to observe long tasks:', error);
    return null;
  }
}

/**
 * Debounce function for performance optimization
 * 
 * @param fn - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      fn(...args);
      timeoutId = null;
    }, delay);
  };
}

/**
 * Throttle function for performance optimization
 * 
 * @param fn - Function to throttle
 * @param limit - Time limit in milliseconds
 * @returns Throttled function
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

/**
 * Request idle callback wrapper
 * 
 * Executes a function when the browser is idle
 */
export function runWhenIdle(
  callback: () => void,
  options?: IdleRequestOptions
): number | null {
  if (typeof window === 'undefined') return null;

  if ('requestIdleCallback' in window) {
    return window.requestIdleCallback(callback, options);
  }

  // Fallback to setTimeout
  return setTimeout(callback, 1) as any;
}

/**
 * Cancel idle callback
 */
export function cancelIdle(id: number | null): void {
  if (id === null || typeof window === 'undefined') return;

  if ('cancelIdleCallback' in window) {
    window.cancelIdleCallback(id);
  } else {
    clearTimeout(id);
  }
}
