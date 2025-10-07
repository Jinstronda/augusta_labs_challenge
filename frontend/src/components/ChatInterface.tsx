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
    <a
      href="#"
      className="font-normal flex space-x-2 items-center text-sm text-foreground py-1 relative z-20"
      onClick={(e) => e.preventDefault()}
    >
      <div className="h-5 w-6 bg-gradient-to-br from-primary to-cyan-500 rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-medium text-foreground whitespace-pre"
      >
        Incentive AI
      </motion.span>
    </a>
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
      label: 'New Chat',
      href: '#',
      icon: <Plus className="text-foreground h-5 w-5 flex-shrink-0" />,
      onClick: handleNewChat,
    },
    {
      label: 'Chat History',
      href: '#',
      icon: <MessageSquare className="text-foreground h-5 w-5 flex-shrink-0" />,
    },
    {
      label: 'Settings',
      href: '#',
      icon: <Settings className="text-foreground h-5 w-5 flex-shrink-0" />,
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
      className="flex flex-col md:flex-row w-full h-screen overflow-hidden"
      style={{
        backgroundColor: darkMode ? '#000000' : '#ffffff',
        color: darkMode ? '#ffffff' : '#000000'
      }}
    >
      {/* Sidebar */}
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-10">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            <Logo />
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link, idx) => (
                <SidebarLink
                  key={idx}
                  link={link}
                  {...(link.onClick && {
                    onClick: link.onClick as React.MouseEventHandler<HTMLAnchorElement>,
                  })}
                />
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-2">
            {/* Theme Toggle */}
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                setDarkMode(!darkMode);
              }}
              className="flex items-center justify-start gap-2 group/sidebar py-2 px-2 rounded-md hover:bg-accent transition-colors cursor-pointer"
            >
              <div className="relative w-5 h-5 flex-shrink-0">
                <Sun
                  className={`absolute inset-0 h-5 w-5 text-amber-500 transition-all duration-500 ${
                    darkMode
                      ? 'rotate-90 scale-0 opacity-0'
                      : 'rotate-0 scale-100 opacity-100'
                  }`}
                />
                <Moon
                  className={`absolute inset-0 h-5 w-5 text-slate-400 dark:text-slate-300 transition-all duration-500 ${
                    darkMode
                      ? 'rotate-0 scale-100 opacity-100'
                      : '-rotate-90 scale-0 opacity-0'
                  }`}
                />
              </div>
              <motion.span
                animate={{
                  display: open ? 'inline-block' : 'none',
                  opacity: open ? 1 : 0,
                }}
                className="text-foreground text-sm group-hover/sidebar:translate-x-1 transition duration-150 whitespace-pre inline-block"
              >
                Theme
              </motion.span>
            </a>
            <SidebarLink
              link={{
                label: 'User Profile',
                href: '#',
                icon: (
                  <div className="h-7 w-7 flex-shrink-0 rounded-full bg-primary flex items-center justify-center">
                    <User className="h-4 w-4 text-primary-foreground" />
                  </div>
                ),
              }}
            />
          </div>
        </SidebarBody>
      </Sidebar>

      {/* Main Content */}
      <div className="flex flex-1 flex-col h-full overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          {messages.length === 0 ? (
            /* Welcome Screen */
            <div className="flex flex-col items-center justify-center h-full max-w-3xl mx-auto">
              <div className="mb-8">
                <div 
                  className="w-16 h-16 rounded-2xl flex items-center justify-center"
                  style={{
                    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)'
                  }}
                >
                  <MessageSquare className="w-8 h-8 text-white" />
                </div>
              </div>
              <h1 
                className="text-3xl md:text-4xl font-bold mb-4 text-center"
                style={{ color: darkMode ? '#ffffff' : '#000000' }}
              >
                <Typewriter
                  text={['How can I help you today?']}
                  speed={70}
                  loop={false}
                  showCursor={false}
                />
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full mt-8">
                {suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputValue(suggestion.text)}
                    className="flex items-center gap-3 p-4 rounded-xl border transition-colors text-left"
                    style={{
                      backgroundColor: darkMode ? '#1f1f1f' : '#f5f5f5',
                      borderColor: darkMode ? '#404040' : '#e5e5e5',
                      color: darkMode ? '#ffffff' : '#000000'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = darkMode ? '#2a2a2a' : '#e5e5e5';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = darkMode ? '#1f1f1f' : '#f5f5f5';
                    }}
                  >
                    <div style={{ color: '#3b82f6' }}>{suggestion.icon}</div>
                    <span className="text-sm">
                      {suggestion.text}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-4',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <div 
                      className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                      style={{
                        background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)'
                      }}
                    >
                      <MessageSquare className="w-4 h-4 text-white" />
                    </div>
                  )}
                  <div
                    className="rounded-2xl px-4 py-3 max-w-[80%]"
                    style={{
                      backgroundColor: message.role === 'user' 
                        ? (darkMode ? '#ffffff' : '#000000')
                        : (darkMode ? '#1f1f1f' : '#f5f5f5'),
                      color: message.role === 'user' 
                        ? (darkMode ? '#000000' : '#ffffff')
                        : (darkMode ? '#ffffff' : '#000000')
                    }}
                  >
                    {message.role === 'user' ? (
                      <p className="text-sm whitespace-pre-wrap">
                        {message.content as string}
                      </p>
                    ) : message.error ? (
                      <p className="text-sm" style={{ color: '#ef4444' }}>{message.error}</p>
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
                    <div 
                      className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                      style={{
                        backgroundColor: darkMode ? '#ffffff' : '#000000'
                      }}
                    >
                      <User className="h-4 w-4" style={{ color: darkMode ? '#000000' : '#ffffff' }} />
                    </div>
                  )}
                </div>
              ))}
              {isTyping && (
                <div className="flex gap-4 justify-start">
                  <div 
                    className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{
                      background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)'
                    }}
                  >
                    <MessageSquare className="w-4 h-4 text-white" />
                  </div>
                  <div 
                    className="rounded-2xl px-4 py-3"
                    style={{
                      backgroundColor: darkMode ? '#1f1f1f' : '#f5f5f5'
                    }}
                  >
                    <MessageLoading />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div 
          className="border-t p-4"
          style={{
            borderColor: darkMode ? '#404040' : '#e5e5e5',
            backgroundColor: darkMode ? '#000000' : '#ffffff'
          }}
        >
          <div className="max-w-3xl mx-auto">
            <div 
              className="flex items-end gap-2 rounded-3xl p-2"
              style={{
                backgroundColor: darkMode ? '#1f1f1f' : '#f5f5f5'
              }}
            >
              <button 
                className="p-2 rounded-full transition-colors"
                style={{
                  color: darkMode ? '#a3a3a3' : '#737373'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = darkMode ? '#2a2a2a' : '#e5e5e5';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <Paperclip className="w-5 h-5" />
              </button>
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message Incentive AI..."
                rows={1}
                className="flex-1 bg-transparent resize-none outline-none px-2 py-2 max-h-[200px]"
                style={{
                  color: darkMode ? '#ffffff' : '#000000'
                }}
              />
              <button 
                className="p-2 rounded-full transition-colors"
                style={{
                  color: darkMode ? '#a3a3a3' : '#737373'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = darkMode ? '#2a2a2a' : '#e5e5e5';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim()}
                className="p-2 rounded-full transition-colors"
                style={{
                  backgroundColor: inputValue.trim() 
                    ? (darkMode ? '#ffffff' : '#000000')
                    : (darkMode ? '#2a2a2a' : '#e5e5e5'),
                  color: inputValue.trim() 
                    ? (darkMode ? '#000000' : '#ffffff')
                    : (darkMode ? '#a3a3a3' : '#737373'),
                  cursor: inputValue.trim() ? 'pointer' : 'not-allowed'
                }}
                onMouseEnter={(e) => {
                  if (inputValue.trim()) {
                    e.currentTarget.style.backgroundColor = darkMode ? '#e5e5e5' : '#404040';
                  }
                }}
                onMouseLeave={(e) => {
                  if (inputValue.trim()) {
                    e.currentTarget.style.backgroundColor = darkMode ? '#ffffff' : '#000000';
                  }
                }}
              >
                <ArrowUp className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;