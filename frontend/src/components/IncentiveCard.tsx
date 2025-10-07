import React from 'react';
import { MapPin, DollarSign, TrendingUp, Sparkles } from 'lucide-react';
import type { IncentiveResult } from '../types/api';

interface IncentiveCardProps {
  incentive: IncentiveResult;
  onCompanyClick?: (companyId: number) => void;
}

const getScoreBadge = (score: number | null) => {
  if (score === null) return null;
  const percentage = (score * 100).toFixed(0);
  let gradientClass = 'from-gray-400 to-gray-500';
  let label = 'Fair';

  if (score >= 0.80) {
    gradientClass = 'from-emerald-400 to-green-500';
    label = 'Excellent';
  } else if (score >= 0.65) {
    gradientClass = 'from-blue-400 to-cyan-500';
    label = 'Strong';
  } else if (score >= 0.50) {
    gradientClass = 'from-yellow-400 to-orange-400';
    label = 'Good';
  } else if (score >= 0.35) {
    gradientClass = 'from-orange-400 to-red-400';
    label = 'Fair';
  } else {
    gradientClass = 'from-red-400 to-pink-500';
    label = 'Weak';
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold text-white bg-gradient-to-r ${gradientClass} shadow-md`}>
        {percentage}%
      </span>
      <span className="text-xs text-muted-foreground">{label}</span>
    </div>
  );
};

export const IncentiveCard: React.FC<IncentiveCardProps> = React.memo(({
  incentive,
  onCompanyClick
}) => {
  return (
    <div className="bg-card border border-border rounded-xl shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden">
      <div className="p-6 space-y-4">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-foreground mb-2 leading-tight">
              {incentive.title}
            </h3>
            {(incentive.ai_description || incentive.description) && (
              <p className="text-sm text-muted-foreground leading-relaxed line-clamp-3">
                {incentive.ai_description || incentive.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {incentive.sector && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-accent text-accent-foreground">
              <Sparkles className="h-3 w-3" />
              {incentive.sector}
            </span>
          )}
          {incentive.geo_requirement && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-accent text-accent-foreground">
              <MapPin className="h-3 w-3" />
              {incentive.geo_requirement}
            </span>
          )}
          {incentive.funding_rate && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-accent text-accent-foreground">
              <DollarSign className="h-3 w-3" />
              {incentive.funding_rate}
            </span>
          )}
        </div>
      </div>

      {incentive.matched_companies && incentive.matched_companies.length > 0 && (
        <div className="px-6 pb-6 space-y-3 border-t border-border">
          <div className="flex items-center gap-2 pt-4">
            <div className="h-px flex-1 bg-border" />
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Top Matches ({incentive.matched_companies.length})
            </h4>
            <div className="h-px flex-1 bg-border" />
          </div>
          <div className="space-y-2">
            {incentive.matched_companies.map((company) => (
              <button
                key={company.id}
                onClick={() => onCompanyClick?.(company.id)}
                className="w-full text-left p-4 rounded-lg bg-muted/50 hover:bg-muted transition-all duration-200 border border-border/50 hover:border-primary/40 hover:shadow-sm group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm mb-1 group-hover:text-primary transition-colors">
                      {company.name}
                    </div>
                    {company.cae_classification && (
                      <div className="text-xs text-muted-foreground">{company.cae_classification}</div>
                    )}
                    {company.location_address && (
                      <div className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {company.location_address}
                      </div>
                    )}
                  </div>
                  {company.company_score !== null && (
                    <div className="flex-shrink-0">
                      {getScoreBadge(company.company_score)}
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

export default IncentiveCard;