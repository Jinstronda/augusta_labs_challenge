/**
 * ChatInterface Component
 * 
 * A ChatGPT-like interface for querying incentives and companies.
 * 
 * Features:
 * - Chat message history with user queries and assistant responses
 * - Auto-scroll to latest message
 * - "New Chat" button to clear history
 * - Integration with QueryInput and ResultsDisplay components
 * - Loading states and error handling
 * 
 * Requirements: 4.1, 4.3, 4.4, 4.5, 4.7, 4.8
 */

import React, { useState, useRef, useEffect } from 'react';
import type { QueryResponse } from '../types/api';
import { QueryInput } from './QueryInput';
import { ResultsDisplay } from './ResultsDisplay';
import { queryIncentivesOrCompanies, ApiError } from '../services/api';

/**
 * Chat message types
 */
interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string | QueryResponse;
  timestamp: Date;
  error?: string;
}

interface ChatInterfaceProps {
  /** Callback when a company is clicked */
  onCompanyClick?: (companyId: number) => void;
  /** Callback when an incentive is clicked */
  onIncentiveClick?: (incentiveId: string) => void;
}

/**
 * Generate unique message ID
 */
const generateMessageId = (): string => {
  return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * ChatInterface Component
 */
export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onCompanyClick,
  onIncentiveClick,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  /**
   * Auto-scroll to latest message when messages change
   */
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  /**
   * Handle query submission
   */
  const handleSubmit = async (query: string) => {
    // Add user message to history
    const userMessage: ChatMessage = {
      id: generateMessageId(),
      type: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call API
      const response = await queryIncentivesOrCompanies(query);

      // Add assistant response to history
      const assistantMessage: ChatMessage = {
        id: generateMessageId(),
        type: 'assistant',
        content: response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      // Add error message to history
      const errorMessage = error instanceof ApiError 
        ? error.message 
        : 'An unexpected error occurred';

      const assistantMessage: ChatMessage = {
        id: generateMessageId(),
        type: 'assistant',
        content: '',
        timestamp: new Date(),
        error: errorMessage,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Clear chat history
   */
  const handleNewChat = () => {
    setMessages([]);
  };

  /**
   * Render a single message
   */
  const renderMessage = (message: ChatMessage) => {
    if (message.type === 'user') {
      // User message
      return (
        <div key={message.id} className="flex justify-end mb-4">
          <div className="max-w-3xl">
            <div className="bg-blue-600 text-white rounded-2xl px-5 py-3 shadow-md">
              <p className="text-sm whitespace-pre-wrap break-words">
                {message.content as string}
              </p>
            </div>
            <div className="text-xs text-gray-500 mt-1 text-right">
              {message.timestamp.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          </div>
        </div>
      );
    } else {
      // Assistant message
      return (
        <div key={message.id} className="flex justify-start mb-4">
          <div className="max-w-4xl w-full">
            {/* Assistant avatar/label */}
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Assistant
              </span>
            </div>

            {/* Message content */}
            <div className="ml-10">
              {message.error ? (
                // Error state
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <svg
                      className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0"
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
                    <div>
                      <p className="text-sm font-semibold text-red-800 mb-1">
                        Error
                      </p>
                      <p className="text-sm text-red-700">
                        {message.error}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                // Results display
                <ResultsDisplay
                  response={message.content as QueryResponse}
                  isLoading={false}
                  error={null}
                  onCompanyClick={onCompanyClick}
                  onIncentiveClick={onIncentiveClick}
                />
              )}

              <div className="text-xs text-gray-500 mt-2">
                {message.timestamp.toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </div>
            </div>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white dark:bg-[#0A0A0A]">
      {/* Minimal Header */}
      <header className="border-b border-gray-100 dark:border-gray-800 px-4 py-3 flex items-center justify-between backdrop-blur-sm bg-white/80 dark:bg-[#0A0A0A]/80 sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <svg
              className="w-4 h-4 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.5}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white tracking-tight">
            Incentive AI
          </h1>
        </div>

        {/* New Chat button - minimal */}
        {messages.length > 0 && (
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-all duration-200"
            aria-label="Start new chat"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            New
          </button>
        )}
      </header>

      {/* Messages container */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto px-6 py-6"
      >
        {messages.length === 0 ? (
          // Empty state - welcome message
          <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mb-6">
              <svg
                className="w-12 h-12 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">
              Welcome to Incentive Query System
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
              Ask me anything about incentives or companies. I'll help you find the best matches.
            </p>

            {/* Example queries */}
            <div className="w-full max-w-xl">
              <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 text-left">
                Try asking:
              </p>
              <div className="space-y-2">
                {[
                  'What incentives are available for tech companies?',
                  'Show me companies eligible for digital innovation funding',
                  'Find incentives for green energy projects',
                  'Which companies qualify for export support?',
                ].map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleSubmit(example)}
                    disabled={isLoading}
                    className="w-full text-left px-4 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg transition-colors duration-200 text-sm text-gray-700 dark:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="text-blue-500 mr-2">→</span>
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          // Chat messages
          <div className="max-w-5xl mx-auto">
            {messages.map(renderMessage)}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="max-w-4xl">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                        />
                      </svg>
                    </div>
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                      Assistant
                    </span>
                  </div>
                  <div className="ml-10">
                    <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                      <span className="text-sm">Thinking...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-4">
        <QueryInput
          onSubmit={handleSubmit}
          isLoading={isLoading}
          placeholder="Ask about incentives or companies..."
        />
      </div>
    </div>
  );
};

export default ChatInterface;
