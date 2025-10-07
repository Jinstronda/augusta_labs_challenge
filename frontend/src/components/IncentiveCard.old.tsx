/**
 * IncentiveCard Component
 * 
 * Displays an incentive with its metadata and top 5 matching companies.
 * Companies are shown as clickable cards with rank badges and score indicators.
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

import React from 'react';
import type { IncentiveResult } from '../types/api';

interface IncentiveCardProps {
  incentive: IncentiveResult;
  onCompanyClick?: (companyId: number) => void;
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

export const IncentiveCard: React.FC<IncentiveCardProps> = React.memo(({ 
  incentive, 
  onCompanyClick 
}) => {
  const handleCompanyClick = (companyId: number) => {
    if (onCompanyClick) {
      onCompanyClick(companyId);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
      {/* Incentive Header */}
      <div className="border-b pb-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {incentive.title}
        </h2>
        
        {/* Incentive Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600 mt-3">
          {incentive.sector && (
            <div>
              <span className="font-semibold">Sector:</span> {incentive.sector}
            </div>
          )}
          {incentive.geo_requirement && (
            <div>
              <span className="font-semibold">Geographic Requirement:</span> {incentive.geo_requirement}
            </div>
          )}
          {incentive.eligible_actions && (
            <div className="col-span-1 md:col-span-2">
              <span className="font-semibold">Eligible Actions:</span> {incentive.eligible_actions}
            </div>
          )}
          {incentive.funding_rate && (
            <div>
              <span className="font-semibold">Funding Rate:</span> {incentive.funding_rate}
            </div>
          )}
          {incentive.investment_eur && (
            <div>
              <span className="font-semibold">Investment:</span> {incentive.investment_eur}
            </div>
          )}
        </div>
      </div>

      {/* Description */}
      {(incentive.ai_description || incentive.description) && (
        <div className="text-gray-700">
          <p className="text-sm leading-relaxed">
            {incentive.ai_description || incentive.description}
          </p>
        </div>
      )}

      {/* Top Companies Section */}
      {incentive.matched_companies && incentive.matched_companies.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <span>Top Matching Companies</span>
            <span className="text-sm font-normal text-gray-500">
              (Ranked by Universal Match Score)
            </span>
          </h3>

          <div className="space-y-2">
            {incentive.matched_companies.map((company) => (
              <div
                key={company.id}
                onClick={() => handleCompanyClick(company.id)}
                className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer group"
              >
                <div className="flex items-start gap-3">
                  {/* Rank Badge */}
                  <div
                    className={`flex-shrink-0 w-8 h-8 rounded-full ${getRankBadgeColor(
                      company.rank
                    )} text-white flex items-center justify-center font-bold text-sm`}
                  >
                    {company.rank || '?'}
                  </div>

                  {/* Company Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                          {company.name}
                        </h4>
                        {company.cae_classification && (
                          <p className="text-xs text-gray-600 mt-1">
                            {company.cae_classification}
                          </p>
                        )}
                      </div>

                      {/* Score Badge */}
                      {company.company_score !== null && (
                        <div className="flex-shrink-0 text-right">
                          <div
                            className={`inline-block px-2 py-1 rounded text-white text-xs font-bold ${getScoreColor(
                              company.company_score
                            )}`}
                          >
                            {(company.company_score * 100).toFixed(0)}%
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {getScoreLabel(company.company_score)}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Score Progress Bar */}
                    {company.company_score !== null && (
                      <div className="mt-3">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all ${getScoreColor(
                              company.company_score
                            )}`}
                            style={{ width: `${company.company_score * 100}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Additional Info */}
                    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600">
                      {company.location_address && (
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
                              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                            />
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                          </svg>
                          <span className="truncate max-w-xs">
                            {company.location_address}
                          </span>
                        </div>
                      )}
                      {company.website && (
                        <a
                          href={company.website}
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
                          <span>Website</span>
                        </a>
                      )}
                    </div>

                    {/* Activities Preview */}
                    {company.activities && (
                      <p className="mt-2 text-xs text-gray-600 line-clamp-2">
                        {company.activities}
                      </p>
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

      {/* No Companies Message */}
      {(!incentive.matched_companies || incentive.matched_companies.length === 0) && (
        <div className="text-center py-8 text-gray-500">
          <p>No matching companies found for this incentive.</p>
        </div>
      )}
    </div>
  );
});
