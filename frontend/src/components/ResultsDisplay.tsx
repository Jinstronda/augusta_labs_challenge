import React from 'react';
import type { QueryResponse } from '../types/api';
import { isIncentiveResults, isCompanyResults } from '../types/api';
import { IncentiveCard } from './IncentiveCard';
import { CompanyCard } from './CompanyCard';

interface ResultsDisplayProps {
  response: QueryResponse | null;
  isLoading: boolean;
  error: string | null;
  onCompanyClick?: (companyId: number) => void;
  onIncentiveClick?: (incentiveId: string) => void;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = React.memo(({
  response,
  isLoading,
  error,
  onCompanyClick,
  onIncentiveClick
}) => {
  if (isLoading || !response || error) {
    return null;
  }

  if (response.result_count === 0 || response.results.length === 0) {
    return (
      <div className="text-base leading-7 text-muted-foreground">
        No results found. Try a different search.
      </div>
    );
  }

  if (isIncentiveResults(response)) {
    return (
      <div className="space-y-4">
        {response.results.map((incentive) => (
          <IncentiveCard
            key={incentive.incentive_id}
            incentive={incentive}
            onCompanyClick={onCompanyClick}
          />
        ))}
        <div className="text-xs text-muted-foreground pt-2 border-t border-border">
          {response.result_count} result{response.result_count !== 1 ? 's' : ''} • {response.processing_time.toFixed(2)}s
        </div>
      </div>
    );
  }

  if (isCompanyResults(response)) {
    return (
      <div className="space-y-4">
        {response.results.map((company) => (
          <CompanyCard
            key={company.company_id}
            company={company}
            onIncentiveClick={onIncentiveClick}
          />
        ))}
        <div className="text-xs text-muted-foreground pt-2 border-t border-border">
          {response.result_count} result{response.result_count !== 1 ? 's' : ''} • {response.processing_time.toFixed(2)}s
        </div>
      </div>
    );
  }

  return null;
});

export default ResultsDisplay;