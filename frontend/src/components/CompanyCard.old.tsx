/**
 * CompanyCard Component
 * 
 * Displays a company with its metadata and eligible incentives.
 * Incentives are shown as clickable cards with rank badges and score indicators.
 * 
 * Scoring Formula (from EQUATION.md):
 * FINAL SCORE = 0.50S + 0.20M + 0.10G + 0.15O′ + 0.05W
 * 
 * Score Interpretation:
 * - 0.80-1.00: Excellent match (green)
 * - 0.65-0.79: Strong match (blue)
 * - 0.50-0.64: Moderate match (yellow)
 * - 0.35-0.49: Weak match (orange)
 * - 0.00-0.34: Poor match (red)
 */

import React, { useState } from 'react';
import type { CompanyResult } from '../types/api';

interface CompanyCardProps {
  company: CompanyResult;
  onIncentiveClick?: (incentiveId: string) => void;
}

/**
 * Get color classes based on company score
 */
const getScoreColor = (score: number | null): string => {
  if (score === null) return 'bg-gray-400';
  if (score >= 0.80) return 'bg-green-500';
  if (score >= 0.65) return 'bg-blue-500';
  if (score >= 0.50) return 'bg-yellow-500';
  if (score >= 0.35) return 'bg-orange-500';
  return 'bg-red-500';
};

/**
 * Get score interpretation text
 */
const getScoreLabel = (score: number | null): string => {
  if (score === null) return 'Unknown';
  if (score >= 0.80) return 'Excellent match';
  if (score >= 0.65) return 'Strong match';
  if (score >= 0.50) return 'Moderate match';
  if (score >= 0.35) return 'Weak match';
  return 'Poor match';
};

/**
 * Get rank badge color
 */
const getRankBadgeColor = (rank: number | null): string => {
  if (rank === null) return 'bg-gray-500';
  if (rank === 1) return 'bg-yellow-500'; // Gold
  if (rank === 2) return 'bg-gray-400'; // Silver
  if (rank === 3) return 'bg-orange-600'; // Bronze
  return 'bg-blue-500'; // Other ranks
};

export const CompanyCard: React.FC<CompanyCardProps> = React.memo(({ 
  company, 
  onIncentiveClick 
}) => {
  const [isActivitiesExpanded, setIsActivitiesExpanded] = useState(false);

  const handleIncentiveClick = (incentiveId: string) => {
    if (onIncentiveClick) {
      onIncentiveClick(incentiveId);
    }
  };

  // Check if activities text is long enough to need expansion
  const activitiesNeedsExpansion = company.activities && company.activities.length > 200;
  const displayedActivities = activitiesNeedsExpansion && !isActivitiesExpanded && company.activities
    ? company.activities.substring(0, 200) + '...'
    : company.activities;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
      {/* Company Header */}
      <div className="border-b pb-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {company.company_name}
        </h2>
        
        {/* Company Metadata */}
        <div className="space-y-2 text-sm text-gray-600 mt-3">
          {company.cae_classification && (
            <div>
              <span className="font-semibold">CAE Classification:</span> {company.cae_classification}
            </div>
          )}
          
          {company.location_address && (
            <div className="flex items-start gap-1">
              <svg
                className="w-4 h-4 mt-0.5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span>
                <span className="font-semibold">Location:</span> {company.location_address}
              </span>
            </div>
          )}
          
          {company.website && (
            <div>
              <span className="font-semibold">Website:</span>{' '}
              <a
                href={company.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 hover:underline inline-flex items-center gap-1"
              >
                <span>{company.website}</span>
                <svg
                  className="w-3 h-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
              </a>
            </div>
          )}
        </div>
      </div>

      {/* Activities Description */}
      {company.activities && (
        <div className="text-gray-700">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Business Activities</h3>
          <p className="text-sm leading-relaxed">
            {displayedActivities}
          </p>
          {activitiesNeedsExpansion && (
            <button
              onClick={() => setIsActivitiesExpanded(!isActivitiesExpanded)}
              className="mt-2 text-sm text-blue-600 hover:text-blue-800 hover:underline font-medium"
            >
              {isActivitiesExpanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
      )}

      {/* Eligible Incentives Section */}
      {company.eligible_incentives && company.eligible_incentives.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <span>Eligible Incentives</span>
            <span className="text-sm font-normal text-gray-500">
              (Ranked by Match Score)
            </span>
          </h3>

          <div className="space-y-2">
            {company.eligible_incentives.map((incentive) => (
              <div
                key={incentive.incentive_id}
                onClick={() => handleIncentiveClick(incentive.incentive_id)}
                className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer group"
              >
                <div className="flex items-start gap-3">
                  {/* Rank Badge */}
                  <div
                    className={`flex-shrink-0 w-8 h-8 rounded-full ${getRankBadgeColor(
                      incentive.rank
                    )} text-white flex items-center justify-center font-bold text-sm`}
                  >
                    {incentive.rank || '?'}
                  </div>

                  {/* Incentive Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                          {incentive.title}
                        </h4>
                        {incentive.sector && (
                          <p className="text-xs text-gray-600 mt-1">
                            Sector: {incentive.sector}
                          </p>
                        )}
                      </div>

                      {/* Score Badge */}
                      {incentive.company_score !== null && (
                        <div className="flex-shrink-0 text-right">
                          <div
                            className={`inline-block px-2 py-1 rounded text-white text-xs font-bold ${getScoreColor(
                              incentive.company_score
                            )}`}
                          >
                            {(incentive.company_score * 100).toFixed(0)}%
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {getScoreLabel(incentive.company_score)}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Score Progress Bar */}
                    {incentive.company_score !== null && (
                      <div className="mt-3">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all ${getScoreColor(
                              incentive.company_score
                            )}`}
                            style={{ width: `${incentive.company_score * 100}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Additional Info */}
                    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600">
                      {incentive.geo_requirement && (
                        <div className="flex items-center gap-1">
                          <svg
                            className="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                          </svg>
                          <span className="truncate max-w-xs">
                            {incentive.geo_requirement}
                          </span>
                        </div>
                      )}
                      {incentive.funding_rate && (
                        <div className="flex items-center gap-1">
                          <svg
                            className="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                          </svg>
                          <span>Funding: {incentive.funding_rate}</span>
                        </div>
                      )}
                      {incentive.source_link && (
                        <a
                          href={incentive.source_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="flex items-center gap-1 text-blue-600 hover:text-blue-800 hover:underline"
                        >
                          <svg
                            className="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                            />
                          </svg>
                          <span>Details</span>
                        </a>
                      )}
                    </div>

                    {/* Description Preview */}
                    {(incentive.ai_description || incentive.description) && (
                      <p className="mt-2 text-xs text-gray-600 line-clamp-2">
                        {incentive.ai_description || incentive.description}
                      </p>
                    )}

                    {/* Eligible Actions */}
                    {incentive.eligible_actions && (
                      <div className="mt-2 text-xs text-gray-600">
                        <span className="font-semibold">Eligible Actions:</span> {incentive.eligible_actions}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Score Formula Info */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-xs text-gray-700">
              <span className="font-semibold">Scoring Formula:</span> Final Score = 0.50×Semantic + 0.20×Activity + 0.10×Geographic + 0.15×Organizational + 0.05×Website
            </p>
          </div>
        </div>
      )}

      {/* No Incentives Message */}
      {(!company.eligible_incentives || company.eligible_incentives.length === 0) && (
        <div className="text-center py-8 text-gray-500">
          <p>No eligible incentives found for this company.</p>
        </div>
      )}
    </div>
  );
});
