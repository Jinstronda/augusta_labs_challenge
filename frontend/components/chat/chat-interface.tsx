"use client";

import * as React from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowUp,
  BookOpen,
  Code,
  MessageSquare,
  Mic,
  Paperclip,
  PenTool,
  Plus,
  Search,
  Settings,
  User,
} from "lucide-react";

import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { MessageLoading } from "@/components/ui/message-loading";
import { Typewriter } from "@/components/ui/typewriter";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const links = [
  {
    label: "New Chat",
    href: "#",
    icon: <Plus className="text-foreground h-5 w-5 flex-shrink-0" aria-hidden="true" />,
  },
  {
    label: "Chat History",
    href: "#",
    icon: <MessageSquare className="text-foreground h-5 w-5 flex-shrink-0" aria-hidden="true" />,
  },
  {
    label: "Settings",
    href: "#",
    icon: <Settings className="text-foreground h-5 w-5 flex-shrink-0" aria-hidden="true" />,
  },
];

const suggestions = [
  { icon: <BookOpen className="w-5 h-5" aria-hidden="true" />, text: "Explain quantum computing" },
  { icon: <Code className="w-5 h-5" aria-hidden="true" />, text: "Write a React component" },
  { icon: <PenTool className="w-5 h-5" aria-hidden="true" />, text: "Draft a professional email" },
  { icon: <Search className="w-5 h-5" aria-hidden="true" />, text: "Research latest AI trends" },
];

export function ChatInterface() {
  const [open, setOpen] = React.useState(false);
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [inputValue, setInputValue] = React.useState("");
  const [isTyping, setIsTyping] = React.useState(false);

  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = React.useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  React.useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  React.useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    const newHeight = Math.min(textarea.scrollHeight, 200);
    textarea.style.height = `${newHeight}px`;
  }, [inputValue]);

  const handleSendMessage = React.useCallback(() => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm a demo assistant. This is a simulated response to your message.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1500);
  }, [inputValue]);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestion = (text: string) => {
    setInputValue(text);
    textareaRef.current?.focus();
  };

  return (
    <div className="flex flex-col md:flex-row bg-background w-full h-screen overflow-hidden">
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-10">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            <Logo />
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link) => (
                <SidebarLink key={link.label} link={link} />
              ))}
            </div>
          </div>
          <div>
            <SidebarLink
              link={{
                label: "User Profile",
                href: "#",
                icon: (
                  <div className="h-7 w-7 flex-shrink-0 rounded-full bg-primary flex items-center justify-center">
                    <User className="h-4 w-4 text-primary-foreground" aria-hidden="true" />
                  </div>
                ),
              }}
            />
          </div>
        </SidebarBody>
      </Sidebar>

      <div className="flex flex-1 flex-col h-full overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full max-w-3xl mx-auto">
              <div className="mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
                  <MessageSquare className="w-8 h-8 text-white" aria-hidden="true" />
                </div>
              </div>
              <h1 className="text-3xl md:text-4xl font-bold mb-4 text-center">
                <Typewriter
                  text={["How can I help you today?"]}
                  speed={70}
                  loop={false}
                  showCursor={false}
                />
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full mt-8">
                {suggestions.map((suggestion) => (
                  <motion.button
                    key={suggestion.text}
                    type="button"
                    onClick={() => handleSuggestion(suggestion.text)}
                    whileHover={{ y: -2, scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    className="flex items-center gap-3 p-4 rounded-xl border border-border bg-muted/40 hover:bg-accent transition-colors text-left"
                  >
                    <div className="text-primary">{suggestion.icon}</div>
                    <span className="text-sm text-foreground">{suggestion.text}</span>
                  </motion.button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex gap-4",
                    message.role === "user" ? "justify-end" : "justify-start",
                  )}
                >
                  {message.role === "assistant" ? (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="w-4 h-4 text-white" aria-hidden="true" />
                    </div>
                  ) : null}
                  <div
                    className={cn(
                      "rounded-2xl px-4 py-3 max-w-[80%] text-sm whitespace-pre-wrap shadow-sm",
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-foreground",
                    )}
                  >
                    {message.content}
                  </div>
                  {message.role === "user" ? (
                    <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-primary-foreground" aria-hidden="true" />
                    </div>
                  ) : null}
                </div>
              ))}
              <AnimatePresence>
                {isTyping ? (
                  <motion.div
                    key="assistant-typing"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 8 }}
                    transition={{ duration: 0.2, ease: "easeInOut" }}
                    className="flex gap-4 justify-start"
                  >
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="w-4 h-4 text-white" aria-hidden="true" />
                    </div>
                    <div className="rounded-2xl px-4 py-3 bg-muted">
                      <MessageLoading />
                    </div>
                  </motion.div>
                ) : null}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="border-t border-border p-4 bg-background">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-end gap-2 bg-muted rounded-3xl p-2">
              <button
                type="button"
                aria-label="Attach file"
                className="p-2 hover:bg-accent rounded-full transition-colors text-muted-foreground"
              >
                <Paperclip className="w-5 h-5" aria-hidden="true" />
              </button>
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(event) => setInputValue(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message ChatGPT..."
                rows={1}
                className="flex-1 bg-transparent resize-none outline-none text-foreground placeholder:text-muted-foreground px-2 py-2 max-h-[200px]"
              />
              <button
                type="button"
                aria-label="Record voice message"
                className="p-2 hover:bg-accent rounded-full transition-colors text-muted-foreground"
              >
                <Mic className="w-5 h-5" aria-hidden="true" />
              </button>
              <button
                type="button"
                onClick={handleSendMessage}
                aria-label="Send message"
                disabled={!inputValue.trim()}
                className={cn(
                  "p-2 rounded-full transition-colors",
                  inputValue.trim()
                    ? "bg-primary text-primary-foreground hover:bg-primary/90"
                    : "bg-muted-foreground/20 text-muted-foreground cursor-not-allowed",
                )}
              >
                <ArrowUp className="w-5 h-5" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Logo() {
  return (
    <Link
      href="#"
      className="font-normal flex space-x-2 items-center text-sm text-foreground py-1 relative z-20"
    >
      <div className="h-5 w-6 bg-primary rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-medium text-foreground whitespace-pre"
      >
        ChatGPT
      </motion.span>
    </Link>
  );
}
