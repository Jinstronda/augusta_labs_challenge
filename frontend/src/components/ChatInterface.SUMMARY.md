# ChatInterface Component - Summary

## Overview
A ChatGPT-like interface component for querying incentives and companies. Manages chat history, integrates with QueryInput and ResultsDisplay, and provides a clean, intuitive user experience.

## File Location
`frontend/src/components/ChatInterface.tsx`

## Component Signature
```typescript
interface ChatInterfaceProps {
  onCompanyClick?: (companyId: number) => void;
  onIncentiveClick?: (incentiveId: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps>
```

## Key Features

### 1. Chat Message History
- Maintains array of user queries and assistant responses
- Each message has unique ID, type, content, and timestamp
- Supports both text (user) and QueryResponse (assistant) content
- Error messages displayed inline

### 2. Auto-scroll
- Automatically scrolls to latest message when new messages arrive
- Smooth scroll animation for better UX
- Uses ref-based scrolling

### 3. "New Chat" Button
- Clears all message history
- Only visible when messages exist
- Located in header for easy access

### 4. ChatGPT-like UI
- Full-height layout with header, messages, and input
- User messages: Blue bubbles on right
- Assistant messages: White cards on left with avatar
- Empty state with welcome message and example queries
- Loading state with animated dots
- Dark mode support

### 5. Integration
- Uses QueryInput for user input
- Uses ResultsDisplay for showing results
- Calls queryIncentivesOrCompanies API
- Passes navigation callbacks to child components

## Usage Example

```typescript
import { ChatInterface } from './components/ChatInterface';

function App() {
  const handleCompanyClick = (companyId: number) => {
    navigate(`/company/${companyId}`);
  };

  const handleIncentiveClick = (incentiveId: string) => {
    navigate(`/incentive/${incentiveId}`);
  };

  return (
    <div className="h-screen">
      <ChatInterface
        onCompanyClick={handleCompanyClick}
        onIncentiveClick={handleIncentiveClick}
      />
    </div>
  );
}
```

## State Management

### Messages State
```typescript
interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string | QueryResponse;
  timestamp: Date;
  error?: string;
}

const [messages, setMessages] = useState<ChatMessage[]>([]);
```

### Loading State
```typescript
const [isLoading, setIsLoading] = useState(false);
```

## Key Functions

### handleSubmit
```typescript
const handleSubmit = async (query: string) => {
  // 1. Add user message to history
  // 2. Call API
  // 3. Add assistant response to history
  // 4. Handle errors
}
```

### handleNewChat
```typescript
const handleNewChat = () => {
  setMessages([]);
}
```

### renderMessage
```typescript
const renderMessage = (message: ChatMessage) => {
  // Renders user or assistant message with appropriate styling
}
```

## UI Structure

```
┌─────────────────────────────────────────┐
│  Header                                  │
│  [Logo] Incentive Query System  [New]   │
├─────────────────────────────────────────┤
│                                          │
│  Messages Area (scrollable)              │
│                                          │
│  User: What incentives for tech?        │
│                                          │
│  Assistant:                              │
│  [IncentiveCard with companies]          │
│                                          │
│  User: Tell me about TechCorp           │
│                                          │
│  Assistant:                              │
│  [CompanyCard with incentives]           │
│                                          │
├─────────────────────────────────────────┤
│  Input Area                              │
│  [QueryInput component]                  │
└─────────────────────────────────────────┘
```

## Empty State
When no messages exist, shows:
- Welcome message
- System description
- 4 example queries as clickable buttons
- Clicking example submits that query

## Loading State
While processing query:
- Shows "Thinking..." with animated dots
- QueryInput is disabled
- Submit button shows spinner

## Error Handling
- API errors displayed in red box
- Network errors show helpful message
- Timeout errors suggest simpler query
- Errors don't break the chat flow

## Styling
- TailwindCSS for all styling
- Responsive design (mobile, tablet, desktop)
- Dark mode support
- Smooth transitions and animations
- Accessible color contrast

## Dependencies
- React (useState, useRef, useEffect)
- QueryInput component
- ResultsDisplay component
- API service (queryIncentivesOrCompanies)
- Types from api.ts

## Requirements Satisfied
- ✅ 4.1: ChatGPT-like interface
- ✅ 4.3: User message display
- ✅ 4.4: Loading indicator
- ✅ 4.5: Formatted response display
- ✅ 4.7: Auto-scroll
- ✅ 4.8: "New Chat" button

## Next Steps
This component is ready to be integrated into the main App component (Task 16) with React Router for navigation between chat, incentive detail, and company detail pages.

## Files Created
1. `ChatInterface.tsx` - Main component
2. `ChatInterface.demo.tsx` - Usage examples
3. `ChatInterface.VERIFICATION.md` - Detailed verification
4. `ChatInterface.SUMMARY.md` - This file
