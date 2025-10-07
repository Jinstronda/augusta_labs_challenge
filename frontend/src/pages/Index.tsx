import { useState, useRef, useEffect } from "react";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import ChatHeader from "@/components/ChatHeader";
import { queryIncentivesOrCompanies, ApiError, waitForBackend } from "@/services/api";
import type { QueryResponse } from "@/types/api";
import { Loader2 } from "lucide-react";
import { useLocation } from "react-router-dom";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  data?: QueryResponse;
  error?: boolean;
}

const suggestions = [
  "Show me digital innovation incentives",
  "Find companies in renewable energy sector",
  "Green technology funding programs",
  "Companies eligible for R&D incentives"
];

// Store chat history outside component to persist across navigation
let chatHistory: Message[] = [];

const Index = () => {
  const location = useLocation();
  const [messages, setMessages] = useState<Message[]>(chatHistory);
  const [isTyping, setIsTyping] = useState(false);
  const [backendReady, setBackendReady] = useState(false);
  const [backendError, setBackendError] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Restore chat history when coming back from detail pages
  useEffect(() => {
    setMessages(chatHistory);
  }, [location]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Check backend health on mount
  useEffect(() => {
    const checkBackend = async () => {
      console.log("Checking backend health...");
      const isReady = await waitForBackend(30, 1000); // Wait up to 30 seconds
      
      if (isReady) {
        console.log("Backend is ready!");
        setBackendReady(true);
      } else {
        console.error("Backend failed to start");
        setBackendError(true);
      }
    };

    checkBackend();
  }, []);

  const handleSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    chatHistory = newMessages; // Persist to global state
    setIsTyping(true);

    try {
      // Call the real API
      const response = await queryIncentivesOrCompanies(text);
      
      // Format response message
      let responseText = "";
      if (response.result_count === 0) {
        responseText = "I couldn't find any results for your query. Try rephrasing or being more specific.";
      } else if (response.query_type === "SPECIFIC_COMPANY") {
        responseText = `Here's the company with its top ${response.results[0]?.eligible_incentives?.length || 0} eligible incentives:`;
      } else if (response.query_type === "COMPANY_GROUP") {
        responseText = `Found ${response.result_count} compan${response.result_count > 1 ? 'ies' : 'y'} matching your criteria:`;
      } else if (response.query_type === "SPECIFIC_INCENTIVE") {
        responseText = `Here's the incentive with its top ${response.results[0]?.matched_companies?.length || 0} matched companies:`;
      } else {
        responseText = `Found ${response.result_count} incentive${response.result_count > 1 ? 's' : ''} matching your criteria:`;
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        isUser: false,
        data: response,
      };
      
      const updatedMessages = [...messages, userMessage, aiMessage];
      setMessages(updatedMessages);
      chatHistory = updatedMessages; // Persist to global state
    } catch (error) {
      console.error("Query error:", error);
      
      let errorMessage = "Sorry, something went wrong. Please try again.";
      if (error instanceof ApiError) {
        errorMessage = error.detail || error.message;
      }

      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: errorMessage,
        isUser: false,
        error: true,
      };
      
      const updatedMessages = [...messages, userMessage, errorMsg];
      setMessages(updatedMessages);
      chatHistory = updatedMessages; // Persist to global state
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (!isTyping) {
      handleSendMessage(suggestion);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    chatHistory = []; // Clear global state too
  };

  // Show loading state while backend is starting
  if (!backendReady && !backendError) {
    return (
      <div className="flex flex-col h-screen bg-background">
        <ChatHeader />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-foreground mb-2">
              Starting Backend...
            </h2>
            <p className="text-muted-foreground">
              Loading AI models and connecting to database
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              This may take up to 30 seconds on first start
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state if backend failed to start
  if (backendError) {
    return (
      <div className="flex flex-col h-screen bg-background">
        <ChatHeader />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md">
            <div className="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⚠️</span>
            </div>
            <h2 className="text-2xl font-semibold text-foreground mb-2">
              Backend Not Available
            </h2>
            <p className="text-muted-foreground mb-4">
              The backend server failed to start or is not responding.
            </p>
            <p className="text-sm text-muted-foreground">
              Please ensure the backend is running:
            </p>
            <code className="block mt-2 p-3 bg-muted rounded-lg text-xs text-left">
              cd backend<br />
              conda activate turing0.1<br />
              uvicorn app.main:app --reload
            </code>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-smooth"
            >
              Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      <ChatHeader onNewChat={messages.length > 0 ? handleNewChat : undefined} />

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-12">
              <h2 className="text-4xl font-semibold text-foreground mb-8">
                How can I help you today?
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    disabled={isTyping || !backendReady}
                    className="p-4 text-left rounded-2xl border border-border bg-card hover:bg-muted transition-smooth text-sm text-foreground disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="py-8">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message.text}
                  isUser={message.isUser}
                  data={message.data}
                  error={message.error}
              