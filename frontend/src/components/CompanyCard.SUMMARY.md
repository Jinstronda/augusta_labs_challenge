# CompanyCard Component - Implementation Summary

## Overview
The CompanyCard component displays a company with its metadata and eligible incentives. It's the counterpart to IncentiveCard, showing incentives instead of companies.

## Component Structure

### Props Interface
```typescript
interface CompanyCardProps {
  company: CompanyResult;
  onIncentiveClick?: (incentiveId: string) => void;
}
```

### Data Types Used
- `CompanyResult` from `../types/api.ts`
- `IncentiveMatch` from `../types/api.ts`

## Features Implemented

### 1. Company Header Section
- **Company Name**: Large, bold heading
- **CAE Classification**: Industry classification code and description
- **Location**: Address with location icon
- **Website**: Clickable link with external link icon

### 2. Business Activities Section
- **Expandable Description**: Shows first 200 characters with "Show more/less" toggle
- **Conditional Rendering**: Only shows if activities exist
- **User-Friendly**: Prevents overwhelming users with long text

### 3. Eligible Incentives Section
- **Clickable Cards**: Each incentive is a clickable card
- **Rank Badges**: Color-coded badges (gold/silver/bronze for top 3)
- **Score Indicators**: Percentage badges with color coding
- **Progress Bars**: Visual representation of match scores
- **Hover Effects**: Border color change and shadow on hover
- **Additional Info**: Icons for geo requirements, funding rates, source links
- **Description Preview**: 2-line clamp of incentive description

### 4. Score Color Coding
- **Green (0.80-1.00)**: Excellent match
- **Blue (0.65-0.79)**: Strong match
- **Yellow (0.50-0.64)**: Moderate match
- **Orange (0.35-0.49)**: Weak match
- **Red (0.00-0.34)**: Poor match

### 5. Rank Badge Colors
- **Gold (Rank 1)**: Yellow background
- **Silver (Rank 2)**: Gray background
- **Bronze (Rank 3)**: Orange background
- **Other Ranks**: Blue background

### 6. Interactive Elements
- **Incentive Cards**: Click to navigate to incentive detail view
- **Website Link**: Opens in new tab (stops propagation to prevent card click)
- **Source Links**: Opens incentive source in new tab
- **Expand/Collapse**: Toggle for long activity descriptions

### 7. Empty State
- Shows friendly message when no eligible incentives exist
- Centered with gray text

### 8. Score Formula Info
- Blue info box at bottom explaining the scoring formula
- Matches the formula from EQUATION.md

## Styling Approach

### TailwindCSS Classes Used
- **Layout**: `flex`, `grid`, `space-y-*`, `gap-*`
- **Colors**: `bg-*`, `text-*`, `border-*`
- **Typography**: `font-bold`, `text-*xl`, `truncate`, `line-clamp-2`
- **Effects**: `hover:*`, `transition-all`, `shadow-*`, `rounded-*`
- **Responsive**: `md:*` breakpoints for tablet/desktop

### Consistency with IncentiveCard
- Same color scheme and score interpretation
- Same rank badge styling
- Same hover effects and transitions
- Same card structure and spacing
- Same icon usage and placement

## Icons Used
All icons are inline SVG from Heroicons:
- **Location**: Map pin icon
- **External Link**: Arrow pointing to top-right
- **Globe**: Geographic requirement icon
- **Currency**: Funding rate icon

## Accessibility Considerations
- Semantic HTML structure
- Clear visual hierarchy
- Sufficient color contrast
- Hover states for interactive elements
- External links open in new tab with `rel="noopener noreferrer"`

## Performance Optimizations
- Conditional rendering to avoid unnecessary DOM nodes
- `line-clamp-2` for description truncation (CSS-based)
- Event handler memoization through component props
- Minimal re-renders with proper state management

## Data Flow
1. Component receives `CompanyResult` from parent
2. Displays company metadata in header
3. Maps over `eligible_incentives` array (pre-sorted by score)
4. Renders each incentive as a clickable card
5. Calls `onIncentiveClick` when user clicks an incentive card

## Integration Points
- **Parent Component**: Provides company data and click handler
- **Router**: Click handler should navigate to `/incentive/:id`
- **API**: Data comes from `/api/company/:id` endpoint
- **Types**: Uses interfaces from `types/api.ts`

## Testing Considerations
- Test with companies that have 0, 1, and 5 incentives
- Test with long activity descriptions (expansion)
- Test with missing optional fields (website, location, etc.)
- Test click handlers (incentive cards, website links)
- Test responsive layout on different screen sizes

## Files Created
1. `CompanyCard.tsx` - Main component
2. `CompanyCard.demo.tsx` - Demo with sample data
3. `CompanyCard.SUMMARY.md` - This file
4. `CompanyCard.VERIFICATION.md` - Verification checklist

## Next Steps
- Integrate into ResultsDisplay component
- Connect to React Router for navigation
- Add to CompanyDetailPage
- Write unit tests with React Testing Library
- Test with real API data
