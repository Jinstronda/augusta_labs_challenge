/**
 * Debounce utility to limit function execution frequency
 * 
 * Useful for preventing excessive API calls during user input.
 */

export type DebouncedFunction<T extends (...args: any[]) => any> = {
  (...args: Parameters<T>): void;
  cancel: () => void;
};

/**
 * Creates a debounced version of a function that delays execution
 * until after `delay` milliseconds have elapsed since the last call.
 * 
 * @param func - The function to debounce
 * @param delay - The delay in milliseconds (default: 300ms)
 * @returns A debounced version of the function with a cancel method
 * 
 * @example
 * const debouncedSearch = debounce((query: string) => {
 *   fetchResults(query);
 * }, 500);
 * 
 * // Call multiple times rapidly
 * debouncedSearch('hello');
 * debouncedSearch('hello world'); // Only this will execute after 500ms
 * 
 * // Cancel pending execution
 * debouncedSearch.cancel();
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number = 300
): DebouncedFunction<T> {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  const debouncedFn = (...args: Parameters<T>) => {
    // Clear existing timeout
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }

    // Set new timeout
    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
    }, delay);
  };

  // Add cancel method
  debouncedFn.cancel = () => {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  return debouncedFn;
}

/**
 * Creates a debounced version of an async function that returns a Promise.
 * Only the last call's promise will resolve; previous calls are cancelled.
 * 
 * @param func - The async function to debounce
 * @param delay - The delay in milliseconds (default: 300ms)
 * @returns A debounced version of the async function
 * 
 * @example
 * const debouncedFetch = debounceAsync(async (query: string) => {
 *   const response = await fetch(`/api/search?q=${query}`);
 *   return response.json();
 * }, 500);
 * 
 * // Only the last call will resolve
 * const result = await debouncedFetch('hello world');
 */
export function debounceAsync<T extends (...args: any[]) => Promise<any>>(
  func: T,
  delay: number = 300
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let latestResolve: ((value: any) => void) | null = null;
  let latestReject: ((reason: any) => void) | null = null;

  return (...args: Parameters<T>): Promise<ReturnType<T>> => {
    // Reject previous pending promise
    if (latestReject) {
      latestReject(new Error('Debounced call cancelled'));
    }

    // Clear existing timeout
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }

    // Return new promise
    return new Promise((resolve, reject) => {
      latestResolve = resolve;
      latestReject = reject;

      timeoutId = setTimeout(async () => {
        try {
          const result = await func(...args);
          if (latestResolve === resolve) {
            resolve(result);
          }
        } catch (error) {
          if (latestReject === reject) {
            reject(error);
          }
        } finally {
          timeoutId = null;
          if (latestResolve === resolve) {
            latestResolve = null;
            latestReject = null;
          }
        }
      }, delay);
    });
  };
}
