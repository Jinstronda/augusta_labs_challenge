import React, { useState, useRef, useEffect } from 'react';
import type { KeyboardEvent, ChangeEvent } from 'react';

interface QueryInputProps {
  onSubmit: (query: string) => Promise<void>;
  isLoading: boolean;
  placeholder?: string;
}

const MAX_LENGTH = 500;

export const QueryInput: React.FC<QueryInputProps> = ({
  onSubmit,
  isLoading,
  placeholder = "Ask anything about incentives or companies..."
}) => {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [value]);

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
  };

  const handleSubmit = async () => {
    if (!value.trim() || value.length > MAX_LENGTH || isLoading) return;
    
    try {
      await onSubmit(value.trim());
      setValue('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch (err) {
      console.error('Query submission error:', err);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative flex items-end gap-2 bg-white dark:bg-[#40414f] border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={isLoading}
        rows={1}
        className="flex-1 px-4 py-3 bg-transparent focus:outline-none resize-none text-base text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50"
        style={{
          minHeight: '52px',
          maxHeight: '200px',
        }}
        aria-label="Message input"
      />
      
      <button
        onClick={handleSubmit}
        disabled={isLoading || !value.trim() || value.length > MAX_LENGTH}
        className="flex-shrink-0 m-2 w-8 h-8 bg-[#10a37f] hover:bg-[#0e8c6f] disabled:bg-gray-300 dark:disabled:bg-gray-600 text-white rounded transition-colors disabled:cursor-not-allowed flex items-center justify-center"
        aria-label="Send message"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  );
};

export default QueryInput;
