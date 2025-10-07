"use client";

import React, { useState, useRef, useEffect } from 'react';
import {
  Moon,
  Sun,
  Plus,
  MessageSquare,
  Settings,
  User,
  Paperclip,
  Mic,
  ArrowUp,
  Search,
  Code,
  PenTool,
  BookOpen,
} from 'lucide-react';
import { motion } from 'framer-motion';
import type { QueryResponse } from '../types/api';
import { ResultsDisplay } from './ResultsDisplay';
import { queryIncentivesOrCompanies, ApiError } from '../services/api';
import { Sidebar, SidebarBody, SidebarLink } from './Sidebar';
import { Typewriter } from './Typewriter';
import { MessageLoading } from './MessageLoading';

/**
 * Message structure
 */
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string | QueryResponse;
  timestamp: Date;
  error?: string;
}

interface ChatInterfaceProps {
  onCompanyClick?: (companyId: number) => void;
  onIncentiveClick?: (incentiveId: string) => void;
}

/**
 * Utility to combine class names
 */
function cn(...inputs: (string | undefined | null | false)[]): string {
  return inputs.filter(Boolean).join(' ');
}

/**
 * Logo component for sidebar
 */
const Logo = () => {
  return (
    <div className="pr-2">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30">
          <MessageSquare className="h-5 w-5" />
        </div>
        <div className="flex flex-col">
          <motion.span
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-lg font-semibold text-slate-900 dark:text-white"
          >
            Incentive AI
          </motion.span>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            Powered by Augusta Labs
          </span>
        </div>
      </div>
    </div>
  );
};

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onCompanyClick,
  onIncentiveClick,
}) => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const newHeight = Math.min(textareaRef.current.scrollHeight, 200);
      textareaRef.current.style.height = `${newHeight}px`;
    }
  }, [inputValue]);

  // Apply dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  /**
   * Handle message submission
   */
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await queryIncentivesOrCompanies(inputValue);
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage =
        error instanceof ApiError
          ? error.message
          : 'An unexpected error occurred';
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        error: errorMessage,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewChat = (e: React.MouseEvent) => {
    e.preventDefault();
    setMessages([]);
    setInputValue('');
  };

  // Sidebar navigation links
  const links = [
    {
      label: 'Chat History',
      href: '#',
      icon: <MessageSquare className="h-5 w-5" />,
    },
    {
      label: 'Settings',
      href: '#',
      icon: <Settings className="h-5 w-5" />,
    },
  ];

  // Suggestion prompts
  const suggestions = [
    { icon: <BookOpen className="w-5 h-5" />, text: 'Tech company incentives' },
    { icon: <Code className="w-5 h-5" />, text: 'Digital innovation funding' },
    { icon: <PenTool className="w-5 h-5" />, text: 'Green energy projects' },
    { icon: <Search className="w-5 h-5" />, text: 'Export support programs' },
  ];

  return (
    <div
      className={cn(
        'flex flex-col md:flex-row w-full h-screen overflow-hidden transition-colors duration-300',
        darkMode ? 'bg-[#343541] text-slate-100' : 'bg-[#f7f7f8] text-slate-900'
      )}
    >
      {/* Sidebar */}
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-8">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            <Logo />
            <button
              type="button"
              onClick={handleNewChat}
              className={cn(
                'mt-6 flex items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors duration-200',
                darkMode
                  ? 'border-white/10 bg-[#343541]/60 text-slate-100 hover:bg-white/10'
                  : 'border-black/10 bg-white text-slate-900 hover:bg-slate-100'
              )}
            >
              <Plus className="h-4 w-4" />
              New chat
            </button>
            <div className="mt-8 text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400/80">
              Recent
            </div>
            <div className="mt-3 flex flex-col gap-1">
              {links.map((link, idx) => (
                <SidebarLink
                  key={idx}
                  link={link}
                  className={cn(
                    'hover:bg-white/10',
                    !darkMode && 'hover:bg-slate-100 text-slate-700'
                  )}
                />
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-3">
            <button
              type="button"
              onClick={() => setDarkMode(!darkMode)}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-200',
                darkMode
                  ? 'text-slate-300 hover:bg-white/10'
                  : 'text-slate-600 hover:bg-slate-100'
              )}
            >
              <div className="relative h-5 w-5 flex-shrink-0">
                <Sun
                  className={cn(
                    'absolute inset-0 h-5 w-5 text-amber-400 transition-all duration-500',
                    darkMode ? 'rotate-90 scale-0 opacity-0' : 'rotate-0 scale-100 opacity-100'
                  )}
                />
                <Moon
                  className={cn(
                    'absolute inset-0 h-5 w-5 text-slate-400 transition-all duration-500',
                    darkMode ? 'rotate-0 scale-100 opacity-100' : '-rotate-90 scale-0 opacity-0'
                  )}
                />
              </div>
              <motion.span
                animate={{
                  display: open ? 'inline-block' : 'none',
                  opacity: open ? 1 : 0,
                }}
                className={cn(
                  'text-sm font-medium transition duration-150 whitespace-pre',
                  darkMode ? 'text-slate-200' : 'text-slate-700'
                )}
              >
                Theme
              </motion.span>
            </button>
            <SidebarLink
              link={{
                label: 'User Profile',
                href: '#',
                icon: (
                  <div
                    className={cn(
                      'flex h-8 w-8 items-center justify-center rounded-full',
                      darkMode
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : 'bg-emerald-500/10 text-emerald-600'
                    )}
                  >
                    <User className="h-4 w-4" />
                  </div>
                ),
              }}
              className={cn(
                'border px-3 py-2',
                darkMode
                  ? 'border-white/10 bg-[#343541]/60 text-slate-200 hover:bg-white/10'
                  : 'border-black/10 bg-white text-slate-700 hover:bg-slate-100'
              )}
            />
          </div>
        </SidebarBody>
      </Sidebar>

      {/* Main Content */}
      <div className="flex flex-1 flex-col h-full overflow-hidden">
        <div className="flex-1 overflow-y-auto px-4 py-6 md:px-8 md:py-10">
          {messages.length === 0 ? (
            <div className="mx-auto flex h-full max-w-3xl flex-col items-center justify-center text-center">
              <div className="mb-8">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/40">
                  <MessageSquare className="h-8 w-8" />
                </div>
              </div>
              <h1 className="text-3xl font-semibold text-slate-900 dark:text-white md:text-4xl">
                <Typewriter
                  text={['How can I help you today?']}
                  speed={70}
                  loop={false}
                  showCursor={false}
                />
              </h1>
              <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
                Pick a conversation starter below or ask your own question.
              </p>
              <div className="mt-8 grid w-full grid-cols-1 gap-3 md:grid-cols-2">
                {suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setInputValue(suggestion.text)}
                    className="group flex items-center gap-3 rounded-2xl border border-black/10 bg-white/80 p-4 text-left text-slate-700 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md dark:border-white/10 dark:bg-[#40414f]/80 dark:text-slate-100"
                  >
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-500 transition duration-200 group-hover:bg-emerald-500/20 dark:bg-emerald-500/20 dark:text-emerald-300">
                      {suggestion.icon}
                    </span>
                    <span className="text-sm font-medium leading-tight">{suggestion.text}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mx-auto max-w-3xl space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-4',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-md shadow-emerald-500/30">
                      <MessageSquare className="h-4 w-4" />
                    </div>
                  )}
                  <div
                    className={cn(
                      'max-w-[80%] rounded-2xl border px-4 py-3 text-sm leading-relaxed shadow-sm backdrop-blur',
                      message.role === 'user'
                        ? 'border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-500/40 dark:bg-[#2f3c35] dark:text-emerald-100'
                        : 'border-black/5 bg-white text-slate-900 dark:border-transparent dark:bg-[#444654] dark:text-slate-100'
                    )}
                  >
                    {message.role === 'user' ? (
                      <p className="whitespace-pre-wrap">{message.content as string}</p>
                    ) : message.error ? (
                      <p className="text-sm text-red-500">{message.error}</p>
                    ) : (
                      <ResultsDisplay
                        response={message.content as QueryResponse}
                        isLoading={false}
                        error={null}
                        onCompanyClick={onCompanyClick}
                        onIncentiveClick={onIncentiveClick}
                      />
                    )}
                  </div>
                  {message.role === 'user' && (
                    <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-emerald-500 text-white shadow-md shadow-emerald-500/30 dark:bg-emerald-500/80">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}
              {isTyping && (
                <div className="flex gap-4 justify-start">
                  <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-md shadow-emerald-500/30">
                    <MessageSquare className="h-4 w-4" />
                  </div>
                  <div className="rounded-2xl border border-black/5 bg-white px-4 py-3 dark:border-transparent dark:bg-[#444654]">
                    <MessageLoading />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-black/5 bg-white/80 p-4 dark:border-white/10 dark:bg-[#343541]">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-end gap-2 rounded-3xl border border-black/10 bg-white px-3 py-3 shadow-sm dark:border-white/10 dark:bg-[#40414f]">
              <button
                type="button"
                className="flex h-10 w-10 items-center justify-center rounded-full text-slate-500 transition-colors duration-200 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/10"
              >
                <Paperclip className="h-5 w-5" />
              </button>
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message Incentive AI..."
                rows={1}
                className="flex-1 max-h-[200px] resize-none bg-transparent px-2 py-2 text-sm text-slate-900 outline-none placeholder:text-slate-400 dark:text-slate-100 dark:placeholder:text-slate-500"
              />
              <button
                type="button"
                className="flex h-10 w-10 items-center justify-center rounded-full text-slate-500 transition-colors duration-200 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/10"
              >
                <Mic className="h-5 w-5" />
              </button>
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim()}
                className={cn(
                  'flex h-10 w-10 items-center justify-center rounded-full transition-colors duration-200',
                  inputValue.trim()
                    ? 'bg-emerald-500 text-white hover:bg-emerald-400'
                    : 'cursor-not-allowed bg-slate-200 text-slate-400 dark:bg-white/10 dark:text-slate-500'
                )}
              >
                <ArrowUp className="h-5 w-5" />
              </button>
            </div>
            <p className="mt-3 text-center text-xs text-slate-400 dark:text-slate-500">
              Incentive AI can make mistakes. Consider verifying important information.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;