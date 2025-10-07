import React, { useState, useRef, useEffect } from 'react';
import type { KeyboardEvent, ChangeEvent } from 'react';

interface QueryInputProps {
  onSubmit: (query: string) => Promise<void>;
  isLoading: boolean;
  placeholder?: string;
}

/**
 * QueryInput Component
 * 
 * A ChatGPT-like input component with:
 * - Auto-resizing textarea
 * - Submit button with loading state
 * - Enter to submit, Shift+Enter for new line
 * - Input validation (1-500 characters matching backend)
 */
export const QueryInput: React.FC<QueryInputProps> = ({
  onSubmit,
  isLoading,
  placeholder = "Ask about incentives or companies..."
}) => {
  const [query, setQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      // Reset height to auto to get the correct scrollHeight
      textarea.style.height = 'auto';
      // Set height to scrollHeight (content height)
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [query]);

  // Validate query length (matching backend: min 1, max 500)
  const validateQuery = (value: string): string | null => {
    if (value.trim().length === 0) {
      return 'Query cannot be empty';
    }
    if (value.length > 500) {
      return 'Query must be 500 characters or less';
    }
    return null;
  };

  // Handle input change
  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setQuery(value);
    
    // Clear error when user starts typing
    if (error) {
      setError(null);
    }

    // Show error if exceeding max length
    if (value.length > 500) {
      setError('Query must be 500 characters or less');
    }
  };

  // Handle form submission
  const handleSubmit = async () => {
    const validationError = validateQuery(query);
    
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      await onSubmit(query.trim());
      // Clear input after successful submission
      setQuery('');
      setError(null);
    } catch (err) {
      // Error handling is done by parent component
      console.error('Query submission error:', err);
    }
  };

  // Handle Enter key (submit) vs Shift+Enter (new line)
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent new line
      if (!isLoading) {
        handleSubmit();
      }
    }
  };

  const isSubmitDisabled = isLoading || query.trim().length === 0 || query.length > 500;

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-4">
      <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={query}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          rows={1}
          className="w-full px-4 py-3 pr-12 resize-none outline-none bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            minHeight: '52px',
            maxHeight: '200px',
            overflowY: 'auto'
          }}
          aria-label="Query input"
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? 'query-error' : undefined}
        />

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={isSubmitDisabled}
          className="absolute right-2 bottom-2 p-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors duration-200"
          aria-label="Submit query"
          title={isLoading ? 'Processing...' : 'Submit (Enter)'}
        >
          {isLoading ? (
            // Loading spinner
            <svg
              className="w-5 h-5 text-white animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ) : (
            // Send icon
            <svg
              className="w-5 h-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div
          id="query-error"
          className="mt-2 text-sm text-red-600 dark:text-red-400 px-2"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Character count */}
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 px-2 text-right">
        {query.length}/500 characters
        {query.length > 0 && (
          <span className="ml-2 text-gray-400 dark:text-gray-500">
            • Press Enter to submit, Shift+Enter for new line
          </span>
        )}
      </div>
    </div>
  );
};

export default QueryInput;
