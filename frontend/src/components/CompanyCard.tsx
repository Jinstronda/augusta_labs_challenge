import React, { useState } from 'react';
import { MapPin, ExternalLink, ChevronDown, ChevronUp, Building2 } from 'lucide-react';
import type { CompanyResult } from '../types/api';

interface CompanyCardProps {
  company: CompanyResult;
  onIncentiveClick?: (incentiveId: string) => void;
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

export const CompanyCard: React.FC<CompanyCardProps> = React.memo(({
  company,
  onIncentiveClick
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const needsExpansion = company.activities && company.activities.length > 300;
  const displayedActivities = needsExpansion && !isExpanded && company.activities
    ? company.activities.substring(0, 300) + '...'
    : company.activities;

  return (
    <div className="bg-card border border-border rounded-xl shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden">
      <div className="p-6 space-y-4">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
            <Building2 className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-foreground mb-1.5 leading-tight">
              {company.company_name}
            </h3>
            {company.cae_classification && (
              <p className="text-sm text-muted-foreground">{company.cae_classification}</p>
            )}
          </div>
        </div>

        {company.activities && (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground leading-relaxed">{displayedActivities}</p>
            {needsExpansion && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="inline-flex items-center gap-1 text-sm text-primary hover:text-primary/80 transition-colors font-medium group"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="h-4 w-4 group-hover:-translate-y-0.5 transition-transform" />
                    Show less
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4 group-hover:translate-y-0.5 transition-transform" />
                    Show more
                  </>
                )}
              </button>
            )}
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {company.location_address && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-accent text-accent-foreground">
              <MapPin className="h-3 w-3" />
              {company.location_address}
            </span>
          )}
          {company.website && (
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-accent text-accent-foreground transition-all hover:bg-primary hover:text-primary-foreground hover:scale-105"
            >
              <ExternalLink className="h-3 w-3" />
              Website
            </a>
          )}
        </div>
      </div>

      {company.eligible_incentives && company.eligible_incentives.length > 0 && (
        <div className="px-6 pb-6 space-y-3 border-t border-border">
          <div className="flex items-center gap-2 pt-4">
            <div className="h-px flex-1 bg-border" />
            <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Eligible Incentives ({company.eligible_incentives.length})
            </h4>
            <div className="h-px flex-1 bg-border" />
          </div>
          <div className="space-y-2">
            {company.eligible_incentives.map((incentive) => (
              <button
                key={incentive.incentive_id}
                onClick={() => onIncentiveClick?.(incentive.incentive_id)}
                className="w-full text-left p-4 rounded-lg bg-muted/50 hover:bg-muted transition-all duration-200 border border-border/50 hover:border-primary/40 hover:shadow-sm group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm mb-1 group-hover:text-primary transition-colors">
                      {incentive.title}
                    </div>
                    {incentive.sector && (
                      <div className="text-xs text-muted-foreground">{incentive.sector}</div>
                    )}
                    {(incentive.ai_description || incentive.description) && (
                      <div className="text-xs text-muted-foreground mt-1 line-clamp-2">
                        {incentive.ai_description || incentive.description}
                      </div>
                    )}
                  </div>
                  {incentive.company_score !== null && (
                    <div className="flex-shrink-0">
                      {getScoreBadge(incentive.company_score)}
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

export default CompanyCard;