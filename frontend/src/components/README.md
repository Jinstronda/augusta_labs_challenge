# Components

This directory contains reusable UI components for the Incentive Query System.

## QueryInput

A ChatGPT-like input component for submitting queries.

### Features

- **Auto-resizing textarea**: Grows with content up to 200px max height
- **Submit button with loading state**: Shows spinner during API calls
- **Keyboard shortcuts**: 
  - `Enter` to submit
  - `Shift+Enter` for new line
- **Input validation**: 
  - Minimum 1 character (non-empty)
  - Maximum 500 characters (matches backend validation)
- **Character counter**: Shows current length and limit
- **Error handling**: Displays validation errors
- **Accessibility**: ARIA labels and keyboard navigation
- **Dark mode support**: Adapts to system theme

### Props

```typescript
interface QueryInputProps {
  onSubmit: (query: string) => Promise<void>;
  isLoading: boolean;
  placeholder?: string;
}
```

- `onSubmit`: Async function called when user submits a query
- `isLoading`: Boolean to show loading state and disable input
- `placeholder`: Optional placeholder text (default: "Ask about incentives or companies...")

### Usage

```tsx
import { QueryInput } from './components/QueryInput';
import { queryIncentivesOrCompanies } from './services/api';

function App() {
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (query: string) => {
    setIsLoading(true);
    try {
      const result = await queryIncentivesOrCompanies(query);
      // Handle result...
    } catch (error) {
      // Handle error...
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <QueryInput
      onSubmit={handleSubmit}
      isLoading={isLoading}
    />
  );
}
```

### Validation Rules

The component enforces the same validation rules as the backend (`backend/app/models.py`):

- **Minimum length**: 1 character (after trimming whitespace)
- **Maximum length**: 500 characters

These rules match the backend's `QueryRequest` model:
```python
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
```

### Styling

The component uses TailwindCSS for styling and supports:
- Light and dark modes
- Responsive design
- Smooth transitions
- Focus states
- Disabled states

### Accessibility

- Semantic HTML with proper ARIA attributes
- Keyboard navigation support
- Screen reader friendly
- Error announcements via `role="alert"`

## Example

See `QueryInput.example.tsx` for a complete working example.
