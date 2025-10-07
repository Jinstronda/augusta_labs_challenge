# ResultsDisplay Component

## Quick Start

The ResultsDisplay component is a smart routing component that displays query results based on the backend's query classification.

## Usage

```typescript
import { ResultsDisplay } from './components/ResultsDisplay';
import { QueryResponse } from './types/api';

function MyComponent() {
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <ResultsDisplay
      response={response}
      isLoading={isLoading}
      error={error}
      onCompanyClick={(id) => navigate(`/company/${id}`)}
      onIncentiveClick={(id) => navigate(`/incentive/${id}`)}
    />
  );
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `response` | `QueryResponse \| null` | Yes | API response with results |
| `isLoading` | `boolean` | Yes | Loading state indicator |
| `error` | `string \| null` | Yes | Error message if any |
| `onCompanyClick` | `(id: number) => void` | No | Callback when company is clicked |
| `onIncentiveClick` | `(id: string) => void` | No | Callback when incentive is clicked |

## States

### 1. Initial State
When `response === null` and `isLoading === false`, nothing is rendered.

### 2. Loading State
When `isLoading === true`, shows an animated skeleton loader.

### 3. Success State
When `response !== null` and `error === null`:
- **INCENTIVE queries** → Shows IncentiveCard(s)
- **COMPANY queries** → Shows CompanyCard(s)

### 4. Empty State
When `response.result_count === 0`, shows "No results found" with suggestions.

### 5. Error State
When `error !== null`, shows error message with contextual suggestions.

## Testing

### Run the Demo
To see all component states in action:

```typescript
// In your App.tsx or test file
import { ResultsDisplayDemo } from './components/ResultsDisplay.demo';

function App() {
  return <ResultsDisplayDemo />;
}
```

The demo includes:
- Loading state
- Incentive results
- Company results
- Empty state
- Network error
- Timeout error
- Generic error

### Manual Testing Checklist

1. **Loading State**
   - [ ] Skeleton loader appears
   - [ ] Animation is smooth
   - [ ] Structure matches result cards

2. **Incentive Results**
   - [ ] IncentiveCard is displayed
   - [ ] Company cards are clickable
   - [ ] Metadata is shown (count, time)

3. **Company Results**
   - [ ] CompanyCard is displayed
   - [ ] Incentive cards are clickable
   - [ ] Metadata is shown (count, time)

4. **Empty State**
   - [ ] "No results found" message appears
   - [ ] Suggestions are contextual
   - [ ] Icon is displayed

5. **Error States**
   - [ ] Network error shows correct message
   - [ ] Timeout error shows correct message
   - [ ] Generic error shows correct message
   - [ ] Suggestions are helpful

## Integration

### With API Service

```typescript
import { queryIncentivesOrCompanies } from './services/api';
import { ResultsDisplay } from './components/ResultsDisplay';

function SearchPage() {
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await queryIncentivesOrCompanies(query);
      setResponse(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <input onChange={(e) => handleSearch(e.target.value)} />
      <ResultsDisplay
        response={response}
        isLoading={isLoading}
        error={error}
      />
    </div>
  );
}
```

### With React Router

```typescript
import { useNavigate } from 'react-router-dom';
import { ResultsDisplay } from './components/ResultsDisplay';

function SearchPage() {
  const navigate = useNavigate();

  return (
    <ResultsDisplay
      response={response}
      isLoading={isLoading}
      error={error}
      onCompanyClick={(id) => navigate(`/company/${id}`)}
      onIncentiveClick={(id) => navigate(`/incentive/${id}`)}
    />
  );
}
```

## Styling

The component uses TailwindCSS utility classes. Key classes:

- **Cards:** `bg-white rounded-lg shadow-lg p-6`
- **Skeleton:** `animate-pulse` with gray backgrounds
- **Spacing:** `space-y-4` for vertical rhythm
- **Text:** Semantic colors (gray-900, gray-600, blue-600, red-400)

## Accessibility

- Semantic HTML structure
- Clear visual hierarchy
- Descriptive error messages
- Loading state indication
- Keyboard navigation (via child components)

## Performance

- Conditional rendering (only renders needed state)
- Efficient array mapping
- No unnecessary re-renders
- Lightweight skeleton loader

## Dependencies

- React
- TypeScript
- TailwindCSS
- IncentiveCard component
- CompanyCard component
- types/api.ts

## Files

```
frontend/src/components/
├── ResultsDisplay.tsx              # Main component
├── ResultsDisplay.demo.tsx         # Interactive demo
├── ResultsDisplay.README.md        # This file
├── ResultsDisplay.SUMMARY.md       # Detailed documentation
└── ResultsDisplay.VERIFICATION.md  # Verification checklist
```

## Troubleshooting

### Component doesn't render
- Check that `response` is not null
- Check that `isLoading` is false
- Check that `error` is null

### Wrong card type displayed
- Verify `response.query_type` is correct
- Check type guards are working
- Verify backend classification is correct

### Click handlers not working
- Ensure callbacks are passed as props
- Check that child components receive callbacks
- Verify event propagation is not stopped

### Styling issues
- Ensure TailwindCSS is configured
- Check that parent container has proper width
- Verify no conflicting CSS

## Next Steps

This component is ready to be integrated into:
1. **ChatInterface** (task 15) - Display results in chat
2. **Main App** (task 16) - Routing and navigation
3. **E2E Testing** (task 21) - Full flow testing

## Support

For questions or issues:
1. Check the SUMMARY.md for detailed documentation
2. Check the VERIFICATION.md for implementation details
3. Run the demo file to see all states
4. Review the backend models for API structure
